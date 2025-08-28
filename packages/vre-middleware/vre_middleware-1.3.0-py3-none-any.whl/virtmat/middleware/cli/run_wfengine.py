"""run a simple workflow engine from the command line"""
import json
import signal
from time import sleep
from argparse import ArgumentParser, BooleanOptionalAction
from fireworks import LaunchPad, Workflow
from fireworks.fw_config import LAUNCHPAD_LOC
from fireworks.user_objects.queue_adapters.common_adapter import CommonAdapter
from virtmat.middleware.engine.wfengine import WFEngine
from virtmat.middleware.utilities import logging, get_logger, LOGGING_LEVELS
from virtmat.middleware.exceptions import ConfigurationException

EXIT_NOW = False


def exit_gracefully(signum, _):
    """signal handler callback function"""
    globals()['EXIT_NOW'] = True
    logger = get_logger('run_wfengine', getattr(logging, 'INFO'))
    logger.info('signal %s received, please wait to exit ...', signum)


signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)


def parse_clargs():
    """parse the command line arguments for the script"""
    m_description = 'run a simple workflow engine from the command line'
    parser = ArgumentParser(description=m_description)
    add_arguments(parser)
    return parser.parse_args()


def add_arguments(parser):
    """add arguments to a parser object"""
    parser.add_argument('-l', '--launchpad-file', default=LAUNCHPAD_LOC,
                        help='path to launchpad file')
    parser.add_argument('-q', '--qadapter-file', default=None, required=False,
                        help='path to default qadapter file')
    parser.add_argument('-n', '--worker-name', default=None, required=False,
                        help='worker name')
    parser.add_argument('-d', '--launchdir', default=None, required=False,
                        help='path to launch directory')
    parser.add_argument('-s', '--sleep-time', default=30, required=False,
                        type=int, help='sleep time for background evaluation in seconds')
    parser.add_argument('-c', '--category', default='all', required=False,
                        choices=('all', 'interactive', 'batch'),
                        help='category of nodes to run')
    parser.add_argument('-f', '--workflow-file', required=False, default=None,
                        help='path to a workflow file')
    parser.add_argument('--wf-query', type=lambda x: x if x else None, default=None,
                        required=False, help='workflow query as JSON string')
    parser.add_argument('--unique-launchdir', default=True, required=False,
                        action=BooleanOptionalAction, help='use unique launchdir')
    parser.add_argument('-r', '--autorun', default=False, required=False,
                        action='store_true', help='run workflow nodes')
    parser.add_argument('--loop', default=True, action=BooleanOptionalAction,
                        required=False, help='run nodes in an endless loop')
    parser.add_argument('--load-from-file', default=None, required=False,
                        type=str, help='load a wfengine from file')
    parser.add_argument('--dump-to-file', default=None, type=str,
                        required=False, help='dump the wfengine to file')
    parser.add_argument('--enable-logging', default=False, required=False,
                        action='store_true', help='enable logging messages')
    parser.add_argument('--logging-level', default='CRITICAL', required=False,
                        choices=LOGGING_LEVELS, help='logging level')


def wfengine_main(clargs):
    """the main function taking clargs as parameter"""
    if not clargs.enable_logging:
        logging.disable(logging.CRITICAL)

    logger = get_logger('run_wfengine', getattr(logging, clargs.logging_level))
    wf_query = clargs.wf_query and json.loads(clargs.wf_query)

    if clargs.load_from_file:
        logger.info('wfengine file: %s', clargs.load_from_file)
        wfe = WFEngine.from_file(clargs.load_from_file)
        if wf_query is not None:
            wfe.wf_query = wf_query
    elif clargs.launchpad_file:
        logger.info('launchpad file: %s', clargs.launchpad_file)
        launchpad = LaunchPad.from_file(clargs.launchpad_file)
        logger.info('qadapter file: %s', clargs.qadapter_file)
        qadapter = clargs.qadapter_file and CommonAdapter.from_file(clargs.qadapter_file)
        wfe = WFEngine(launchpad, qadapter=qadapter, wf_query=wf_query,
                       name=clargs.worker_name, launchdir=clargs.launchdir,
                       unique_launchdir=clargs.unique_launchdir,
                       sleep_time=clargs.sleep_time)
    else:
        logger.critical('no launchpad could be detected')
        raise ConfigurationException('no launchpad could be detected')

    logger.info('workflow query: %s', wfe.wf_query)
    logger.info('worker name: %s', wfe.name)
    logger.info('launch directory: %s', wfe.launchdir)
    logger.info('unique launch directory: %s', wfe.unique_launchdir)
    logger.info('workflow file: %s', clargs.workflow_file)

    if clargs.workflow_file:
        wfe.add_workflow(Workflow.from_file(clargs.workflow_file))

    if clargs.dump_to_file:
        logger.info('dumping engine to file: %s', clargs.dump_to_file)
        wfe.to_file(clargs.dump_to_file)

    logger.info('autorun: %s', clargs.autorun)

    launcher = {'batch': 'qlaunch', 'interactive': 'rlaunch'}
    categories = ('batch', 'interactive') if clargs.category == 'all' else (clargs.category,)

    if clargs.autorun:
        logger.info('loop: %s', clargs.loop)
        logger.info('sleep time: %s', wfe.sleep_time)
        logger.info('running categories: %s', categories)
        logger.info('to exit, press Ctrl+C and wait %s seconds', wfe.sleep_time)
        while True:
            for category in categories:
                fw_q = {'state': 'READY', 'spec._category': category}
                fw_ids = wfe.launchpad.get_fw_ids_in_wfs(wfe.wf_query, fw_q)
                logger.debug('%s nodes to run: %s', category, fw_ids)
                for fw_id in fw_ids:
                    getattr(wfe, launcher[category])(fw_id)
            logger.info('failed nodes: %s', wfe.get_failed())
            sleep(wfe.sleep_time)
            if EXIT_NOW or not clargs.loop:
                break


def main():
    """main function in module used as entry point"""
    wfengine_main(parse_clargs())
