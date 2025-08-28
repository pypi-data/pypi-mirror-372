################################################################################
""" Curses-based pop-up message

Usage:
    with PopUp(curses_screen, message, colour):
        do_stuff

Popup message is displayed for the duration of the with statement, and
has optional parameters to wait for a keypress, and/or pause before removing
the popup again.

"""
################################################################################

import time
import curses

################################################################################

class PopUp():
    """ Class to enable popup windows to be used via with statements """

    def __init__(self, screen, msg, colour, waitkey=False, sleep=True, centre=True, refresh=True):
        """ Initialisation - just save the popup parameters """

        self.panel = None
        self.screen = screen
        self.msg = msg
        self.centre = centre
        self.colour = curses.color_pair(colour)
        self.refresh = refresh
        self.sleep = sleep and not waitkey
        self.waitkey = waitkey
        self.start_time = 0

    def __enter__(self):
        """ Display the popup """

        lines = self.msg.split('\n')
        height = len(lines)

        width = 0
        for line in lines:
            width = max(width, len(line))

        width += 2
        height += 2

        size_y, size_x = self.screen.getmaxyx()

        window = curses.newwin(height, width, (size_y - height) // 2, (size_x - width) // 2)
        self.panel = curses.panel.new_panel(window)

        window.bkgd(' ', self.colour)
        for y_pos, line in enumerate(lines):
            x_pos = (width - len(line)) // 2 if self.centre else 1
            window.addstr(y_pos + 1, x_pos, line, self.colour)

        self.panel.top()
        curses.panel.update_panels()
        self.screen.refresh()

        self.start_time = time.monotonic()

        if self.waitkey:
            while True:
                keypress = self.screen.getch()
                if keypress != curses.KEY_RESIZE:
                    break

                curses.panel.update_panels()
                self.screen.refresh()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """ Remove the popup """

        if self.panel:
            if self.sleep:
                elapsed = time.monotonic() - self.start_time

                if elapsed < 1:
                    time.sleep(1 - elapsed)

            del self.panel

        if self.refresh:
            self.screen.refresh()
