"""A simple interface to query fireworks and workflows"""
from virtmat.middleware.exceptions import ConfigurationException


def get_launch(lpad, query):
    """Return a single firework from a query and its most recent launch"""
    fw_list = list(lpad.fireworks.find(query))
    if len(fw_list) == 0:
        return None, None
    if len(fw_list) != 1:
        raise ConfigurationException('fw_list must have length 0 or 1')
    fwk = fw_list[0]
    if len(fwk['launches']) > 0:
        launch = lpad.launches.find_one({'launch_id': fwk['launches'][-1]})
    else:
        launch = None
    return fwk, launch


def db_select(lpad, filters=None, ids=None, selects=None):
    """Apply workflow query filters and then select updates from launch"""

    if filters is None:
        filters = {}
    if ids is None:
        ids = []
    if selects is None:
        selects = []
    if not (isinstance(filters, dict) or ids):
        raise ConfigurationException('filters be a dict or ids may not be empty')
    if not ids:
        wfq = filters.get('workflows', {})
        fwq = filters.get('fireworks', {})
        projection = {'nodes': True}
        wfns = [i['nodes'] for i in lpad.workflows.find(wfq, projection)]
        if fwq:
            projection = {'fw_id': True}
            fws = [i['fw_id'] for i in lpad.fireworks.find(fwq, projection)]
            wfnsf = [wfn[0] for wfn in wfns if any(i in wfn for i in fws)]
        else:
            wfnsf = [wfn[0] for wfn in wfns]
    else:
        wfnsf = ids

    result = []
    for wf_id in wfnsf:
        wfl = lpad.workflows.find_one({'nodes': wf_id})
        wf_data = {}
        wf_data['name'] = wfl['name']
        wf_data['metadata'] = wfl['metadata']
        wf_data['state'] = wfl['state']
        wf_data['fws'] = []
        for select in selects:
            query = {'name': select['fw_name'], 'fw_id': {'$in': wfl['nodes']}}
            fwk, launch = get_launch(lpad, query)
            fw_data = {}
            if fwk:
                fw_data['name'] = select['fw_name']
                fw_data['id'] = fwk['fw_id']
                fw_data['updated_on'] = fwk['updated_on']
                fw_data['created_on'] = fwk['created_on']
                fw_data['state'] = fwk['state']
                fw_data['parents'] = wfl['parent_links'].get(str(fwk['fw_id']))
                if select.get('add fw_spec', False):
                    fw_data['spec'] = fwk['spec']
                if launch and launch.get('action'):
                    outputs = select.get('fw_updates')
                    updates = launch['action'].get('update_spec')
                    if isinstance(outputs, list):
                        fw_data['updates'] = {o: updates[o] for o in outputs}
                    elif outputs:
                        fw_data['updates'] = updates
                    else:
                        fw_data['updates'] = None
                else:
                    fw_data['updates'] = None
                if launch:
                    fw_data['launch_dir'] = launch.get('launch_dir')
            wf_data['fws'].append(fw_data)
        result.append(wf_data)
    return result
