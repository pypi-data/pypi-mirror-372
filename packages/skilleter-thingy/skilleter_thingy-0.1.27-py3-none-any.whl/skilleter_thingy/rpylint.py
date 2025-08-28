#! /usr/bin/env python3

################################################################################
""" Run pylint on all the Python source files in the current tree

    Copyright (C) 2017-18 John Skilleter """
################################################################################

import os
import sys
import argparse
import glob

# TODO: Convert to use thingy.proc
import thingy.process as process

################################################################################

def main():
    """ Main code. Exits directly on failure to locate source files, or returns
        the status code from Pylint otherwise. """

    # Parse the comand line

    parser = argparse.ArgumentParser(description='Run pylint in the current (or specified) directory/ies')

    parser.add_argument('paths', nargs='*', help='List of files or paths to lint')

    args = parser.parse_args()

    if not args.paths:
        args.paths = ['.']

    sourcefiles = []

    # Use rgrep to find source files that have a Python 3 #!

    for entry in args.paths:
        if os.path.isdir(entry):
            try:
                sourcefiles += process.run(['rgrep', '-E', '--exclude-dir=.git', '-l', '#![[:space:]]*/usr/bin/(env[[:space:]])?python3'] + args.paths)
            except process.RunError as exc:
                if exc.status == 1:
                    sys.stderr.write('No Python3 source files found\n')
                    sys.exit(2)
                else:
                    sys.stderr.write('%d: %s\n' % (exc.status, exc.msg))
                    sys.exit(1)
        elif os.path.isfile(entry):
            sourcefiles.append(entry)
        else:
            files = glob.glob(entry)

            if not files:
                sys.stderr.write('No files found matching "%s"' % entry)
                sys.exit(2)

            sourcefiles += files

    # Run pylint on all the files

    try:
        process.run(['pylint3', '--output-format', 'parseable'] + sourcefiles, foreground=True)
    except process.RunError as exc:
        status = exc.status
    else:
        status = 0

    if status >= 64:
        sys.stderr.write('Unexpected error: %d\n' % status)

    # Function return code is the status return from pylint

    return status

################################################################################

def rpylint():
    """Entry point"""

    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    rpylint()
