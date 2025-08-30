"""JSON schemas for serialized data"""
import os
from fireworks_schema import register_schema, RegistryError
from virtmat.language.utilities.errors import ConfigurationError

SCHEMA_DIR = os.path.dirname(os.path.abspath(__file__))


def register_schemas():
    """register all JSON schema files in the module's directory"""
    all_files = os.listdir(SCHEMA_DIR)
    schema_files = filter(lambda f: os.path.splitext(f)[1] == '.json', all_files)
    for schema_file in schema_files:
        try:
            register_schema(os.path.join(SCHEMA_DIR, schema_file))
        except RegistryError as err:  # not covered
            raise ConfigurationError(err) from err
