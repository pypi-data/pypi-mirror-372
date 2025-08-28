#!/usr/bin/env python3
"""Hash photos to find closely-similar images and report them"""

import sys
import os
import pickle
import argparse

import PIL

from collections import defaultdict

from PIL import Image
import imagehash

################################################################################

def read_image_hashes(directories):
    """Read all the specfied directories and hash every picture therein"""

    hashes = defaultdict(list)

    # Walk each directory tree

    for directory in directories:
        print(f'Scanning directory tree {directory}')

        for root, _, files in os.walk(directory):
            print(f'Scanning directory {root}')

            for file in files:
                filepath = os.path.join(root, file)

                fileext = os.path.splitext(file)[1]

                if fileext.lower() not in ('.jbf', '.ini', '.xml', '.ffs_db'):
                    # Calculate the hash and store path, dimensions and file size under the hash entry in the hashes table

                    try:
                        with Image.open(filepath) as image:
                            hash_value = imagehash.average_hash(image, hash_size=12)

                            size = os.stat(filepath).st_size
                            hashes[hash_value].append({'path': filepath, 'width': image.width, 'height': image.height, 'size': size})

                    except PIL.UnidentifiedImageError:
                        sys.stderr.write(f'ERROR: Unrecognized format {filepath} (size={size})\n')

                    except OSError:
                        sys.stderr.write(f'ERROR: Unable to read {filepath} (size={size})\n')

    # Return the hash table

    return hashes

################################################################################

def main():
    """Read the hashes and report duplicates in a vaguely civilised way"""

    parser = argparse.ArgumentParser(description='Search for similar images')
    parser.add_argument('directories', nargs='*', action='store', help='Directories to search')

    args = parser.parse_args()

    if not args.directories:
        print('You must be specify at least one directory')
        sys.exit(1)

    try:
        print('Loading cached data')

        with open('photodupe.pickle', 'rb') as pickles:
            hashes = pickle.load(pickles)
    except (FileNotFoundError, EOFError):
        print('Scanning directories')

        hashes = read_image_hashes(args.directories)

    # Sort the list of hashes so that we can easily find close matches

    print('Sorting hashes')

    hash_values = sorted([str(hashval) for hashval in hashes])

    for hash_value in hash_values:
        if len(hashes[hash_value]) > 1:
            print(hash_value)
            max_len = 0
            min_size = None

            for entry in hashes[hash_value]:
                max_len = max(max_len, len(entry['path']))

                if min_size is None:
                    min_size = entry['size']
                else:
                    min_size = min(min_size, entry['size'])

                if min_size >= 1024 * 1024:
                    size_suffix = 'MiB'
                    size_div = 1024*1024

                elif min_size > 1024:
                    size_suffix = 'KiB'
                    size_div = 1024
                else:
                    size_div = 1
                    size_suffix = ''

            for entry in hashes[hash_value]:
                size = entry['size'] // size_div
                print(f'    {entry["path"]:{max_len}} {size:>4} {size_suffix} ({entry["width"]}x{entry["height"]})')

    with open('photodupe.pickle', 'wb') as pickles:
        pickle.dump(hashes, pickles)

################################################################################

def photodupe():
    """Entry point"""

    try:
        main()

    except KeyboardInterrupt:
        sys.exit(1)

    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    photodupe()
