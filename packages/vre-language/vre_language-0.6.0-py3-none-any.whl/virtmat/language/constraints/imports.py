"""
contraints applied to imported objects
"""
from textx import get_children_of_type, get_metamodel, textx_isinstance
from virtmat.language.utilities.errors import ObjectImportError, textxerror_wrap
from virtmat.language.utilities.errors import NonCallableImportError


@textxerror_wrap
def get_object_import(obj):
    """return an imported object"""
    assert hasattr(obj, 'name') and hasattr(obj, 'namespace')
    try:
        module = __import__('.'.join(obj.namespace), fromlist=[obj.name], level=0)
    except ImportError as err:
        raise ObjectImportError(obj) from err
    try:
        retval = getattr(module, obj.name)
    except AttributeError as err:
        raise ObjectImportError(obj) from err
    return retval


def check_imports_processor(model, _):
    """check all imported objects in a program"""
    for obj in get_children_of_type('ObjectImport', model):
        get_object_import(obj)


def check_function_import(obj):
    """check that an imported object is callable"""
    assert textx_isinstance(obj, get_metamodel(obj)['ObjectImport'])
    if not callable(get_object_import(obj)):
        raise NonCallableImportError(obj)
