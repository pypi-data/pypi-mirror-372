"""serialization/deserialization code"""
import os
import pathlib
import typing
import uuid
import json
import zlib
import urllib
from dataclasses import dataclass
from json import JSONEncoder
from itertools import islice
from functools import cached_property
import numpy
import pandas
import pint_pandas
import yaml
from fireworks import fw_config
from fireworks.utilities.fw_serializers import FWSerializable
from fireworks.utilities.fw_serializers import serialize_fw
from fireworks.utilities.fw_serializers import recursive_serialize
from fireworks.utilities.fw_serializers import recursive_deserialize
from fireworks.utilities.fw_serializers import recursive_dict, load_object
from fireworks.utilities.fw_utilities import get_fw_logger
from fireworks_schema import validate, fw_schema_serialize, fw_schema_deserialize
from virtmat.language.schema.register import register_schemas
from virtmat.language.utilities import ioops, logging, amml, chemistry
from .errors import RuntimeTypeError, FILE_READ_EXCEPTIONS, ObjectFromFileError
from .units import ureg
from .lists import list_flatten

pint_pandas.pint_array.DEFAULT_SUBDTYPE = None
DATA_SCHEMA_VERSION = 7
register_schemas()


def data_schema_validate_debug():
    """return true if current logging level is debug"""
    return logging.LOGGING_LEVEL == logging.get_logging_level('DEBUG')


def versioned_deserialize(func):
    """func must be a *from_dict* method"""
    def decorator(cls, dct):
        assert isinstance(cls, type) and issubclass(cls, FWSerializable)
        assert dct.pop('_fw_name') == getattr(cls, '_fw_name')
        assert isinstance(dct, dict)
        version = dct.pop('_version', None)
        if version == DATA_SCHEMA_VERSION:
            return func(cls, dct)  # current version
        if version is None:  # non-tagged is implicitly version 6, to be deprecated
            return func(cls, dct)
        return getattr(cls, f'from_dict_{version}')(cls, dct)  # not covered
    return decorator


def versioned_serialize(func):
    """func must be a *to_dict* method"""
    def decorator(*args, **kwargs):
        dct = func(*args, **kwargs)
        dct['_version'] = DATA_SCHEMA_VERSION
        return dct
    return decorator


def get_json_size(obj, max_size):
    """compute JSON size in bytes of a JSON serializable object up to max_size"""
    gen = JSONEncoder().iterencode(obj)
    chunk_size = 1024
    json_size = 0
    next_chunk = len(''.join(islice(gen, chunk_size)).encode())
    while next_chunk and json_size < max_size:
        json_size += next_chunk
        next_chunk = len(''.join(islice(gen, chunk_size)).encode())
    return json_size


