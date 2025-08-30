"""handling domain-specific errors"""
import sys
import importlib
import traceback
from textx.exceptions import TextXError, TextXSemanticError, TextXSyntaxError
from pint.errors import PintError, DimensionalityError, UndefinedUnitError
from pint.errors import OffsetUnitCalculusError
from ase.calculators.calculator import CalculatorSetupError
from virtmat.middleware.exceptions import ConfigurationException
from virtmat.middleware.exceptions import ResourceConfigurationError
from virtmat.language.utilities.textx import get_location_context
from virtmat.language.utilities.logging import logging, get_logger
from virtmat.language.utilities.jupyter import in_jupyter_notebook

FILE_READ_EXCEPTION_IMPORTS = {'ruamel.yaml.parser': 'ParserError',
                               'ruamel.yaml.scanner': 'ScannerError',
                               'json.decoder': 'JSONDecodeError',
                               'jsonschema.exceptions': 'ValidationError'}
FILE_READ_EXCEPTIONS = [FileNotFoundError, IsADirectoryError, PermissionError, UnicodeDecodeError]
FILE_WRITE_EXCEPTIONS = [FileExistsError, IsADirectoryError, PermissionError, UnicodeEncodeError]
for mod, exc in FILE_READ_EXCEPTION_IMPORTS.items():
    try:
        module = importlib.import_module(mod)
        class_ = getattr(module, exc)
    except ModuleNotFoundError:
        continue
    else:
        FILE_READ_EXCEPTIONS.append(class_)
FILE_READ_EXCEPTIONS = tuple(FILE_READ_EXCEPTIONS)

MONGODB_EXCEPTION_IMPORTS = {'pymongo.errors': 'PyMongoError',
                             'bson.errors': 'InvalidDocument'}
MONGODB_EXCEPTIONS = []
for mod, exc in MONGODB_EXCEPTION_IMPORTS.items():
    try:
        module = importlib.import_module(mod)
        class_ = getattr(module, exc)
    except ModuleNotFoundError:  # not covered
        continue
    else:
        MONGODB_EXCEPTIONS.append(class_)


class CompatibilityError(Exception):
    """raise this exception if grammar, data schema or python versions are incompatible"""


class InvalidUnitError(RuntimeError):
    """raise this exception if an invalid unit is detected"""


class ConvergenceError(RuntimeError):
    """raise this exception if a calculation has not converged"""


class StructureInputError(RuntimeError):
    """raise this exception if any exceptions are raised by ase.io.read"""


class StaticTypeError(Exception):
    """raise this exception if an invalid type is detected"""


class StaticValueError(Exception):
    """raise this exception if an invalid value is detected"""


class RuntimeTypeError(Exception):
    """raise this exception if an invalid type is detected at run time"""


class RuntimeValueError(Exception):
    """raise this exception if an invalid value is detected at run time"""


class PropertyError(Exception):
    """raise this exception if an error with accessing a property occurs"""


class SubscriptingError(Exception):
    """raise this exception if an error with a subscript occurs"""


class EvaluationError(Exception):
    """raised if an exception has been raised during evaluation"""


class AncestorEvaluationError(Exception):
    """raised if an exception has been raised during evaluation of ancestors"""


class NonCompletedException(Exception):
    """this exception should be raised if a variable is not yet evaluated"""


class ModelNotFoundError(Exception):
    """raise this exception if a model cannot be found on persistent storage"""


class VaryError(Exception):
    """raise this exception for any errors related to vary statements"""


class TagError(Exception):
    """raise this exception for any errors related to tag statements"""


class QueryError(Exception):
    """raise this exception for any errors related to query statements"""


class ReuseError(Exception):
    """raise this exception for any errors related to submodel reuse"""


class UpdateError(Exception):
    """raise this exception for errors related to variable update / rerun """


class ConfigurationError(Exception):
    """raise this exception if critical parameters are missing or invalid"""


class InitializationError(TextXError):
    """raise this exception in case of variable initialization errors"""

    def __init__(self, obj):
        err_type = 'Initialization error'
        msg = f'Repeated initialization of "{obj.name}"'
        super().__init__(msg, **get_location_context(obj), err_type=err_type)


