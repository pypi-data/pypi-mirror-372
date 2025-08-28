#!/usr/bin/env python3

"""
Sync a directory tree full of photos into a tree organised by year, month and date
"""

# TODO: Ignore patterns for source and destination file paths (.trashed* and .stversions)
# TODO: Use inotify to detect changes and run continuously

import os
import glob
import shutil
import sys
import logging
import argparse
import re

from enum import Enum

################################################################################

# Default locations for local storage of photos and videos

DEFAULT_PHOTO_DIR = os.path.expanduser('~/Pictures')
DEFAULT_VIDEO_DIR = os.path.expanduser('~/Videos')

# File extensions (case-insensitive)

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')
VIDEO_EXTENSIONS = ('.mp4', '.mov')

# Enum of filetypes

class FileType(Enum):
    """File types"""
    IMAGE = 0
    VIDEO = 1
    UNKNOWN = 2
    IGNORE = 3

################################################################################

def error(msg, status=1):
    """Exit with an error message"""

    print(msg)
    sys.exit(status)

################################################################################

def parse_command_line():
    """Parse and validate the command line options"""

    parser = argparse.ArgumentParser(description='Sync photos from Google Photos')

    parser.add_argument('--verbose', '-v', action='store_true', help='Output verbose status information')
    parser.add_argument('--dryrun', '--dry-run', '-D', action='store_true', help='Just list files to be copied, without actually copying them')
    parser.add_argument('--picturedir', '-P', action='store', default=DEFAULT_PHOTO_DIR,
                        help=f'Location of local picture storage directory (defaults to {DEFAULT_PHOTO_DIR})')
    parser.add_argument('--videodir', '-V', action='store', default=DEFAULT_VIDEO_DIR,
                        help=f'Location of local video storage directory (defaults to {DEFAULT_VIDEO_DIR})')
    parser.add_argument('--path', '-p', action='store', default=None, help='Path to sync from')

    args = parser.parse_args()

    if not args.path:
        error('You must specify a source directory')

    # Configure debugging

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # Report parameters if verbose

    logging.debug('Source:    %s', args.path)
    logging.debug('Pictures:  %s', args.picturedir)
    logging.debug('Videos:    %s', args.videodir)
    logging.debug('Dry run:   %d', args.dryrun)

    return args

################################################################################

def get_filetype(filename):
    """Return the type of a file"""

    _, ext = os.path.splitext(filename)

    ext = ext.lower()

    if ext in IMAGE_EXTENSIONS:
        return FileType.IMAGE

    if ext in VIDEO_EXTENSIONS:
        return FileType.VIDEO

    return FileType.UNKNOWN

################################################################################

def media_sync(args):
    """Sync photos and videos from args.path to date-structured directory
       trees in args.picturedir and args.videodir.
       Assumes that the source files are in Android naming format:
           (IMG|VID)_YYYYMMDD_*.(jpg|mp4)
       Looks for a destination directory called:
           YYYY/YYYY-MM-DD*/
       If multiple destination directories exist, it uses the first one when the
       names are sorted alphbetically
       If a file with the same name exists in the destination directory it is
       not overwritten"""

    files_copied = 0

    filetype_re = re.compile(r'(PANO|IMG|VID)[-_](\d{4})(\d{2})(\d{2})[-_.].*')

    for sourcefile in [source for source in glob.glob(os.path.join(args.path, '*')) if os.path.isfile(source)]:
        filetype = get_filetype(sourcefile)

        if filetype == FileType.IMAGE:
            dest_dir = args.picturedir
        elif filetype == FileType.VIDEO:
            dest_dir = args.videodir
        else:
            logging.info('Ignoring %s - unable to determine file type', sourcefile)
            continue

        date_match = filetype_re.fullmatch(os.path.basename(sourcefile))
        if not date_match:
            logging.debug('Ignoring %s - unable to extract date from filename', sourcefile)
            continue

        year = date_match.group(2)
        month = date_match.group(3)
        day = date_match.group(4)

        default_dest_dir = f'{dest_dir}/{year}/{year}-{month}-{day}'
        dest_dir_pattern = f'{default_dest_dir}*'

        dest_dirs = [path for path in glob.glob(dest_dir_pattern) if os.path.isdir(path)]

        sourcefile_name = os.path.basename(sourcefile)

        # Search any matching destination directories to see if the file exists

        if dest_dirs:
            for dest_dir in dest_dirs:
                if os.path.isfile(os.path.join(dest_dir, sourcefile_name)):
                    break
            else:
                dest_dir = sorted(dest_dirs)[0]
        else:
            if not args.dryrun:
                os.makedirs(default_dest_dir)

            dest_dir = default_dest_dir

        dest_file = os.path.join(dest_dir, sourcefile_name)

        if os.path.exists(dest_file):
            logging.debug('Destination file %s already exists', dest_file)
        else:
            logging.info('Copying %s to %s', sourcefile, dest_file)

            if not args.dryrun:
                shutil.copyfile(sourcefile, dest_file)

            files_copied += 1

    if files_copied:
        print(f'{files_copied} files copied')

################################################################################

def localphotosync():
    """Entry point"""
    try:
        args = parse_command_line()

        media_sync(args)

    except KeyboardInterrupt:
        sys.exit(1)

    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    localphotosync()