@dataclass
class FWDataObject(FWSerializable):
    """top-level FWSerializable dataclass to hold any FWSerializable objects"""
    __value: typing.Any = None
    datastore: dict = None
    filename: str = None
    url: str = None
    serialized: bool = None
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    @fw_schema_serialize(debug=data_schema_validate_debug())
    @serialize_fw
    @versioned_serialize
    def to_dict(self):
        f_name = f'{__name__}.{self.__class__.__name__}.to_dict()'
        logger = get_fw_logger(f_name)
        logger.debug('%s: starting', f_name)
        if self.datastore is None:
            logger.debug('%s: data type: %s', f_name, type(self.value))
            if ioops.DATASTORE_CONFIG['type'] is not None:
                b_thres = ioops.DATASTORE_CONFIG['inline-threshold']
                b_size = get_json_size(self.serialized_value, b_thres)
                logger.debug('%s: data size [B]: %s', f_name, b_size)
                logger.debug('%s: inline-threshold [B]: %s', f_name, b_thres)
                if b_size > b_thres:
                    logger.info('%s: inline data limit exceeded: %s', f_name, b_size)
                    self.datastore, self.filename = self.offload_data()
                    logger.info('%s: data offloaded in %s', f_name, self.filename)
                    return {'datastore': self.datastore, 'filename': self.filename}
            self.datastore = {'type': None}
            logger.info('%s: data not offloaded', f_name)
            return {'value': self.serialized_value, 'datastore': self.datastore}
        logger.debug('%s: datastore: %s', f_name, self.datastore)
        if self.datastore['type'] is None:
            return {'value': self.serialized_value, 'datastore': self.datastore}
        logger.debug('%s: data in file: %s', f_name, self.filename)
        return {'datastore': self.datastore, 'filename': self.filename}

    @classmethod
    @fw_schema_deserialize(debug=data_schema_validate_debug())
    @versioned_deserialize
    def from_dict(cls, m_dict):
        assert 'datastore' in m_dict and m_dict['datastore'] is not None
        if m_dict['datastore']['type'] is None:
            return cls(m_dict['value'], m_dict['datastore'], serialized=True)
        assert 'value' not in m_dict
        return cls(serialized=True, **m_dict)

    @cached_property
    def value(self):
        """return the FW serializable value"""

        def restore_value(val):
            @recursive_deserialize
            def restore_from_dict(_, dct):
                return dct
            return restore_from_dict(None, {'v': val})['v']

        if self.datastore is None:
            assert not self.serialized
            return self.__value
        return restore_value(self.serialized_value)

    @cached_property
    def serialized_value(self):
        """return the JSON serializable value, retrieve from datastore if needed"""
        if self.datastore is None or self.datastore['type'] is None:
            if self.serialized:
                return self.__value
            return recursive_dict(self.__value)
        if self.datastore['type'] in ('file', 'gridfs'):
            assert self.filename is not None
        else:
            assert self.datastore['type'] == 'url'
            assert self.url is not None
        assert self.__value is None
        self.__value = lade_data(self.datastore, self.filename, self.url)
        self.serialized = True
        return self.__value

    @classmethod
    def from_obj(cls, obj):
        """create an instance from a serializable object of any type"""
        return cls(get_serializable(obj), serialized=False)

    def offload_data(self, datastore=None, filename=None, url=None):
        """offload FW/JSON serializable data to a datastore"""
        datastore = datastore or ioops.DATASTORE_CONFIG
        assert datastore['type'] is not None
        if datastore['type'] in ('file', 'gridfs'):
            if 'format' not in datastore:
                assert filename
                datastore['format'] = get_datastore_format_from_filename(filename)
            if 'compress' not in datastore:
                assert filename
                datastore['compress'] = get_datastore_compress_from_filename(filename)
            if filename is None and datastore['format'] in ['json', 'yaml']:
                filename = f"{uuid.uuid4().hex}.{datastore['format']}"
                if datastore['compress']:
                    filename += '.zz'
        else:
            assert datastore['type'] == 'url'
            path = urllib.parse.urlparse(url).path
            if 'format' not in datastore:
                datastore['format'] = get_datastore_format_from_filename(path)
            if 'compress' not in datastore:
                datastore['compress'] = get_datastore_compress_from_filename(path)
        if datastore['format'] in ('json', 'yaml'):
            dump_func = yaml.safe_dump if datastore['format'] == 'yaml' else json.dump
            dumps_func = yaml.safe_dump if datastore['format'] == 'yaml' else json.dumps
            data = self.serialized_value
            _validate_value(data)
        elif datastore['format'] == 'custom':
            data = self.value
        else:
            assert datastore['format'] == 'hdf5'
            raise NotImplementedError('datastore format hdf5 not implemented')
        if datastore['type'] == 'file':
            if not os.path.isabs(filename):
                path = os.path.join(datastore.get('path', './'), filename)
            else:
                path = filename
            if datastore['format'] in ('json', 'yaml'):
                if datastore['compress']:
                    with open(path, 'xb') as out:
                        out.write(zlib.compress(dumps_func(data).encode()))
                else:
                    with open(path, 'x', encoding='utf-8') as out:
                        dump_func(data, out)
            elif datastore['format'] == 'custom':
                if not hasattr(data, 'to_own_file'):
                    raise RuntimeTypeError(f'unsupported data type {type(data)}')
                data.to_own_file(path)
        elif datastore['type'] == 'gridfs':
            assert datastore['format'] in ['json', 'yaml']
            bytes_ = dumps_func(data).encode()
            bytes_ = zlib.compress(bytes_) if datastore['compress'] else bytes_
            ioops.GRIDFS_DATASTORE.get(datastore).put(bytes_, filename=filename)
        elif datastore['type'] == 'url':
            raise NotImplementedError('datastore type url not implemented')
        return datastore, filename


