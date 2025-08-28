#! /usr/bin/env python3

################################################################################
""" Find duplicate files and do things with them.

    Uses the 'jdupes' utility

    TODO: Option to ignore by filetype
    TODO: Ignore folder.jpg files

    NOTE: The option to ignore directories in jdupes doesn't work (at least in the version in Ubuntu 18.04) so we do this after searching for duplicates
"""
################################################################################

import os
import argparse
import logging
import subprocess
import sys
import re
import pickle
import copy
import fnmatch

################################################################################

ALWAYS_IGNORE_DIRS = ['.git']

################################################################################

def error(msg):
    """ Report an error and exit """

    sys.stderr.write('%s\n' % msg)
    sys.exit(1)

################################################################################

def parse_command_line():
    """ Parse the command line """

    parser = argparse.ArgumentParser(description='Find duplicate files created by SyncThing or in temporary directories in a given path')
    parser.add_argument('--debug', action='store_true', help='Debug output')
    parser.add_argument('--save', action='store', help='Save duplicate file list')
    parser.add_argument('--load', action='store', help='Load duplicate file list')
    parser.add_argument('--script', action='store', help='Generate a shell script to delete the duplicates')
    parser.add_argument('--exclude', action='append', help='Directories to skip when looking for duplicates')
    parser.add_argument('--ignore', action='append', help='Wildcards to ignore when looking for duplicates')
    parser.add_argument('path', nargs='?', default='.', help='Path(s) to search for duplicates')

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.ERROR)

    if args.save and args.load:
        error('The save and load options are mutually exclusive')

    return args

################################################################################

def jdupes(path,
           one_file_system=False,
           no_hidden=False,
           check_permissions=False,
           quick=False,
           recurse=True,
           follow_symlinks=False,
           exclude=None,
           zero_match=False):
    """ Run jdupes with the specified options """

    cmd = ['jdupes', '--quiet']

    if one_file_system:
        cmd.append('--one-file-system')

    if no_hidden:
        cmd.append('--nohidden')

    if check_permissions:
        cmd.append('--permissions')

    if quick:
        cmd.append('--quick')

    if recurse:
        cmd += ['--recurse', path]
    else:
        cmd.append(path)

    if follow_symlinks:
        cmd.append('--symlinks')

    if exclude:
        cmd += ['--exclude', exclude]

    if zero_match:
        cmd.append('--zeromatch')

    logging.debug('Running %s', ' '.join(cmd))

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except FileNotFoundError:
        error('The jdupes utility is not installed')

    results = [[]]
    for output in result.stdout.split('\n'):
        output = output.strip()

        logging.debug(output)

        if output:
            results[-1].append(output)
        else:
            results.append([])

    while results and results[-1] == []:
        results = results[:-1]

    logging.debug('Found %d duplicated files', len(results))
    for entry in results:
        logging.debug('    %s', ', '.join(entry))

    return results

################################################################################

def remove_excluded_entries(args, duplicates):
    """ Now filter out enties in the duplicates lists that are in the
        directories that we are supposed to be ignoring """

    # Build the list of directories to ignore - add the default list

    ignore_dirs = ALWAYS_IGNORE_DIRS
    if args.exclude:
        ignore_dirs += args.exclude

    # Build the list of absolute and relative paths to ignore
    # both are in the form '/path/'

    ignore_prefixes = []
    ignore_subdirs = []

    for ignore in ignore_dirs:
        if ignore[-1] != '/':
            ignore = '%s/' % ignore

        if ignore[0] == '/':
            ignore_prefixes.append(ignore)
        else:
            ignore_subdirs.append('/%s' % ignore)

    # Now remove entries from the duplicate list that are within the ignored
    # directories. If the resultant duplicate record is empty or only contains
    # one entry, then remove it.

    filtered_duplicates = []

    for duplicate in duplicates:
        # Set of entries in the record to remove

        remove_entries = set()

        for entry in duplicate:
            # If the entry is in an excluded directory tree, remove it

            for ignore in ignore_prefixes:
                if entry.startswith(ignore):
                    remove_entries.add(entry)

            # If the entry is in an excluded subdirectory tree, remove it

            for ignore in ignore_subdirs:
                if ignore in entry:
                    remove_entries.add(entry)

            # If we have a list of files to ignore then check each entry against the list
            # and remove any matches.

            for ignore in args.ignore or []:
                if fnmatch.fnmatch(os.path.basename(entry), ignore):
                    remove_entries.add(entry)

            # If we loaded a saved list and the entry doesn't exist, remove it

            if args.load and entry not in remove_entries and not os.path.isfile(entry):
                remove_entries.add(entry)

        # If we have entries to remove from the record, then remove them

        if remove_entries:
            for entry in remove_entries:
                duplicate.remove(entry)

        # Only add to the filtered duplicate list if we have more than one duplicate in the entry

        if len(duplicate) >= 2:
            filtered_duplicates.append(duplicate)

    return filtered_duplicates

