#! /usr/bin/env python3

################################################################################
""" Check how much free space is available on all filesystems, ignoring
    read-only filesystems, /dev and tmpfs.

    Issue a warning if any are above 90% used.
"""
################################################################################

import sys
import argparse
import psutil

################################################################################

WARNING_LEVEL = 15

################################################################################

def main():
    """ Do everything """

    parser = argparse.ArgumentParser(description='Check for filesystems that are running low on space')
    parser.add_argument('--level', action='store', type=int, default=WARNING_LEVEL,
                        help='Warning if less than this amount of space is available on any writeable, mounted filesystem (default=%d)' % WARNING_LEVEL)
    args = parser.parse_args()

    if args.level < 0 or args.level > 100:
        print('Invalid value: %d' % args.level)
        sys.exit(3)

    disks = psutil.disk_partitions()
    devices = []
    warning = []

    for disk in disks:
        if 'ro' not in disk.opts.split(',') and disk.device not in devices:
            devices.append(disk.device)
            usage = psutil.disk_usage(disk.mountpoint)

            disk_space = 100 - usage.percent

            if disk_space < args.level:
                warning.append('%s has only %2.1f%% space available' % (disk.mountpoint, disk_space))

    if warning:
        print('Filesystems with less than %d%% available space:' % args.level)
        print('\n'.join(warning))

################################################################################

def diskspacecheck():
    """Entry point"""

    try:
        main()

    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    diskspacecheck()