def get_datastore_format_from_filename(filename):
    """return data format from filename suffix"""
    suffs = pathlib.Path(filename).suffixes
    if any(s in suffs for s in ('.yml', '.yaml')):
        return 'yaml'
    if '.json' in suffs:
        return 'json'
    if any(s in suffs for s in ('.hdf', '.h4', '.hdf4', '.he2', '.h5', '.hdf5', '.he5')):
        return 'hdf5'
    return 'custom'


def get_datastore_compress_from_filename(filename):
    """return compression from filename suffix"""
    return '.zz' in pathlib.Path(filename).suffixes


def _validate_value(value):
    """validate JSON serializable value against a JSON schema"""
    if fw_config.JSON_SCHEMA_VALIDATE:
        validate(value, 'FWDataObjectValue', debug=data_schema_validate_debug())


def lade_data(datastore, filename=None, url=None):
    """retrieve JSON serializable data from a datastore"""
    assert datastore['type'] is not None
    if datastore['type'] in ('file', 'gridfs'):
        assert filename is not None
        if 'format' not in datastore:
            datastore['format'] = get_datastore_format_from_filename(filename)
        if 'compress' not in datastore:
            datastore['compress'] = get_datastore_compress_from_filename(filename)
    else:
        assert datastore['type'] == 'url'
        path = urllib.parse.urlparse(url).path
        if 'format' not in datastore:
            datastore['format'] = get_datastore_format_from_filename(path)
        if 'compress' not in datastore:
            datastore['compress'] = get_datastore_compress_from_filename(path)
    if datastore['format'] in ('json', 'yaml'):
        load_func = yaml.safe_load if datastore['format'] == 'yaml' else json.load
        loads_func = yaml.safe_load if datastore['format'] == 'yaml' else json.loads
    else:
        assert datastore['format'] in ('custom', 'hdf5')
        msg = f"datastore with {datastore['format']} format not implemented"
        raise NotImplementedError(msg)
    if datastore['type'] == 'file':
        if not os.path.isabs(filename):
            path = os.path.join(datastore.get('path', './'), filename)
        else:
            path = filename
        if datastore['compress']:
            with open(path, 'rb') as inp:
                val = loads_func(zlib.decompress(inp.read()).decode())
        else:
            with open(path, 'r', encoding='utf-8') as inp:
                val = load_func(inp)
    elif datastore['type'] == 'gridfs':
        with ioops.GRIDFS_DATASTORE.get(datastore).find_one({'filename': filename}) as inp:
            if datastore['compress']:
                val = loads_func(zlib.decompress(inp.read()).decode())
            else:
                val = load_func(inp)
    else:
        assert datastore['type'] == 'url'
        with urllib.request.urlopen(url) as inp:
            val = load_func(inp)  # not covered
    _validate_value(val)
    return val


def load_value(url=None, filename=None):
    """load data from file or from URL and deserialize to FW serializable"""
    assert url or filename, 'either filename or url must be specified'
    datastore = {'type': 'file'} if filename else {'type': 'url'}
    dct = {'datastore': datastore, 'filename': filename, 'url': url}
    try:
        return FWDataObject(**dct).value
    except tuple(FILE_READ_EXCEPTIONS) as err:  # tuple() to avoid E0712
        raise ObjectFromFileError(err, filename or url) from err


