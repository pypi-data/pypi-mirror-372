"""manage all available computing resources needed in fireworks"""
import os
import sys
import grp
import getpass
import numbers
import uuid
import typing
import warnings
import json
from dataclasses import dataclass, field
from subprocess import PIPE, Popen
from semantic_version import Version, SimpleSpec
from fireworks.utilities.fw_serializers import FWSerializable
from fireworks.utilities.fw_serializers import serialize_fw
from fireworks.utilities.fw_serializers import recursive_serialize
from fireworks.utilities.fw_serializers import recursive_deserialize
import fireworks_schema
from virtmat.middleware.exceptions import ResourceConfigurationError, SlurmError
from virtmat.middleware.utilities import lmod_env_module

SCHEMA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resconfig.json')
fireworks_schema.register_schema(SCHEMA)


def get_resconfig_loc():
    """return the resconfig path"""
    if 'RESCONFIG_LOC' in os.environ:
        return os.environ['RESCONFIG_LOC']
    return os.path.join(os.path.expanduser('~'), '.fireworks', 'res_config.yaml')


def get_default_resconfig():
    """return default resconfig"""
    resconfig_loc = get_resconfig_loc()
    if not os.path.exists(resconfig_loc):
        return None
    try:
        return ResConfig.from_file(resconfig_loc)
    except Exception as err:
        msg = f'Error occured loading configuration file {resconfig_loc}.'
        raise ResourceConfigurationError(msg) from err


def configure(resconfig_loc):
    """create default resconfig and resconfig_loc path, and write resconfig"""
    try:
        cfg = ResConfig.from_scratch()
        set_defaults_from_guess(cfg.default_worker)
    except SlurmError as err:
        print(err)
    except ResourceConfigurationError as err:
        print(err)
    else:
        resconfig_dir = os.path.dirname(resconfig_loc)
        if not os.path.exists(resconfig_dir):
            os.makedirs(resconfig_dir, exist_ok=True)
        cfg.to_file(resconfig_loc)


def get_env_modules(typ):
    """return a list of environment modules with their versions"""
    cmd_map = {'loaded': 'list', 'available': 'spider'}
    mods_dct = lmod_env_module(cmd_map[typ])
    mods_lst = []
    if mods_dct is None:
        return mods_lst
    for mod_name, versions in mods_dct.items():
        divisions = mod_name.split('/')
        prefix = '/'.join(divisions[:-1]) or None
        mods_lst.append(ModuleConfig(prefix, divisions[-1], versions))
    return mods_lst


def get_venv():
    """return a dictionary with venv type, name and path of activated"""
    if os.environ.get('CONDA_DEFAULT_ENV') is not None:
        return {'type': 'conda', 'name': os.environ.get('CONDA_DEFAULT_ENV'),
                'prefix': os.environ.get('CONDA_PREFIX')}
    if sys.prefix != sys.base_prefix:
        return {'type': 'venv', 'name': sys.prefix.rsplit('/', maxsplit=1)[-1],
                'prefix': sys.prefix}
    return None


class ResConfigSerializable(FWSerializable):
    """base serialization class for resource classes"""
    _fw_name = None

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        return self.__dict__

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert cls._fw_name == m_dict.pop('_fw_name')
        return cls(**m_dict)


def resource_type_checker(func):
    """decorate the menimum, maximum and default methods of ResourceConfig"""
    def wrapper(*args, **kwargs):
        if (isinstance(args[1], bool) or
           not (isinstance(args[1], (int, float)) or args[1] is None)):
            raise ResourceConfigurationError('resource must be real numeric type')
        return func(*args, **kwargs)
    return wrapper


