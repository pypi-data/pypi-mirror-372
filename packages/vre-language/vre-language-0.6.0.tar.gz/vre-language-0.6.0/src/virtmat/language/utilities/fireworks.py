"""helper functions to interface fireworks"""
import os
import contextlib
from collections import Counter
import pandas
from fireworks import Workflow, Firework, FWorker, Launch
from fireworks.utilities.fw_serializers import load_object
from fireworks.core.rocket_launcher import rapidfire, launch_rocket
from fireworks.core.launchpad import WFLock
from virtmat.middleware.engine.wfengine import WFEngine
from virtmat.middleware.resconfig import get_default_resconfig
from virtmat.middleware.utilities import get_slurm_job_state, exec_cancel
from virtmat.language.utilities.errors import FILE_READ_EXCEPTIONS
from virtmat.language.utilities.errors import ObjectFromFileError, UpdateError
from virtmat.language.utilities.mongodb import get_iso_datetime
from virtmat.language.utilities.serializable import tag_deserialize
from virtmat.language.utilities.formatters import formatter


@contextlib.contextmanager
def launchdir(tmp_dir):
    """switch to a launch directory temporarily"""
    init_dir = os.getcwd()
    os.chdir(tmp_dir)
    try:
        yield
    finally:
        os.chdir(init_dir)


def run_fireworks(lpad, fw_ids, worker_name=None, create_subdirs=False):
    """launch fireworks with the provided fw_ids"""
    fw_query = {'fw_id': {'$in': fw_ids}}
    launch_kwargs = {'strm_lvl': lpad.strm_lvl}
    launch_kwargs['fworker'] = FWorker(name=worker_name, query=fw_query)
    cfg = get_default_resconfig()
    if cfg:
        if worker_name:
            wcfg = next(w for w in cfg.workers if w.name == worker_name)
        else:
            wcfg = cfg.default_worker  # not covered
        default_launchdir = wcfg.default_launchdir or os.getcwd()
    else:
        default_launchdir = os.getcwd()  # not covered
    with launchdir(default_launchdir):
        if create_subdirs:
            rapidfire(lpad, nlaunches=0, local_redirect=True, **launch_kwargs)
        else:
            for _ in fw_ids:
                launch_rocket(lpad, **launch_kwargs)


def get_nodes_providing(lpad, uuid, name):
    """find all nodes providing an output name in a workflow with given uuid"""
    return lpad.get_fw_ids_in_wfs({'metadata.uuid': uuid}, {'spec._tasks.outputs': name})


def get_var_names(lpad, fw_ids):
    """return a list of names of variables corresponding to a list of fw_ids"""
    fw_q = {'fw_id': {'$in': fw_ids}}
    fw_p = {'spec._tasks.outputs': True}
    nodes = [n for w in get_nodes_info_mongodb(lpad, {}, fw_q, fw_p) for n in w['nodes']]
    return [t['outputs'][0] for node in nodes for t in node['spec']['_tasks']]


def get_root_node_ids(lpad, uuid):
    """find the special root node in a workflow with given uuid"""
    return lpad.get_fw_ids_in_wfs({'metadata.uuid': uuid}, {'name': '_fw_root_node'})


def get_parent_nodes(lpad, uuid, firework):
    """find parent nodes for a new firework in a workflow with a given uuid"""
    if all('inputs' in t and len(t['inputs']) == 0 for t in firework.tasks):
        parents = get_root_node_ids(lpad, uuid)
        assert len(parents) == 1
    else:
        inputs = [i for t in firework.tasks for i in t['inputs']]
        parents = set()
        for inp in inputs:
            nodes = get_nodes_providing(lpad, uuid, inp)
            if len(nodes) != 0:
                assert len(nodes) == 1
                parents.update(nodes)
            elif inp in firework.spec:
                parents.add('root_node')
            else:
                parents.add(None)
        assert len(parents) > 0
        if 'root_node' in parents:
            parents.remove('root_node')
            if len(parents) == 0:
                parents = get_root_node_ids(lpad, uuid)
                assert len(parents) == 1
    return list(parents)


