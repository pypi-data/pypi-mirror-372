"""
check for duplicated initializations
"""
from virtmat.language.utilities.textx import get_identifiers
from virtmat.language.utilities.errors import InitializationError


def check_duplicates_processor(model, _):
    """
    processor to detect all duplicate object initializations
    """
    objs = get_identifiers(model)
    seen = set()
    dobjs = [v for v in objs if v.name in seen or seen.add(v.name)]
    if len(dobjs) != 0:
        raise InitializationError(dobjs[0])
