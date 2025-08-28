#! /usr/bin/env python3

################################################################################
""" Thingy file and directory functionality

    Copyright (C) 2017-18 John Skilleter

    Licence: GPL v3 or later
"""
################################################################################

import os
import logging

################################################################################

class PathError(Exception):
    """ Exception raised by the module """

    def __init__(self, msg):
        super(PathError, self).__init__(msg)
        self.msg = msg

################################################################################

def is_subdirectory(root_path, sub_path):
    """ Return True if sub_path is a sub-directory of root_path """

    abs_sub_path = os.path.abspath(sub_path)
    abs_root_path = os.path.abspath(root_path)

    logging.debug('root path: %s', abs_root_path)
    logging.debug('sub path : %s', abs_sub_path)

    return abs_sub_path.startswith('%s/' % abs_root_path)

################################################################################

def trimpath(full_path, trim_width):
    """ Trim a path to a specified maximum width, but always leaving the
        lowest-level directory (even if it exceeds the trim width). """

    logging.debug('Path: "%s"', full_path)
    logging.debug('Required width: %d', trim_width)

    full_path = os.path.abspath(full_path)

    # Remove any trailing '/' from the path

    if full_path != '/' and full_path[-1] == '/':
        full_path = full_path[:-1]

    # If the path starts with the user's home directory then convert the prefix
    # into a '~'

    home_dir = os.path.expanduser('~')

    if full_path == home_dir:
        full_path = '~'
        logging.debug('Converted path to "~"')

    elif is_subdirectory(home_dir, full_path):
        full_path = "~/%s" % full_path[len(home_dir) + 1:]

        logging.debug('Converted path to "%s"', full_path)

    # If the path is too long then slice it into directories and cut sub-directories
    # out of the middle until it is short enough. Always leave the last element
    # in place, even if this means total length exceeds the requirement.

    path_len = len(full_path)

    logging.debug('Path length: %d', path_len)

    # Already within maximum width, so just return it

    if path_len <= trim_width:
        return full_path

    # Split into an array of directories and trim out middle ones

    directories = full_path.split('/')

    logging.debug('Path has %d elements: "%s"', len(directories), directories)

    if len(directories) == 1:
        # If there's only one element in the path, just give up

        logging.debug('Only 1 directory in the path, leaving it as-is')

    elif len(directories) == 2:
        # If there's only two elements in the path then replace the first
        # element with '...' and give up

        logging.debug('Only 2 directories in the path, so setting the first to "..."')

        directories[0] = '...'

    else:
        # Start in the middle and remove entries to the left and right until the total
        # path length is shortened to a sufficient extent

        right = len(directories) // 2
        left = right - 1
        first = True

        while path_len > trim_width:

            path_len -= len(directories[right]) + 1

            if first:
                path_len += 4
                first = False

            if right == len(directories) - 1:
                break

            right += 1

            if path_len > trim_width:
                path_len -= len(directories[left]) + 1

                if left == 0:
                    break

                left -= 1

        logging.debug('Removing entries %d..%d from the path', left, right)

        directories = directories[0:left + 1] + ['...'] + directories[right:]

    full_path = '/'.join(directories)

    logging.debug('Calculated width is %d and actual width is %d', path_len, len(full_path))

    return full_path

################################################################################

if __name__ == '__main__':
    PARENT = '/1/2/3/5'
    CHILD = '/1/2/3/5/6'

    print('Is %s a subdirectory of %s: %s (expecting True)' % (CHILD, PARENT, is_subdirectory(PARENT, CHILD)))
    print('Is %s a subdirectory of %s: %s (expecting False)' % (PARENT, CHILD, is_subdirectory(CHILD, PARENT)))

    LONG_PATH = '/home/jms/source/womble-biscuit-token-generation-service/subdirectory'

    for pathname in (LONG_PATH, os.path.realpath('.')):
        print('Full path: %s' % pathname)

        for length in (80, 60, 40, 20, 16, 10):
            print('Trimmed to %d characters: %s' % (length, trimpath(pathname, length)))
