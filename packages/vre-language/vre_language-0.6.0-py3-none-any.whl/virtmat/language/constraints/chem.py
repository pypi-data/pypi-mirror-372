"""constraints applied to chem objects"""
from textx import get_children_of_type, textx_isinstance
from virtmat.language.utilities.textx import get_reference
from virtmat.language.utilities.errors import StaticValueError, raise_exception
from virtmat.language.utilities.warnings import warnings, TextSUserWarning
from virtmat.language.utilities.chemistry import is_equation_balanced


def check_chem_reaction_balance(react, metamodel):
    """check that the equation a chemical reqaction is balanced"""
    lcomps = []
    rcomps = []
    lcoeff = []
    rcoeff = []
    bigzip = zip((react.educts, react.products), (lcoeff, rcoeff), (lcomps, rcomps))
    for terms, coeff, comps in bigzip:
        for term in terms:
            composition = get_reference(term.species).composition
            if textx_isinstance(composition, metamodel['GeneralReference']):
                return
            if textx_isinstance(composition, metamodel['String']):
                comps.append(composition.value)
                coeff.append(term.coefficient)
    if len(lcomps+rcomps) != len(react.educts+react.products):
        msg = ('reaction balance check skipped due to missing '
               'composition in some terms')
        warnings.warn(TextSUserWarning(msg, obj=react))
        return
    if not is_equation_balanced(lcomps, lcoeff, rcomps, rcoeff):
        msg = ('Reaction equation is not balanced. Check '
               'coefficients and compositions of species.')
        raise_exception(react, StaticValueError, msg)


def check_chem_reaction_processor(model, metamodel):
    """apply constraints to chem reaction objects"""
    for react in get_children_of_type('ChemReaction', model):
        check_chem_reaction_balance(react, metamodel)
