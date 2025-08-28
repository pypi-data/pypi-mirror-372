"""Perform simple workflow queries"""
import re
import copy
from prettytable import PrettyTable
from virtmat.middleware.exceptions import ConfigurationException


WF_PROJECTION = {
    '$project': {
        '_id': False,
        'name': True,
        'metadata': True,
        'state': True,
        'nodes': True,
        'parent_links': True,
        'fws': True,
        'created_on': True,
        'updated_on': True
    }
}


FW_PROJECTION = {
    '$project': {
        '_id': False,
        'fw_id': True,
        'name': True,
        'spec': True,
        'state': True,
        'created_on': True,
        'updated_on': True,
        'updates': True,
        'launch_dir': True
    }
}


FW_PIPELINE = [
    {
        '$match': {
            '$expr': {
                '$in': ['$fw_id', '$$mynodes']
            }
        }
    },
    {
        '$project': {
            'last_launch_id': {
                '$slice': ['$launches', -1]
            },
            'fw_id': True,
            'name': True,
            'spec': True,
            'state': True,
            'created_on': True,
            'updated_on': True
        }
    },
    {
        '$lookup': {
            'from': 'launches',
            'localField': 'last_launch_id',
            'foreignField': 'launch_id',
            'as': 'last_launch'
        }
    },
    {
        '$addFields': {
            'updates': {
                '$arrayElemAt': ['$last_launch.action.update_spec', 0]
            },
            'launch_dir': {
                '$arrayElemAt': ['$last_launch.launch_dir', 0]
            }
        }
    },
    FW_PROJECTION
]


CLEANUP_WFS = {'$match': {'fws': {'$not': {'$size': 0}}}}


def io_info(fw_dict, io_kind, storage):
    """
    Get tuples of data names and types from a firework, restricted to PyTask

    Args:
        fw_dict (dict): Firework dictionary
        io_kind (str): Either 'inputs' or 'outputs'
        storage (dict): Dictionary where the data has been stored
    Returns:
        ([tuple]): A list of tuples containing data names and data types
    """
    names = []
    for task in fw_dict['spec']['_tasks']:
        if task['_fw_name'] == 'PyTask':
            names.extend(task.get(io_kind, []))
    types = [type(storage.get(n)) for n in names]
    return list(zip(names, types))


def task_info(fw_dict):
    """
    Get info about dataflow tasks, restricted to PyTask

    Args:
        fw_dict (dict): Firework dictionary
    Returns:
        res ([dict]): A list of dictionaries with the following keys:
            name (str): the Python function called in the PyTask
            inputs (list, None): List of input data names
            outputs (list, None): List of output data names
    """
    res = []
    for task in fw_dict['spec']['_tasks']:
        if task['_fw_name'] == 'PyTask':
            info = {'name': task['func'], 'inputs': task.get('inputs'),
                    'outputs': task.get('outputs')}
            res.append(info)
    return res