@dataclass
class ResourceConfig(ResConfigSerializable):
    """Computing resource

    Attributes:
        name: the name of the resource
    """
    name: str
    _minimum: typing.Union[int, float] = None
    _maximum: typing.Union[int, float] = None
    _default: typing.Union[int, float] = None
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    @property
    def minimum(self) -> typing.Union[int, float]:
        """The minimum value of the resource

        Returns:
            (float|int): the minimum value of the resource
        """
        return self._minimum

    @minimum.setter
    @resource_type_checker
    def minimum(self, val) -> None:
        if val is not None:
            if not isinstance(val, numbers.Number):
                msg = f'value must be numeric type: {val}'
                raise ResourceConfigurationError(msg)
            if val < 0:
                msg = f'negative value is not allowed: {val}'
                raise ResourceConfigurationError(msg)
            if self._maximum is not None and val > self._maximum:
                self._maximum = None
            if self._default is not None and val > self._default:
                self._default = None
        self._minimum = val

    @property
    def maximum(self):
        """The maximum value of the resource

        Returns:
            (float|int): the maximum value of the resource
        """
        return self._maximum

    @maximum.setter
    @resource_type_checker
    def maximum(self, val):
        if val is not None:
            if not isinstance(val, numbers.Number):
                msg = f'value must be numeric type: {val}'
                raise ResourceConfigurationError(msg)
            if val < 0:
                msg = f'negative value is not allowed: {val}'
                raise ResourceConfigurationError(msg)
            if self._minimum is not None and val < self._minimum:
                self._minimum = None
            if self._default is not None and val < self._default:
                self._default = None
        self._maximum = val

    @property
    def default(self):
        """The default value of the resource

        Returns:
            (float|int): the default value of the resource
        """
        return self._default

    @default.setter
    @resource_type_checker
    def default(self, val):
        if val is not None:
            if isinstance(val, numbers.Number) and val < 0:
                msg = f'negative value is not allowed: {val}'
                raise ResourceConfigurationError(msg)
            if self._maximum is not None and val > self._maximum:
                msg = f'cannot set default {val} greater than maximum {self._maximum}'
                raise ResourceConfigurationError(msg)
            if self._minimum is not None and val < self._minimum:
                msg = f'cannot set default {val} less than minimum {self._minimum}'
                raise ResourceConfigurationError(msg)
        self._default = val


@dataclass
class QueueConfig(ResConfigSerializable):
    """Queue configuration

    Attributes:
        name (str): queue name
        public (bool): True if publicly available, default None
        resources ([ResourceConfig]): list of configured resources
        accounts_allow ([str]): list of usernames allowed to use the queue
        accounts_deny ([str]): list of usernames disallowed to use the queue
        groups_allow ([str]): list of groups allowed to use the queue
    """
    name: str = None
    public: bool = None
    resources: list[ResourceConfig] = field(default_factory=list)
    accounts_allow: list[str] = field(default_factory=list)
    accounts_deny: list[str] = field(default_factory=list)
    groups_allow: list[str] = field(default_factory=list)
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    def set_resource(self, res, type_, val):
        """Set the value of a specific computing resource configuration

        Args:
            res (str): resource name
            type_ (str): resource type: default, minimum, maximum
            val (int|float): value of the resource

        Raises:
            ValueError: if type_ has invalid value
        """
        if type_ not in ('minimum', 'maximum', 'default'):
            raise ValueError(f'invalid resource type {type_}')
        if res in (r.name for r in self.resources):
            setattr(next(r for r in self.resources if res == r.name), type_, val)
        else:
            resource = ResourceConfig(name=res)
            setattr(resource, type_, val)
            self.resources.append(resource)

    def get_resource(self, res):
        """Get a specific computing resource configuration

        Args:
            res (str): resource name

        Returns:
            ResourceConfig object if resource exists, None otherwise
        """
        if res in (r.name for r in self.resources):
            return next(r for r in self.resources if r.name == res)
        return None

    def validate_resource(self, name, val):
        """Check if resource value is between minimum and maximum

        Args:
            name (str): resource name
            val (int|float): reource value

        Raises:
            ResourceConfigurationError: if resource value exceeds limits
        """
        if self.get_resource(name) is None:
            msg = f'resource {name} is not configured'
            raise ResourceConfigurationError(msg)
        if (self.get_resource(name).maximum is not None and
           val > self.get_resource(name).maximum):
            msg = f'resource {name} is greater than maximum'
            raise ResourceConfigurationError(msg)
        if (self.get_resource(name).minimum is not None and
           val < self.get_resource(name).minimum):
            msg = f'resource {name} is less than minimum'
            raise ResourceConfigurationError(msg)


