#! /usr/bin/env python3

################################################################################
""" Thingy file handling functions

    Copyright (C) 2017-18 John Skilleter

    High-level file access functions not provided by the Python libraries
"""
################################################################################

import os
import shutil

# TODO: Convert to use thingy.proc
import thingy.process as process

################################################################################

def is_binary_file(filename):
    """ Return True if there is a strong likelihood that the specified file
        is binary. """

    return file_type(filename, mime=True).endswith('binary')

################################################################################

def file_type(filename, mime=False):
    """ Return a textual description of the file type """

    # The file utility does not return an error if the file does not exist or
    # is not a file, so we have to do that.

    if not os.path.isfile(filename) or not os.access(filename, os.R_OK):
        raise IOError('Unable to access %s' % filename)

    cmd = ['file', '--brief']

    if mime:
        cmd.append('--mime')

    cmd.append(filename)

    return process.run(cmd)[0]

################################################################################

def format_size(size, always_suffix=False):
    """ Convert a memory/disk size into appropriately-scaled units in bytes,
        MiB, GiB, TiB as a string """

   # Keep all the maths positive

    if size < 0:
        size = -size
        sign = '-'
    else:
        sign = ''

    # Default divisor and number of decimal places output

    div = 1

    # Step through the multipliers

    for units in (' bytes' if always_suffix else '', ' KiB', ' MiB', ' GiB', ' TiB'):
        # If we can't scale up to this multiplier quit the loop

        if size // div < 1024:
            break

        # Increase the divisor and set the number of decimal places
        # to 1 (set to 0 when we don't have a divisor).

        div *= 1024
    else:
        units = ' PiB'

    # Calculate the size in 10ths so the we get the first digit after
    # the decimal point, doing all the work in the integer domain to
    # avoid rounding errors.

    size_x_10 = (size * 10) // div

    # If the decimal part would be '.0' don't output it

    if size_x_10 % 10 == 0:
        return '%s%d%s' % (sign, size_x_10 // 10, units)

    return '%s%d.%d%s' % (sign, size_x_10 // 10, size_x_10 % 10, units)

################################################################################

def backup(filename, extension='bak', copyfile=True, timestamps=True):
    """ Create a backup of a file by copying or renaming it into a file with extension
        .bak, deleting any existing file with that name.

        Copies the file by default, unless copyfile is False
        Sets the timetamps of the backup file to be the same as the original, unless
        timestamps is False."""

    # Do nothing if the file does not exist

    if not os.path.isfile(filename):
        return

    # Split on the dot characters

    filename_comp = filename.split('.')

    # Replace the extension with the specified on (or 'bak' by
    # default) or add it if the filename did not have an extension.

    if len(filename_comp) > 1:
        filename_comp[-1] = extension
    else:
        filename_comp.append(extension)

    backupname = '.'.join(filename_comp)

    # Remove any existing backup file

    if os.path.isfile(backupname):
        os.unlink(backupname)

    # Create the backup by copying or renaming the file, optionally preserving the
    # timestamp of the original file

    if timestamps:
        file_info = os.stat(filename)

    if copyfile:
        shutil.copyfile(filename, backupname)
    else:
        os.rename(filename, backupname)

    if timestamps:
        os.utime(backupname, ns=(file_info.st_atime_ns, file_info.st_mtime_ns))

################################################################################
# Test code

if __name__ == "__main__":
    print('Is /bin/sh binary:      %s' % is_binary_file('/bin/sh'))
    print('Is files.py binary:     %s' % is_binary_file('thingy/files.py'))
    print('')

    for mimeflag in (False, True):
        print('/bin/sh is:             %s' % file_type('/bin/sh', mimeflag))
        print('/bin/dash is:           %s' % file_type('/bin/dash', mimeflag))
        print('git-ca is:              %s' % file_type('git-ca', mimeflag))
        print('')

    for sizevalue in (0, 1, 999, 1024, 1025, 1.3 * 1024, 2**32 - 1, 2**64 + 2**49):
        print('%24d is %s' % (sizevalue, format_size(sizevalue)))
