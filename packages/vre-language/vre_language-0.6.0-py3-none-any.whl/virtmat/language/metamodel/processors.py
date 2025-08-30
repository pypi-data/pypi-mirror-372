"""
Register object and model processors

Model processors are callables that are called at the end of the parsing when
the whole model is instantiated. These processors accept the model and metamodel
as parameters.

Object processors are registered for particular classes (grammar rules) and are
called when objects of the given class are instantiated. Object processors
are registered by defining a map between a rule name and the callable that will
process the instances of the metamodel class correspoding to the rule. The rule
must be a match rule and no abstract rule.

Register object processors *only here*
"""
from virtmat.language.constraints.processors import add_constraints_processors
from virtmat.language.constraints.processors import check_variable_update_processor
from virtmat.language.interpreter.workflow_executor import workflow_model_processor
from virtmat.language.utilities.textx import isinstance_m
from virtmat.language.utilities.errors import raise_exception, StaticTypeError
from virtmat.language.utilities.warnings import warnings, TextSUserWarning
from .function import function_call_processor
from .workflow import source_code_statement_processor, qadapter_processor
from .workflow import default_worker_name_processor, resources_processor
from .workflow import parallelizable_processor, variable_update_processor
from .amml import amml_calculator_processor, amml_algorithm_processor
from .amml import amml_property_processor, chem_term_processor
from .io import output_processor


def object_import_processor(obj):
    """add namespace of parent ObjectImports to ObjectImport"""
    obj.namespace = obj.parent.namespace


def table_processor(obj):
    """fill in the list of table columns"""
    if obj.columns_tuple:
        assert len(obj.columns) == 0
        obj.columns = obj.columns_tuple.params


def null_processor(obj):
    """set the attributes of Null objects"""
    obj.func = (lambda: None, tuple())
    obj.value = None
    obj.type_ = None


def number_processor(obj):
    """set the attributes of Number objects"""
    if obj.imag_ is None:
        obj.value = obj.real
        obj.type_ = type(obj.real)
    else:
        imag = - obj.imag_ if obj.sign == '-' else obj.imag_
        real = type(imag)(0) if obj.real is None else obj.real
        obj.value = complex(real, imag)
        obj.type_ = complex


def general_reference_processor(obj):
    """check the metamodel type of the ref attribute (matched any object in RREL)"""
    classes = ['Variable', 'Dummy', 'ObjectImport', 'Series']
    if not isinstance_m(obj.ref, classes):
        msg = f'invalid use of reference to {obj.ref.__class__.__name__}'
        raise_exception(obj, StaticTypeError, msg)


def condition_comparison_processor(obj):
    """normalize: column is on the left, operand is on the right"""
    inv_map = {'==': '==', '!=': '!=', '>': '<', '<': '>', '>=': '<=', '<=': '>='}
    if obj.operand_left is not None:
        obj.operand_right = obj.operand_left
        obj.operand_left = None
        obj.column_left = obj.column_right
        obj.column_right = None
        obj.operator = inv_map[obj.operator]


def print_parameter_processor(obj):
    """process print parameter objects"""
    if not hasattr(obj, 'inp_units'):  # compatibility to grammar version < 28
        setattr(obj, 'inp_units', getattr(obj, 'units', None))


def tag_processor(obj):
    """warn if tag is found in instant or in deferred evaluation modes"""
    msg = 'tags are interpreted only in workflow evaluation mode'
    warnings.warn(TextSUserWarning(msg, obj=obj))


def vary_processor(obj):
    """warn if vary is found in instant or in deferred evaluation modes"""
    warnings.warn(TextSUserWarning('vary statement has no effect', obj=obj))


def add_obj_processors(metamodel, wflow_processors=False):
    """register object processors, one per each class in the metamodel"""
    obj_processors = {'Null': null_processor,
                      'Number': number_processor,
                      'GeneralReference': general_reference_processor,
                      'ObjectImport': object_import_processor,
                      'Table': table_processor,
                      'ConditionComparison': condition_comparison_processor,
                      'ChemTerm': chem_term_processor,
                      'AMMLCalculator': amml_calculator_processor,
                      'AMMLAlgorithm': amml_algorithm_processor,
                      'AMMLProperty': amml_property_processor}
    if wflow_processors:
        obj_processors['Resources'] = resources_processor
        obj_processors['Map'] = parallelizable_processor
        obj_processors['Filter'] = parallelizable_processor
        obj_processors['Reduce'] = parallelizable_processor
        obj_processors['PrintParameter'] = print_parameter_processor
    else:
        obj_processors['Vary'] = vary_processor
        obj_processors['Tag'] = tag_processor
    metamodel.register_obj_processors(obj_processors)


def add_mod_processors(metamodel, constr_processors=True, io_processors=True,
                       wflow_processors=False):
    """register model processors in the order of their application"""
    metamodel.register_model_processor(function_call_processor)
    if constr_processors:
        metamodel.register_model_processor(check_variable_update_processor)
    if wflow_processors:
        metamodel.register_model_processor(source_code_statement_processor)
        metamodel.register_model_processor(variable_update_processor)
    if constr_processors:
        add_constraints_processors(metamodel)
    if wflow_processors:
        metamodel.register_model_processor(default_worker_name_processor)
        metamodel.register_model_processor(qadapter_processor)
        metamodel.register_model_processor(workflow_model_processor)
    elif io_processors:
        metamodel.register_model_processor(output_processor)


def add_processors(metamodel, constr_processors=True, io_processors=True,
                   wflow_processors=False):
    """register the processors on the metamodel instance"""
    add_obj_processors(metamodel, wflow_processors)
    add_mod_processors(metamodel, constr_processors=constr_processors,
                       io_processors=io_processors,
                       wflow_processors=wflow_processors)