class FWDataFrame(pandas.DataFrame, FWSerializable):
    """serializable pandas.DataFrame"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    def __init__(self, *args, **kwargs):
        pandas.DataFrame.__init__(self, *args, **kwargs)

    @serialize_fw
    @recursive_serialize
    @versioned_serialize
    def to_dict(self):  # pylint: disable=arguments-differ
        return {'data': [get_serializable(self[c]) for c in self.columns]}

    @classmethod
    @recursive_deserialize
    @versioned_deserialize
    def from_dict(cls, m_dict):  # pylint: disable=arguments-differ
        if len(m_dict['data']) == 0:
            return cls()
        return cls(pandas.concat(m_dict['data'], axis=1))

    def to_base(self):
        """return an instance of the base class"""
        return pandas.DataFrame(self)


class FWSeries(pandas.Series, FWSerializable):
    """serializable pandas.Series"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            if len(args[0]) == 0:
                kwargs['dtype'] = 'object'
        elif len(kwargs['data']) == 0:
            kwargs['dtype'] = 'object'
        pandas.Series.__init__(self, *args, **kwargs)

    @serialize_fw
    @recursive_serialize
    @versioned_serialize
    def to_dict(self):  # pylint: disable=arguments-differ
        if not isinstance(self.dtype, pint_pandas.PintType):
            return {'name': self.name, 'data': get_serializable(self.tolist()),
                    'datatype': str(self.dtype)}
        units = [str(x.to_reduced_units().units) for x in self]
        unit = max(((u, units.count(u)) for u in set(units)), key=lambda c: c[1])[0]
        data = [get_serializable(x.to(unit).magnitude) for x in self]
        datatypes = [type(e).__name__ for e in data if e is not None]
        datatype = next(iter(datatypes)) if datatypes else None
        datatype = 'complex' if datatype == 'tuple' else datatype
        return {'name': self.name, 'data': data, 'units': unit, 'datatype': datatype}

    @classmethod
    @recursive_deserialize
    @versioned_deserialize
    def from_dict(cls, m_dict):
        datatype = m_dict['datatype']
        if datatype in ('int', 'float'):
            dtype = pint_pandas.PintType(m_dict.get('units', 'dimensionless'))
            return cls(data=m_dict['data'], name=m_dict['name'], dtype=dtype)
        if datatype == 'complex':
            data = [complex(*e) for e in m_dict['data']]
            dtype = pint_pandas.PintType(m_dict.get('units', 'dimensionless'))
            return cls(data=data, name=m_dict['name'], dtype=dtype)
        return cls(data=m_dict['data'], name=m_dict['name'])


class FWQuantity(FWSerializable, ureg.Quantity):
    """FW serializable pint.Quantity"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    @serialize_fw
    @recursive_serialize
    @versioned_serialize
    def to_dict(self):
        mag, units = self.to_tuple()
        return {'data': (get_serializable(mag), units)}

    @classmethod
    @recursive_deserialize
    @versioned_deserialize
    def from_dict(cls, m_dict):
        assert isinstance(m_dict['data'], (list, tuple))
        mag, units = m_dict['data']
        for unit in units:  # https://github.com/hgrecco/pint/issues/2199
            ureg.get_name(unit[0])
        if isinstance(mag, (int, float)):
            return super().from_tuple(m_dict['data'])
        if mag is None:
            return super().from_tuple((pandas.NA, units))
        assert isinstance(mag, (list, tuple))
        return super().from_tuple((complex(*mag), units))

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        return cls.from_tuple(obj.to_tuple())


class FWBoolArray(numpy.ndarray, FWSerializable):
    """FW serializable bool numpy.ndarray"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    def __new__(cls, data):
        return numpy.asarray(data).view(cls)

    @serialize_fw
    @recursive_serialize
    @versioned_serialize
    def to_dict(self):
        return {'data': self.tolist()}

    @classmethod
    @recursive_deserialize
    @versioned_deserialize
    def from_dict(cls, m_dict):
        assert isinstance(m_dict['data'], list)
        assert all(isinstance(e, bool) for e in list_flatten(m_dict['data']))
        return cls(m_dict['data'])


class FWStrArray(numpy.ndarray, FWSerializable):
    """FW serializable str numpy.ndarray"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    def __new__(cls, data):
        return numpy.asarray(data).view(cls)

    @serialize_fw
    @recursive_serialize
    @versioned_serialize
    def to_dict(self):
        return {'data': self.tolist()}

    @classmethod
    @recursive_deserialize
    @versioned_deserialize
    def from_dict(cls, m_dict):
        assert isinstance(m_dict['data'], list)
        assert all(isinstance(e, str) for e in list_flatten(m_dict['data']))
        return cls(m_dict['data'])


class FWNumArray(FWSerializable, ureg.Quantity):
    """FW serializable numeric array"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    @serialize_fw
    @recursive_serialize
    @versioned_serialize
    def to_dict(self):
        tpl = self.to_tuple()
        return {'data': (tpl[0].tolist(), tpl[1]),
                'dtype': self.magnitude.dtype.name}

    @classmethod
    @recursive_deserialize
    @versioned_deserialize
    def from_dict(cls, m_dict):
        array = numpy.array(m_dict['data'][0], dtype=m_dict['dtype'])
        units = m_dict['data'][1]
        for unit in units:  # https://github.com/hgrecco/pint/issues/2199
            ureg.get_name(unit[0])
        return super().from_tuple((array, units))

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        return cls.from_tuple(obj.to_tuple())


