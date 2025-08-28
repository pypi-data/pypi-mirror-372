"""utility functions dealing with fireworks qadapter"""
import os
import math
from fireworks.user_objects.queue_adapters.common_adapter import CommonAdapter
from virtmat.middleware.exceptions import ResourceConfigurationError
from virtmat.middleware.resconfig import get_default_resconfig

res_mapper = {'nodes': 'nodes', 'ntasks_per_node': 'cpus_per_node',
              'cpus_per_task': 'cpus_per_task', 'walltime': 'time',
              'mem_per_cpu': 'memory_per_cpu'}


def get_default_qadapter(cfg=None, w_name=None, lp_file=None):
    """
    Construct a default qadapter from a resconfig object

    Args:
        cfg (ResConfig): rsource configuration object, if None then it will
        be loaded from resconfig file
        w_name (str): name of worker, if None then default_worker will be used
        lp_file (str): a custom launchpad file to be specified in the
        rocket_launch section of qadapter

    Returns:
        a CommonAdapter object if worker type is not None, otherwise None
    """
    if cfg is None:
        cfg = get_default_resconfig()
        if cfg is None:
            msg = 'Resource configuration file not found.'
            raise ResourceConfigurationError(msg)
    if w_name is None:
        wcfg = cfg.default_worker
        if wcfg is None:
            raise ResourceConfigurationError('no default worker found')
    else:
        try:
            wcfg = next(w for w in cfg.workers if w.name == w_name)
        except StopIteration as err:
            msg = f'no worker with {w_name} found'
            raise ResourceConfigurationError(msg) from err
    if wcfg.type_ is None:
        return None
    queue = wcfg.default_queue
    if queue is None:
        raise ResourceConfigurationError('no default queue found')
    qadapter = {}
    qadapter['q_type'] = wcfg.type_
    qadapter['q_name'] = wcfg.default_queue.name
    qadapter['queue'] = wcfg.default_queue.name  # the launcher requires this redundant key
    for key1, key2 in res_mapper.items():
        res = queue.get_resource(key2)
        if res is not None:
            qadapter[key1] = res.default
    qadapter['ntasks'] = qadapter['nodes'] * qadapter['ntasks_per_node']
    if lp_file is not None:
        if not os.path.exists(lp_file):
            raise ResourceConfigurationError(f'file {lp_file} does not exist')
        qadapter['rocket_launch'] = f'rlaunch -l {lp_file} singleshot'
    else:
        qadapter['rocket_launch'] = 'rlaunch singleshot'
    qadapter['account'] = wcfg.default_account
    qadapter['pre_rocket'] = get_pre_rocket(wcfg)
    if wcfg.default_launchdir:
        qadapter['launch_dir'] = wcfg.default_launchdir
    return CommonAdapter(**qadapter)


def get_pre_rocket(wcfg, **kwargs):
    """Return a pre_rocket string for qadapter

    Args:
        wcfg (WorkerConfig): worker config
        kwargs (dict): required resources

    Raises:
        ResourceConfigurationError: in case of no match
    """
    pre_rocket_lst = []
    if wcfg.modules:
        pre_rocket_lst.append('module purge')
    pre_rocket_lst.extend([m.get_command(m.name) for m in wcfg.default_modules])
    if kwargs.get('modules'):
        for key, val in kwargs.get('modules').items():
            miter = (m.get_command(key, val) for m in wcfg.modules)
            try:
                match = next(m for m in miter if m is not None)
            except StopIteration as err:
                msg = f'no matching module {key}{val}'
                raise ResourceConfigurationError(msg) from err
            pre_rocket_lst.append(match)
    default_venv = []
    if wcfg.default_venv:
        if wcfg.default_venv['type'] == 'conda':
            venv_name = wcfg.default_venv['name']
            default_venv.append(f'conda activate {venv_name}')
        elif wcfg.default_venv['type'] == 'venv':
            venv_prefix = wcfg.default_venv['prefix']
            activate = os.path.join(venv_prefix, 'bin', 'activate')
            default_venv.append(f'source {activate}')
    pre_rocket_lst.extend(default_venv)
    default_vars = []
    for key in wcfg.default_envvars:
        if key not in wcfg.envvars:
            raise ResourceConfigurationError(f'default envvar {key} not in envvars')
        val = wcfg.envvars[key]
        comm = f'unset {key}' if val is None else f'export {key}={val}'
        default_vars.append(comm)
    pre_rocket_lst.extend(default_vars)
    if kwargs.get('envs'):
        for key, val in kwargs.get('envs').items():
            if key not in wcfg.default_envvars:
                if key in wcfg.envvars:
                    val = wcfg.envvars[key]
                comm = f'unset {key}' if val is None else f'export {key}={val}'
                pre_rocket_lst.append(comm)
    pre_rocket_lst.extend([c.get_command() for c in wcfg.default_commands])
    return '; '.join(pre_rocket_lst)


def validate_resources(wcfg, qcfg, g_name=None, **kwargs):
    """Validate required resources for a specific worker and queue

    Args:
        wcfg (WorkerConfig): worker configuration object
        qcfg (QueueConfig): queue configuration object
        g_name (str): group name to be used for accounting
        kwargs (dict): required resources

    Raises:
        ResourceConfigurationError: if the required resources are not valid
    """
    if qcfg.name not in (q.name for q in wcfg.queues):
        msg = f'queue {qcfg.name} not in the list of queues'
        raise ResourceConfigurationError(msg)
    if g_name is not None:
        if g_name not in wcfg.accounts:
            msg = f'group {g_name} not in the list of groups'
            raise ResourceConfigurationError(msg)
    for key, val in kwargs.items():
        if key in res_mapper:
            qcfg.validate_resource(res_mapper[key], val)
    get_pre_rocket(wcfg, **kwargs)


