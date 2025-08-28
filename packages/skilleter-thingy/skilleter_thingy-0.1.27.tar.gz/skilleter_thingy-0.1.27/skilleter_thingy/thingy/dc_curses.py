#! /usr/bin/env python3

""" Convert colour highlighting codes from the LS_COLORS environment variable
    used by ls to curses
"""

################################################################################

import sys
import os
import glob
import fnmatch
import curses
import stat

################################################################################

class CursesDircolors:
    """ Convert dircolors codes to curses colours """

    # Convert standard foreground and background codes to curses equivalents

    ANSI_CONVERT_FORE = {
        30: curses.COLOR_BLACK,
        31: curses.COLOR_RED,
        32: curses.COLOR_GREEN,
        33: curses.COLOR_YELLOW,
        34: curses.COLOR_BLUE,
        35: curses.COLOR_MAGENTA,
        36: curses.COLOR_CYAN,
        37: curses.COLOR_WHITE,
    }

    ANSI_CONVERT_BACK = {
        40: curses.COLOR_BLACK,
        41: curses.COLOR_RED,
        42: curses.COLOR_GREEN,
        43: curses.COLOR_YELLOW,
        44: curses.COLOR_BLUE,
        45: curses.COLOR_MAGENTA,
        46: curses.COLOR_CYAN,
        47: curses.COLOR_WHITE,
    }

    # Convert attribute codes to their meanings
    # TODO: Attributes not handled yet

    ANSI_CONVERT_ATTR = {
        0: 0,
        1: curses.A_BOLD,
        4: curses.A_UNDERLINE,
        5: curses.A_BLINK,
        7: curses.A_BLINK,
        8: curses.A_INVIS,
    }

    # Default colour

    DEFAULT_ATTR = {'attr': [], 'fore': -1, 'back': -1}

    ################################################################################

    def __init__(self, reserved=0):
        # Create the lookup tables associating special type codes or wildcards
        # with colour pairs.

        self.colour_pairs = [[-1, -1]]

        self.wildcard_highlight = {}
        self.special_highlight = {}

        self.reserved = reserved

        self.init_ls_colours()

    ################################################################################

    def curses_alloc_pair(self, attr):
        """ Given a set of attributes return the equivalent curses colour pair,
            creating a new one if a matching one doesn't already exsit """

        # TODO: Take account of attributes as well as colours

        colours = [attr['fore'], attr['back']]

        # Get an existing colour pair that uses the same colours or create
        # a new one if one doesn't exist

        if colours in self.colour_pairs:
            pair_index = self.colour_pairs.index(colours) + self.reserved
        else:
            pair_index = len(self.colour_pairs) + self.reserved
            self.colour_pairs.append(colours)
            curses.init_pair(pair_index, attr['fore'], attr['back'])

        return pair_index

    ################################################################################

    def curses_colour(self, code):
        """ Return a cursors colour pair index for the specified dircolor colour
            code string. """

        # Default attribute

        attr = {'attr': [], 'fore': -1, 'back': -1}

        # Non-zero if processing multi-value colour code

        special = 0
        special_item = None

        # We trigger a ValueError and fail on anything that's wrong in the code

        try:
            # Split into fields and convert to integer values

            codes = [int(c) for c in code.split(';')]

            for entry in codes:
                # Process 2nd entry in a special colour sequence - must have value of 5

                if special == 1:
                    if entry != 5:
                        raise ValueError
                    special = 2

                # Process 3rd entry in a special colour sequence - must be the colour
                # code between 0 and 255

                elif special == 2:
                    if entry < 0 or entry > 255:
                        raise ValueError

                    attr[special_item] = entry
                    special = 0

                # Normal foreground colour

                elif entry in self.ANSI_CONVERT_FORE:
                    attr['fore'] = self.ANSI_CONVERT_FORE[entry]

                # Normal background colour

                elif entry in self.ANSI_CONVERT_BACK:
                    attr['back'] = self.ANSI_CONVERT_BACK[entry]

                # Special foreground colour in the form 38;5;VALUE

                elif entry == 38:
                    special = 1
                    special_item = 'fore'

                # Special background colour in the form 48;5;VALUE

                elif entry == 48:
                    special = 1
                    special_item = 'back'

                # Attribute (underline, bold, etc.)

                elif entry in self.ANSI_CONVERT_ATTR:
                    attr['attr'].append(self.ANSI_CONVERT_ATTR[entry])

                # Anything else is an error

                else:
                    raise ValueError

        except ValueError:
            print(f'Invalid colour specification: "{code}"')
            sys.exit(1)

        # Allocate a colour pair for the colour combination and return it

        return self.curses_alloc_pair(attr)

    ################################################################################

    def init_ls_colours(self):
        """ Generate tables matching special file types (fifos, sockets, etc.) and
            wildcards to curses colour pairs """

        colour_data = os.environ.get('LS_COLORS', '').split(':')

        # Iterate through the highlighters, create/get a colour pair corresponding
        # to the colour codes and save one of the tables.

        for item in colour_data:
            item = item.strip()
            if '=' in item:
                code, colour = item.split('=')

                colour_pair = self.curses_colour(colour)

                if len(code) == 2 and '*' not in code and '.' not in code:
                    self.special_highlight[code] = colour_pair
                else:
                    self.wildcard_highlight[code] = colour_pair

    ################################################################################

    def get_colour(self, filename, filemode=None):
        """ Get the curses colour for a filename, returns 0 if no highlighting
            is needed """

        if filemode:
            if stat.S_ISDIR(filemode):
                if 'di' in self.special_highlight:
                    return self.special_highlight['di']
            elif stat.S_ISLNK(filemode):
                destfile = os.readlink(filename)

                if os.path.exists(destfile):
                    if 'ln' in self.special_highlight:
                        return self.special_highlight['ln']
                elif 'or' in self.special_highlight:
                    return self.special_highlight['or']

            elif stat.S_ISBLK(filemode):
                if 'bd' in self.special_highlight:
                    return self.special_highlight['bd']
            elif stat.S_ISCHR(filemode):
                if 'cd' in self.special_highlight:
                    return self.special_highlight['cd']

            if filemode & stat.S_IXUSR:
                if 'ex' in self.special_highlight:
                    return self.special_highlight['ex']

        for entry in self.wildcard_highlight:
            if fnmatch.fnmatch(filename, entry):
                colour = self.wildcard_highlight[entry]
                break
        else:
            colour = 0

        return colour

    ################################################################################

    def get_colour_pair(self, filename, filemode=None):
        """ Get the curses colour pair for a filename, optionally specifying the
            file mode (as per os.stat()) """

        return curses.color_pair(self.get_colour(filename, filemode))

################################################################################

def _test_code(stdscr):
    """ Entry point """

    curses.start_color()
    curses.use_default_colors()

    # Initialise colours

    dc = CursesDircolors()

    # Demo code to list files specified by the first command line argument
    # highlighted appropriately

    y = 0
    for filename in glob.glob(sys.argv[1]):
        colour = dc.get_colour(filename)

        stdscr.addstr(y, 0, filename, curses.color_pair(colour))

        y += 1
        if y > 30:
            break

    stdscr.getch()

################################################################################

if __name__ == "__main__":
    curses.wrapper(_test_code)