################################################################################

def find_duplicates(args):
    """ Find duplicates, or load them from a saved status file """

    if args.load:
        logging.debug('Loading duplicate file data from %s', args.load)

        with open(args.load, 'rb') as infile:
            duplicates = pickle.load(infile)

        logging.debug('Data loaded, %d duplicates', len(duplicates))
    else:
        duplicates = jdupes(args.path)

    if args.save:
        logging.debug('Saving duplicate file data to %s', args.save)

        with open(args.save, 'wb') as outfile:
            pickle.dump(duplicates, outfile)

        print('Duplicate file data saved')
        sys.exit(0)

    return remove_excluded_entries(args, duplicates)

################################################################################

def check_duplicates(duplicate):
    """ Given a list of duplicate files work out what to do with them.
        Returns:
            List of files (if any) to keep
            List of files (if any) to be deleted
            Name of a file that is similar to the duplicates (both in name and content)
            True if the files being removed are .ini files with mangled names
            Any error/warning message associated with processing the duplicates
    """

    keep = set()
    remove = set()
    similar = None
    error_msg = None

    # We can just delete entries that are conflicting picasa.ini files

    for entry in duplicate:
        if re.fullmatch(r'.*/\.?[pP]icasa.sync-conflict-.*\.ini', entry):
            logging.debug('Remove picasa.ini sync conflict: %s', entry)

            remove.add(entry)

    if remove:
        for item in remove:
            duplicate.remove(item)

    ini_file_purge = (len(remove) > 0)

    # If all of the files are called 'picasa.ini' then we skip them as it is valid to have multiple picasa.ini files

    if duplicate:
        for entry in duplicate:
            if os.path.basename(entry).lower() not in ('picasa.ini', '.picasa.ini'):
                break
        else:
            print('Keeping picasa.ini files: %s' % (', '.join(duplicate)))
            duplicate = []

    # Skip other checks if we don't have any files that aren't conflicting picasa.ini files

    if duplicate:
        # Look for entries that are in known temporary directories

        for entry in duplicate:
            if re.match(r'.*/(\$RECYCLE\.BIN|.Picasa3Temp|.Picasa3Temp_[0-9]+|.picasaoriginals)/.*', entry):
                logging.debug('Removing temporary directory item: %s', entry)
                remove.add(entry)
            else:
                keep.add(entry)

        # Look for lists of copies where some are marked as copies with _X appended to the file name

        if len(keep) > 1:
            copies = set()
            originals = set()

            for entry in keep:
                if re.fullmatch(r'.*_[1-9][0-9]{0,2}\.[^/]+', entry):
                    copies.add(entry)
                else:
                    originals.add(entry)

            # If we have at least one original, then we can remove the copies

            if originals:
                if copies:
                    logging.debug('Removing copies: %s', list(copies))
                    logging.debug('Keeping originals: %s', originals)

                    remove |= copies
                    keep = originals
            else:
                error_msg = 'No originals found in %s' % (', '.join(keep))

            # Looks for lists of copies where some are marked as copies with (N) appended to the file name

            copies = set()
            originals = set()

            for entry in keep:
                if re.fullmatch(r'.*\([0-9]+\)\.[^/]+', entry):
                    copies.add(entry)
                else:
                    originals.add(entry)

            # If we have at least one original, then we can remove the copies

            if originals:
                if copies:
                    logging.debug('Removing copies: %s', list(copies))
                    logging.debug('Keeping originals: %s', originals)

                    remove |= copies
                    keep = originals
            else:
                error_msg = 'No originals found in %s' % (', '.join(keep))

        # Now look for sync conflicts

        if len(keep) > 1:
            conflicts = set()

            for entry in keep:
                if re.fullmatch(r'.*(\.sync-conflict-|/.stversions/).*', entry):
                    conflicts.add(entry)

            if conflicts:
                keep = keep.difference(conflicts)

                if keep:
                    logging.debug('Removing sync conflicts: %s', conflicts)
                    logging.debug('Keeping: %s', keep)

                    remove |= conflicts
                else:
                    logging.debug('No non-conflicting files found in %s', (', '.join(conflicts)))

                    originals = set()

                    for entry in conflicts:
                        originals.add(re.sub(r'(\.sync-conflict-[0-9]{8}-[0-9]{6}-[A-Z]{7}|/.stversions/)', '', entry))

                    if len(originals) == 1:
                        original = originals.pop()
                        if os.path.isfile(original):

                            similar = original
                            remove = conflicts

        # Now look for files that differ only by case

        if len(keep) > 1:
            # Take a copy of the set, then compare the lower case versions of the entries
            # and remove any that match
            # TODO: We only check for a match against a lower case version of the first entry

            keep_c = copy.copy(keep)
            name_lc = keep_c.pop().lower()

            for entry in keep_c:
                if entry.lower() == name_lc:
                    logging.debug('Removing duplicate mixed-case entry: %s', entry)

                    remove.add(entry)

            keep = keep.difference(remove)

        # Now look for files with '~' in the name

        if len(keep) > 1:
            tilde = set()

            for k in keep:
                if '~' in k:
                    tilde.add(k)

            if tilde != keep:
                remove |= tilde
                keep = keep.difference(tilde)

        # Now remove entries with the shorter subdirectory names

        if len(keep) > 1:
            longest = ""
            longest_name = None

            for k in sorted(list(keep)):
                subdir = os.path.split(os.path.dirname(k))[1]

                if len(subdir) > len(longest):
                    longest = subdir
                    longest_name = k

            if longest_name:
                for k in keep:
                    if k != longest_name:
                        remove.add(k)

            keep = keep.difference(remove)

        # Now remove entries with the shorter file names

        if len(keep) > 1:
            longest = ""
            longest_name = None

            for k in sorted(list(keep)):
                filename = os.path.basename(k)

                if len(filename) > len(longest):
                    longest = filename
                    longest_name = k

            if longest_name:
                for k in keep:
                    if k != filename:
                        remove.add(k)

            keep = keep.difference(remove)

        # Don't allow files called 'folder.jpg' to be removed - multiple directories can
        # have the same cover art.

        if remove:
            for r in remove:
                if os.path.basename(r) in ('folder.jpg', 'Folder.jpg', 'cover.jpg', 'Cover.jpg'):
                    keep.add(r)

            remove = remove.difference(keep)

    return sorted(list(keep)), sorted(list(remove)), similar, ini_file_purge, error_msg

