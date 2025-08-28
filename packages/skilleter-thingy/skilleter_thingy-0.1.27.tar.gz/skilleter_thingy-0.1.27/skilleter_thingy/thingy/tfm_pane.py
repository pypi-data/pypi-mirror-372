################################################################################
""" Pane class for tfm """
################################################################################

import sys
import os
import curses
import fnmatch
import stat
import glob
import time
import threading

from enum import IntEnum

if sys.platform == 'linux':
    import inotify.adapters

import thingy.dc_curses as dc_curses
import thingy.path as path
import thingy.popup as popup

################################################################################

class SortOrder(IntEnum):
    """ Sort order for filename list """

    FILENAME = 0
    EXTENSION = 1
    MODIFIED_DATE = 2
    SIZE = 3
    NUM_SORTS = 4

SORT_TYPE = ('filename', 'extension', 'modified date', 'size')

################################################################################

def inotify_wait(self):
    """Thread to wait for inotify events and post an event to the queue if there
       any create/delete/modify events in the current directory.
       Sends no more than 1 update per second to avoid drowning the recipient."""

    while True:
        trigger = False
        for event in self.ino.event_gen(yield_nones=False, timeout_s=1):
            (_, events, path, _) = event

            if path == self.current_dir and ('IN_CREATE' in events or 'IN_DELETE' in events or 'IN_MODIFY' in events):
                trigger = True

        if trigger:
            self.event_queue.put(('inotify', self.index))

################################################################################

