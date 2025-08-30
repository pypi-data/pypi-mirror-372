"""i/o operations"""
import os
import uuid
import tempfile
import yaml
from gridfs import GridFS
from fireworks import fw_config, LaunchPad
from virtmat.language.utilities.warnings import warnings, TextSUserWarning

FW_CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.fireworks')
DATASTORE_CONFIG_DEFAULT = {'path': os.path.join(FW_CONFIG_DIR, 'vre-language-datastore'),
                            'type': 'file',  # in ['file', 'gridfs', 'url', None]
                            'format': 'json',  # in ['json', 'yaml', 'hdf5', 'custom']
                            'name': 'vre_language_datastore',
                            'launchpad': fw_config.LAUNCHPAD_LOC,
                            'compress': True,
                            'inline-threshold': 100000}
# volatile storage, will be automatically cleaned up on exit
TEMP_STORE_DIR = tempfile.TemporaryDirectory()  # pylint: disable=R1732


def get_datastore_config(**kwargs):
    """update, set globally and return the data store configuration"""
    config = DATASTORE_CONFIG_DEFAULT
    if 'DATASTORE_CONFIG' in os.environ:
        conf_path = os.environ['DATASTORE_CONFIG']
        if not os.path.exists(conf_path):
            msg = f'The config file {conf_path} does not exist.'
            raise FileNotFoundError(msg)
    else:
        conf_path = os.path.join(FW_CONFIG_DIR, 'datastore_config.yaml')
    if os.path.exists(conf_path):
        with open(conf_path, 'r', encoding='utf-8') as inp:
            custom_config = yaml.safe_load(inp)
        config.update(custom_config)
    if config['type'] == 'file' and not os.path.exists(config['path']):
        os.makedirs(config['path'], exist_ok=True)  # not covered
    config.update(kwargs)
    globals()['DATASTORE_CONFIG'] = config
    return config


class GridFSDataStore(list):
    """store a list of unique GridFS datastores"""

    def add(self, conf, lpad=None):
        """add a datastore with a configuration and launchpad object lpad"""
        if conf['type'] != 'gridfs':
            return
        if self._get(conf) is None:
            lp_f = conf.get('launchpad')
            config = {'launchpad': lp_f, 'name': conf['name']}
            if lpad is None:
                lpad = LaunchPad() if lp_f is None else LaunchPad.from_file(lp_f)
            config['gridfs'] = GridFS(lpad.db, conf['name'])
            self.append(config)

    def get(self, conf):
        """get a datastore and add it if not yet included"""
        if conf['type'] == 'gridfs' and self._get(conf) is None:
            self.add(conf)
        return self._get(conf)

    def _get(self, conf):
        """get a datastore for specified configuration conf"""
        for entry in self:
            if (entry['launchpad'] == conf.get('launchpad')
               and entry['name'] == conf['name']):
                return entry['gridfs']
        return None


def get_uuid_filename(extension=None):
    """get a unique filename by applying evaluation mode policies"""
    basename = uuid.uuid4().hex
    filename = extension and f'{basename}.{extension}' or basename
    if 'WORKFLOW_EVALUATION_MODE' in os.environ and os.environ['WORKFLOW_EVALUATION_MODE'] == 'yes':
        if DATASTORE_CONFIG['type'] == 'file':
            directory = DATASTORE_CONFIG['path']
        else:
            msg = (f"Datastore type {DATASTORE_CONFIG['type']} cannot be used. "
                   f"Falling back to current working directory {os.getcwd()}.")
            warnings.warn(TextSUserWarning(msg))
            directory = os.path.abspath(os.getcwd())
    else:
        directory = TEMP_STORE_DIR.name
    return os.path.join(directory, filename)


GRIDFS_DATASTORE = GridFSDataStore()
DATASTORE_CONFIG = get_datastore_config()
