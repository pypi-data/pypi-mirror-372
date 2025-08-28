#! /usr/bin/env python3

"""
Wrapper for the borg backup command

Copyright (C) 2018 John Skilleter

TODO: Major tidy-up as this is a translation of a Bash script.
TODO: Merge with the usb-backup script since both do almost the same job
TODO: Default configuration file should be named for the hostname
TODO: Move all configuration data into the configuration file
"""

################################################################################
# Imports

import sys
import os
import time
import argparse
import configparser
import subprocess
from pathlib import Path

################################################################################
# Variables

DEFAULT_CONFIG_FILE = Path('borger.ini')

COMMANDS = ('backup', 'mount', 'umount', 'compact', 'info', 'prune', 'check', 'init')

# TODO: NOT USED
PRUNE_OPTIONS = [
    '--keep-within', '7d',
    '--keep-daily', '30',
    '--keep-weekly', '26',
    '--keep-monthly', '24',
    '--keep-yearly', '10',
]

################################################################################

def run(args, cmd):
    """Run a subprocess."""

    if args.debug:
        cmd_str = ' '.join(cmd)
        print(f'Running "{cmd_str}"')

    try:
        return subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print('Borg backup is not installed')
        sys.exit(1)

################################################################################

def borg_backup(args, exclude_list):
    """Perform a backup."""

    create_options = ['--compression', 'auto,lzma']

    version = time.strftime('%Y-%m-%d-%H:%M:%S')

    print(f'Creating backup version {version}')

    if args.verbose:
        create_options += ['--list', '--filter=AMC']

    if args.dryrun:
        create_options.append('--dry-run')
    else:
        create_options.append('--stats')

    exclude_opts = []

    if exclude_list:
        for exclude in exclude_list:
            exclude_opts += ['--exclude', exclude]

    os.chdir(args.source)

    run(args,
        ['borg'] + args.options + ['create', f'{str(args.destination)}::{version}', str(args.source)] + create_options +
        ['--show-rc', '--one-file-system', '--exclude-caches'] + exclude_opts)

################################################################################

def borg_prune(args):
    """Prune the repo by limiting the number of backups stored."""

    print('Pruning old backups')

    # Keep all backups for at least 7 days, 1 per day for 30 days, 1 per week for 2 years
    # 1 per month for 4 years and 1 per year for 10 years.

    run(args, ['borg'] + args.options + ['prune', str(args.destination)] + PRUNE_OPTIONS)

################################################################################

def borg_compact(args):
    """Compact the repo."""

    print('Compacting the backup')

    # Keep all backups for at least 7 days, 1 per day for 30 days, 1 per week for 2 years
    # 1 per month for 4 years and 1 per year for 10 years.

    run(args, ['borg'] + args.options + ['compact', str(args.destination)])

################################################################################

def borg_info(args):
    """Info."""

    run(args, ['borg'] + args.options + ['info', str(args.destination)])

################################################################################

def borg_mount(args):
    """Mount."""

    print(f'Mounting Borg backups at {args.mount_dir}')

    mount = Path(args.mount_dir)

    if not mount.is_dir():
        mount.mkdir()

    run(args, ['borg'] + args.options + ['mount', str(args.destination), str(mount)])

################################################################################

def borg_umount(args):
    """Unmount."""

    print('Unmounting {args.mount}')

    run(args, ['borg'] + args.options + ['umount', str(args.mount)])

################################################################################

def borg_check(args):
    """Check the status of a backup."""

    run(args, ['borg'] + args.options + ['check', str(args.destination)])

################################################################################

def borg_init(args):
    """Initialise a backup."""

    run(args, ['borg'] + args.options + ['init', str(args.destination), '--encryption=none'])

################################################################################

def process_excludes(exclude_data):
    """Process the include list from the configuration file."""

    return exclude_data.replace('%', str(Path.cwd())).split('\n')

################################################################################

def main():
    """Entry point."""

    command_list = ', '.join(COMMANDS)

    parser = argparse.ArgumentParser(description='Wrapper app for Borg backup to make it easier to use')
    parser.add_argument('--dryrun', '--dry-run', '-D', action='store_true', help='Dry-run comands')
    parser.add_argument('--debug', '-d', action='store_true', help='Debug')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbosity to the maximum')
    parser.add_argument('--config', '-c', default=None, help='Specify the configuration file')
    parser.add_argument('commands', nargs='+', help=f'One or more commands ({command_list})')
    args = parser.parse_args()

    # If no config file specified then look in all the usual places

    if args.config:
        args.config = Path(args.config)
    elif DEFAULT_CONFIG_FILE.is_file():
        args.config = DEFAULT_CONFIG_FILE
    else:
        args.config = Path.home() / DEFAULT_CONFIG_FILE

        if not args.config.is_file():
            args.config = Path(sys.argv[0]).parent / DEFAULT_CONFIG_FILE

    # Check that the configuration file exists

    if not args.config.is_file():
        print(f'Configuration file "{args.config}" not found')
        sys.exit(1)

    # Default options

    args.options = []

    # Read the configuration file

    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read(args.config)

    if 'borger' not in config:
        print('Invalid configuration file "args.config"')
        sys.exit(1)

    exclude = process_excludes(config['borger']['exclude']) if 'exclude' in config['borger'] else []

    if 'prune' in config['borger']:
        # TODO: Stuff
        print('Parser for the prune option is not implemented yet')
        sys.exit(1)

    if 'destination' in config['borger']:
        args.destination = config['borger']['destination']
    else:
        print('Destination directory not specified')
        sys.exit(1)

    if 'source' in config['borger']:
        args.source = Path(config['borger']['source'])
    else:
        print('Source directory not specified')
        sys.exit(1)

    # Initialise if necessary

    if args.debug:
        args.options.append('--verbose')

    if args.verbose:
        args.options.append('--progress')

    # Decide what to do

    for command in args.commands:
        if command == 'backup':
            borg_backup(args, exclude)
        elif command == 'mount':
            borg_mount(args)
        elif command == 'umount':
            borg_umount(args)
        elif command == 'info':
            borg_info(args)
        elif command == 'prune':
            borg_prune(args)
        elif command == 'check':
            borg_check(args)
        elif command == 'init':
            borg_init(args)
        elif command == 'compact':
            borg_compact(args)
        else:
            print(f'Unrecognized command: {command}')
            sys.exit(2)

################################################################################

def borger():
    """Entry point"""

    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    borger()
