"""custom duplicate finders for use with the custom firetasks"""
from fireworks.features.dupefinder import DupeFinderBase
from virtmat.language.utilities.logging import get_logger
from virtmat.language.utilities.compatibility import versions


class DupeFinderFunctionTask(DupeFinderBase):
    """for nodes with FunctionTask only; don't use in root, meta and i/o nodes"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    def query(self, spec):
        queries_fast = []
        queries_slow = []
        assert '_source_code' in spec
        assert len(spec['_tasks']) == len(spec['_source_code'])
        for ind, (tsk, src) in enumerate(zip(spec['_tasks'], spec['_source_code'])):
            assert 'FunctionTask' in tsk['_fw_name']
            query = {}
            query['spec._source_code.'+str(ind)] = src
            query['spec._tasks.'+str(ind)+'._fw_name'] = tsk['_fw_name']
            query['spec._tasks.'+str(ind)+'.inputs'] = tsk['inputs']
            query['spec._tasks.'+str(ind)+'.outputs'] = tsk['outputs']
            queries_fast.append(query)
            query_data = {'spec.'+inp: spec.get(inp) for inp in tsk['inputs']}
            queries_slow.append(query_data)
        query = {}
        query['spec._grammar_version'] = {'$in': versions['grammar']}
        query['spec._data_schema_version'] = {'$in': versions['data_schema']}
        queries_fast.append(query)
        queries = queries_fast + queries_slow
        get_logger(__name__).debug('query: %s', queries)
        dfn = {'spec._dupefinder._fw_name': self._fw_name}
        return {'$and': [{'launches': {'$ne': []}}, dfn, *queries]}

    def verify(self, spec1, spec2):
        return True