class Pane():
    """ Class for a file manager pane """

    def __init__(self, index, num_panes, colours, event_queue):
        # Create window for the pane (dummy size and position initially)

        self.screen = curses.newwin(1, 1, 0, 0)

        self.index = index

        self.current_dir = ''

        self.ino = inotify.adapters.Inotify() if sys.platform == 'linux' else None

        self.set_current_dir(os.getcwd())

        self.event_queue = event_queue

        if sys.platform == 'linux':
            inotify_thread = threading.Thread(target=inotify_wait, args=(self,), daemon=True)
            inotify_thread.start()

        # Default sort order

        self.sort_order = SortOrder.FILENAME
        self.reverse_sort = False

        # Set the attributes of the current review (some are initialised
        # when the screen is drawn)

        # Index of the current file in the filtered_file_indices

        self.current = 0

        self.offset = 0
        self.num_panes = num_panes
        self.colours = colours

        self.searchstring = None

        self.height = self.width = -1
        self.file_list_y = 1
        self.file_list_h = -1

        # File list is a list of the files in the current directory

        self.file_list = []

        # Filtered file list is a list of the indices in file_list of the visible files
        # in the current directory

        self.filtered_file_indices = []

        # Set of the names of currently-tagged files

        self.tagged_set = set()

        self.in_filter = self.out_filter = None
        self.hide_hidden_filter = True

        self.file_display_fields = ['size', 'mtime']

        # Set up dircolor highlighting

        self.dircolours = dc_curses.CursesDircolors(reserved=self.colours['reserved_colours'])

        # Generate the list of files to be shown (takes filtering into account)

        self.update_files()

    ################################################################################

    def sort_file_list(self):
        """ Sort the file list according to the current sort order """

        if self.sort_order == SortOrder.FILENAME:
            self.file_list.sort(reverse=self.reverse_sort, key=lambda entry: (not entry['isdir'], os.path.basename(entry['name'])))
        elif self.sort_order == SortOrder.EXTENSION:
            self.file_list.sort(reverse=self.reverse_sort, key=lambda entry: (not entry['isdir'], entry['name'].split('.')[-1]))
        elif self.sort_order == SortOrder.MODIFIED_DATE:
            self.file_list.sort(reverse=self.reverse_sort, key=lambda entry: (not entry['isdir'], entry['mtime']))
        elif self.sort_order == SortOrder.SIZE:
            self.file_list.sort(reverse=self.reverse_sort, key=lambda entry: (not entry['isdir'], entry['size']))

    ################################################################################

    def update_files(self):
        """ Get the list of files
        """

        def file_stats(filename):
            """ Get the stats for a file """

            filestat = os.stat(filename, follow_symlinks=False)

            info = {'name': filename,
                    'mode': filestat.st_mode,
                    'uid': filestat.st_uid,
                    'gid': filestat.st_gid,
                    'size': filestat.st_size,
                    'atime': filestat.st_atime,
                    'mtime': filestat.st_mtime,
                    'ctime': filestat.st_ctime,
                    'isdir': stat.S_ISDIR(filestat.st_mode)}

            return info

        # Rebuild the file list

        self.file_list = []
        for filename in glob.glob(os.path.join(self.current_dir, '*')) + glob.glob(os.path.join(self.current_dir, '.*')):
            self.file_list.append(file_stats(filename))

        # Update the tagged file list to contain only current files

        self.tagged_set = {entry['name'] for entry in self.file_list if entry['name'] in self.tagged_set}

        # Optionally add '..' as an entry

        if self.current_dir != '/':
            self.file_list.append(file_stats('..'))

        self.sort_file_list()
        self.update_file_list()

    ################################################################################

    def update_file_list(self):
        """ Generate the file list from the list of current files with filtering
            applied if enabled """

        self.sort_file_list()

        if self.active_filters():
            self.filtered_file_indices = [i for i, entry in enumerate(self.file_list) if not self.filtered(entry)]
        else:
            self.filtered_file_indices = range(len(self.file_list))

    ################################################################################

    def active_filters(self):
        """ Return true if any filters are active """

        return self.out_filter or \
               self.in_filter or \
               self.hide_hidden_filter

    ################################################################################

    def filtered(self, entry):
        """ Return True if an entry is hidden by one or more filters """

        result = False

        if self.out_filter and fnmatch.fnmatch(entry['name'], self.out_filter):
            result = True

        elif self.in_filter and not fnmatch.fnmatch(entry['name'], self.in_filter):
            result = True

        elif self.hide_hidden_filter:
            base_name = os.path.basename(entry['name'])
            if base_name[0] == '.' and base_name != '..':
                result = True

        return result

    ################################################################################

    def constrain_display_parameters(self):
        """ Ensure that the current display parameters are within range - easier
            to do it in one place for all of them than check individually whenever we
            change any of them """

        self.current = max(min(self.current, len(self.filtered_file_indices) - 1), 0)
        self.offset = min(len(self.filtered_file_indices) - 1, max(0, self.offset))

        # Keep the current entry on-screen

        if self.current >= self.offset + self.height - 2:
            self.offset = self.current
        elif self.current < self.offset:
            self.offset = self.current

    ################################################################################

    def file_info_display(self, filename):
        """ Extract the additional file info fields displayed to the right
            of the filename """

        data = []
        for field in self.file_display_fields:
            if field == 'name':
                data.append(filename['name'])
            elif field in ('atime', 'mtime', 'ctime'):
                data.append(time.strftime('%x %X', time.gmtime(filename[field])))
            elif field == 'uid':
                pass
            elif field == 'gid':
                pass
            elif field == 'mode':
                pass
            elif field == 'size':
                data.append(str(filename[field]))

        return ' '.join(data)

    ################################################################################

    def show_file_list(self, current_pane):
        """ Draw the current page of the file list """

        for ypos in range(0, self.file_list_h):

            normal_colour = curses.color_pair(self.colours['normal'])

            if 0 <= self.offset + ypos < len(self.filtered_file_indices):
                # Work out what colour to render the file details in

                current_file = self.file_list[self.filtered_file_indices[self.offset + ypos]]

                current = self.offset + ypos == self.current

                # The text to render

                filename = os.path.basename(current_file['name'])

                data = self.file_info_display(current_file)

                name = f'/{filename}' if current_file['isdir'] else filename
                name = f'* {name}' if current_file['name'] in self.tagged_set else f'  {name}'

                if len(name) > self.width - len(data):
                    entry = name[:self.width - 3] + '...'
                else:
                    entry = name + ' ' * (self.width - len(name) - len(data)) + data

                file_colour = self.dircolours.get_colour_pair(current_file['name'], current_file['mode'])
            else:
                filename = entry = None
                current = False
                file_colour = normal_colour

            # Reverse the colours if this the cursor line

            if current and current_pane:
                file_colour |= curses.A_REVERSE
                normal_colour |= curses.A_REVERSE

            # Write the prefix, filename, and, if necessary, padding

            self.screen.move(self.file_list_y + ypos, 0)
            if entry:
                self.screen.addstr(entry, file_colour)
            else:
                self.screen.clrtoeol()

            # if len(filename) < self.width:
            #    self.screen.addstr(self.file_list_y + ypos, len(filename), ' ' * (self.width - len(filename)), normal_colour)

        current_dir = path.trimpath(self.current_dir, self.width)

        self.screen.move(0, 0)
        self.screen.attron(curses.color_pair(self.colours['status']))
        self.screen.addstr(current_dir + ' '*(self.width-len(current_dir)))

        self.screen.refresh()

        if not self.filtered_file_indices:
            with popup.PopUp(self.screen, 'All files are hidden - Press \'c\' to clear filters.', self.colours['status']):
                pass

    ################################################################################

    def filter_description(self):
        """ Return a textual description of the active filters """

        filters = []

        if self.out_filter:
            filters.append('filter-out wildcard')

        if self.in_filter:
            filters.append('filter-in wildcard')

        return ', '.join(filters)

    ################################################################################

    def clear_filters(self):
        """ Clear all filters """

        if self.out_filter or self.in_filter:
            self.out_filter = self.in_filter = None
            self.update_file_list()

    ################################################################################

    def reload_changes(self):
        """ Update the list of files in case something external has
            changed it. """

        self.update_files()

    ################################################################################

    def get_current_dir(self):
        """ Get the current directory for the pane """

        return self.current_dir

    ################################################################################

    def set_current_dir(self, directory):
        """ Set the current directory for the pane """

        if self.current_dir and self.ino:
            self.ino.remove_watch(self.current_dir)

        self.current_dir = os.path.normpath(directory)

        if self.ino:
            self.ino.add_watch(directory)

    ################################################################################

    def get_current_file(self):
        """ Get the current file for the pane """

        return self.file_list[self.filtered_file_indices[self.current]]

    ################################################################################

    def get_tagged_files(self):
        """ Get the list of tagged files, or the current file if none are tagged """

        if self.tagged_set:
            return [self.file_list[entry] for entry in self.filtered_file_indices if self.file_list[entry]['name'] in self.tagged_set]

        return [self.get_current_file()]

    ################################################################################

    def search_entry(self, searchstring):
        """ Search for the next match with the specified search string """

        for i in list(range(self.current + 1, len(self.filtered_file_indices))) + list(range(0, self.current)):
            if fnmatch.fnmatch(os.path.basename(self.file_list[self.filtered_file_indices[i]]['name']), searchstring):
                self.current = i
                break

    ################################################################################

    def search_match(self, searchstring):
        """ Search for the first match """

        self.searchstring = searchstring
        self.search_next_match()

    ################################################################################

    def search_next_match(self):
        """ Search for the next match with the current search string """

        self.search_entry(self.searchstring)

    ################################################################################

    def move_end(self):
        """ Move to the end of the file list """

        self.current = len(self.filtered_file_indices) - 1

    ################################################################################

    def move_top(self):
        """ Move to the top of the file list """

        self.current = self.offset = 0

    ################################################################################

    def move_to_file(self, filename):
        """ Move to the specified file (if it exists) in the current directory
            or to the top if not """

        self.current = self.offset = 0
        if filename:
            self.search_entry(filename)

    ################################################################################

    def move(self, delta):
        """ Move up or down the file list """

        self.current += delta

    ################################################################################

    def filter_out(self, filter_out):
        """ Set an exclusion filter """

        self.out_filter = filter_out
        self.in_filter = None
        self.update_file_list()

    ################################################################################

    def filter_in(self, filter_in):
        """ Set an inclusion filter """

        self.in_filter = filter_in
        self.out_filter = None
        self.update_file_list()

    ################################################################################

    def move_page_down(self):
        """ Page down """

        pos = self.current - self.offset
        self.offset += self.file_list_h - 1
        self.current = self.offset + pos

    ################################################################################

    def move_page_up(self):
        """ Page up """

        pos = self.current - self.offset
        self.offset -= self.file_list_h - 1
        self.current = self.offset + pos

    ################################################################################

    def set_sort_order(self, value):
        """ Set the sort order """

        self.sort_order = (self.sort_order + value) % SortOrder.NUM_SORTS

        self.update_sort()

    ################################################################################

    def get_sort_order(self):
        """ Get the current sort order """

        return self.sort_order

    ################################################################################

    def sort_type_msg(self):
        """ Return a textual explanation of the current sort type """

        if self.reverse_sort:
            msg = f'Reverse-sorting by {SORT_TYPE[self.sort_order]}'
        else:
            msg = f'Sorting by {SORT_TYPE[self.sort_order]}'

        return msg

    ################################################################################

    def reverse_sort_order(self):
        """ Reverse the sort order """

        self.reverse_sort = not self.reverse_sort
        self.update_sort()

    ################################################################################

    def update_sort(self):
        """ Update the sort """

        msg = self.sort_type_msg()

        with popup.PopUp(self.screen, msg, self.colours['status']):
            self.update_file_list()

    ################################################################################

    def set_pane_coords(self, y, x, height, width):
        """ Set the pane height given the pane display area """

        pane_width = width//self.num_panes

        self.height = height
        self.file_list_h = height-1
        self.width = pane_width-1  # TODO: Why '-1'?
        self.screen.resize(height, pane_width)
        self.screen.mvwin(y, x + pane_width*self.index)

    ################################################################################

    def tag_current(self):
        """ Tag the current entry (unless it is '..') """

        current = self.file_list[self.filtered_file_indices[self.current]]['name']

        if current != '..':
            if current in self.tagged_set:
                self.tagged_set.remove(current)
            else:
                self.tagged_set.add(current)

    ################################################################################

    def untag(self, wildcard=None):
        """ Tag all, or selected tagged items """

        if wildcard:
            remove_tags = set()
            for entry in self.tagged_set:
                if fnmatch.fnmatch(self.filtered_file_indices[entry], wildcard):
                    remove_tags.add(entry)

                self.tagged_set -= remove_tags
        else:
            self.tagged_set = set()

    ################################################################################

    def get_hidden_visibility(self):
        """ Return the current state of hidden file visibility """

        return not self.hide_hidden_filter

    ################################################################################

    def set_hidden_visibility(self, state=False):
        """ Set the visibility of hidden files """

        self.hide_hidden_filter = not state

        change_txt = 'Hiding' if self.hide_hidden_filter else 'Showing'

        with popup.PopUp(self.screen, f'{change_txt} hidden files', self.colours['status']):
            self.update_file_list()
