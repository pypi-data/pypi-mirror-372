"""the main entry point for the virtmat language supporting tools"""
import importlib
import argparse
from virtmat.language.utilities.errors import ConfigurationError, error_handler


@error_handler
def texts():
    """main function selecting one of the main modes - session or script"""
    try:
        run_model = importlib.import_module('virtmat.language.cli.run_model')
        run_session = importlib.import_module('virtmat.language.cli.run_session')
        version_mod = importlib.import_module('virtmat.language.cli.version')
        version = getattr(version_mod, 'VERSION')
    except SyntaxError as err:
        raise err
    except Exception as err:
        msg = 'An error ocurred during initialization. Check your configuration files.\n'
        raise ConfigurationError(msg+str(err)) from err
    parser = argparse.ArgumentParser(prog='texts', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version=version)

    subparsers = parser.add_subparsers(help='Select the main mode', required=True,
                                       dest='session or script')
    help_i = 'Start an interactive session in workflow evaluation mode'
    parser_i = subparsers.add_parser(name='session',
                                     description='Start an interactive session',
                                     help=help_i)
    run_session.add_arguments(parser_i)
    parser_i.set_defaults(func=run_session.main)
    help_b = 'Run a script in instant, deferred or workflow evaluation mode'
    parser_b = subparsers.add_parser(name='script',
                                     description='Run a script',
                                     help=help_b)
    run_model.add_arguments(parser_b)
    parser_b.set_defaults(func=run_model.main)
    clargs = parser.parse_args()
    clargs.func(clargs)
# python -m cProfile src/virtmat/language/cli/__init__.py [texts options] 2>&1 | tee cProfile.out
# uncomment for profiling
# if __name__ == '__main__':
#    texts()
