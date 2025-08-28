#! /usr/bin/env python3

################################################################################
""" Copy a directory full of pictures to a destination, creating subdiretories
    with N pictures in each in the destination directory
"""
################################################################################

import os
import glob
import argparse

from PIL import Image

################################################################################
# Constants

DEFAULT_SOURCE_DIR = '/storage/Starred Photos/'
DEFAULT_DEST_DIR = '/media/jms/48A7-BE16'
DEFAULT_MAX_SIZE = 3840

################################################################################

def parse_command_line():
    """ Parse the command line """

    parser = argparse.ArgumentParser(description='Copy a collection of pictures to a set of numbered directories')

    parser.add_argument('--pics', type=int, help='Number of pictures per directory (default is not to use numbered subdirectories)', default=None)
    parser.add_argument('--max-size', type=int, help='Maximum size for each image in pixels (default=%d, images will be resized if larger)' %
                        DEFAULT_MAX_SIZE, default=DEFAULT_MAX_SIZE)
    parser.add_argument('source', nargs=1, help='Source directory', default=DEFAULT_SOURCE_DIR)
    parser.add_argument('destination', nargs=1, help='Destination directory', default=DEFAULT_DEST_DIR)

    args = parser.parse_args()

    return args

################################################################################

def copy_images(args):
    """ Copy the images """

    dir_num = -1

    pictures = glob.glob(os.path.join(args.source[0], '*'))
    dest_dir = args.destination[0]

    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir)

    for index, picture in enumerate(pictures):
        picture_name = os.path.basename(picture)

        # Create the new directory in the destination every N pcitures

        if args.pics and index % args.pics == 0:
            dir_num += 1
            dest_dir = os.path.join(args.destination[0], '%05d' % dir_num)
            if not os.path.isdir(dest_dir):
                os.makedirs(dest_dir)

        print('%d/%d: Copying %s to %s' % (index + 1, len(pictures), picture, dest_dir))

        # Resize the image if neccessary

        image = Image.open(picture)

        if args.max_size and (image.width > args.max_size or image.height > args.max_size):
            if image.width > image.height:
                scale = image.width / args.max_size
            else:
                scale = image.height / args.max_size

            new_size = (round(image.width / scale), round(image.height / scale))

            print('    Resizing from %d x %d to %d x %d' % (image.width, image.height, new_size[0], new_size[1]))

            image.resize(new_size)

        # Write the image

        destination = os.path.join(dest_dir, picture_name)

        image.save(destination)

################################################################################

def splitpics():
    """Entry point"""

    args = parse_command_line()

    copy_images(args)

################################################################################

if __name__ == '__main__':
    splitpics()