def get_ancestors(lpad, fw_id):
    """return a list of all ancestors' fw_ids of a node with fw_id"""
    wfl = get_nodes_info(lpad, {'nodes': fw_id}, {}, {'_id': True}, {'links': True})
    wfl_pl = Workflow.Links.from_dict(wfl[0]['links']).parent_links
    parents = wfl_pl.get(fw_id, [])
    ancestors = set()
    while parents:
        ancestors.update(parents)
        new_parents = set()
        for par in iter(parents):
            new_parents.update(wfl_pl.get(par, []))
        parents = new_parents
    return list(ancestors)


def safe_update(lpad, fw_id, update_dict):
    """update the node spec in a safe way"""
    state = lpad.fireworks.find_one({'fw_id': fw_id}, {'state': True})['state']
    if state == 'COMPLETED':
        lpad.defuse_fw(fw_id, rerun_duplicates=False)
        lpad.update_spec([fw_id], update_dict)
        lpad.reignite_fw(fw_id)
    elif state in ['WAITING', 'READY']:
        lpad.update_spec([fw_id], update_dict)
    elif state == 'FIZZLED':
        lpad.update_spec([fw_id], update_dict)
        lpad.rerun_fw(fw_id, rerun_duplicates=False)
    elif state == 'DEFUSED':
        lpad.update_spec([fw_id], update_dict)
        lpad.reignite_fw(fw_id)
        state = lpad.fireworks.find_one({'fw_id': fw_id}, {'state': True})['state']
        if state not in ['READY', 'WAITING']:
            lpad.rerun_fw(fw_id, rerun_duplicates=False)
    elif state == 'PAUSED':
        lpad.update_spec([fw_id], update_dict)
        lpad.resume_fw(fw_id)
    else:
        assert state in ['ARCHIVED', 'RESERVED', 'RUNNING']
        raise UpdateError(f'Cannot update variable in {state} state.')


def get_nodes_info_mongodb(lpad, wf_query, fw_query, fw_proj, wf_proj=None):
    """find all nodes for each matching workflow and returns selected info"""
    wfp = {'metadata.uuid': True} if wf_proj is None else dict(wf_proj)
    fw_pipeline = [{'$match': {**fw_query, '$expr': {'$in': ['$fw_id', '$$mynodes']}}},
                   {'$project': {**fw_proj, '_id': False}}]
    wf_lookup = {'from': 'fireworks', 'let': {'mynodes': '$nodes'},
                 'pipeline': fw_pipeline, 'as': 'nodes'}
    wf_pipeline = [{'$match': wf_query}, {'$lookup': wf_lookup},
                   {'$project': {'_id': False, 'nodes': True, **wfp}}]
    cursor = lpad.workflows.aggregate(wf_pipeline)
    return list(cursor)


def get_nodes_info_mongomock(lpad, wf_query, fw_query, fw_proj, wf_proj=None):  # not covered
    """find all nodes for each matching workflow and returns selected info"""
    wfp = {'metadata.uuid': True} if wf_proj is None else dict(wf_proj)
    wfp.update({'nodes': True, '_id': False})
    wfs = []
    for wfn in lpad.workflows.find(wf_query, wfp):
        fwq = {**fw_query, '$expr': {'$in': ['$fw_id', wfn['nodes']]}}
        wfn['nodes'] = list(lpad.fireworks.find(fwq, fw_proj))
        wfs.append(wfn)
    return wfs


if os.environ.get('MONGOMOCK_SERVERSTORE_FILE'):
    get_nodes_info = get_nodes_info_mongomock  # not covered
else:
    get_nodes_info = get_nodes_info_mongodb


def object_from_file(class_, path):
    """a wrapper function to call various from_file-type class methods"""
    try:
        return class_.from_file(path)
    except tuple(FILE_READ_EXCEPTIONS) as err:  # tuple() to avoid E0712
        raise ObjectFromFileError(err, path) from err


def retrieve_value(lpad, launch_id, name):
    """retrieve the output value from the FWAction of a given launch"""
    return lpad.get_launch_by_id(launch_id).action.update_spec[name].value


