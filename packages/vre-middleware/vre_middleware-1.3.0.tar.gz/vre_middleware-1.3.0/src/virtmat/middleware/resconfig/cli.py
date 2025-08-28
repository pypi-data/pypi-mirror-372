"""command-line tools to configure available resources"""
import os
from virtmat.middleware.resconfig import get_resconfig_loc, configure


def setup_resconfig(resconfig_loc=None):
    """setup resource configuration interactively"""
    if resconfig_loc is None:
        resconfig_loc = get_resconfig_loc()
    if os.path.exists(resconfig_loc):
        print(f'Resource configuration {resconfig_loc} exists.')
        return

    print(f'Resource configuration {resconfig_loc} not found.\n'
          'Do you want to create it?')
    while True:
        try:
            inp = input('Yes(default) | No | Ctrl+C to skip: ').strip()
        except KeyboardInterrupt:
            print('\n')
            break
        else:
            if inp.lower() in ('no', 'n'):
                break
            if inp.lower() in ('yes', ''):
                configure(resconfig_loc)
                break
            continue