class FWAMMLStructure(amml.AMMLStructure, FWSerializable):
    """FW serializable amml.AMMLStructure"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    @serialize_fw
    @recursive_serialize
    @versioned_serialize
    def to_dict(self):
        return {'data': get_serializable(self.tab), 'name': self.name}

    @classmethod
    @recursive_deserialize
    @versioned_deserialize
    def from_dict(cls, m_dict):
        return cls(m_dict['data'], m_dict['name'])

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        return cls(obj.tab, obj.name)


class FWCalculator(amml.Calculator, FWSerializable):
    """FW serializable amml.Calculator"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    _keys = ['name', 'parameters', 'pinning', 'version', 'task']

    @serialize_fw
    @recursive_serialize
    @versioned_serialize
    def to_dict(self):
        return {k: get_serializable(getattr(self, k)) for k in self._keys}

    @classmethod
    @recursive_deserialize
    @versioned_deserialize
    def from_dict(cls, m_dict):
        return cls(**m_dict)

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        return cls(**{k: getattr(obj, k) for k in cls._keys})


class FWAlgorithm(amml.Algorithm, FWSerializable):
    """FW serializable amml.Calculator"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    _keys = ['name', 'parameters', 'many_to_one']

    @serialize_fw
    @recursive_serialize
    @versioned_serialize
    def to_dict(self):
        return {k: get_serializable(getattr(self, k)) for k in self._keys}

    @classmethod
    @recursive_deserialize
    @versioned_deserialize
    def from_dict(cls, m_dict):
        return cls(**m_dict)

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        return cls(**{k: getattr(obj, k) for k in cls._keys})


class FWProperty(amml.Property, FWSerializable):
    """FW serializable amml.Property"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    _keys = ('names', 'structure', 'calculator', 'algorithm', 'constraints', 'results')

    @serialize_fw
    @recursive_serialize
    @versioned_serialize
    def to_dict(self):
        return {k: get_serializable(getattr(self, k)) for k in self._keys}

    @classmethod
    @recursive_deserialize
    @versioned_deserialize
    def from_dict(cls, m_dict):
        return cls(**m_dict)

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        kwargs = {k: getattr(obj, k) for k in cls._keys}
        return cls(**kwargs)


class FWConstraint(amml.Constraint, FWSerializable):
    """FW serializable amml.Constraint"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    @serialize_fw
    @recursive_serialize
    @versioned_serialize
    def to_dict(self):
        ser_kwargs = {k: get_serializable(v) for k, v in self.kwargs.items()}
        return {'name': self.name, **ser_kwargs}

    @classmethod
    @recursive_deserialize
    @versioned_deserialize
    def from_dict(cls, m_dict):
        return cls(**m_dict)

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        return cls(obj.name, **obj.kwargs)


class FWTrajectory(amml.Trajectory, FWSerializable):
    """FW serializable amml.Trajectory"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    _keys = ('description', 'structure', 'properties', 'constraints', 'filename')

    @serialize_fw
    @recursive_serialize
    @versioned_serialize
    def to_dict(self):
        return {k: get_serializable(getattr(self, k)) for k in self._keys}

    @classmethod
    @recursive_deserialize
    @versioned_deserialize
    def from_dict(cls, m_dict):
        return cls(**m_dict)

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        kwargs = {k: getattr(obj, k) for k in cls._keys}
        return cls(**kwargs)


class FWChemSpecies(chemistry.ChemSpecies, FWSerializable):
    """FW serializable chemistry.ChemSpecies"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    _keys = ['name', 'composition', 'props']

    @serialize_fw
    @recursive_serialize
    @versioned_serialize
    def to_dict(self):
        return {k: get_serializable(getattr(self, k)) for k in self._keys}

    @classmethod
    @recursive_deserialize
    @versioned_deserialize
    def from_dict(cls, m_dict):
        return cls(**m_dict)

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        kwargs = {k: getattr(obj, k) for k in cls._keys}
        return cls(**kwargs)


class FWChemReaction(chemistry.ChemReaction, FWSerializable):
    """FW serializable chemistry.ChemReaction"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    _keys = ['terms', 'props']

    @serialize_fw
    @recursive_serialize
    @versioned_serialize
    def to_dict(self):
        return {k: get_serializable(getattr(self, k)) for k in self._keys}

    @classmethod
    @recursive_deserialize
    @versioned_deserialize
    def from_dict(cls, m_dict):
        return cls(**m_dict)

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        return cls(obj.terms, obj.props)


