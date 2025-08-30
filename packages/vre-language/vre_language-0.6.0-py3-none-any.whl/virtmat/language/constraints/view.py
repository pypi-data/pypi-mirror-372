"""apply constraints for all view statements"""
from virtmat.language.utilities.errors import textxerror_wrap
from .amml import check_view_amml_structure_processor


@textxerror_wrap
def check_view_processor(model, metamodel):
    """apply constraints for all view statements"""
    # check_view_lineplot_processor(model, metamodel)
    # check_view_scatterplot_processor(model, metamodel)
    check_view_amml_structure_processor(model, metamodel)
    # check_view_amml_trajectory_processor(model, metamodel)
    # check_view_amml_vibration_processor(model, metamodel)
    # check_view_amml_neb_processor(model, metamodel)
    # check_view_amml_bs_processor(model, metamodel)
    # check_view_amml_eos_processor(model, metamodel)
    # check_view_amml_waterfall_processor(model, metamodel)