def get_worker_get_queue(cfg=None, w_name=None, q_name=None, g_name=None, **kwargs):
    """
    Return worker and queue matching a resource requirement

    Args:
        cfg (ResConfig): resource configuration object, if None then it will
        be loaded from resconfig file
        w_name (str): name of worker
        q_name (str): name of the queue, ignored if w_name is None
        g_name (str): group name to be used for accounting
        kwargs (dict): required resources

    Returns:
        tuple(WorkerConfig, QueueConfig): worker and queue in case of match,
        (None, None) otherwise

    Raises:
        ResourceConfigurationError: if resconfig (cfg) is not provided / found
    """
    cfg = cfg or get_default_resconfig()
    if cfg is None:
        msg = 'Resource configuration file not found.'
        raise ResourceConfigurationError(msg)
    if w_name is None:
        for wcfg in (cfg.default_worker, *cfg.workers):
            for queue in (wcfg.default_queue, *wcfg.queues):
                if queue:
                    try:
                        validate_resources(wcfg, queue, g_name, **kwargs)
                    except ResourceConfigurationError:
                        continue
                    return wcfg, queue
    else:
        try:
            wcfg = next(w for w in cfg.workers if w.name == w_name)
        except StopIteration:
            return None, None
        if q_name is None:
            for queue in (wcfg.default_queue, *wcfg.queues):
                if queue:
                    try:
                        validate_resources(wcfg, queue, g_name, **kwargs)
                    except ResourceConfigurationError:
                        continue
                    return wcfg, queue
        else:
            try:
                queue = next(q for q in wcfg.queues if q.name == q_name)
                validate_resources(wcfg, queue, g_name, **kwargs)
            except (StopIteration, ResourceConfigurationError):
                return None, None
            return wcfg, queue
    return None, None


def get_custom_qadapter(cfg=None, w_name=None, q_name=None, g_name=None,
                        lp_file=None, **kwargs):
    """
    Construct a custom queue adapter for the first matching resources
    always starting from the default resources

    Args:
        cfg (ResConfig): resource configuration object, if None then it will
        be loaded from resconfig file
        w_name (str): name of worker
        q_name (str): name of the queue, ignored if w_name is None
        g_name (str): group name to be used for accounting
        lp_file (str): a custom launchpad file to be specified in the
        rocket_launch section of qadapter

    Returns:
        tuple (str, CommonAdapter): worker name, qadapter object in case of match,
        (None, None) otherwise
    """
    wcfg, qcfg = get_worker_get_queue(cfg, w_name, q_name, g_name, **kwargs)
    if not (wcfg and qcfg):
        return None, None
    return wcfg.name, get_qadapter(wcfg, qcfg, g_name, lp_file, **kwargs)


def get_qadapter(wcfg, qcfg, g_name=None, lp_file=None, **kwargs):
    """
    Return a qadapter for specific worker, queue and optionally specified
    resources

    Args:
        wcfg (WorkerConfig): worker configuration object
        qcfg (QueueConfig): queue configuration object
        g_name (str): group name to be used for accounting
        lp_file (str): a custom launchpad file to be specified in the
        rocket_launch section of qadapter

    Returns:
        CommonAdapter: qadapter object
        None: if worker type not specified
    """
    if wcfg.type_ is None:
        return None
    qadapter = {}
    qadapter['q_type'] = wcfg.type_
    assert qcfg.name in (q.name for q in wcfg.queues)
    qadapter['q_name'] = qcfg.name
    qadapter['queue'] = qcfg.name  # the launcher requires this redundant key
    ntasks = kwargs.pop('ntasks', None)
    if ntasks is not None:
        if 'cpus_per_task' not in kwargs:
            kwargs['cpus_per_task'] = qcfg.get_resource('cpus_per_task').default
        if 'ntasks_per_node' not in kwargs:
            if 'nodes' not in kwargs:
                ncores = ntasks * kwargs['cpus_per_task']
                ncores_per_node = qcfg.get_resource('cpus_per_node').maximum
                kwargs['nodes'] = math.ceil(ncores/ncores_per_node)
            kwargs['ntasks_per_node'] = ntasks // kwargs['nodes']
    for key, val in kwargs.items():
        if key in res_mapper:
            qadapter[key] = val
    for key1, key2 in res_mapper.items():
        if key1 not in kwargs:
            res = qcfg.get_resource(key2)
            if res is not None:
                qadapter[key1] = res.default
    if lp_file is not None:
        if not os.path.exists(lp_file):
            raise ResourceConfigurationError(f'file {lp_file} does not exist')
        qadapter['rocket_launch'] = f'rlaunch -l {lp_file} singleshot'
    else:
        qadapter['rocket_launch'] = 'rlaunch singleshot'
    qadapter['ntasks'] = qadapter['nodes'] * qadapter['ntasks_per_node']
    if g_name is not None:
        assert g_name in wcfg.accounts
        qadapter['account'] = g_name
    else:
        qadapter['account'] = wcfg.default_account
    qadapter['pre_rocket'] = get_pre_rocket(wcfg, **kwargs)
    if wcfg.default_launchdir:
        qadapter['launch_dir'] = wcfg.default_launchdir
    return CommonAdapter(**qadapter)