@dataclass
class ModuleConfig(ResConfigSerializable):
    """Module configuration

    Attributes:
        prefix (str): module prefix, if module name has prefix, else None
        name (str): module name, mandatory
        versions ([str]): available module versions, empty list if no versions
        path (str): module path, if different from default path, else None
    """
    prefix: str = None
    name: str = None
    versions: list[str] = field(default_factory=list)
    path: str = None
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    def _format_command(self, version=None):
        """Format the module load command

        Args:
            version (str): optional version, no version if None

        Returns:
            (str): the formatted shell command to load the module
        """
        path_cmd = f'module use {self.path}; ' if self.path else ''
        comps = []
        if self.prefix:
            comps.append(self.prefix)
        comps.append(self.name)
        if version:
            assert version in self.versions
            comps.append(version)
        load_cmd = 'module load ' + '/'.join(comps)
        return path_cmd + load_cmd

    def get_command(self, name, spec=None):
        """Return the module load command

        Args:
            name (str): name to match
            spec (str): a requirement specification (like '<=0.9.3')

        Returns:
            (str): the shell command to load the module if matching else None
        """
        if name == self.name:
            if spec is None:
                if self.versions:
                    semvers = [Version.coerce(v) for v in self.versions]
                    ind = semvers.index(max(semvers))
                    return self._format_command(self.versions[ind])
                return self._format_command()
            spec_ = SimpleSpec(spec)
            for version in self.versions:
                if spec_.match(Version.coerce(version)):
                    return self._format_command(version)
        return None


@dataclass
class CommandConfig(ResConfigSerializable):
    """Shell command configuration

    Attributes:
        cmd (str): a shell command
        args ([str]): a list of command arguments, default: empty list
        commands ([str]): a list of allowed commands

    Raises:
        ResourceConfigurationError: if a command is not allowed
    """
    cmd: str = None
    args: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=lambda: ['umask', 'alias'])
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    def __post_init__(self):
        if self.cmd not in self.commands:
            msg = f'command {self.cmd} not in the list of allowed commands'
            raise ResourceConfigurationError(msg)

    def get_command(self):
        """return the command as a string"""
        return self.cmd + ' ' + ' '.join(self.args)


@dataclass
class WorkerConfig(ResConfigSerializable):
    """Worker configuration

    Every computing cluster is mapped to a worker.

    Attributes:
        name (str): worker name
        type_ (str): type of batch queuing system, only 'SLURM' supported
        queues ([QueueConfig]): a list of configured queues
        accounts ([str]): a list of groups available for accounting
        modules: ([ModuleConfig]): a list of available environment modules
        envvars: (dct): a dict of environment variables
        default_modules: ([ModuleConfig]): a list of default environment modules
        default_envvars: ([str]): a list of default environment variables
        default_venv: (dict): a dict of default virtual environment
        default_launchdir: (str): default directory for launching jobs
        default_commands: [CommandConfig]: a list of default commands
    """
    name: str = None
    type_: str = None
    queues: list[QueueConfig] = field(default_factory=list)
    accounts: list[str] = field(default_factory=list)
    modules: list[ModuleConfig] = field(default_factory=list)
    envvars: dict = field(default_factory=dict)
    default_modules: list[ModuleConfig] = field(default_factory=list)
    default_envvars: list[str] = field(default_factory=list)
    default_venv: dict = None
    default_launchdir: str = None
    default_commands: list[CommandConfig] = field(default_factory=list)
    _default_queue: QueueConfig = None
    _default_account: str = None
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    @classmethod
    def from_scratch(cls, name=None):
        """Extract all relevant available resources from slurm partitions

        Args:
            name (str): optional worker name, if skipped one will be generated

        Returns:
            WorkerConfig object

        """
        name = uuid.uuid4().hex if name is None else name
        command = ['/usr/bin/scontrol', '--json', 'show', 'partition']
        try:
            with Popen(command, stdout=PIPE, shell=False) as proc:  # nosec B603
                slurm_res = json.load(proc.stdout)
        except FileNotFoundError as err:
            if 'No such file or directory: \'/usr/bin/scontrol\'' in str(err):
                return cls(name=name)
            raise ResourceConfigurationError('An unknown error occurred') from err
        queues = []
        for part in slurm_res['partitions']:
            q_kwargs = {}
            acc_allow = part['accounts']['allowed'].strip()
            acc_deny = part['accounts']['deny'].strip()
            grp_allow = part['groups']['allowed'].strip()
            q_kwargs['public'] = (acc_allow == '' and grp_allow == '') or acc_deny != ''
            if acc_allow:
                q_kwargs['accounts_allow'] = [a.strip() for a in acc_allow.split(',')]
            if acc_deny:
                q_kwargs['accounts_deny'] = [a.strip() for a in acc_deny.split(',')]
            if grp_allow:
                q_kwargs['groups_allow'] = [g.strip() for g in grp_allow.split(',')]
            q_kwargs['name'] = part['name']
            q_kwargs['resources'] = []
            queue = QueueConfig(**q_kwargs)
            for sec in ('maximums', 'minimums', 'defaults'):
                for key, val in part[sec].items():
                    if isinstance(val, dict):
                        if 'infinite' in val and 'number' in val:
                            value = float('inf') if val['infinite'] else val['number']
                        else:
                            continue
                    else:
                        value = val
                    try:
                        queue.set_resource(key, sec[:-1], value)
                    except ResourceConfigurationError:
                        queue.set_resource(key, sec[:-1], None)
                        msg = (f'resource {sec[:-1]} {key} has invalid value '
                               f'{val} or type {type(val)} and was set to null')
                        warnings.warn(msg, UserWarning)
            queues.append(queue)
        user = getpass.getuser()
        accounts = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
        return cls(name=name, type_='SLURM', queues=queues, accounts=accounts,
                   modules=get_env_modules('available'), default_venv=get_venv(),
                   default_modules=get_env_modules('loaded'))

    @property
    def default_account(self):
        """The default group used for accounting

        Returns:
            str: the default group used for accounting if set, otherwise None

        Raises:
            ResourceConfigurationError: if the group is not in the list of groups
        """
        return self._default_account

    @default_account.setter
    def default_account(self, acc=None):
        if acc not in self.accounts:
            msg = f'group {acc} not in the list of groups'
            raise ResourceConfigurationError(msg)
        self._default_account = acc

    def set_default_account(self):
        """select the currently active group as default group for accounting"""
        self.default_account = grp.getgrgid(os.getgid()).gr_name

    @property
    def default_queue(self) -> QueueConfig:
        """The default queue

        Returns:
            QueueConfig: the default queue configuration if set, otherwise None

        Raises:
            ResourceConfigurationError: if the queue is not in the list of queues
        """
        return self._default_queue

    @default_queue.setter
    def default_queue(self, queue: QueueConfig) -> None:
        if queue not in self.queues:
            msg = f'queue {queue} not in queues list'
            raise ResourceConfigurationError(msg)
        self._default_queue = queue

    def set_default_queue(self):
        """select the first configured queue as default queue"""
        if self._default_queue is None:
            if len(self.queues) == 0:
                raise ResourceConfigurationError('no queues configured')
            self._default_queue = self.queues[0]


