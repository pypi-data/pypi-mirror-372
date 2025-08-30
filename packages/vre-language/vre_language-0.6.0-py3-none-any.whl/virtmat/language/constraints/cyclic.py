"""
check for cyclic dependencies
"""
from textx import get_children_of_type, textx_isinstance
from virtmat.language.utilities.errors import CyclicDependencyError


def detect_cycles(lhs_var, rhs_var, meta):
    """detect cycles by a recursive walk through the dependency tree"""
    # objects that include references to Variable objects:
    obj_refs = {('GeneralReference', 'ref')}
    objs = []
    for obj, attr in obj_refs:
        for var_ref_obj in get_children_of_type(obj, rhs_var.parameter):
            ref = getattr(var_ref_obj, attr)
            if textx_isinstance(ref, meta['Variable']):
                objs.append((var_ref_obj, ref))
    rhs_vars = set()
    for obj, var in objs:
        if var is not lhs_var:
            rhs_vars.add(var)
            rhs_vars.update(detect_cycles(lhs_var, var, meta))
        else:
            raise CyclicDependencyError(lhs_var, obj)
    return rhs_vars


def check_cycles_processor(model, metamodel):
    """model processor to check for cyclic dependencies in the program"""
    for var in get_children_of_type('Variable', model):
        detect_cycles(var, var, metamodel)
