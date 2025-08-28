"""A simple workflow engine"""
import threading
import os
from time import sleep
from fireworks import fw_config, LaunchPad, Workflow, Firework, PyTask, FWorker
from fireworks.core.rocket_launcher import launch_rocket
from fireworks.queue.queue_launcher import launch_rocket_to_queue
from fireworks.utilities.fw_serializers import FWSerializable
from fireworks.utilities.fw_serializers import serialize_fw
from fireworks.utilities.fw_serializers import recursive_serialize
from fireworks.utilities.fw_serializers import recursive_deserialize
from fireworks.utilities.fw_utilities import get_fw_logger
from fireworks.utilities.fw_utilities import create_datestamp_dir
import fireworks_schema
from prettytable import PrettyTable
from virtmat.middleware.query.wfquery import WFQuery
from virtmat.middleware.resconfig import get_default_resconfig
from virtmat.middleware.resconfig import get_default_qadapter
from virtmat.middleware.exceptions import ConfigurationException
from virtmat.middleware.exceptions import InvalidStateException
from virtmat.middleware.exceptions import ResourceConfigurationError
from virtmat.middleware.utilities import get_logger, get_unreserved_nodes
from virtmat.middleware.utilities import exec_cancel

SCHEMA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wfengine.json')
fireworks_schema.register_schema(SCHEMA)


