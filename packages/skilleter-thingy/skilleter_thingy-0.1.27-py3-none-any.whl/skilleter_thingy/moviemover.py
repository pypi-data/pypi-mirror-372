#! /usr/bin/env python3

""" Search for files matching a wildcard in a directory tree and move them to an
    equivalent location in a different tree """

import argparse
import os
import sys
import glob
import pathlib
import shutil
import filecmp

################################################################################

def error(msg, status=1):
    """ Exit with an error message """

    print(msg)

    sys.exit(status)

################################################################################

def parse_command_line():
    """ Handle command line arguments """

    parser = argparse.ArgumentParser(description='File relocation - move files by wildcard from one directory tree to another')

    parser.add_argument('--source', '-s', type=str, required=True, help='Source directory')
    parser.add_argument('--destination', '-d', type=str, required=True, help='Destination directory')
    parser.add_argument('--dry-run', '-D', action='store_true', help='Report what files would be moved, without actually moving them')
    parser.add_argument('files', nargs='*', help='List of wildcard matches')

    args = parser.parse_args()

    if not args.files:
        print('You must specify at least one wildcard/regex parameter')

    if not os.path.isdir(args.source):
        error(f'{args.source} is not a directory')

    if not os.path.isdir(args.destination):
        error(f'{args.destination} is not a directory')

    args.source_path = pathlib.Path(os.path.realpath(args.source))
    args.destination_path = pathlib.Path(os.path.realpath(args.destination))

    if args.source_path == args.destination_path:
        error('Source and destination paths cannot be the same')

    if args.source_path in args.destination_path.parents:
        error('The destination directory cannot be within the source path')

    if args.destination_path in args.source_path.parents:
        error('The source directory cannot be within the destination path')

    return args

################################################################################

def main():
    """ Entry point """

    args = parse_command_line()

    # Process each wildcard

    for wild in args.files:
        # Find matching files in the source tree

        for source_file in args.source_path.glob(f'**/{wild}'):
            # Ignore anything that isn't a file

            if source_file.is_file():
                # Determine where to put it

                dest_file = args.destination_path / source_file.relative_to(args.source_path)

                if dest_file.exists():

                    if filecmp.cmp(source_file, dest_file, shallow=False):
                        print(f'Destination file {dest_file} already exists and is identical, so deleting source')
                        if not args.dry_run:
                            os.unlink(source_file)
                    else:
                        print(f'Destination file {dest_file} already exists and is DIFFERENT')
                else:
                    # If the destination directory doesn't exist, then create it

                    if not dest_file.parent.is_dir():
                        print(f'Creating directory {dest_file.parent}')

                        if not args.dry_run:
                            dest_file.parent.mkdir(parents=True, exist_ok=True)

                    # Move the file

                    print(f'Moving {source_file.name} to {dest_file.parent}')

                    if not args.dry_run:
                        try:
                            shutil.move(source_file, dest_file)
                        except PermissionError:
                            print(f'WARNING: Permissions error moving {source_file}')

                    # Delete the source directory if it is not empty

                    source_dir = os.path.dirname(source_file)

                    if not glob.glob(source_dir, recursive=True):
                        print('Deleting directory "{source_dir}"')
                        if not args.dry_run:
                            os.path.unlink(source_dir)

################################################################################

def moviemover():
    """Entry point"""

    try:
        main()

    except KeyboardInterrupt:
        sys.exit(1)

    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    moviemover()
