#! /usr/bin/env python3

""" Perform various tidying operations on a directory full of photos:
    1. Remove leading '$' and '_' from filenames
    2. Move files in hidden directories up 1 level
    3. If the EXIF data in a photo indicates that it was taken on date that
       doesn't match the name of the directory it is stored in (in YYYY-MM-DD format)
       then it is moved to the correct directory, creating it if necessary.

    All move/rename operations are carried out safely with the file being moved having
    a numeric suffix added to the name if it conflicts with an existing file.

    TODO: Ignore .stversions files

"""

################################################################################

import argparse
import os
import sys
import pathlib
import re

from PIL import UnidentifiedImageError
from PIL import Image
from PIL.ExifTags import TAGS

import thingy.colour as colour

################################################################################

FILE_TYPES = ('.jpg', '.jpeg')

DATE_RE = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}')

NUMBER_RE = re.compile(r'(.*) +\([0-9]+\).*')

################################################################################

def error(msg, status=1):
    """ Exit with an error message """

    print(msg)

    sys.exit(status)

################################################################################

def parse_command_line():
    """ Handle command line arguments """

    parser = argparse.ArgumentParser(description='Re-organise photos into (hopefully) the correct folders.')

    parser.add_argument('--dry-run', '-D', action='store_true', help='Report what files would be moved, without actually moving them')
    parser.add_argument('path', nargs=1, help='Path to the picture storage directory')

    args = parser.parse_args()

    if not os.path.isdir(args.path[0]):
        error(f'{args.path} is not a directory')

    args.path = pathlib.Path(os.path.realpath(args.path[0]))

    return args

################################################################################

def safe_rename(args, source_file, new_name):
    """ Rename a file, adding a numeric suffix to avoid overwriting anything """

    # If the destination file exists, add a numeric suffix to the new name
    # until we find one that doesn't

    index = 1
    new_name_stem = new_name.stem

    while new_name.exists():
        new_name = new_name.with_name(f'{new_name_stem}-{index}{new_name.suffix}')
        index += 1

    colour.write(f'Rename [BLUE:{source_file}] to [BLUE:{new_name}]')

    # Panic if the destination parent directory exists, but isn't actually a directory

    if new_name.parent.exists and not new_name.parent.is_dir:
        colour.write('[RED:WARNING]: Destination [BLUE:{new_name.parent}] exists, but is not a directory - [BLUE:{source_file}] will not be renamed')
        return source_file

    # Rename and return the new namem, creating the directory for it to go in, if necessary

    if not args.dry_run:
        new_name.parent.mkdir(parents=True, exist_ok=True)

        source_file.rename(new_name)

    return new_name

################################################################################

def get_exif_date(source_file):
    """ Try an extract the daste when the photo was taken from the EXIF data
        and return it in YYYY/YYYY-MM-DD format as the subdirectory where
        the photo should be located """

    # Get the EXIF data

    try:
        photo = Image.open(source_file)
    except (OSError, UnidentifiedImageError):
        colour.write(f'[RED:ERROR]: [BLUE:{source_file}] does not appear to be a valid image - ignoring EXIF data')
        return None

    exif = photo.getexif()

    # Search for the original date/time tag

    for tag_id in exif:
        tag = TAGS.get(tag_id, tag_id)

        if tag == 'DateTimeOriginal':
            data = exif.get(tag_id)
            if isinstance(data, bytes):
                data = data.decode()

            # Ignore dummy value

            if data.startswith('0000:00:00'):
                return None

            # Convert to YYYY-MM-DD format, removing the time

            date = f'{int(data[0:4]):04}-{int(data[5:7]):02}-{int(data[8:10]):02}'

            return date

    # No date tag found

    return None

################################################################################

def fix_file(args, source_file):
    """ Fix a file by moving or renaming it to fix naming or directory issues """

    # Get the image date from the EXIF data

    image_date = get_exif_date(source_file)

    # If the file starts with $, ~, _ or ., rename it to remove it

    while source_file.name[0] in ('$', '~', '_', '.'):
        new_name = source_file.with_name(source_file.name[1:])

        source_file = safe_rename(args, source_file, new_name)

    # If filename contains '~' then truncate it

    if '~' in source_file.name:
        new_name = source_file.with_name(source_file.name.split('~')[0] + source_file.suffix)

        source_file = safe_rename(args, source_file, new_name)

    # If the directory name starts with . or $ move the file up 1 level

    while source_file.parts[-2][0] in ('$', '.'):
        new_name = source_file.parent.parent / source_file.name

        source_file = safe_rename(args, source_file, new_name)

    # If the filename has a number in parentheses, then remove it

    num_match = NUMBER_RE.fullmatch(source_file.stem)
    if num_match:
        new_name = source_file.parent / (num_match.group(1) + source_file.suffix)

        source_file = safe_rename(args, source_file, new_name)

    # See if the date in the EXIF data matches the directory name prefix
    # and move it to the correct location if it doesn't

    if image_date:
        image_year = image_date.split('-')[0]

        image_path = args.path / image_year / image_date

        # If the file isn't already in a directory with the correct year and date
        # move it to one that it

        if not str(source_file.parent).startswith(str(image_path)):
            # If the source directory has a description after the date, append that
            # to the destination directory
            # Otherwise, if the source directory doesn't have a date, append the whole
            # directory name.

            source_parent_dir = source_file.parts[-2]

            if DATE_RE.match(source_parent_dir):
                if len(source_parent_dir) > 10:
                    image_path = args.path / image_year / f'{image_date}{source_parent_dir[10:]}'
            else:
                image_path = args.path / image_year / f'{image_date} - {source_parent_dir}'

            source_file = safe_rename(args, source_file, image_path / source_file.name)

################################################################################

def main():
    """ Entry point """

    args = parse_command_line()

    # Disable the maximum image size in PIL

    Image.MAX_IMAGE_PIXELS = None

    # Find matching files in the source tree

    print(f'Searching {args.path} with extension matching {", ".join(FILE_TYPES)}')

    all_matches = args.path.glob('**/*')

    matches = [file for file in all_matches if file.suffix.lower() in FILE_TYPES and file.is_file()]

    print(f'Found {len(matches)} matching files')

    for source_file in matches:
        if '.stversions' not in source_file.parts:
            fix_file(args, source_file)

################################################################################

def phototidier():
    """Entry point"""

    try:
        main()

    except KeyboardInterrupt:
        sys.exit(1)

    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    phototidier()
