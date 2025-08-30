"""interactive session"""
import os
from argparse import ArgumentParser
from fireworks import LaunchPad
from fireworks.fw_config import LAUNCHPAD_LOC
from fireworks.user_objects.queue_adapters.common_adapter import CommonAdapter
from virtmat.middleware.resconfig import setup_resconfig
from virtmat.language.interpreter.session_manager import SessionManager
from virtmat.language.utilities.errors import error_handler, ConfigurationError
from virtmat.language.utilities.fireworks import object_from_file
from virtmat.language.utilities.textx import GRAMMAR_LOC
from virtmat.language.utilities.ioops import get_datastore_config, GRIDFS_DATASTORE
from virtmat.language.utilities.warnings import warnings, TextSUserWarning
from virtmat.language.utilities import logging


def parse_clargs():
    """parse the command line arguments for the script"""
    m_description = 'Execute a program remotely in deferred mode'
    parser = ArgumentParser(description=m_description)
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    """add arguments to a parser object"""
    parser.add_argument('-g', '--grammar-path', required=False,
                        help='path to grammar root file', default=GRAMMAR_LOC)
    parser.add_argument('-l', '--launchpad-file',
                        help='path to launchpad file', default=LAUNCHPAD_LOC)
    parser.add_argument('-u', '--uuid', default=None, required=False,
                        help='UUID of a model')
    parser.add_argument('-r', '--autorun', default=False, required=False,
                        action='store_true', help='run the model')
    parser.add_argument('-a', '--async-run', default=False, required=False,
                        action='store_true', help='run in background')
    parser.add_argument('-d', '--on-demand', default=False, required=False,
                        action='store_true', help='run on demand')
    parser.add_argument('-s', '--sleep-time', default=30, required=False,
                        type=int, help='sleep time for background evaluation in seconds')
    parser.add_argument('-q', '--qadapter-file', default=None, required=False,
                        help='path to default qadapter file')
    parser.add_argument('-f', '--model-file', required=False, default=None,
                        help='path to model file')
    parser.add_argument('-w', '--ignore-warnings', default=False, required=False,
                        action='store_true', help='do not display warnings')
    parser.add_argument('--no-unique-launchdir', default=False, required=False,
                        action='store_true', help='disable unique launchdir')
    parser.add_argument('--enable-logging', default=False, required=False,
                        action='store_true', help='enable logging messages')
    parser.add_argument('--logging-level', default='CRITICAL', required=False,
                        choices=logging.LOGGING_LEVELS, help='logging level')
    parser.add_argument('--logfile', default=None, required=False, help='logfile')
    parser.add_argument('--no-duplicate-detection', default=False, required=False,
                        action='store_true', help='disable duplicate detection')


@error_handler
def main(clargs):
    """main function"""
    logging.LOGGING_LEVEL = logging.get_logging_level(clargs.logging_level)
    if not clargs.enable_logging:
        logging.disable_logging()
        if logging.LOGGING_LEVEL > 20:
            warnings.filterwarnings('ignore')
    elif clargs.logfile:
        logging.logging.basicConfig(filename=clargs.logfile)
    warnings.filterwarnings('default', category=TextSUserWarning)
    if clargs.ignore_warnings:
        warnings.filterwarnings('ignore', category=TextSUserWarning)  # not covered

    setup_resconfig()

    if clargs.launchpad_file is None:
        if 'MONGOMOCK_SERVERSTORE_FILE' not in os.environ:
            msg = ('Neither default Launchpad file configured nor custom '
                   'Launchpad file is specified.')
            raise ConfigurationError(msg)
        # not covered
        lp_path = None
        lp_obj = LaunchPad()
        config_dir = os.path.dirname(os.environ['MONGOMOCK_SERVERSTORE_FILE'])
    else:
        lp_path = os.path.abspath(os.path.expanduser(clargs.launchpad_file))
        lp_obj = object_from_file(LaunchPad, lp_path)
        config_dir = os.path.dirname(lp_path)
    GRIDFS_DATASTORE.add(get_datastore_config(launchpad=lp_path), lp_obj)
    qadapter = clargs.qadapter_file and object_from_file(CommonAdapter, clargs.qadapter_file)
    detect_duplicates = not clargs.no_duplicate_detection
    grammar_path = clargs.grammar_path if clargs.uuid is None else None
    mgr = SessionManager(lp_obj, uuid=clargs.uuid, autorun=clargs.autorun,
                         grammar_path=grammar_path, on_demand=clargs.on_demand,
                         async_run=clargs.async_run, config_dir=config_dir,
                         qadapter=qadapter, detect_duplicates=detect_duplicates,
                         unique_launchdir=not clargs.no_unique_launchdir,
                         model_path=clargs.model_file, sleep_time=clargs.sleep_time,
                         lp_path=lp_path)
    mgr.main_loop()