class WFEngine(FWSerializable):
    """A simple engine to manage workflows"""
    logger = get_logger(__name__)
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    def __init__(self, launchpad, qadapter=None, wf_query=None, name=None,
                 launchdir=None, unique_launchdir=True, sleep_time=30):
        """
        Args:
            launchpad (LaunchPad): a launchpad to establish connection to a
                FireWorks database
            qadapter (CommonAdapter, None): a qadapter for submitting
                batch jobs
            wf_query (dict, None): a workflow query
            name (str, None): name of the engine; it must be a valid worker name;
                if None then the default worker name will be used
            launchdir (str): top-level launch directory for both interactive
                and batch jobs; if None then default_launchdir from the resconfg
                is used if not None, otherwise the current working directory
            unique_launchdir (bool): create individual directory with unique
                name for every single launch of interactive nodes, default True
            sleep_time (int): launcher thread awakes every `sleep_time` seconds
        """
        if isinstance(launchpad, LaunchPad):
            self.launchpad = launchpad
        else:
            msg = f'launchpad is not of type LaunchPad but {type(launchpad)}'
            self.logger.error(msg)
            raise TypeError(msg)

        self.wf_ids = ([] if wf_query is None else
                       self.launchpad.get_wf_ids(wf_query))
        self.unique_launchdir = unique_launchdir
        self.sleep_time = sleep_time
        self.wf_query = {'nodes': {'$in': self.wf_ids}}
        self._set_name(name)
        self._set_launchdir(launchdir)
        self._set_qadapter(qadapter)
        self._set_fworkers()
        self.nodes_torun = None
        self.thread = None
        self.event = None

    def _set_name(self, name=None):
        """set the name of the worker"""
        cfg = get_default_resconfig()
        if cfg is None:
            raise ConfigurationException('no resconfig found')
        if name is None:
            if cfg.default_worker is None:
                raise ConfigurationException('default worker not found')
            self.__name = cfg.default_worker.name
        else:
            if name not in (w.name for w in cfg.workers):
                msg = f'worker {name} not found in list of workers'
                raise ConfigurationException(msg)
            self.__name = name

    def _set_launchdir(self, launchdir=None):
        """set the launch directory"""
        if launchdir is None:
            cfg = get_default_resconfig()
            if cfg is None:
                raise ConfigurationException('no resconfig found')
            if cfg.default_worker is None:
                raise ConfigurationException('default worker not found')
            self.launchdir = cfg.default_worker.default_launchdir or os.getcwd()
        else:
            self.launchdir = launchdir
        if not os.path.exists(self.launchdir):
            msg = f'Launch directory {self.launchdir} does not exist'
            raise ConfigurationException(msg)

    def _set_qadapter(self, qadapter=None):
        """set the default qadapter"""
        assert self.name is not None
        if qadapter is None:
            try:
                self.qadapter = get_default_qadapter(w_name=self.name)
            except ResourceConfigurationError:
                self.qadapter = None
        else:
            self.qadapter = qadapter

    def _set_fworkers(self):
        """set the fworkers"""
        assert self.name is not None
        self.fworker_rlaunch = FWorker(name=self.name, category='interactive')
        if self.qadapter:
            self.fworker_qlaunch = FWorker(name=self.name, category='batch')
        else:
            self.fworker_qlaunch = None

    @property
    def name(self):
        """get the name of the engine"""
        return self.__name

    @name.setter
    def name(self, new_name):
        """set the name of the engine"""
        self._set_name(new_name)
        self._set_qadapter()
        self._set_fworkers()

    @property
    def wf_query(self):
        """get the query for the engine"""
        return self.__wf_query

    @wf_query.setter
    def wf_query(self, new_wf_query):
        """set the query for the engine"""
        self.__wf_query = new_wf_query
        self.__wf_ids = self.launchpad.get_wf_ids(self.wf_query)

    @property
    def wf_ids(self):
        """get the workflow ids of the engine"""
        return self.__wf_ids

    @wf_ids.setter
    def wf_ids(self, wf_ids):
        """set the workflow ids of the engine; wf_ids: a list of new wf_ids"""
        self.__wf_ids = wf_ids
        self.__wf_query = {'nodes': {'$in': self.wf_ids}}

    def append_wf_id(self, wf_id):
        """append a workflow id (wf_id) to the list of wf_ids"""
        self.__wf_ids.append(wf_id)
        self.__wf_query = {'nodes': {'$in': self.wf_ids}}

    def remove_wf_id(self, wf_id):
        """remove a workflow id (wf_id) from the list of wf_ids"""
        self.__wf_ids.remove(wf_id)
        self.__wf_query = {'nodes': {'$in': self.wf_ids}}

    @property
    def fw_ids(self):
        """get the current firework ids of the engine"""
        return self.launchpad.get_fw_ids_in_wfs(self.wf_query)

    def show_nodes_status(self):
        """Display the status summary of the nodes"""
        wfq = WFQuery(self.launchpad, wf_query=self.wf_query)
        fw_info = wfq.get_fw_info()
        if len(fw_info) > 0:
            columns = fw_info[0].keys()
            table = PrettyTable(columns)
            for fwk in fw_info:
                table.add_row([fwk[i] for i in columns])
            print(table)
        else:
            print('No nodes')

    def show_wf_status(self, add_io_info=True):
        """Display the status summary of the workflows"""
        wfq = WFQuery(self.launchpad, wf_query=self.wf_query)
        wfq.get_wf_info(add_io_info=add_io_info)

    def status_summary(self):
        """Display a status summary of workflows and nodes"""
        self.show_wf_status(add_io_info=False)
        print('Nodes summary:')
        self.show_nodes_status()

    def show_launcher_status(self):
        """Check whether a launcher thread is running"""
        if self.thread:
            if self.thread.is_alive():
                print('launcher thread is currently running')
            else:
                print('launcher thread not started')
        else:
            print('launcher thread not created')

    def status_detail(self, *fw_ids):
        """
        Print a detailed status of specified nodes

        Args:
            fw_ids ([int]): One or more fw_ids of the nodes
        Returns:
            a list of dictionaries, containing the nodes
        """
        def get_launches(launch_ids):
            launches = []
            projection = {'_id': False}
            for launch_id in launch_ids:
                l_query = {'launch_id': launch_id}
                launch = self.launchpad.launches.find_one(l_query, projection)
                launches.append(launch)
            return launches

        fw_list = []
        for fw_id in fw_ids:
            fw_query = {'fw_id': fw_id}
            projection = {'_id': False}
            fw_dict = self.launchpad.fireworks.find_one(fw_query, projection)
            fw_dict['launches'] = get_launches(fw_dict['launches'])
            fw_dict['archived_launches'] = get_launches(fw_dict['archived_launches'])
            fw_list.append(fw_dict)
        return fw_list

    def get_failed(self):
        """
        Get failed job ids

        Returns:
            ([int]): a list of fw_ids of failed jobs
        """
        wfq = WFQuery(self.launchpad, wf_query=self.wf_query,
                      fw_query={'state': 'FIZZLED'})
        return wfq.get_fw_ids()

    def qlaunch(self, fw_id):
        """
        Launch a batch node by submitting a job to the queuing system

        Args:
            fw_id (int): a fwd_id of the node to launch
        """

        if fw_config.MONGOMOCK_SERVERSTORE_FILE is not None:
            raise ConfigurationException('qlaunch error: cannot launch with Mongomock')
        if fw_id not in self.fw_ids:
            raise ConfigurationException(f'qlaunch error: invalid fw_id: {fw_id}')
        if self.qadapter is None:
            raise ConfigurationException('qlaunch error: qadapter is not defined')
        if self.fworker_qlaunch is None:
            raise ConfigurationException('qlaunch error: fworker is not defined')
        launch_rocket_to_queue(self.launchpad, self.fworker_qlaunch,
                               self.qadapter, reserve=True,
                               create_launcher_dir=True,
                               launcher_dir=self.launchdir,
                               fw_id=fw_id)

    def rlaunch(self, fw_id):
        """
        Launch an interactive node

        Args:
            fw_id (int): a fwd_id of the node to launch
        """
        if fw_id not in self.fw_ids:
            raise ConfigurationException(f'rlaunch error: invalid fw_id: {fw_id}')
        init_dir = os.getcwd()
        if self.unique_launchdir:
            logger = get_fw_logger('interactive', l_dir=self.launchpad.get_logdir())
            launch_dir = create_datestamp_dir(self.launchdir, logger, prefix='launcher_')
        else:
            launch_dir = self.launchdir
        try:
            os.chdir(launch_dir)
            launch_rocket(self.launchpad, self.fworker_rlaunch, fw_id)
        finally:
            os.chdir(init_dir)

    def get_lost_jobs(self, time=14400, fizzle=False):
        """
        Detect nodes that have been launched but not updated within the
        specified time.

        Args:
            time (int): minimim time in seconds since the most recent update
            fizzle (bool): set state of detected nodes to FIZZLED

        Returns:
            lost_fw_ids ([int]): a list of fw_ids of the lost runs
        """
        fw_query = {'fw_id': {'$in': self.fw_ids}}
        lostjobs = self.launchpad.detect_lostruns(expiration_secs=time,
                                                  fizzle=fizzle, query=fw_query)
        lost_fw_ids = lostjobs[1]
        if len(lost_fw_ids) != 0:
            self.logger.warning('Lost jobs detected: %s.', str(lost_fw_ids))
        return lost_fw_ids

    def get_unreserved_nodes(self, time=1209600):
        """
        Detect reserved nodes, i.e. in 'RESERVED' state within FireWorks, that
        have not been updated for a while. Possible inconsistent states in
        SLURM are 'CANCELLED', 'FAILED', 'COMPLETED', 'OUT_OF_MEMORY',
        'BOOT_FAIL', 'TIMEOUT' and 'DEADLINE'

        Args:
            time (int): minimum time in seconds since the most recent update

        Returns:
            ([dict]): a list of dictionaries containing the fw_ids, the
            reservation ids, the SLURM states and the launch directories of
            such reserved nodes
        """
        return get_unreserved_nodes(self.launchpad, self.fw_ids, expiration_time=time)

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        return {'launchpad': self.launchpad,
                'qadapter': self.qadapter,
                'wf_query': self.wf_query,
                'name': self.name,
                'launchdir': self.launchdir,
                'unique_launchdir': self.unique_launchdir,
                'sleep_time': self.sleep_time}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert cls._fw_name == m_dict.pop('_fw_name')
        launchpad = LaunchPad.from_dict(m_dict.pop('launchpad'))
        return cls(launchpad=launchpad, **m_dict)

    def start(self, raise_exception=False):
        """Start a launcher thread"""
        if self.thread and self.thread.is_alive():
            self.logger.warning('launcher thread is already running')  # not covered
        elif fw_config.MONGOMOCK_SERVERSTORE_FILE is None:
            self.event = threading.Event()
            self.thread = threading.Thread(target=self._launcher, args=(self.event,))
            self.thread.start()
        else:
            msg = 'launcher thread cannot be used with Mongomock'
            exc = ConfigurationException(msg)
            if raise_exception:
                raise exc
            print(exc)

    def stop(self, join=False):
        """Gracefully stop the launcher thread if it is running"""
        if self.event and not self.event.is_set():
            self.event.set()
            self.logger.info('stopping the launcher thread')
            if join:
                self.thread.join()

    def _get_launcher_fw_ids(self):
        """update the list of fw_ids to process in the launcher"""
        fw_query = {'state': 'READY', 'spec._category': {'$in': ['batch', 'interactive']}}
        if self.nodes_torun is not None:
            if len(self.nodes_torun) == 0:
                return []
            fw_query['fw_id'] = {'$in': self.nodes_torun}
        return self.launchpad.get_fw_ids_in_wfs(self.wf_query, fw_query)

    def _launcher(self, stop_event):
        """
        The main loop of the launcher

        Args:
            stop_event (threading.Event): an object used to quit the launcher
        """
        while not stop_event.is_set():
            fw_ids = self._get_launcher_fw_ids()
            while fw_ids:
                if stop_event.is_set():
                    self.logger.info('launcher thread stopped')
                    return
                for fw_id in fw_ids:
                    fw_p = {'spec._category': True}
                    fw = self.launchpad.fireworks.find_one({'fw_id': fw_id}, fw_p)
                    try:
                        if fw['spec']['_category'] == 'batch':
                            self.qlaunch(fw_id)
                        else:
                            self.rlaunch(fw_id)
                    except Exception as err:  # very broad exception due to fireworks
                        self.logger.exception('Launch error: %s', str(err))
                fw_ids = self._get_launcher_fw_ids()
            sleep(self.sleep_time)
        self.logger.info('launcher thread stopped')

    def add_node(self, func, inputs, outputs=None, name=None, kwargs=None,
                 category=None, fworker=None, qadapter=None):
        """
        Add a python function node to an existing workflow

        Args:
            func (str): a function name with an optional module name in the
                format 'module.function'
            inputs ([tuple]): a list of positional arguments for the provided
                function. Every input is described by a tuple (fw_id, name, value)
                with the following elements:
                fw_id (int): The fw_id of a parent node providing the input; if the
                input is provided as a constant value, then None should be specified.
                name (str): The name of the input as provided in the list of outputs of
                the parent node;
                value: The value of the input; if output data from a parent node
                is used as input, then this should be set to None.

            outputs ([str]): names of the outputs
            name (str, None): name of the node
            kwargs (dict, None): a dictionary of keyword arguments for func
            category (str, None): job category, either 'batch' or 'interactive'
            fworker (FWorker, None): fworker for executing the batch jobs
            qadapter (CommonAdapter, None): qadapter for submitting batch jobs
        """
        if outputs is None:
            outputs = []
        if kwargs is None:
            kwargs = {}
        try:
            if fw_config.MONGOMOCK_SERVERSTORE_FILE is not None and category == 'batch':
                raise ConfigurationException('cannot add batch node with Mongomock')
            node_ids = list(set(i[0] for i in inputs if i[0] is not None))
            # check that all parent nodes are in the managed wfs
            if not all(n in self.fw_ids for n in node_ids):  # not covered
                raise ConfigurationException('some parent nodes are not in engine')
            # check that all parent nodes are in one worfklow
            qres = self.launchpad.get_wf_ids({'nodes': {'$in': node_ids}})
            if len(qres) <= 0:
                raise ConfigurationException('no valid parent nodes defined')
            if len(qres) != 1:
                raise ConfigurationException('some parent nodes are not in one workflow')
            # later, add all upstream fireworks of the nodes from other workflows
            # later check the outputs of parent nodes to match the inputs
            inps = [i[1] for i in inputs]
            # check that any equal inputs have the same source
            msg = 'input "{}" has more than one source'
            for inp in set(inps):
                sources = set(i[0] for i in inputs if i[1] == inp)
                if len(sources) != 1:
                    raise ConfigurationException(msg.format(inp))

            task = PyTask(func=func, inputs=inps, outputs=outputs, kwargs=kwargs)
            spec = {}
            spec['_dupefinder'] = {'_fw_name': 'DupeFinderExact'}
            spec['_fworker'] = fworker or self.name
            spec['_category'] = category or 'interactive'
            if spec['_category'] == 'batch':
                spec['_qadapter'] = qadapter
            locs = {i[1]: i[2] for i in inputs if i[0] is None}
            spec.update(locs)
            wflow = Workflow([Firework(tasks=[task], spec=spec, name=name)])
            self.launchpad.append_wf(wflow, fw_ids=node_ids)
        except Exception as exception:
            self.logger.error(exception, exc_info=1)
            raise

    def add_workflow(self, workflow=None, fw_id=None):
        """
        Add a workflow to the engine.
        Either a workflow object or a fw_id must be defined.

        Args:
            workflow (Workflow, None): a workflow object
            fw_id (int, None): a fw_id of a workflow existing on the launchpad
        """
        try:
            if ((workflow is None and fw_id is None)
                    or (workflow is not None and fw_id is not None)):
                msg = 'Either a workflow object or fw_id is needed.'
                raise ConfigurationException(msg)
            if fw_id is None:
                if not isinstance(workflow, (Workflow, Firework)):
                    msg = 'workflow must be instance of Workflow or Firework'
                    raise ConfigurationException(msg)
                fw_id = list(self.launchpad.add_wf(workflow).values())[0]
            else:
                if not isinstance(fw_id, int):
                    raise ConfigurationException('fw_id must be integer')
                if fw_id in self.fw_ids:
                    raise ConfigurationException('workflow already in engine')
                fw_ids = self.launchpad.get_fw_ids({'fw_id': fw_id})
                if len(fw_ids) != 1:
                    raise ConfigurationException('no workflow with this ID')
            self.append_wf_id(fw_id)
            self.logger.info('Added workflow ID: %d', fw_id)
        except Exception as exception:
            self.logger.error(exception, exc_info=1)
            raise

    def remove_workflow(self, fw_id):
        """
        Remove a workflow from the engine (but not deleted from launchpad)

        Args:
            fw_id (int): a fw_id of a node in the workflow to remove
        """
        self.remove_wf_id(fw_id)
        self.logger.info('Removed workflow ID: %d', fw_id)

    def update_node(self, fw_id, update_dict):
        """
        Update (modify) a workflow node.
        Only nodes in FIZZLED, DEFUSED, PAUSED, WAITING, and READY states
        can be modified.

        Args:
           fw_id (int): the fw_id of the node to modify
           update_dict (dict): a dictionary with the updates to perform
        """
        allowed_states = ['FIZZLED', 'DEFUSED', 'PAUSED', 'WAITING', 'READY']
        try:
            if fw_id not in self.fw_ids:
                msg = f'Node ID not configured in engine: {fw_id}'
                raise ConfigurationException(msg)
            fw = self.launchpad.fireworks.find_one({'fw_id': fw_id}, {'state': True})
            if fw['state'] not in allowed_states:
                msg = f'Node state must be in {allowed_states}'
                raise InvalidStateException(msg, fw_id)
            self.launchpad.update_spec([fw_id], update_dict)
        except Exception as exception:
            self.logger.error(exception, exc_info=1)
            raise

    def rerun_node(self, fw_id):
        """
        Rerun a workflow node.
        Nodes in FIZZLED and COMPLETED states will be directly rerun.
        Nodes in PAUSED and DEFUSED states are resumed and reignited, respectively.
        In all cases the target node state is WAITING. The final state can be
        READY if all parents are COMPLETED.

        Args:
            fw_id: the fw_id of the node to rerun
        """
        allowed_states = ['FIZZLED', 'DEFUSED', 'PAUSED', 'COMPLETED']
        try:
            if fw_id not in self.fw_ids:
                msg = f'Node ID not configured in engine: {fw_id}'
                raise ConfigurationException(msg)
            fw = self.launchpad.fireworks.find_one({'fw_id': fw_id}, {'state': True})
            if fw['state'] not in allowed_states:
                msg = f'Node state must be in {allowed_states}'
                raise InvalidStateException(msg, fw_id)
            if fw['state'] in ['FIZZLED', 'COMPLETED']:
                self.launchpad.rerun_fw(fw_id)
            elif fw['state'] == 'DEFUSED':
                self.launchpad.reignite_fw(fw_id)
            else:
                self.launchpad.resume_fw(fw_id)
        except Exception as exception:
            self.logger.error(exception, exc_info=1)
            raise

    def update_rerun_node(self, fw_id, update_dict):
        """
        Update (modify) and rerun a workflow node combined in one function.
        Only nodes in FIZZLED, DEFUSED, PAUSED, and COMPLETED states can be
        processed.

        Args:
            fw_id (int): the fw_id of the node to process
            update_dict (dict): a dictionary with the updates to perform
        """
        allowed_states = ['FIZZLED', 'DEFUSED', 'PAUSED', 'COMPLETED']
        try:
            if fw_id not in self.fw_ids:
                msg = f'Node ID not configured in engine: {fw_id}'
                raise ConfigurationException(msg)
            fw = self.launchpad.fireworks.find_one({'fw_id': fw_id}, {'state': True})
            if fw['state'] not in allowed_states:
                msg = f'Node state must be in {allowed_states}'
                raise InvalidStateException(msg, fw_id)
            if fw['state'] == 'COMPLETED':
                self.launchpad.defuse_fw(fw_id, rerun_duplicates=False)
                self.launchpad.update_spec([fw_id], update_dict)
                self.launchpad.reignite_fw(fw_id)
            elif fw['state'] == 'FIZZLED':
                self.launchpad.update_spec([fw_id], update_dict)
                self.launchpad.rerun_fw(fw_id, rerun_duplicates=False)
            elif fw['state'] == 'DEFUSED':
                self.launchpad.update_spec([fw_id], update_dict)
                self.launchpad.reignite_fw(fw_id)
            else:
                self.launchpad.update_spec([fw_id], update_dict)
                self.launchpad.resume_fw(fw_id)
        except Exception as exception:
            self.logger.error(exception, exc_info=1)
            raise

    def cancel_job(self, fw_id, restart=False, deactivate=False):
        """
        Cancel the execution of a node in RESERVED or RUNNING state.
        Either restart or deactivate can be set to True if required.

        Args:
            fw_id (int): the fw_id of the node to cancel
            restart (bool): restart node after cancelling
            deactivate (bool): deactivate node after cancelling
        """
        allowed_states = ['RESERVED', 'RUNNING']
        try:
            if fw_id not in self.fw_ids:
                msg = f'Node ID not configured in engine: {fw_id}'
                raise ConfigurationException(msg)
            if restart == deactivate:
                msg = 'Either restart or deactivate must be set to True'
                raise ConfigurationException(msg)
            fw_p = {'state': True, 'spec._category': True}
            fw = self.launchpad.fireworks.find_one({'fw_id': fw_id}, fw_p)
            if fw['state'] not in allowed_states:
                msg = f'Node state must be in {allowed_states}'
                raise InvalidStateException(msg, fw_id)
            reserve_id = self.launchpad.get_reservation_id_from_fw_id(fw_id)
            if fw['spec']['_category'] == 'batch':
                exec_cancel(reserve_id)
            if fw['state'] == 'RESERVED':  # not covered
                self.launchpad.cancel_reservation_by_reservation_id(reserve_id)
                if deactivate:
                    self.launchpad.pause_fw(fw_id)
            elif fw['state'] == 'RUNNING':  # not covered
                if restart:
                    self.launchpad.rerun_fw(fw_id)
                else:
                    self.launchpad.defuse_fw(fw_id)
        except Exception as exception:
            self.logger.error(exception, exc_info=1)
            raise