@dataclass
class ResConfig(ResConfigSerializable):
    """collect and store all computing resources needed to use fireworks"""
    workers: list[WorkerConfig] = field(default_factory=list)
    default_worker: WorkerConfig = None
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    @classmethod
    def from_scratch(cls, name=None):
        """create a top-level resource configuration object from scratch"""
        worker = WorkerConfig.from_scratch(name)
        return cls(workers=[worker], default_worker=worker)

    def add_worker_from_scratch(self, name=None, default=False):
        """add a worker from scratch"""
        worker = WorkerConfig.from_scratch(name)
        self.workers.append(worker)
        if default:
            self.default_worker = worker

    @fireworks_schema.fw_schema_serialize
    def to_dict(self):
        return super().to_dict()


def set_defaults_from_guess(wcfg):
    """Set defaults of specific resources from a guess

    Args:
        wcfg (WorkerConfig): a worker configuration object
    """
    if wcfg.name is None:
        wcfg.name = uuid.uuid4().hex
    if len(wcfg.queues) > 0:
        if wcfg.default_queue is None:
            wcfg.set_default_queue()
        queue = wcfg.default_queue
        if wcfg.default_account is None:
            wcfg.set_default_account()
        time = queue.get_resource('time')
        if time is None:
            queue.set_resource('time', 'default', 5)
        else:
            if time.default is None:
                if time.minimum is None:
                    queue.set_resource('time', 'default', 5)
                else:
                    queue.set_resource('time', 'default', time.minimum)
        nodes = queue.get_resource('nodes')
        if nodes is None or nodes.default is None:
            queue.set_resource('nodes', 'default', 1)
        cpus_per_node = queue.get_resource('cpus_per_node')
        if cpus_per_node is None or cpus_per_node.default is None:
            queue.set_resource('cpus_per_node', 'default', 1)
        cpus_per_task = queue.get_resource('cpus_per_task')
        if cpus_per_task is None or cpus_per_task.default is None:
            queue.set_resource('cpus_per_task', 'default', 1)