class CyclicDependencyError(TextXError):
    """raise this exception if a cyclic dependency is detected"""

    def __init__(self, var, ref):
        err_type = 'Cyclic dependency'
        msg1 = format_textxerr_msg(TextXError('', **get_location_context(var)))
        msg2 = format_textxerr_msg(TextXError('', **get_location_context(ref)))
        msg = f'Cycle detected:\n    Variable: {msg1}\n    Reference: {msg2}'
        super().__init__(msg, **get_location_context(ref), err_type=err_type)


class ObjectImportError(TextXError):
    """raise this exception if an object cannot be imported"""

    def __init__(self, obj):
        err_type = 'Import error'
        obj_namespace = '.'.join(obj.namespace)
        message = f'Object could not be imported: "{obj_namespace}.{obj.name}"'
        super().__init__(message, **get_location_context(obj), err_type=err_type)


class NonCallableImportError(TextXError):
    """raise this exception if an imported object is not callable"""

    def __init__(self, obj):
        err_type = 'Non-callable import'
        obj_namespace = '.'.join(obj.namespace)
        message = f'Imported object is not callable: "{obj_namespace}.{obj.name}"'
        super().__init__(message, **get_location_context(obj), err_type=err_type)


class ExpressionTypeError(TextXError):
    """raise this exception if an invalid type is used in an expression"""

    def __init__(self, obj):
        self.obj = obj
        err_type = 'Expression type error'
        message = 'Invalid type in expression'
        super().__init__(message, **get_location_context(obj), err_type=err_type)


class TypeMismatchError(TextXError):
    """raise this exception if two objects have incompatible types"""

    def __init__(self, obj1, obj2):
        err_type = 'Type mismatch error'
        msg1 = format_textxerr_msg(TextXError('', **get_location_context(obj1)))
        msg2 = format_textxerr_msg(TextXError('', **get_location_context(obj2)))
        message = ('Type mismatch:\n    ' +
                   repr(obj1.type_.__name__).strip(r"'") + ': ' + msg1 + '\n    ' +
                   repr(obj2.type_.__name__).strip(r"'") + ': ' + msg2)
        super().__init__(message, **get_location_context(obj1), err_type=err_type)


class IterablePropertyError(TextXError):
    """raise this exception if an iterable does not have a property"""

    def __init__(self, obj, obj_type, prop):
        err_type = 'Iterable property error'
        message = f'Parameter of type {obj_type} has no property "{prop}"'
        super().__init__(message, **get_location_context(obj), err_type=err_type)


class ParallelizationError(TextXError):
    """raise this error if error occurs in parallel map, reduce and filter"""

    def __init__(self, obj, msg):
        err_type = 'Parallelization error'
        super().__init__(msg, **get_location_context(obj), err_type=err_type)


class ObjectFromFileError(Exception):
    """to be raised if the causing exception is in FILE_READ_EXCEPTIONS"""

    def __init__(self, msg, path):
        self.path = path
        super().__init__(msg)

    def __str__(self):
        cause_cls = self.__cause__.__class__.__qualname__
        cause_mod = self.__cause__.__class__.__module__
        return f'{cause_mod}.{cause_cls}: {self.path}\n{self.__cause__}'

    def __reduce__(self):
        return (self.__class__, (*self.args, self.path), {'__cause__': self.__cause__})


def print_stderr(*args, **kwargs):
    """print to stderr"""
    print(*args, file=sys.stderr, **kwargs)


def textxerror_wrap(func):
    """
    This is a decorator similar to the 'textxerror_wrap' from textX but it also
    sets the error context and accepts arbitrary list of arguments. The first
    positional argument must be a textX model object.
    """
    def wrapper(*args, **kwargs):
        obj = args[0]
        try:
            return func(*args, **kwargs)
        except Exception as err:
            if isinstance(err, TextXError):
                raise
            raise TextXError(str(err), **get_location_context(obj)) from err
    return wrapper


def format_textxerr_msg(err):
    """format a TextXError message"""
    msg = str(err.filename) + ':' + str(err.line) + ':' + str(err.col)
    if err.context:
        msg += ' --> ' + err.context + ' <--'
    if err.message:
        msg += '\n' + err.message
    return msg