def get_vary_df(lpad, uuid):
    """retrieve the vary table from the meta-node"""
    wf_q = {'metadata.uuid': uuid}
    fw_q = {'name': '_fw_meta_node', 'spec._vary': {'$exists': True}}
    fw_p = {'spec._vary': True}
    nodes = next(d['nodes'] for d in get_nodes_info(lpad, wf_q, fw_q, fw_p))
    if nodes:
        assert len(nodes) == 1
        return load_object(nodes[0]['spec']['_vary'])
    return None


def get_lost_reserved_running_ids(lpad=None, uuid=None, wfengine=None):
    """return firework IDs with lost reserved or lost running launches"""
    assert lpad and uuid or wfengine
    wfe = wfengine or WFEngine(lpad, wf_query={'metadata.uuid': uuid})
    return wfe.get_unreserved_nodes(), wfe.get_lost_jobs()


def get_lost_reserved_running(lpad=None, uuid=None, wfengine=None):
    """return names of variables with lost reserved or lost running launches"""
    assert lpad and uuid or wfengine  # eliminate wfengine in future
    wfe = wfengine or WFEngine(lpad, wf_query={'metadata.uuid': uuid})
    lpad = lpad or wfe.launchpad
    unres, lostj = get_lost_reserved_running_ids(wfengine=wfe)
    unres_vars = unres and get_var_names(lpad, [n['fw_id'] for n in unres])
    lostj_vars = lostj and get_var_names(lpad, lostj)
    return unres_vars, lostj_vars


def cancel_eval(lpad, fw_id, restart=False, deactivate=False):  # not covered
    """cancel a pending or running evaluation"""
    fw_p = {'state': True, 'spec._category': True}
    fw = lpad.fireworks.find_one({'fw_id': fw_id}, fw_p)
    assert fw['state'] in ['RESERVED', 'RUNNING']
    assert restart or deactivate
    assert not restart or not deactivate
    res_id = lpad.get_reservation_id_from_fw_id(fw_id)
    if fw['spec']['_category'] == 'batch':
        try:
            if get_slurm_job_state(res_id) in ['PENDING', 'RUNNING']:
                exec_cancel(res_id)
        except RuntimeError as err:
            raise UpdateError(str(err)) from err
    if fw['state'] == 'RESERVED':
        if deactivate:
            lpad.pause_fw(fw_id)
        else:
            lpad.cancel_reservation_by_reservation_id(res_id)
    elif fw['state'] == 'RUNNING':
        if restart:
            lpad.rerun_fw(fw_id)
        else:
            lpad.defuse_fw(fw_id)


def rerun_vars(lpad, uuid, var_names):
    """manually change the state of a list of variables: apply rerun"""
    mapping = {'FIZZLED': lpad.rerun_fw,
               'DEFUSED': lpad.reignite_fw,
               'PAUSED': lpad.resume_fw,
               'RESERVED': lambda x: cancel_eval(lpad, x, restart=True),
               'RUNNING': lambda x: cancel_eval(lpad, x, restart=True),
               'COMPLETED': lpad.rerun_fw}
    change_vars(lpad, uuid, var_names, mapping)


def cancel_vars(lpad, uuid, var_names):
    """manually change the state of a list of variables: apply cancel"""
    mapping = {'FIZZLED': lpad.defuse_fw,
               'PAUSED': lpad.defuse_fw,
               'WAITING': lpad.pause_fw,
               'READY': lpad.pause_fw,
               'RESERVED': lambda x: cancel_eval(lpad, x, deactivate=True),
               'RUNNING': lambda x: cancel_eval(lpad, x, deactivate=True)}
    change_vars(lpad, uuid, var_names, mapping)


