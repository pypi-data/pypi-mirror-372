"""main script for model execution in one of three different modes"""
import os
from argparse import ArgumentParser
from textx import metamodel_from_file
from textx.export import model_export
from fireworks import LaunchPad
from fireworks.fw_config import LAUNCHPAD_LOC
from fireworks.user_objects.queue_adapters.common_adapter import CommonAdapter
from virtmat.language.metamodel.properties import add_properties
from virtmat.language.metamodel.processors import add_processors
from virtmat.language.interpreter.session import Session
from virtmat.language.utilities.textx import GRAMMAR_LOC, GrammarString
from virtmat.language.utilities.compatibility import check_compatibility
from virtmat.language.utilities.errors import error_handler, ConfigurationError
from virtmat.language.utilities.warnings import warnings, TextSUserWarning
from virtmat.language.utilities.fireworks import object_from_file
from virtmat.language.utilities.ioops import get_datastore_config, GRIDFS_DATASTORE
from virtmat.language.utilities import logging


def parse_clargs():
    """parse the command line arguments for the script"""
    m_description = 'Execute a program in one of three different modes'
    parser = ArgumentParser(description=m_description)
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    """add arguments to a parser object"""
    parser.add_argument('-f', '--model-file', required=True,
                        help='path to model file')
    parser.add_argument('-g', '--grammar-path', required=False,
                        help='path to grammar root file', default=GRAMMAR_LOC)
    parser.add_argument('-m', '--mode', required=False, default='instant',
                        help='execution mode', choices=['instant', 'deferred', 'workflow'])
    parser.add_argument('-l', '--launchpad-file', default=LAUNCHPAD_LOC,
                        help='path to launchpad file (workflow mode only)')
    parser.add_argument('-u', '--uuid', default=None, required=False,
                        help='UUID of a model to extend/run (workflow mode only)')
    parser.add_argument('-r', '--autorun', default=False, required=False,
                        action='store_true', help='run the model (workflow mode only)')
    parser.add_argument('-d', '--on-demand', default=False, required=False,
                        action='store_true', help='run on demand')
    parser.add_argument('-q', '--qadapter-file', default=None, required=False,
                        help='path to default qadapter file (workflow mode only)')
    parser.add_argument('-w', '--ignore-warnings', default=False, required=False,
                        action='store_true', help='do not display warnings')
    parser.add_argument('--no-unique-launchdir', default=False, required=False,
                        action='store_true', help='disable unique launchdir')
    parser.add_argument('--enable-logging', default=False, required=False,
                        action='store_true', help='enable logging messages')
    parser.add_argument('--logging-level', default='CRITICAL', required=False,
                        choices=logging.LOGGING_LEVELS, help='logging level')
    parser.add_argument('--no-duplicate-detection', default=False, required=False,
                        action='store_true', help='disable duplicate detection')
    parser.add_argument('--no-interpreter', default=False, required=False,
                        action='store_true', help='do not run the interpreter')
    parser.add_argument('--show-model', default=False, required=False,
                        action='store_true', help='export model AST to dot file')


@error_handler
def run_instant_deferred(clargs, deferred=False, apply_constraints=True):
    """run a model in instant or deferred mode"""
    def check_clargs(attr_, val_, bstr_):
        if ((val_ in (None, False, True) and getattr(clargs, attr_)) or
           getattr(clargs, attr_) != val_):
            warnings.warn(f'argument {attr_} {bstr_}', TextSUserWarning)
    bstr = f'will be ignored in {clargs.mode} mode'
    attrs = {'launchpad_file': LAUNCHPAD_LOC, 'uuid': None, 'autorun': False,
             'qadapter_file': None, 'no_unique_launchdir': False,
             'no_duplicate_detection': False, 'on_demand': False}
    for attr, val in attrs.items():
        check_clargs(attr, val, bstr)

    check_compatibility(GrammarString(clargs.grammar_path).string)
    meta = metamodel_from_file(clargs.grammar_path, auto_init_attributes=False)
    add_properties(meta, deferred_mode=deferred)
    add_processors(meta, constr_processors=apply_constraints)

    with open(clargs.model_file, 'r', encoding='utf-8') as inp:
        model_str = inp.read()
    return meta.model_from_file(clargs.model_file, deferred_mode=deferred,
                                source_code=model_str)


@error_handler
def run_workflow(clargs):
    """run a model through a workflow system"""
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
    session = Session(lp_obj, uuid=clargs.uuid, grammar_path=grammar_path,
                      model_path=clargs.model_file, autorun=clargs.autorun,
                      on_demand=clargs.on_demand, detect_duplicates=detect_duplicates,
                      config_dir=config_dir, qadapter=qadapter, lp_path=lp_path,
                      unique_launchdir=not clargs.no_unique_launchdir)
    prog = session.get_model()
    session.stop_runner()
    if prog:
        print('program UUID:', prog.uuid)
    return prog


@error_handler
def evaluate_prog(prog):
    """evaluate the model"""
    print(f'program output: >>>\n{prog.value}\n<<<')


def main(clargs):
    """main function"""
    logging.LOGGING_LEVEL = logging.get_logging_level(clargs.logging_level)
    if not clargs.enable_logging:
        logging.disable_logging()
    if not clargs.enable_logging and logging.LOGGING_LEVEL > 20:
        warnings.filterwarnings('ignore')
    warnings.filterwarnings('default', category=TextSUserWarning)
    if clargs.ignore_warnings:
        warnings.filterwarnings('ignore', category=TextSUserWarning)

    if clargs.show_model:
        if clargs.mode != 'instant':
            msg = 'switching to instant mode due to argument show-model'
            warnings.warn(msg, TextSUserWarning)
            clargs.mode = 'instant'
        prog = run_instant_deferred(clargs, apply_constraints=False)
        if prog is not None and not isinstance(prog, str):
            model_export(prog, os.path.splitext(clargs.model_file)[0]+'.dot')
        return

    if clargs.no_interpreter:
        if clargs.mode != 'instant':
            msg = 'switching to instant mode due to argument no-interpreter'
            warnings.warn(msg, TextSUserWarning)
            clargs.mode = 'instant'
        run_instant_deferred(clargs)
        return

    if clargs.mode == 'instant':
        prog = run_instant_deferred(clargs, deferred=False)
    elif clargs.mode == 'deferred':
        prog = run_instant_deferred(clargs, deferred=True)
    else:
        assert clargs.mode == 'workflow'
        prog = run_workflow(clargs)
    if prog is not None and not isinstance(prog, str):
        evaluate_prog(prog)
