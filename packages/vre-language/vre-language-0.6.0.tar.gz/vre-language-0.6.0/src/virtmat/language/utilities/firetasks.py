"""custom firetasks for use in the interpreter"""
import os
import base64
import contextlib
import dill
import pandas
import numpy
from fireworks import Firework
from fireworks.core.firework import FWAction, FireTaskBase
from virtmat.language.utilities.serializable import FWDataObject
from virtmat.language.utilities.errors import CompatibilityError


def get_exception_serializable(exc):
    """make an exception fireworks-serializable
    https://materialsproject.github.io/fireworks/failures_tutorial.html
    """
    cls = exc.__class__
    dct = {'name': cls.__name__, 'module': cls.__module__, 'msg': str(exc),
           'pkl': base64.b64encode(dill.dumps(exc)).decode('utf-8')}
    exc.to_dict = lambda: dct
    return exc


@contextlib.contextmanager
def setenv(varname, value):
    """set or change an environment variable temporarily"""
    var_bck = os.environ.get(varname)
    os.environ[varname] = str(value)
    try:
        yield
    finally:
        if var_bck is None:
            del os.environ[varname]
        else:
            os.environ[varname] = var_bck


class FunctionTask(FireTaskBase):
    """call a pickled function with JSON serializable inputs, return JSON
    serializable outputs"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    required_params = ['func', 'inputs', 'outputs']

    def run_task(self, fw_spec):
        inputs = self.get('inputs', [])
        assert isinstance(inputs, list)
        try:
            params = [fw_spec[i].value for i in inputs]
            func = dill.loads(base64.b64decode(self['func'].encode()))
            with setenv('WORKFLOW_EVALUATION_MODE', 'yes'):
                f_output = func(*params)
        except SystemError as err:  # not covered
            if 'unknown opcode' in str(err):
                python = fw_spec.get('_python_version') or 'unknown'
                msg = (f'This statement has been compiled with incompatible python '
                       f'version: {python}.\nEither rerun and use the same version'
                       f' or use variable update ":=" to re-compile the statement.')
                raise get_exception_serializable(CompatibilityError(msg)) from err
            raise get_exception_serializable(err) from err
        except BaseException as err:
            raise get_exception_serializable(err) from err
        return self.get_fw_action(f_output)

    def get_fw_action(self, output):
        """construct a FWAction object from the output of a function"""
        outputs = self.get('outputs', [])
        assert isinstance(outputs, list)
        assert all(isinstance(o, str) for o in outputs)
        if len(outputs) == 1:
            update_dct = {outputs[0]: FWDataObject.from_obj(output)}
            return FWAction(update_spec=update_dct)
        assert len(outputs) == 0 and output is None
        return FWAction()


class ExportDataTask(FireTaskBase):
    """export specified data to a file or url"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    required_params = ['varname']
    optional_params = ['filename', 'url']

    def run_task(self, fw_spec):
        datastore = {'type': 'file'} if self.get('filename') else {'type': 'url'}
        data_obj = fw_spec[self.get('varname')]
        data_obj.offload_data(datastore=datastore, url=self.get('url'),
                              filename=self.get('filename'))
        return FWAction()


class ScatterTask(FireTaskBase):
    """implement parallelized map function as a dynamic sub-workflow"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    required_params = ['func', 'split', 'inputs', 'chunk_ids', 'spec']

    def run_task(self, fw_spec):
        assert isinstance(self['inputs'], list)
        assert isinstance(self['chunk_ids'], list)
        assert isinstance(self['split'], list)
        assert all(isinstance(i, str) for i in self['inputs'])
        assert all(isinstance(o, str) for o in self['chunk_ids'])
        assert all(isinstance(i, str) for i in self['split'])
        assert len(set((len(fw_spec[i].value) for i in self['split']))) == 1
        nchunks = len(self['chunk_ids'])

        dcts = [self['spec'].copy() for _ in range(nchunks)]
        for inp in self['split']:
            assert isinstance(fw_spec[inp].value, (pandas.Series, pandas.DataFrame))
            chunks = numpy.array_split(fw_spec[inp].value, nchunks)
            for dct, chunk in zip(dcts, chunks):
                dct[inp] = FWDataObject.from_obj(chunk)
        for inp in self['inputs']:
            if inp not in self['split']:  # not covered
                for dct in dcts:
                    dct[inp] = fw_spec[inp]
        fireworks = []
        for chunk_id, dct in zip(self['chunk_ids'], dcts):
            task = FunctionTask(func=self['func'], inputs=self['inputs'],
                                outputs=[chunk_id])
            fireworks.append(Firework(task, spec=dct, name=chunk_id))
        return FWAction(detours=fireworks)
