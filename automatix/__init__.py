import os
import sys
from copy import deepcopy
from csv import DictReader
from importlib import import_module
from time import time
from typing import List

from .automatix import Automatix
from .command import Command, SkipBatchItemException, AbortException
from .config import arguments, CONFIG, get_script, LOG, update_script_from_row, collect_vars, SCRIPT_FIELDS, VERSION

try:
    import python_progress_bar as progress_bar

    PROGRESS_BAR = True
except ImportError:
    PROGRESS_BAR = False


def main():
    if os.getenv('AUTOMATIX_SHELL'):
        print('You are running Automatix from an interactive shell of an already running Automatix!')
        answer = input('Do you really want to proceed? Then type "yes" and ENTER.\n')
        if answer != 'yes':
            sys.exit(0)

    starttime = time()
    args = arguments()

    if CONFIG.get('logging_lib'):
        log_lib = import_module(CONFIG.get('logging_lib'))
        init_logger = log_lib.init_logger
    else:
        from .logger import init_logger

    init_logger(name=CONFIG['logger'], debug=args.debug)

    if CONFIG.get('bundlewrap'):
        from .bundlewrap import BWCommand, AutomatixBwRepo

        CONFIG['bw_repo'] = AutomatixBwRepo(repo_path=os.environ.get('BW_REPO_PATH', '.'))
        cmd_class = BWCommand
    else:
        cmd_class = Command

    LOG.info(f'Automatix Version {VERSION}')

    configfile = CONFIG.get('config_file')
    if configfile:
        LOG.info(f'Using configuration from: {configfile}')
    else:
        LOG.warning('Configuration file not found or not configured. Using defaults.')

    script = get_script(args=args)

    batch_items: List[dict] = [{}]
    if args.vars_file:
        with open(args.vars_file) as csvfile:
            batch_items = list(DictReader(csvfile))
        script['batch_mode'] = True
        script['batch_items_count'] = len(batch_items)
        LOG.notice('Detected batch processing from CSV file.')

    if args.steps:
        exclude = script['exclude'] = args.steps.startswith('e')
        script['steps'] = {int(s) for s in (args.steps[1:] if exclude else args.steps).split(',')}

    try:
        if PROGRESS_BAR:
            progress_bar.setup_scroll_area()
        for i, row in enumerate(batch_items, start=1):
            script_copy = deepcopy(script)
            update_script_from_row(row=row, script=script_copy, index=i)

            variables = collect_vars(script_copy)

            auto = Automatix(
                script=script_copy,
                variables=variables,
                config=CONFIG,
                cmd_class=cmd_class,
                script_fields=SCRIPT_FIELDS,
                cmd_args=args,
                batch_index=i,
            )

            auto.set_command_count()
            try:
                auto.run()
            except SkipBatchItemException as exc:
                LOG.info(str(exc))
                LOG.notice('=====> Jumping to next batch item.')
                continue
            except AbortException as exc:
                sys.exit(int(exc))
            except KeyboardInterrupt:
                LOG.warning('\nAborted by user. Exiting.')
                sys.exit(130)
    finally:
        if PROGRESS_BAR:
            progress_bar.destroy_scroll_area()

    if 'AUTOMATIX_TIME' in os.environ:
        LOG.info(f'The Automatix script took {round(time() - starttime)}s!')
