#! /usr/bin/env python3

################################################################################
""" Apply or update a tag, optionally updating it on the remote as well.

    Copyright (C) 2025 John Skilleter

    Licence: GPL v3 or later
"""
################################################################################

import sys
import argparse

import thingy.git2 as git

################################################################################

def main():
    """ Main function """

    # Command line parameters

    parser = argparse.ArgumentParser(description='Apply or update a tag, optionally updating it on the remote as well.')
    parser.add_argument('--push', '-p', action='store_true', help='Push the tag to the remote')
    parser.add_argument('tag', nargs=1, help='The tag')

    args = parser.parse_args()

    tag = args.tag[0]

    # Delete the tag if it currently exists, optionally pushing the deletion

    if tag in git.tags():
        git.tag_delete(tag, push=args.push)

    # Apply the tag

    git.tag_apply(tag, push=args.push)

################################################################################

def git_retag():
    """Entry point"""

    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    git_retag()
