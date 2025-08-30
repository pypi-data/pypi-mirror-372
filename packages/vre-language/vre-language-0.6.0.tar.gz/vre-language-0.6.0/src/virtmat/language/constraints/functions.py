"""
constraints applied to callable objects
"""
from textx import get_children_of_type, textx_isinstance
from virtmat.language.utilities.errors import raise_exception, StaticValueError
from .imports import check_function_import


def check_function_definition(obj, metamodel):
    """check the arguments matching in FunctionDefinition or Lambda"""
    if textx_isinstance(obj, metamodel['FunctionDefinition']):
        fname = f'function {obj.name}'
    else:
        assert textx_isinstance(obj, metamodel['Lambda'])
        fname = 'lambda function'
    if len(obj.args) == 0:
        msg = 'Function definition must have at least one argument'
        raise_exception(obj, StaticValueError, msg)
    vrefs = get_children_of_type('GeneralReference', obj.expr)
    refs = [r.ref for r in vrefs if textx_isinstance(r.ref, metamodel['Dummy'])]
    refs_uniq_names = set(ref.name for ref in refs if ref in obj.args)
    args_names = [a.name for a in obj.args]
    args_uniq_names = set(args_names)
    if len(args_names) != len(args_uniq_names):
        args_names = [a.name for a in obj.args]
        args_uniq_names = set(args_names)
        dups = ', '.join(a for a in args_uniq_names if args_names.count(a) > 1)
        message = f'Duplicate argument(s) in {fname}: {dups}'
        raise_exception(obj, StaticValueError, message)
    calls = get_children_of_type('FunctionCall', obj.expr)
    call_dummies = set()
    for call in calls:
        if not textx_isinstance(call.function, metamodel['ObjectImport']):
            for arg in call.function.args:
                call_dummies.add(arg.name)
    # assert not any(d in args_uniq_names for d in call_dummies)  # the bug has been fixed
    args_uniq_names.update(call_dummies)
    refs_uniq_names.update(call_dummies)
    if list(sorted(refs_uniq_names)) != list(sorted(args_uniq_names)):
        message = (f'Dummy variables {list(sorted(refs_uniq_names))} '
                   f'do not match arguments {list(sorted(args_uniq_names))} '
                   f'in {fname}')
        raise_exception(obj, StaticValueError, message)


def check_function_call(obj, metamodel):
    """check a function call object"""
    if textx_isinstance(obj.function, metamodel['ObjectImport']):
        check_function_import(obj.function)  # has a valid imported function
    else:
        assert textx_isinstance(obj.function, metamodel['FunctionDefinition'])
        if len(obj.params) != len(obj.function.args):
            message = (f'Function "{obj.function.name}" takes {len(obj.function.args)} '
                       f'parameters but {len(obj.params)} were given')
            raise_exception(obj, StaticValueError, message)


def check_functions_processor(model, metamodel):
    """processor to check function definitions and function calls"""
    for cls in ('FunctionDefinition', 'Lambda'):
        for func in get_children_of_type(cls, model):
            check_function_definition(func, metamodel)
    for call in get_children_of_type('FunctionCall', model):
        check_function_call(call, metamodel)