def get_serializable(obj):
    """convert a Python object to a FW serializable object"""
    if not isinstance(obj, FWSerializable):
        if isinstance(obj, numpy.generic):
            retval = get_serializable(getattr(obj, 'item', lambda: obj)())
        elif isinstance(obj, (bool, int, float, str, type(None))):
            retval = obj
        elif isinstance(obj, (list, tuple)):
            retval = [get_serializable(o) for o in obj]
        elif isinstance(obj, dict):
            retval = {k: get_serializable(v) for k, v in obj.items()}
        elif obj is pandas.NA or obj is numpy.nan:
            retval = None
        elif isinstance(obj, complex):
            retval = (obj.real, obj.imag)
        elif isinstance(obj, ureg.Quantity):
            if isinstance(obj.magnitude, numpy.ndarray):
                retval = FWNumArray.from_base(obj)
            else:
                retval = FWQuantity.from_base(obj)
        elif isinstance(obj, pandas.DataFrame):
            retval = FWDataFrame(obj)
        elif isinstance(obj, pandas.Series):
            retval = FWSeries(obj)
        elif isinstance(obj, numpy.ndarray):
            if obj.dtype.type is numpy.bool_:
                retval = FWBoolArray(obj)
            else:
                assert obj.dtype.type is numpy.str_
                retval = FWStrArray(obj)
        elif isinstance(obj, amml.AMMLStructure):
            retval = FWAMMLStructure.from_base(obj)
        elif isinstance(obj, amml.Calculator):
            retval = FWCalculator.from_base(obj)
        elif isinstance(obj, amml.Algorithm):
            retval = FWAlgorithm.from_base(obj)
        elif isinstance(obj, amml.Property):
            retval = FWProperty.from_base(obj)
        elif isinstance(obj, amml.Constraint):
            retval = FWConstraint.from_base(obj)
        elif isinstance(obj, amml.Trajectory):
            retval = FWTrajectory.from_base(obj)
        elif isinstance(obj, chemistry.ChemSpecies):
            retval = FWChemSpecies.from_base(obj)
        elif isinstance(obj, chemistry.ChemReaction):
            retval = FWChemReaction.from_base(obj)
        else:
            raise TypeError(f'cannot serialize {obj} of type {type(obj)}')
    elif isinstance(obj, FWNumArray) and not isinstance(obj.magnitude, numpy.ndarray):
        retval = FWQuantity.from_base(obj)
    else:
        retval = obj
    return retval


def tag_serialize(tagtab):
    """allowed types: DataFrame, tuple / list, Quantity, bool, str"""
    assert isinstance(tagtab, pandas.DataFrame)

    def _recursive_serialize(obj):
        if isinstance(obj, pandas.DataFrame):
            out = {}
            for key, val in obj.to_dict(orient='list').items():
                assert isinstance(val, list)
                assert len(val) == 1
                out[key] = _recursive_serialize(val[0])
            return out
        if isinstance(obj, ureg.Quantity):
            return get_serializable(obj).to_dict()
        if isinstance(obj, (bool, str)) or obj is None:
            return obj
        if isinstance(obj, (tuple, list)):
            return [_recursive_serialize(e) for e in obj]
        raise RuntimeTypeError(f'unsupported type for query/tag: {type(obj)}')
    return _recursive_serialize(tagtab)


def tag_deserialize(tagdct):
    """deserialize a tag dict to a DataFrame object"""
    assert isinstance(tagdct, dict)

    def _recursive_deserialize(obj):
        if isinstance(obj, dict):
            if '_fw_name' in obj:
                return load_object(obj)
            dct = {k: [_recursive_deserialize(v)] for k, v in obj.items()}
            return pandas.DataFrame.from_dict(dct)
        if isinstance(obj, (bool, str)) or obj is None:
            return obj
        assert isinstance(obj, (tuple, list))
        return [_recursive_deserialize(e) for e in obj]
    return _recursive_deserialize(tagdct)
