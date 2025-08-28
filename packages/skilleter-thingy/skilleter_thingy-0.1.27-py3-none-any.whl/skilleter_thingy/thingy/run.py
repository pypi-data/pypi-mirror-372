#! /usr/bin/env python3

################################################################################
""" Code for running a subprocess, optionally capturing stderr and/or stdout and
    optionally echoing either or both to the console in realtime and storing.

    Uses threads to capture and output stderr and stdout since this seems to be
    the only way to do it (Popen does not have the ability to output the process
    stdout output to the stdout output).

    Intended for more versatile replacement for the thingy process.run() function
    which can handle all combinations of foreground/background console/return
    stderr/stdout/both options. """

# TODO: This does not run on Python versions <3.5 (so Ubuntu 14.04 is a problem!)
################################################################################

################################################################################
# Imports

import sys
import subprocess
import threading
import shlex

import thingy.colour as colour
import thingy.tidy as tidy

################################################################################

class RunError(Exception):
    """ Run exception """

    def __init__(self, msg, status=1):
        super().__init__(msg)
        self.msg = msg
        self.status = status

################################################################################

def capture_output(cmd, input_stream, output_streams, ansi_clean):
    """ Capture data from a stream (input_stream), optionally
        outputting it (if output_streams is not None and optionally
        saving it into a variable (data, if not None), terminating
        when the specified command (cmd, which is presumed to be the process
        outputting to the input stream) exits.
        TODO: Use of convert_ansi should be controlled via a parameter (off/light/dark)
        TODO: Another issue is that readline() only returns at EOF or EOL, so if you get a prompt "Continue?" with no newline you do not see it until after you respond to it.
    """

    while True:
        output = input_stream.readline()

        if output:
            if output_streams:
                for stream in output_streams:
                    if isinstance(stream, list):
                        stream.append(output.rstrip())
                    else:
                        if stream in (sys.stdout, sys.stderr):
                            stream.write(tidy.convert_ansi(output))
                        elif ansi_clean:
                            stream.write(tidy.remove_ansi(output))
                        else:
                            stream.write(output)

        elif cmd.poll() is not None:
            return

################################################################################

def capture_continuous(cmd, input_stream, output_streams, ansi_clean):
    """ Capture data from a stream (input_stream), optionally
        outputting it (if output_streams is not None and optionally
        saving it into a variable (data, if not None), terminating
        when the specified command (cmd, which is presumed to be the process
        outputting to the input stream) exits.
        TODO: Use of convert_ansi should be controlled via a parameter (off/light/dark)
        TODO: ansi_clean not implemented
    """

    output_buffer = []

    while True:
        output = input_stream.read(1)

        if output:
            if output_streams:
                for stream in output_streams:
                    if isinstance(stream, list):
                        if output == '\n':
                            stream.append(''.join(output_buffer))
                            output_buffer = []
                        else:
                            output_buffer.append(output)
                    else:
                        stream.write(output)
                        stream.flush()

        elif cmd.poll() is not None:
            if output_buffer:
                stream.append(''.join(output_buffer))

            return

################################################################################

