#! /usr/bin/env python3

################################################################################
""" Basic subprocess handling - simplified API to the Python subprocess module

    Copyright (C) 2017-18 John Skilleter

    Licence: GPL v3 or later
"""
################################################################################

import subprocess
import sys
import logging

################################################################################

class RunError(Exception):
    """ Run exception """

    def __init__(self, msg, status=1):
        super(RunError, self).__init__(msg)
        self.msg = msg
        self.status = status

################################################################################

def run(command, foreground=False, shell=False):
    """ Run the specified command and return the output.
        command - the command to run as an array of command+arguments
        foreground - set to True to run the command in the foreground, using stdin/err/out
        shell - set to True to run the command inside a shell (allows the command to be specified
                as a string, but needs spaces to bew quoted
        Returns an empty array if foreground is True or an array of the output otherwise. """

    # TODO: for background use subprocess.Popen but use devnull = open('/dev/null', 'w') for stdio and return proc instead of communicating with it?

    logging.info('Running "%s"', ' '.join(command))

    # If running in the foreground, run the command and either return an empty value
    # on success (output is to the console) or raise a RunError

    if foreground:
        try:
            if shell:
                # TODO: Handle command lines with parameters containing spaces
                command = ' '.join(command)

            status = subprocess.run(command, shell=shell).returncode
            if status:
                raise RunError('Error %d' % status, status)
            else:
                return []
        except OSError as exc:
            raise RunError(exc)
    else:
        # Run the command and capture stdout and stderr

        try:
            proc = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
        except OSError as exc:
            raise RunError(exc)

        logging.info('Stdout: %s', proc.stdout)
        logging.info('Stderr: %s', proc.stderr)

        # If it returned an error raise a RunError exception with the stdout text as the
        # exception message

        if proc.returncode:
            raise RunError(proc.stderr)

        # Otherwise return the stdout data or nothing

        if proc.stdout:
            output = proc.stdout.split('\n')
        else:
            output = []

        # Remove trailing blank lines from the output

        while output and output[-1] == '':
            output = output[:-1]

        logging.info('Output: %s', output)
        return output

################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    print('Run ls -l:')

    cmd_output = run(['ls', '-l'])

    for o in cmd_output:
        print(o)

    print('Run wombat (should fail):')
    try:
        run(['wombat'])
    except RunError as exc:
        print('Failed with error: %s' % exc.msg)

    if sys.stdout.isatty():
        print('Run vi in the foreground')

        run(['vi'], foreground=True)
    else:
        print('Not testing call to run() with foreground=True as stdout is not a TTY')
