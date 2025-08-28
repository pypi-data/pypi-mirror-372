#! /usr/bin/env python3

################################################################################
"""
    Monitor window titles and rename them to fit an alphabetical grouping
    in 'Appname - Document' format.
"""
################################################################################

import sys
import re
import subprocess

################################################################################
# Hard coded table of regexes for window titles to rename
# TODO: This should be a configuration file

RENAMES = [
    [r'^\[(.*)\]$', r'\1'],
    [r'(.*) - Mozilla Firefox', r'Firefox - \1'],
    [r'(.*) - Mozilla Thunderbird', r'Thunderbird - \1'],
    [r'\[(.*) - KeePass\]', r'Keepass - \1'],
    [r'(.*) - LibreOffice Calc', r'LibreOffice Calc - \1'],
    [r'(.*) - Zim$', r'Zim - \1'],
    [r'(.*) - Chromium$', r'Chromium - \1'],
]

################################################################################

def main():
    """ Search for windows and rename them appropriately """

    # Build the re. to match renameable windows

    regex = '|'.join([rename[0] for rename in RENAMES])

    # Build the command to wait for a matching visible window to appear

    cmd = ['xdotool', 'search', '--sync', '--name', '--onlyvisible', regex]

    while True:
        # Wait for one or more matching windows

        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)

        if result.returncode:
            sys.stderr.write('ERROR %d returned from xdotool search, ignoring it.\n' % result.returncode)
            continue

        # Parse the list of window IDs

        for window_id in result.stdout.split('\n'):
            if window_id:
                # Get the window name

                names = subprocess.run(['xdotool', 'getwindowname', window_id], stdout=subprocess.PIPE, universal_newlines=True)

                if result.returncode:
                    sys.stderr.write('ERROR %d returned from xdotool getwindowname, ignoring it.\n' % result.returncode)
                    return

                name = names.stdout.split('\n')[0].strip()

                if name:
                    # If it matches an entry in the list then rename it

                    for entry in RENAMES:
                        new_name = re.sub(entry[0], entry[1], name)

                        if new_name != name:
                            print('%s -> %s' % (name, new_name))
                            subprocess.run(['wmctrl', '-i', '-r', window_id, '-N', new_name])
                            if result.returncode:
                                sys.stderr.write('ERROR %d returned from wmctrl set_window, ignoring it.\n' % result.returncode)

                            break

################################################################################

def window_rename():
    """Entry point"""
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    window_rename()
