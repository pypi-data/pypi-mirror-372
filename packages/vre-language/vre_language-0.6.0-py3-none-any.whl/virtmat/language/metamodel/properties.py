"""set property and further class attributes to metamodel classes"""
from textx import textx_isinstance
from virtmat.language.constraints.typechecks import add_type_properties
from virtmat.language.interpreter.instant_executor import add_value_properties
from virtmat.language.interpreter.deferred_executor import add_deferred_value_properties
from virtmat.language.interpreter.workflow_executor import add_workflow_properties
from virtmat.language.interpreter.deferred_executor import add_func_properties
from virtmat.language.utilities.logging import get_logger
from virtmat.language.utilities.textx import get_reference
from .function import add_function_call_properties
from .clone import add_deepcopy
from .view import add_display


def add_metamodel_classes_attributes(metamodel):
    """add various attributes to metamodel classes"""

    def get_column_names(self):
        """get the column names of a table, returns a list of strings"""
        names = []
        for col in self.columns:
            sobj = get_reference(col)
            if textx_isinstance(sobj, metamodel['Series']):
                names.append(sobj.name)
        return names

    def get_column(self, name):
        """get a column with given name from a table, return series"""
        for col in self.columns:
            sobj = get_reference(col)
            if textx_isinstance(sobj, metamodel['Series']):
                if sobj.name == name:
                    return sobj
        return None

    metamodel['Table'].get_column = get_column
    metamodel['Table'].get_column_names = get_column_names


def add_properties(metamodel, deferred_mode=False, workflow_mode=False):
    """set attributes and properties in the metamodel"""
    add_model_param_defs(metamodel)
    add_deepcopy(metamodel)
    add_metamodel_classes_attributes(metamodel)
    add_type_properties(metamodel)
    if deferred_mode or workflow_mode:
        get_logger(__name__).info('running %s in deferred mode', metamodel)
        add_func_properties(metamodel)
        if workflow_mode:
            get_logger(__name__).info('running %s in workflow mode', metamodel)
            add_workflow_properties(metamodel)
        else:
            add_deferred_value_properties(metamodel)
    else:
        get_logger(__name__).info('running %s in instant mode', metamodel)
        add_value_properties(metamodel)
    add_function_call_properties(metamodel)
    add_display(metamodel)


def add_model_param_defs(metamodel):
    """add model parameter definitions to access with model._tx_model_params"""
    metamodel.model_param_defs.add('model_instance', 'Model instance')
    metamodel.model_param_defs.add('source_code', 'Source code of the model')
    metamodel.model_param_defs.add('grammar_str', 'Grammar for parsing the model')
    metamodel.model_param_defs.add('deferred_mode', 'Deferred evaluation mode')
    metamodel.model_param_defs.add('detect_duplicates', 'Enable duplicates detection')
    metamodel.model_param_defs.add('autorun', 'Run the model')
    metamodel.model_param_defs.add('on_demand', 'Run the model nodes on demand')
    metamodel.model_param_defs.add('unique_launchdir', 'Launch in unique directories')
    metamodel.model_param_defs.add('display_graphics', 'Toggle graphics display')
