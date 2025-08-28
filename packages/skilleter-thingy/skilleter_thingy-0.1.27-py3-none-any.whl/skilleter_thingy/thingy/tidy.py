#! /usr/bin/env python3

################################################################################
""" Functions for making log files and similar more easily viewed and/or compared

    Defaults to making things readable on a light background but has the
    option to make things readable on a dark background or for removing
    colours altogether.

    Has functions for removing times, AWS ID values, colours, SHA1 values,
    Also function for making ANSI codes more readable on light or dark backgrounds

    Currently this is very cude and needs to be a lot more cleverer.

    TODO: Handle multiple colour changes in a single ANSI sequence
    TODO: Take account of the background colour when determining how to change the foreground colour
    TODO: More colour conversions (currently only converts bright yellow on white to dark yellow)
    TODO: Handle 256 colour codes
    TODO: More time formats
"""
################################################################################

import re

################################################################################
# Regular expressions

# Match an ANSI colour control sequence

ANSI_REGEXES = [
    re.compile(r'\x1b\[([0-9][0-9;]*)*m'),
    re.compile(r'\x1b\[m'),
    re.compile(r'\x1b\[[0-9][A-Z]'),
]

# Match and ANSI colour control sequence and capture the colour bit

RE_DEBUG = re.compile(r'\x1b(\[[0-9][0-9;]*m)')

# Colour conversions for light backgrounds

LIGHT_TABLE = [['1;33', '0;33']]

# Colour conversions for dark backgrounds

DARK_TABLE = []

# Common time formats found in log files

RE_TIME = [
    {'regex': re.compile(r'[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[.][0-9]+Z?'), 'replace': '{DATE+TIME}'},
    {'regex': re.compile(r'[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}(Z|,[0-9]+)'), 'replace': '{TIME}'},
    {'regex': re.compile(r'[0-9]{1,2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,6})?([+][0-9]{2}:[0-9]{2})?'), 'replace': '{TIME}'},

    {'regex': re.compile(r'[1-9][0-9]{3}/[0-9][0-9]?/[1-9][0-9]'), 'replace': '{DATE}'},
    {'regex': re.compile(r'[1-9][0-9]/[0-9][0-9]?/[1-9][0-9]{3}'), 'replace': '{DATE}'},
    {'regex': re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}'), 'replace': '{DATE}'},
    {'regex': re.compile(r'[0-9]{2}-[0-9]{2}-[0-9]{4}'), 'replace': '{DATE}'},

    {'regex': re.compile(r'[0-9]([.][0-9]*)*\s*(second[s]?)'), 'replace': '{ELAPSED}'},

    {'find': '{DATE} {TIME}', 'replace': '{DATE+TIME}'},
    {'regex': re.compile(r'[0-9]+m *[0-9]+s'), 'replace': '{ELAPSED}'},
]

# SHA values

RE_SHA256 = [
    {'regex': re.compile(r'[0-9a-f]{64}'), 'replace': '{SHA256}'},
]

RE_SHA1 = [
    {'regex': re.compile(r'[0-9a-f]{40}'), 'replace': '{SHA1}'},
]

# AWS ids

RE_AWS = \
    [
        {'regex': re.compile(r'eni-0[0-9a-f]{16}'), 'replace': '{ENI-ID}'},
        {'regex': re.compile(r'ami-0[0-9a-f]{16}'), 'replace': '{AMI-ID}'},
        {'regex': re.compile(r'snap-0[0-9a-f]{16}'), 'replace': '{AMI-SNAP}'},
        {'regex': re.compile(r'vol-0[0-9a-f]{16}'), 'replace': '{AMI-VOL}'},
        {'regex': re.compile(r'sir-[0-9a-z]{8}'), 'replace': '{SPOT-INSTANCE}'},
        {'regex': re.compile(r'i-0[0-9a-f]{16}'), 'replace': '{EC2-ID}'},
        {'regex': re.compile(r'request id: [0-0a-f]{8}-[0-0a-f]{4}-[0-0a-f]{4}-[0-0a-f]{4}-[0-0a-f]{12}'),
         'replace': 'request id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'},
    ]

# Data transfer speeds

RE_SPEED = \
    [
        {'regex': re.compile(r'[0-9.]+ *MB/s'), 'replace': '{SPEED}'},
        {'regex': re.compile(r'[0-9.]+ *MiB/s'), 'replace': '{SPEED}'},
    ]

################################################################################

def regex_replace(data, regexes):
    """ Do a set of regex replacements """

    for regex in regexes:
        if 'find' in regex:
            data = data.replace(regex['find'], regex['replace'])
        elif 'regex' in regex:
            data = regex['regex'].sub(regex['replace'], data)
        else:
            assert False

    return data

################################################################################

def debug_format(data):
    """ Make the ANSI colour codes in the specified string human-readable """

    return RE_DEBUG.sub('{ESC\\1}', data)

################################################################################

def convert_ansi(data, light=True):
    """ Use the conversion table to convert ANSI codes in the string for display
        on a light or dark background """

    table = LIGHT_TABLE if light else DARK_TABLE

    for entry in table:
        data = data.replace('\x1b[%s' % entry[0], '\x1b[%s' % entry[1])

    return data

################################################################################

def remove_times(data):
    """ Attempt to remove obvious time and duration references from a string """

    return regex_replace(data, RE_TIME)

################################################################################

def remove_sha1(data):
    """ Attempt to remove SHA1 references from a string """

    return regex_replace(data, RE_SHA1)

################################################################################

def remove_sha256(data):
    """ Attempt to remove SHA256 references from a string """

    return regex_replace(data, RE_SHA256)

################################################################################

def remove_aws_ids(data):
    """ Attempt to remove a variety of AWS ID references from a string """

    return regex_replace(data, RE_AWS)

################################################################################

def remove_speeds(data):
    """ Attempt to remove data transfer speed references from a string """

    return regex_replace(data, RE_SPEED)

################################################################################

def remove_ansi(text):
    """ Remove ANSI codes from a string """

    if '\x1b' in text:
        for regex in ANSI_REGEXES:
            text = regex.sub('', text)

    return text
