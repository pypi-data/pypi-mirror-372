"""Launch workflow nodes on remote resources"""

import os
import copy
import datetime
from time import sleep
from fabric2 import Connection
from fireworks.fw_config import FW_BLOCK_FORMAT
from fireworks import LaunchPad, FWorker
from fireworks.utilities.fw_serializers import recursive_serialize
from fireworks.utilities.fw_serializers import recursive_deserialize
from virtmat.middleware.engine.wfengine import WFEngine
from virtmat.middleware.exceptions import ConfigurationException, InvalidStateException
from virtmat.middleware.utilities import get_logger


class WFEngineRemote(WFEngine):
    """
    A subclass of wfEngine to manage remote workers

    Args:
        host: hostname of the remote resource
        user: username on the remote resource
        conf: configuration command to set up the remote environment

    Passwordless connection via SSH to the remote system must be enabled.
    Otherwise the following error message will occur:
    PasswordRequiredException: private key file is encrypted
    """

    logger = get_logger(__name__)

    def __init__(self, launchpad, qadapter, wf_query, host=None, user=None,
                 conf='', **kwargs):
        super().__init__(launchpad, qadapter, wf_query, **kwargs)
        if not (host and user and qadapter):
            raise ConfigurationException("host, user and qadapter needed.")
        self.host = host
        self.user = user
        self.conf = conf  # for example '. python-3.6.8-custom/bin/activate'
        self.setup_remote_launchpad()
        self.setup_remote_qadapter()
        self.setup_remote_fworker()
        self.setup_remote_configuration()

    def setup_remote_launchpad(self):
        """Create launchpad file for remote worker"""
        lpad = copy.deepcopy(self.launchpad)
        self.remote_launchpad_file = 'launchpad_' + self.name + '.yaml'
        remote_launchpad = LaunchPad.from_dict(lpad.to_db_dict())
        self.remote_launchpad_path = os.path.join(self.launchdir, self.remote_launchpad_file)
        if hasattr(lpad, 'ssl_ca_certs') and lpad.ssl_ca_certs:
            ssl_ca_certs_file = os.path.basename(lpad.ssl_ca_certs)
            ssl_ca_certs_path = os.path.join(self.launchdir, ssl_ca_certs_file)
            remote_launchpad.ssl_ca_certs = ssl_ca_certs_path
        if hasattr(lpad, 'ssl_certfile') and lpad.ssl_certfile:
            ssl_certfile_file = os.path.basename(lpad.ssl_certfile)
            ssl_certfile_path = os.path.join(self.launchdir, ssl_certfile_file)
            remote_launchpad.ssl_certfile = ssl_certfile_path
        remote_launchpad.to_file(self.remote_launchpad_file)
        if hasattr(lpad, 'mongoclient_kwargs'):
            lp_mongo_new = lpad.mongoclient_kwargs
            if 'tlsCAFile' in lp_mongo_new and lp_mongo_new['tlsCAFile']:
                tlscafile = os.path.basename(lp_mongo_new['tlsCAFile'])
                tlscapath = os.path.join(self.launchdir, tlscafile)
                remote_launchpad.mongoclient_kwargs['tlsCAFile'] = tlscapath
            if 'tlsCertificateKeyFile' in lp_mongo_new and lp_mongo_new['tlsCertificateKeyFile']:
                tlscrlfile = os.path.basename(lp_mongo_new['tlsCertificateKeyFile'])
                tlscrlpath = os.path.join(self.launchdir, tlscrlfile)
                remote_launchpad.mongoclient_kwargs['tlsCertificateKeyFile'] = tlscrlpath
            remote_launchpad.to_file(self.remote_launchpad_file)

    def setup_remote_qadapter(self):
        """Create qadapter file for remote worker"""
        self.qadapter_file = 'qadapter_' + self.name + '.yaml'
        self.remote_qadapter_path = os.path.join(self.launchdir, self.qadapter_file)
        if 'pre_rocket' in self.qadapter and self.qadapter['pre_rocket'] is not None:
            commands = self.qadapter['pre_rocket'].split(';')  # List commands of pre_rocket
            if commands[-1] != self.conf:  # Check if the pre_rocket is already modified
                self.qadapter['pre_rocket'] = self.qadapter['pre_rocket'] + ';' + self.conf
        else:
            self.qadapter['pre_rocket'] = self.conf
        self.qadapter['rocket_launch'] = 'rlaunch -l ' + self.remote_launchpad_path + ' singleshot'
        self.qadapter.to_file(self.qadapter_file)

    def setup_remote_fworker(self):
        """Create configuration for remote worker"""
        self.fworker_file = 'fworker_' + self.name + '.yaml'
        self.remote_fworker_path = os.path.join(self.launchdir, self.fworker_file)
        FWorker(name=self.name, category='remote').to_file(self.fworker_file)

    def setup_remote_configuration(self):
        """Create remote launch directory and copy all configuration files"""
        with Connection(host=self.host, user=self.user) as conn:
            conn.run('mkdir -p ' + self.launchdir)
            conn.put(local=self.remote_launchpad_file, remote=self.launchdir)
            conn.put(local=self.qadapter_file, remote=self.launchdir)
            conn.put(local=self.fworker_file, remote=self.launchdir)
            if hasattr(self.launchpad, 'ssl_ca_certs') and self.launchpad.ssl_ca_certs:
                conn.put(local=self.launchpad.ssl_ca_certs, remote=self.launchdir)
            if hasattr(self.launchpad, 'ssl_certfile') and self.launchpad.ssl_certfile:
                conn.put(local=self.launchpad.ssl_certfile, remote=self.launchdir)
            lpad = copy.deepcopy(self.launchpad)
            if hasattr(lpad, 'mongoclient_kwargs'):
                lp_mongo_new = lpad.mongoclient_kwargs
                if 'tlsCAFile' in lp_mongo_new and lp_mongo_new['tlsCAFile']:
                    conn.put(local=lp_mongo_new['tlsCAFile'], remote=self.launchdir)
                if ('tlsCertificateKeyFile' in lp_mongo_new and
                        lp_mongo_new['tlsCertificateKeyFile']):
                    conn.put(local=lp_mongo_new['tlsCertificateKeyFile'], remote=self.launchdir)

    def slaunch(self, fw_id):
        """Launch a batch node on a remote resource"""
        # do some tests in case this is not called by launcher()
        try:
            if fw_id not in self.fw_ids():
                raise ConfigurationException('invalid fw_id')
            firework = self.launchpad.get_fw_by_id(fw_id)
            if firework.state != 'READY':
                raise InvalidStateException(f'invalid state: {firework.state}', fw_id)
            fw_spec = firework.spec
            if '_category' not in fw_spec:
                raise ConfigurationException('no category specified')
            if '_fworker' not in fw_spec:
                raise ConfigurationException('no worker specified')
            if fw_spec['_category'] != 'remote':
                raise ConfigurationException('invalid category')
            if fw_spec['_fworker'] != self.name:
                raise ConfigurationException('invalid worker name')

            prefix = 'launcher_'
            uniq_name = prefix+datetime.datetime.utcnow().strftime(FW_BLOCK_FORMAT)
            new_launch_dir = os.path.join(self.launchdir, uniq_name)
            launch_comm = []
            if self.conf:
                launch_comm.extend([self.conf, '&&'])
            launch_comm.extend(['mkdir -p', new_launch_dir])
            launch_comm.extend(['&&', 'qlaunch',
                                '--launchpad_file', self.remote_launchpad_path,
                                '--queueadapter_file', self.remote_qadapter_path,
                                '--fworker_file', self.remote_fworker_path,
                                '--launch_dir', new_launch_dir])
            launch_comm.extend(['--reserve', 'singleshot', '--fw_id', str(fw_id)])
            with Connection(self.host, self.user) as conn:
                conn.run(' '.join(launch_comm))
        except Exception as exception:
            self.logger.error(exception, exc_info=1)  # log error with traceback
            raise  # reraise the Exception to be handled by the caller

    def launcher(self, stop_event):
        """Awake every sleep_time seconds and launch all READY nodes"""
        wf_query = {'nodes': {'$in': self.wf_ids}}
        fw_query = {'state': 'READY', 'spec._category': 'remote',
                    'spec._fworker': self.name}
        while not stop_event.is_set():
            fw_ids = self.launchpad.get_fw_ids_in_wfs(wf_query, fw_query)
            for fw_id in fw_ids:
                self.slaunch(fw_id)
            sleep(self.sleep_time)
        print('launcher thread stopped')

    def exec_cancel(self, res_id):
        """Execute the slurm cancel command remotely"""
        with Connection(host=self.host, user=self.user) as conn:
            conn.run(f'scancel {res_id}')

    def check_jobcancel(self, res_id):
        """Execute the slurm sacct command remotely"""
        with Connection(host=self.host, user=self.user) as conn:
            output = conn.run(f'sacct -j {res_id}')
            substring = 'CANCELLED'
            if substring not in output.stdout:
                raise RuntimeError('Error job is not cancelled')

    @recursive_serialize
    def to_dict(self):
        """
        Serialize the engine object to a dictionary

        Returns:
            (dict): a dictionary with all parameters needed to call __init__
        """
        m_dict = super().to_dict()
        m_dict.update({'host': self.host, 'user': self.user, 'conf': self.conf})
        return m_dict

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        """
        Construct an engine object from a dictionary

        Args:
            m_dict (dict): a dict with all parameters needed to call __init__

        Returns:
            FWEngineRemote object
        """
        launchpad = LaunchPad.from_dict(m_dict.get('launchpad'))
        qadapter = m_dict.get('qadapter')
        wf_query = m_dict.get('wf_query')
        name = m_dict.get('name')
        launchdir = m_dict.get('launchdir')
        sleep_time = m_dict.get('sleep_time')
        host = m_dict.get('host')
        user = m_dict.get('user')
        conf = m_dict.get('conf')
        return cls(launchpad=launchpad, qadapter=qadapter, wf_query=wf_query,
                   name=name, launchdir=launchdir, sleep_time=sleep_time,
                   host=host, user=user, conf=conf)
