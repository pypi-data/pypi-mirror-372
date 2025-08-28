#! /usr/bin/env python3

################################################################################
""" Push to Gitlab and create a merge request at the same time """
################################################################################

import logging
import sys
import argparse

import thingy.git as git
import thingy.colour as colour

################################################################################

DESCRIPTION = 'Push a feature branch to GitLab and create a merge request'

################################################################################

def parse_arguments():
    """ Parse and return command line arguments """

    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--force', '-f', action='store_true', help='Force-push the branch')
    parser.add_argument('--parent', '-p', action='store', help='Override the default parent and specify the branch to merge onto')
    parser.add_argument('--reviewer', '-r', action='store', help='Specify the name of the reviewer for the merge request')
    parser.add_argument('--keep', '-k', action='store_true', help='Keep the source branch after the merge (default is to delete it).')

    args = parser.parse_args()

    # Enable logging if requested

    if args.debug:
        logging.basicConfig(level=logging.INFO)

    return args

################################################################################

def main():
    """ Main function - parse the command line and perform the pushing """

    args = parse_arguments()

    if args.parent:
        parents = [args.parent]
    else:
        parents, _ = git.parents()

        if not parents:
            colour.error('Unable to determine parent branch. Use the [BLUE]--parent[NORMAL] option to specify the appropriate one.')

        if len(parents) > 1:
            parent_list = ', '.join(parents)
            colour.error(
                f'Branch has multiple potential parents: [BLUE]{parent_list}[NORMAL]. Use the [BLUE]--parent[NORMAL] option to specify the appropriate one.')

    options = ['merge_request.create', f'merge_request.target={parents[0]}']

    if args.reviewer:
        options.append(f'merge_request.assign={args.reviewer}')

    if not args.keep:
        options.append('merge_request.remove_source_branch')

    logging.debug('Running git push with:')
    logging.debug('  force: %s', args.force)
    logging.debug('  push options: %s', options)

    result = git.push(force_with_lease=args.force, push_options=options)

    for text in result:
        print(text)

################################################################################

def git_mr():
    """Entry point"""

    try:
        main()

    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    git_mr()
