"""create a string with version information"""
import sys
from importlib.metadata import version
from virtmat.language.utilities.compatibility import versions, get_grammar_version
from virtmat.language.utilities.textx import GrammarString
from virtmat.language.utilities.serializable import DATA_SCHEMA_VERSION

grammar_version = get_grammar_version(GrammarString().string)

VERSION = (f"vre-language: {version('vre-language')}\n"
           f"vre-middleware: {version('vre-middleware')}\n"
           f"grammar version: {grammar_version}\n"
           f"data schema version: {DATA_SCHEMA_VERSION}\n"
           f"compatible grammar versions: {versions['grammar']}\n"
           f"compatible data schema versions: {versions['data_schema']}\n"
           f"python version: {sys.version}")
