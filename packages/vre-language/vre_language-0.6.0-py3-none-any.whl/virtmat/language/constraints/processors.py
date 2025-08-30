"""
Register model processors

Model processors are callables that are called at the end of the parsing when
the whole model is instantiated. These processors accept the model and metamodel
as parameters.

Do not register object processors here
"""
from textx import get_children_of_type, get_parent_of_type, textx_isinstance
from virtmat.language.utilities.errors import VaryError, TagError, InvalidUnitError
from virtmat.language.utilities.errors import raise_exception, UpdateError
from virtmat.language.utilities.logging import get_logger
from virtmat.language.utilities.lists import duplicates
from virtmat.language.utilities.fireworks import get_vary_df
from virtmat.language.utilities.types import is_numeric_type
from .cyclic import check_cycles_processor
from .duplicates import check_duplicates_processor
from .functions import check_functions_processor
from .imports import check_imports_processor
from .units import check_units_processor
from .parallel import check_parallelizable_processor
from .view import check_view_processor
from .amml import check_amml_property_processor
from .chem import check_chem_reaction_processor


def check_types_processor(model, _):
    """evaluate type of all objects that have type"""
    # assume that parents call obj.type_ for their children, see issue #345
    classes = ['Variable', 'Print', 'ObjectImport', 'Tag']
    for cls in classes:
        for obj in get_children_of_type(cls, model):
            _ = obj.type_


def check_series_units_processor(model, metamodel):
    """check that the units of all series elements are the same"""
    for obj in get_children_of_type('Series', model):
        if obj.inp_units is None and is_numeric_type(obj.type_):
            if textx_isinstance(obj.elements[0], metamodel['Quantity']):
                if len(set(e.inp_units for e in obj.elements)) != 1:
                    msg = 'Numeric type series must have elements of the same units.'
                    raise_exception(obj, InvalidUnitError, msg)


def check_vary_processor(model, metamodel):
    """check whether vary statements contain references to series"""
    for gref in get_children_of_type('GeneralReference', model):
        if textx_isinstance(gref.ref, metamodel['Series']):
            if get_parent_of_type('Vary', gref.ref):
                msg = f'reference to series \"{gref.ref.name}\" in vary statement'
                raise VaryError(msg)


def check_tag_processor(model, metamodel):
    """check that table in tag objects contains only one row"""
    for tag in get_children_of_type('Tag', model):
        if textx_isinstance(tag.tagtab.tab, metamodel['Table']):
            if any(len(col.elements) > 1 for col in tag.tagtab.tab.columns):
                raise_exception(tag, TagError, 'tag table must have only one row')


def check_variable_update_processor(model, metamodel):
    """apply constraints to variable update objects"""
    if not textx_isinstance(model, metamodel['Program']):
        return
    mod_vars = get_children_of_type('VariableUpdate', model)
    if not mod_vars:
        return
    model_instance = getattr(model, '_tx_model_params').get('model_instance')
    if model_instance is None:
        msg = 'Variables can be updated in workflow mode only.'
        raise_exception(mod_vars[0], UpdateError, msg)

    def get_refs(obj):
        """return a list of names of all references used in obj"""
        grefs = [r.ref for r in get_children_of_type('GeneralReference', obj)]
        mrefs = set()
        for gref in grefs:
            if textx_isinstance(gref, metamodel['Variable']):
                mrefs.add(gref.name)
            elif (hasattr(gref, 'obj')
                  and textx_isinstance(gref.obj, metamodel['GeneralReference'])):
                mrefs.add(gref.obj.ref.name)
        return mrefs

    dupes = duplicates((m.ref.name for m in mod_vars))
    if dupes:
        msg = f'Multiple updates of variables: {dupes}'
        mod_var = next(m for m in mod_vars if m.ref.name in dupes)
        raise_exception(mod_var, UpdateError, msg)
    for mod_var in mod_vars:
        trefs = get_refs(mod_var.ref)
        mrefs = get_refs(mod_var)
        fmsg = ' references in Variable %s: %s; references in VariableUpdate: %s'
        get_logger(__name__).debug(fmsg, mod_var.ref.name, list(trefs), list(mrefs))
        if mrefs != trefs:
            diff = (mrefs | trefs) - (mrefs & trefs)
            msg = f'Invalid or missing references: {list(diff)}'
            raise_exception(mod_var, UpdateError, msg)

    if model_instance['uuid']:
        vary_df = get_vary_df(model_instance['lpad'], model_instance['uuid'])
        if vary_df is None:
            return
        for mod_var in mod_vars:
            varname = mod_var.ref.name
            if varname in vary_df.columns:
                msg = f'Cannot update \"{varname}\" which is varied in a model group'
                raise_exception(mod_var, UpdateError, msg)


def add_constraints_processors(metamodel):
    """register the constraints processors on the metamodel instance"""
    metamodel.register_model_processor(check_duplicates_processor)
    metamodel.register_model_processor(check_cycles_processor)
    metamodel.register_model_processor(check_imports_processor)
    metamodel.register_model_processor(check_functions_processor)
    metamodel.register_model_processor(check_types_processor)
    metamodel.register_model_processor(check_units_processor)
    metamodel.register_model_processor(check_series_units_processor)
    metamodel.register_model_processor(check_parallelizable_processor)
    metamodel.register_model_processor(check_vary_processor)
    metamodel.register_model_processor(check_tag_processor)
    metamodel.register_model_processor(check_view_processor)
    metamodel.register_model_processor(check_amml_property_processor)
    metamodel.register_model_processor(check_chem_reaction_processor)
