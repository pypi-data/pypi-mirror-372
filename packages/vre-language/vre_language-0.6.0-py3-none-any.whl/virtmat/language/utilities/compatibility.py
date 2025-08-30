"""define/check grammar and data schema versions compatible to the interpreter"""
import re
from virtmat.language.utilities.logging import get_logger
from virtmat.language.utilities.errors import CompatibilityError

versions = {'grammar': [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 28,
                        29, 30, 31, 32, 33, 34, 35],
            'data_schema': [6, 7]}


def get_grammar_version(grammar_str):
    """extract the version number from the grammar"""
    regex = re.compile(r'\/\*\s*grammar version\s+(\d+)\s*\*\/', re.MULTILINE)
    match = re.search(regex, grammar_str)
    if match:
        version = int(match.group(1))
    else:
        raise ValueError('cannot find version tag in grammar')
    return version


def check_compatibility(grammar_str=None, grammar_ver=None, data_schema=None):
    """check compatibility of grammar and data schema"""
    logger = get_logger(__name__)
    assert grammar_str is not None or grammar_ver is not None
    if grammar_ver is None:
        grammar_ver = get_grammar_version(grammar_str)
    if grammar_ver not in versions['grammar']:
        msg = (f"Provided grammar has version {grammar_ver} but the supported "
               f"versions are {versions['grammar']}")
        logger.error(msg)
        raise CompatibilityError(msg)
    logger.debug('found grammar version')
    if data_schema is not None:
        logger.debug('checking the schema')
        if data_schema not in versions['data_schema']:
            msg = f'Data schema version {data_schema} is not supported'
            logger.error(msg)
            raise CompatibilityError(msg)