class WFQuery(list):
    """
    Perform a query in fireworks launchpad

    Args:
        lpad (LaunchPad): a FireWorks LaunchPad object
        wf_query (dict): pymongo query for the workflows collection
        fw_query (dict): pymongo query for the fireworks collection
    """

    def __init__(self, lpad, wf_query=None, fw_query=None, metadata_only=False):
        if wf_query is None:
            wf_query = {}
        if fw_query is None:
            fw_query = {}
        fw_pipeline = copy.deepcopy(FW_PIPELINE)
        if metadata_only:
            fw_pipeline[1]['$project']['spec'] = {'_tasks': True}
            del fw_pipeline[3]['$addFields']['updates']
        query_wfs = {'$match': wf_query}
        query_fws = {'$lookup': {
            'from': 'fireworks',
            'let': {'mynodes': '$nodes'},
            'pipeline': [{'$match': fw_query}] + fw_pipeline,
            'as': 'fws'}}
        pipeline = [query_wfs, query_fws, WF_PROJECTION, CLEANUP_WFS]
        super().__init__(lpad.workflows.aggregate(pipeline))

    def get_wf_ids(self):
        """Return the firework ids, one for each worklfow"""
        return [next(fw['fw_id'] for fw in wf['fws']) for wf in self]

    def get_fw_ids(self):
        """Return the firework ids, complete list"""
        return [fw['fw_id'] for wf in self for fw in wf['fws']]

    def check_fw_ids(self, fw_ids=None):
        """
        If None return full list of fw_ids otherwise make a check

        Args:
            fw_ids ([int], None): list of firework ids
        Returns:
            retval ([int]): list of firework ids
        """
        my_fw_ids = self.get_fw_ids()
        if fw_ids is None:
            retval = my_fw_ids
        else:
            if not all(i in my_fw_ids for i in fw_ids):
                raise ConfigurationException('invalid fw_ids')
            retval = fw_ids
        return retval

    def get_wf_info(self, fw_ids=None, add_io_info=True):
        """
        Display a summary of workflows including specific nodes

        Args:
            fw_ids ([int], None): list of firework ids
            add_io_info (bool): display/not display node inputs and outputs
        """
        my_fw_ids = self.check_fw_ids(fw_ids)
        fw_info = self.get_fw_info(add_io_info=add_io_info)
        for wfl in self:
            if any(i in wfl['nodes'] for i in my_fw_ids):
                templ = '\nworkflow name: {}\nworkflow state: {}\nupdated on: {}'
                print(templ.format(wfl['name'], wfl['state'], wfl['updated_on']))
                columns = fw_info[0].keys()
                table = PrettyTable(columns)
                for fwk in fw_info:
                    if fwk['fw_id'] in wfl['nodes']:
                        table.add_row([fwk[i] for i in columns])
                print(table)

    def get_fw_info(self, fw_ids=None, add_io_info=True):
        """
        Provide detailed information about specific nodes

        Args:
            fw_ids ([int], None): list of firework ids
            add_io_info (bool): indicates whether to add node inputs and outputs
        Returns:
            res ([dict]): a list of dictionaries with name, fw_id, state,
                          time stamp, parents, inputs and outputs
        """
        my_fw_ids = self.check_fw_ids(fw_ids)
        res = []
        for wfl in self:
            for fwk in wfl['fws']:
                if fwk['fw_id'] in my_fw_ids:
                    outputs = fwk.get('updates', {})
                    o_name_type = io_info(fwk, 'outputs', outputs)
                    i_name_type = io_info(fwk, 'inputs', fwk['spec'])
                    parents = wfl['parent_links'].get(str(fwk['fw_id']), [])
                    fwinfo_keys = ['name', 'fw_id', 'state', 'updated_on']
                    fwinfo = [fwk[k] for k in fwinfo_keys]
                    if add_io_info:
                        fwinfo += [parents, i_name_type, o_name_type]
                        fwinfo_keys += ['parents', 'inputs', 'outputs']
                    else:
                        fwinfo += [parents]
                        fwinfo_keys += ['parents']
                    res.append(dict(zip(fwinfo_keys, fwinfo)))
        return res

    def get_i_names(self, fw_ids=None):
        """
        Return input data names in selected fireworks

        Args:
            fw_ids ([int], None): list of firework ids
        Returns:
            ({str}): a set of input data names in the specified fireworks
        """
        my_fw_ids = self.check_fw_ids(fw_ids)
        fws = self.get_fw_info(my_fw_ids)
        return set(i for fw in fws for i in fw['inputs'])

    def get_o_names(self, fw_ids=None):
        """
        Return output data names in selected fireworks

        Args:
            fw_ids ([int], None): list of firework ids
        Returns:
            ({str}): a set of output data names in the specified fireworks
        """
        my_fw_ids = self.check_fw_ids(fw_ids)
        fws = self.get_fw_info(my_fw_ids)
        return set(o for fw in fws for o in fw['outputs'])

    def get_task_info(self, fw_ids=None):
        """
        Return the dataflow from PyTask firetasks in selected fireworks

        Args:
            fw_ids ([int], None): list of firework ids
        Returns:
            res ([dict]): list of dictionaries containing the task info
        """
        my_fw_ids = self.check_fw_ids(fw_ids)
        res = []
        for wfl in self:
            for fwk in wfl['fws']:
                if fwk['fw_id'] in my_fw_ids:
                    res.append({'fw id': fwk['fw_id'], 'tasks': task_info(fwk)})
        return res

    def get_data(self, dname, io_kind):
        """
        Return the input/output data for a given data name

        Args:
            dname (str): data name
            io_kind (str): one of 'input' or 'output'
        Returns:
            res ([dict]): a list of dictionaries with the following keys:
                fw_id (int): firework ID
                dname (str): data name, the value is the data or None
        """
        if io_kind not in ['input', 'output']:
            raise ConfigurationException('io_kind not input or output')
        dct = 'spec' if io_kind == 'input' else 'updates'
        res = []
        for wfl in self:
            for fwk in wfl['fws']:
                if fwk.get(dct):
                    data = fwk[dct].get(dname)
                    if data:
                        res.append({'fw id': fwk['fw_id'], dname: data})
        return res

    def get_i_data(self, dname):
        """
        Return the input data for a given data name

        Args:
            dname (str): data name
        Returns:
            res ([dict]): a list of dictionaries with the following keys:
                fw_id (int): firework ID
                dname (str): data name, the value is the data or None
        """
        return self.get_data(dname, 'input')

    def get_o_data(self, dname):
        """
        Return the output data for a given data name

        Args:
            dname (str): data name
        Returns:
            res ([dict]): a list of dictionaries with the following keys:
                fw_id (int): firework ID
                dname (str): data name, the value is the data or None
        """
        return self.get_data(dname, 'output')

    def get_nodes_providing(self, dname, match='string'):
        """
        Return the ids of nodes providing a specified output

        Args:
            dname (str): output data name (or a regular expression)
            match (str): either 'string' for an exact string match or
            'regex' for a regular expression match
        Returns:
            ([int]): a list of matching node ids
        """
        fws = self.get_fw_info()
        if match == 'string':
            return [f['fw_id'] for f in fws for o, _ in f['outputs'] if dname == o]
        if match != 'regex':
            raise ConfigurationException('match type must be either string or regex')
        return [f['fw_id'] for f in fws for o, _ in f['outputs'] if re.match(dname, o)]