################################################################################

def process_duplicates(args, duplicates):
    """ Process the duplicate file records """

    # Optionally generate the shell script

    if args.script:
        script = open(args.script, 'wt')

        script.write('#! /usr/bin/env bash\n\n'
                     '# Auto-generated shell script to delete duplicate files\n\n'
                     'set -o pipefail\n'
                     'set -o errexit\n'
                     'set -o nounset\n\n')

    # List of errors - we report everything that doesn't work at the end

    errors = []

    # Decide what to do with each duplication record

    for duplicate in duplicates:
        keep, remove, similar, ini_file_purge, error_msg = check_duplicates(duplicate)

        if error_msg:
            errors.append(error_msg)

        # Report what we'd do

        if args.script and (remove or keep):
            script.write('\n')

            for k in keep:
                script.write('# Keep %s\n' % k)

            if ini_file_purge:
                script.write('# Remove conflicting, renamed picasa.ini files\n')

            if similar:
                script.write('# Similar file: %s\n' % similar)

            for r in remove:
                r = r.replace('$', '\\$')
                script.write('rm -- "%s"\n' % r)

        if remove:
            print('Duplicates found:')

            if keep:
                print('    Keep:    %s' % (', '.join(keep)))

            if similar:
                print('    Similar: %s' % similar)

            print('    Delete:  %s' % (', '.join(remove)))

        elif keep and not remove:
            errors.append('Keeping all copies of %s' % (', '.join(keep)))

        elif len(keep) > 1:
            print('Keeping %d copies of %s' % (len(keep), ', '.join(keep)))
            print('    Whilst removing %s' % (', '.join(remove)))

        elif duplicate and remove and not keep:
            errors.append('All entries classified for removal: %s' % (', '.join(remove)))

    if errors:
        errors.sort()

        print('-' * 80)
        print('Problems:')

        for error in errors:
            print(error)

        if args.script:
            script.write('\n'
                         '# %s\n'
                         '# There are a number of duplicates where it is not clear which one should be kept,\n'
                         '# or whether all copies should be kept. These are listed below.\n'
                         '# %s\n\n' % ('-' * 80, '-' * 80))

            for error in errors:
                script.write('# %s\n' % error)

################################################################################

def rmdupe():
    """ Main function """

    try:
        args = parse_command_line()

        duplicates = find_duplicates(args)

        process_duplicates(args, duplicates)

    except KeyboardInterrupt:
        sys.exit(1)

    except BrokenPipeError:
        sys.exit(2)

################################################################################
# Entry point

if __name__ == '__main__':
    rmdupe()