@textxerror_wrap
def raise_exception(_, exception, msg, where_used=None):
    """utility function to raise an exception at a custom location"""
    if where_used is not None:
        err = TextXError('', **get_location_context(where_used))
        msg += f'\n    used here: {format_textxerr_msg(err)}'
    raise exception(msg)


TEXTX_WRAPPED_EXCEPTIONS = (DimensionalityError, UndefinedUnitError, PintError,
                            InvalidUnitError, CalculatorSetupError, StructureInputError,
                            StaticTypeError, RuntimeTypeError, StaticValueError,
                            RuntimeValueError, PropertyError, SubscriptingError,
                            EvaluationError, AncestorEvaluationError, ObjectFromFileError,
                            ArithmeticError, FileExistsError, OSError)


def process_error(err):
    """generic error processor for errors of class TextXError"""
    c_mapping = (('Dimensionality error', DimensionalityError),
                 ('Undefined unit', UndefinedUnitError),
                 ('Offset unit calculus error', OffsetUnitCalculusError),
                 ('Units error', PintError),
                 ('Invalid units error', InvalidUnitError),
                 ('Calculator setup error', CalculatorSetupError),
                 ('Structure input error', StructureInputError),
                 ('Type error', (StaticTypeError, RuntimeTypeError)),
                 ('Value error', (StaticValueError, RuntimeValueError)),
                 ('Invalid key', PropertyError),
                 ('Invalid index', SubscriptingError),
                 ('Convergence error', ConvergenceError),
                 ('Evaluation error', EvaluationError),
                 ('Ancestor evaluation error', AncestorEvaluationError),
                 ('Variable update error', UpdateError),
                 ('Tag error', TagError),
                 ('Resource configuration error', ResourceConfigurationError),
                 ('Data input error', ObjectFromFileError),
                 ('Arithmetic error', ArithmeticError),
                 ('Not implemented', NotImplementedError),
                 ('File exists error', FileExistsError),
                 ('Operating system error', OSError),
                 ('Unknown error', Exception))
    if err.err_type is None:
        if isinstance(err, TextXSyntaxError):
            err_type = 'Syntax error'
        elif isinstance(err, TextXSemanticError):  # not covered
            err_type = 'Semantic error'
        else:
            for msg, cls in c_mapping:
                if isinstance(err.__cause__, cls):
                    err_type = msg
                    break
    else:
        err_type = err.err_type

    if not in_jupyter_notebook():
        if get_logger(__name__).getEffectiveLevel() == logging.DEBUG:
            traceback.print_exception(*sys.exc_info(), file=sys.stderr)
        print_stderr(err_type + ': ' + format_textxerr_msg(err))
    else:
        err.err_type = err_type
        # raise it to be handled by Jupyter frontend
        raise err


def error_handler(func):
    """error handler decorator function"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TextXError as err:
            process_error(err)
            return None
        except ObjectFromFileError as err:
            print_stderr(f'Data input error: {err}')
            return None
        except CompatibilityError as err:
            print_stderr(f'Compatibility error: {err}')
            return None
        except VaryError as err:  # not covered
            print_stderr(f'Vary error: {err}')
            return None
        except QueryError as err:
            print_stderr(f'Query error: {err}')
            return None
        except ReuseError as err:  # not covered
            print_stderr(f'Reuse error: {err}')
            return None
        except ModelNotFoundError as err:
            print_stderr(f'Model not found: {err}')
            return None
        except (ConfigurationError, ConfigurationException) as err:
            print_stderr(f'Configuration error: {err}')
            return None
        except UpdateError as err:
            print_stderr(f'Variable update error: {err}')
            return None
        except tuple([*MONGODB_EXCEPTIONS, *FILE_READ_EXCEPTIONS]) as err:
            err_cls = err.__class__
            print_stderr(f'{err_cls.__module__}.{err_cls.__qualname__}: {err}')
            return None
        except Exception as err:  # not covered
            raise RuntimeError('non-handled exception') from err
    return wrapper