def change_vars(lpad, uuid, var_names, mapping):
    """manually change the state of a list of variables"""
    for name in var_names:
        wf_q = {'metadata.uuid': uuid}
        fw_q = {'spec._tasks.outputs': {'$in': var_names}}
        fw_p = {'state': True, 'spec._tasks.outputs': True, 'fw_id': True}
        wfs = get_nodes_info(lpad, wf_q, fw_q, fw_p)
        assert len(wfs) == 1
        var_names_found = []
        for node in wfs[0]['nodes']:
            v_names = [o for t in node['spec']['_tasks'] for o in t['outputs']]
            assert len(v_names) == 1  # assume always one task with one output
            var_names_found.extend(v_names)
        if not all(n in var_names_found for n in var_names):
            not_found = next(n for n in var_names if n not in var_names_found)
            raise UpdateError(f'Variable {not_found} not found in the model.')
        for node, name in zip(wfs[0]['nodes'], var_names_found):
            if node['state'] not in mapping:
                msg = f'State of variable {name} not allowed: {node["state"]}'
                raise UpdateError(msg)
            mapping[node['state']](node['fw_id'])


def get_representative_launch(launches):
    """
    Select a representative launch (one with the largest state rank) from a list.
    If there are multiple COMPLETED launches then the most recent of them is returned.
    This function is almost identical to the internal static method with the same
    name in fireworks/core/firework.py

    Args:
        launches ([Launch]): iterable of Launch objects

    Returns:
        (Launch): a representative launch
    """
    max_score = Firework.STATE_RANKS['ARCHIVED']
    m_launch = None
    completed_launches = []
    for launch in launches:
        if Firework.STATE_RANKS[launch.state] > max_score:
            max_score = Firework.STATE_RANKS[launch.state]
            m_launch = launch
            if launch.state == 'COMPLETED':
                completed_launches.append(launch)
    if completed_launches:
        return max(completed_launches, key=lambda v: v.time_end)
    return m_launch


def get_launches(lpad, launch_ids):
    """get launches (without action and trackers) from a list of launch IDs"""
    launch_q = {'launch_id': {'$in': launch_ids}}
    launch_p = {'action': False, 'trackers': False}  # avoid bulky objects
    return [Launch.from_dict(d) for d in lpad.launches.find(launch_q, launch_p)]


def get_fw_metadata(lpad, wf_query, fw_query):
    """retrieve fireworks metadata"""
    proj_keys = ['fw_id', 'name', 'state', 'created_on', 'updated_on',
                 'launches', 'archived_launches', 'spec._category',
                 'spec._worker', 'spec._grammar_version', 'spec._python_version',
                 'spec._data_schema_version', 'spec._dupefinder']
    wfs = get_nodes_info(lpad, wf_query, fw_query, {k: True for k in proj_keys},
                         {'metadata': True, 'parent_links': True})
    assert len(wfs) == 1
    assert len(wfs[0]['nodes']) == 1
    node = wfs[0]['nodes'][0]
    launches = get_launches(lpad, node['launches'])
    arch_launches = get_launches(lpad, node['archived_launches'])
    total_runtime = (sum(i.runtime_secs or 0 for i in launches) +
                     sum(i.runtime_secs or 0 for i in arch_launches))
    repr_launch = get_representative_launch(launches)
    reprl_runtime = repr_launch and repr_launch.runtime_secs or 0
    lostres, lostrun = get_lost_reserved_running_ids(lpad, wfs[0]['metadata']['uuid'])
    slurm_states = [n['slurm_state'] for n in lostres if n['fw_id'] == node['fw_id']]
    slurm_state = slurm_states[0] if slurm_states else None
    return {'group UUID': wfs[0]['metadata']['g_uuid'],
            'model UUID': wfs[0]['metadata']['uuid'],
            'node UUID': node['name'],
            'node ID': node['fw_id'],
            'parent IDs': wfs[0]['parent_links'].get(str(node['fw_id']), []),
            'node state': node['state'],
            'created on': get_iso_datetime(node['created_on']),
            'updated on': get_iso_datetime(node['updated_on']),
            'grammar version': node['spec'].get('_grammar_version'),
            'data schema version': node['spec'].get('_data_schema_version'),
            'python version': node['spec'].get('_python_version'),
            'category': node['spec'].get('_category'),
            'fworker': node['spec'].get('_worker'),
            'dupefinder': bool(node['spec'].get('_dupefinder')),
            'reservation ID': lpad.get_reservation_id_from_fw_id(node['fw_id']),
            'number of launches': len(node['launches']),
            'number of archived launches': len(node['archived_launches']),
            'launch_dir': [lnch.launch_dir for lnch in launches],
            'archived launch_dir': [lnch.launch_dir for lnch in arch_launches],
            'runtime_secs': reprl_runtime,
            'runtime_secs total': total_runtime,
            'lost launch':  bool(slurm_states) or node['fw_id'] in lostrun,
            'slurm state': slurm_state
            }


