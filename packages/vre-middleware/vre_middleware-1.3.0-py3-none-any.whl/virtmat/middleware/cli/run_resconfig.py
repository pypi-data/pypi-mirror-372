"""create a resource configuration"""
import os
import warnings
from argparse import ArgumentParser
from virtmat.middleware.resconfig import get_resconfig_loc, configure, setup_resconfig
from virtmat.middleware.utilities import format_warning_wrapper


def parse_clargs():
    """parse the command line arguments for the script"""
    m_description = 'create a resource configuration file from scratch'
    parser = ArgumentParser(description=m_description)
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    """add arguments to a parser object"""
    parser.add_argument('-i', '--interactive', default=False, required=False,
                        action='store_true', help='enable interactive mode, no overwrite')
    parser.add_argument('-o', '--overwrite', default=False, required=False,
                        action='store_true', help='overwrite existing configuration')
    parser.add_argument('-f', '--path', type=str, default=None, required=False,
                        help='non-default resconfig location, overrides RESCONFIG_LOC')


def resconfig_main(clargs):
    """main resconfig function"""
    warnings.formatwarning = format_warning_wrapper(warnings.formatwarning)
    resconfig_loc = clargs.path or get_resconfig_loc()
    if clargs.interactive:
        setup_resconfig(resconfig_loc)
        return
    if os.path.exists(resconfig_loc) and not clargs.overwrite:
        print(f'Resource configuration {resconfig_loc} exists.')
        return
    configure(resconfig_loc)


def main():
    """main function in module used as entry point"""
    resconfig_main(parse_clargs())