def process(command,
            stdout=None, stderr=None,
            return_stdout=False, return_stderr=False,
            shell=False,
            output=None,
            ansi_clean=False,
            exception=True,
            continuous=False):
    """ Run an external command.

        stdout and stderr indicate whether stdout/err are output and/or sent to a file and/or stored in a variable.
        They can be boolean (True: output to sys.stdout/err, False: Do nothing), a file handle or a variable, or an
        array of any number of these (except booleans).

        return_stdout and return_stderr indicate whether stdout/err should be returned from the function (setting
        these to False saves memory if the output is not required).

        If shell is True the command will be run in a shell and wildcard arguments expanded

        If exception is True an exception will be raised if the command returns a non-zero status

        If output is True then stdout and stderr are both output as if stdout=True and stderr=True (in addition to
        any other values passed in those parameters)

        If ansi_clean is True then ANSI control sequences are removed from any streams in stdout and stderr but
        not from the console output.

        If continuous is True then output is processed character-by-character (normally for use when output=True)
        TODO: Currently this causes the ansi_clean option to be ignored

        The return value is a tuple consisting of the status code, captured stdout (if any) and captured
        stderr (if any).

        Will raise OSError if the command could not be run and RunError if exception is True and the
        command returned a non-zero status code. """

    # If stdout/stderr are booleans then output to stdout/stderr if True, else discard output

    if isinstance(stdout, bool):
        stdout = sys.stdout if stdout else None

    if isinstance(stderr, bool):
        stderr = sys.stderr if stderr else None

    # If stdout/stderr are not arrays then make them so

    if not isinstance(stdout, list):
        stdout = [stdout] if stdout else []

    if not isinstance(stderr, list):
        stderr = [stderr] if stderr else []

    # If output is True then add stderr/out to the list of outputs

    if output:
        if sys.stdout not in stdout:
            stdout.append(sys.stdout)

        if sys.stderr not in stderr:
            stderr.append(sys.stderr)

    # Capture stdout/stderr to arrays unless asked not to

    stdout_data = []
    stderr_data = []

    if return_stdout:
        stdout.append(stdout_data)

    if return_stderr:
        stderr.append(stderr_data)

    # If running via the shell then the command should be a string, otherwise
    # it should be an array

    if shell:
        if not isinstance(command, str):
            command = ' '.join(command)
    else:
        if isinstance(command, str):
            command = shlex.split(command, comments=True)

    # Use a pipe for stdout/stderr if are are capturing it
    # and send it to /dev/null if we don't care about it at all.

    if stdout == [sys.stdout] and not stderr:
        stdout_stream = subprocess.STDOUT
        stderr_stream = subprocess.DEVNULL
    else:
        stdout_stream = subprocess.PIPE if stdout else subprocess.DEVNULL
        stderr_stream = subprocess.PIPE if stderr else subprocess.DEVNULL

    # Run the command with no buffering and capturing output if we
    # want it - this will raise OSError if there was a problem running
    # the command.

    cmd = subprocess.Popen(command,
                           bufsize=0,
                           stdout=stdout_stream,
                           stderr=stderr_stream,
                           text=True,
                           errors='ignore',
                           encoding='ascii',
                           shell=shell)

    # Create threads to capture stderr and/or stdout if necessary

    if stdout_stream == subprocess.PIPE:
        stdout_thread = threading.Thread(target=capture_continuous if continuous else capture_output, args=(cmd, cmd.stdout, stdout, ansi_clean), daemon=True)
        stdout_thread.start()
    else:
        stdout_thread = None

    if stderr_stream == subprocess.PIPE:
        stderr_thread = threading.Thread(target=capture_continuous if continuous else capture_output, args=(cmd, cmd.stderr, stderr, ansi_clean), daemon=True)
        stderr_thread.start()
    else:
        stderr_thread = None

    # Wait until the command terminates (and set the returncode)

    if stdout_thread:
        stdout_thread.join()

    if stderr_thread:
        stderr_thread.join()

    cmd.wait()

    # If the command failed, raise an exception (if required)

    if exception and cmd.returncode:
        if return_stderr:
            raise RunError('\n'.join(stderr_data))
        else:
            raise RunError('Error %d running "%s"' % (cmd.returncode, (command if isinstance(command, str) else ' '.join(command))))

    # Return status, stdout, stderr (the latter 2 may be empty if we did not capture data).

    return {'status': cmd.returncode, 'stdout': stdout_data, 'stderr': stderr_data}

################################################################################

def run(command,
        stdout=None, stderr=None,
        shell=False,
        output=None,
        ansi_clean=False,
        exception=True,
        continuous=False):
    """ Simple interface to the process() function
        Has the same parameters, with the same defaults.
        The return value is either the data output to stdout, if any
        or the data output to stderr otherwise.
        The status code is not returned, but the function will raise an exception
        by default if it is non-zero """

    result = process(command=command,
                     stdout=stdout, stderr=stderr,
                     return_stdout=True, return_stderr=True,
                     shell=shell,
                     output=output,
                     ansi_clean=ansi_clean,
                     exception=exception,
                     continuous=continuous)

    return result['stdout'] if result['stdout'] else result['stderr']

################################################################################

def status(command, shell=False, output=False):
    """ Alternative simple interface to the process() function
        Just takes a command and the shell flag.
        Runs the command without capturing the output
        Optionally outputting both stdout and stderr
        and returns the status code.
        Will only raise an exception if the command could not be run. """

    return process(command,
                   stdout=output,
                   stderr=output,
                   shell=shell,
                   exception=False)['status']

################################################################################

if __name__ == '__main__':
    def test_run(cmd,
                 stdout=None, stderr=None,
                 return_stdout=True, return_stderr=True,
                 shell=False,
                 exception=True):
        """ Test wrapper for the process() function. """

        print('-' * 80)
        print('Running: %s' % (cmd if isinstance(cmd, str) else ' '.join(cmd)))

        result = process(cmd,
                         stdout=stdout, stderr=stderr,
                         return_stdout=return_stdout, return_stderr=return_stderr,
                         shell=shell,
                         exception=exception)

        print('Status: %d' % result['status'])

    def test():
        """ Test code """

        test_run('echo nothing')

        test_run(['ls', '-l', 'run_jed'])
        test_run(['ls -l run_*'], stdout=True, shell=True)
        test_run('false', exception=False)
        test_run('true', stdout=sys.stdout, exception=False)
        test_run(['git', 'status'], stdout=sys.stdout, stderr=sys.stderr, exception=False)

        test_run(['make'], stderr=sys.stderr, exception=False)
        test_run(['make'], stdout=sys.stdout, stderr=[sys.stderr], exception=False)
        test_run(['make'], stdout=True, exception=False)
        test_run(['make'], stdout=sys.stdout, exception=False)
        test_run(['make'], exception=False)

        output = []
        test_run('ls -l x*; sleep 1; echo "Bye!"', stderr=[sys.stderr, output], stdout=sys.stdout, shell=True, return_stdout=False)
        print('Output=%s' % output)

    test()
