#!/usr/bin/env python3

"""
Report the oldest commit in common in the history of two commits
"""

################################################################################

import sys
import argparse

import thingy.colour as colour
import thingy.git as git

################################################################################

def main():
    """ Main function """

    parser = argparse.ArgumentParser(description='Find the most recent common ancestor for two commits')

    parser.add_argument('--short', '-s', action='store_true', help='Just output the ancestor commit ID')
    parser.add_argument('--long', '-l', action='store_true', help='Output the log entry for the commit')
    parser.add_argument('commit1', nargs='?', default='HEAD', help='First commit (default=HEAD)')
    parser.add_argument('commit2', nargs='?', default='master', help='Second commit (default=master)')

    args = parser.parse_args()

    if args.long and args.short:
        colour.error('The [BLUE:--long] and [BLUE:--short] options cannot be used together', prefix=True)

    try:
        ancestor = git.find_common_ancestor(args.commit1, args.commit2)
    except git.GitError as exc:
        colour.error(exc, status=exc.status, prefix=True)

    if args.short:
        print(ancestor)
    elif args.long:
        print('\n'.join(git.log(ancestor)))
    else:
        colour.write(f'Last common commit between [BLUE:{args.commit1}] and [BLUE:{args.commit2}] is [BLUE:{ancestor}]')

################################################################################
# Entry point

def git_common():
    """Entry point"""

    try:
        main()

    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    git_common()
