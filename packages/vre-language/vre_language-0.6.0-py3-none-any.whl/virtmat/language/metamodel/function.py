# pylint: disable=protected-access
"""properties and attributes of FunctionCall class"""
from copy import deepcopy
from textx import get_children_of_type, get_children, get_parent_of_type
from textx import get_metamodel
from textx import textx_isinstance

comparisons = ['Equal', 'LessThan', 'GreaterThan', 'LessThanOrEqual',
               'GreaterThanOrEqual']


def complete_expr(self):
    """substitute all references to dummy variables with call parameters"""
    meta = get_metamodel(self)
    vrefs = get_children_of_type('GeneralReference', self.__expr)
    for vref in filter(lambda x: textx_isinstance(x.ref, meta['Dummy']), vrefs):
        for par, arg in zip(self.params, self.function.args):
            if vref.ref.name == arg.name:
                if textx_isinstance(par, meta['GeneralReference']):
                    vref.ref = par.ref
                else:
                    vref.ref = par
                break
    return self.__expr


def add_function_call_properties(metamodel):
    """Add complete_expr() method using monkey style patching"""
    metamodel['FunctionCall'].expr = property(complete_expr)


def function_call_processor(model, metamodel):
    """copy expression tree from the function definition object"""
    if not get_parent_of_type('FunctionDefinition', model):
        for call in get_children_of_type('FunctionCall', model):
            if not call.__expr:
                if textx_isinstance(call.function, metamodel['FunctionDefinition']):
                    call.__expr = deepcopy(call.function.expr)
                    new_objs = get_children(lambda x: True, call.__expr)
                    for new_obj in new_objs:
                        if new_obj is not call.__expr:
                            new_obj.parent = new_obj.parent.last_copy
                    call.__expr.parent = call
                    function_call_processor(call.expr, metamodel)
                else:
                    call.__expr = None


def subst(caller, func, params, types):
    """
    substitute dummy identifiers (bound variables) with their parameters
    caller: the object of which the new returned expression will become a child
    func: object of type FunctionDefinition or Lambda that contain expr
    params: an iterable with the parameters in the order of substitution
    """
    expr = deepcopy(func.expr)
    new_objs = get_children(lambda x: True, expr)
    for new_obj in new_objs:
        if new_obj is not expr:
            new_obj.parent = new_obj.parent.last_copy
    expr.parent = caller
    meta = get_metamodel(caller)
    vrefs = get_children_of_type('GeneralReference', expr)
    for vref in filter(lambda x: textx_isinstance(x.ref, meta['Dummy']), vrefs):
        for par, typ, arg in zip(params, types, func.args):
            if vref.ref.name == arg.name:
                if textx_isinstance(par, meta['GeneralReference']):
                    vref.ref = par.ref
                else:
                    vref.ref = type('', tuple(), {'type_': typ, 'value': par})()
                break
    return expr