def get_model_nodes(lpad, uuid):
    """return the list of nodes in a persistent model with provided uuid"""
    wf_q = {'metadata.uuid': uuid}
    fw_q = {'spec._source_code': {'$exists': True}}
    fw_p = {'spec._source_code': True, 'updated_on': True, 'state': True}
    wfs = get_nodes_info(lpad, wf_q, fw_q, fw_p)
    if wfs:
        return wfs[0]['nodes']
    return []


def get_model_history(lpad, uuid):
    """return node history with some node attributes as pandas dataframe"""
    dct = {'State': [], 'Updated on': [], 'Statement': []}
    for fwk in get_model_nodes(lpad, uuid):
        if fwk['spec']['_source_code']:
            dct['State'].append(fwk['state'])
            timestamp = get_iso_datetime(fwk['updated_on'], add_tzinfo=False, sep=' ')
            dct['Updated on'].append(timestamp)
            dct['Statement'].append('; '.join(fwk['spec']['_source_code']))
    df = pandas.DataFrame(dct).sort_values('Updated on')
    return df[['Updated on', 'State', 'Statement']]  # pylint: disable=E1136


def get_model_tag(lpad, uuid):
    """return the model tag as pandas dataframe"""
    wf_q = {'metadata.uuid': uuid}
    fw_q = {'name': '_fw_meta_node'}
    fw_p = {'spec._tag': True}
    wfs = get_nodes_info(lpad, wf_q, fw_q, fw_p)
    assert len(wfs) == 1
    assert len(wfs[0]['nodes']) == 1
    tag_dct = wfs[0]['nodes'][0]['spec']['_tag']
    return tag_deserialize(tag_dct) if tag_dct else None


def get_models_tags(lpad, uuids):
    """evaluate differences in tags for a list of models"""
    tags = []
    for uuid in uuids:
        tag = get_model_tag(lpad, uuid)
        if tag is not None:
            tag['__'] = pandas.Series([None])
        else:
            tag = pandas.DataFrame({'__': pandas.Series([None])})
        tags.append(tag)
    df = pandas.concat(tags).map(formatter)
    nunique = df.nunique()
    df.drop(nunique[nunique == 1].index, axis=1, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def get_models_overview(lpad, uuids):
    """create an overview of a list of models with given UUIDs"""
    wf_q = {'metadata.uuid': {'$in': uuids}}
    wf_p = {'metadata.uuid': True, 'updated_on': True}
    wfs = list(lpad.workflows.find(wf_q, wf_p))
    gen1 = (get_iso_datetime(wf['updated_on'], add_tzinfo=False, sep=' ') for wf in wfs)
    gen2 = (wf['metadata']['uuid'] for wf in wfs)
    df_1 = pandas.DataFrame({'Updated on': gen1, 'Model UUID': gen2})
    wf_states = []
    for wf in wfs:
        hist = get_model_history(lpad, wf['metadata']['uuid'])
        wf_states.append(dict(Counter(hist['State'].tolist())))
    df_2 = pandas.DataFrame(wf_states).fillna(0).astype('int64')
    df_2.rename(lambda x: x[0:3], axis='columns', inplace=True)
    df_3 = get_models_tags(lpad, uuids)
    return pandas.concat([df_1, df_2, df_3], axis='columns')


def append_wf(lpad, new_wf, fw_ids, detour=False, pull_spec_mods=True):
    """replace LaunchPad.append_wf() adding a performance optimization"""
    wf = lpad.get_wf_by_fw_id_lzyfw(fw_ids[0])
    updated_ids = wf.append_wf(new_wf, fw_ids, detour=detour, pull_spec_mods=pull_spec_mods)
    with WFLock(lpad, fw_ids[0]):
        getattr(lpad, '_update_wf')(wf, updated_ids)  # due to protected member
