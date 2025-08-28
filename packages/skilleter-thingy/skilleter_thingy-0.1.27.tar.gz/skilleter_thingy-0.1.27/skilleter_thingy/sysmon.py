#!/usr/bin/env python3

################################################################################
"""Very simple system monitoring dashboard"""
################################################################################

import sys
import datetime
import time
import curses

import psutil

################################################################################

NUM_BOXES_V = 5
NUM_BOXES_H = 2

UPDATE_PERIOD = 1

################################################################################

def show_system_load(scr, first, w, h, x, y):
    """Load averaged"""

    load = psutil.getloadavg()

    x += 2

    if first:
        scr.addstr(y+1, x, '1 minute:')
        scr.addstr(y+2, x, '5 minute:')
        scr.addstr(y+3, x, '15 minute:')
    else:
        scr.addstr(y+1, x+10, f'{load[0]:6.2f}')
        scr.addstr(y+2, x+10, f'{load[1]:6.2f}')
        scr.addstr(y+3, x+10, f'{load[2]:6.2f}')

################################################################################

def show_cpu_times(scr, first, w, h, x, y):
    """CPU times"""

    info = psutil.cpu_times()

    x += 2

    if first:
        scr.addstr(y+1, x, 'Idle:')
        scr.addstr(y+2, x, 'System:')
        scr.addstr(y+3, x, 'User:')
        scr.addstr(y+4, x, 'Nice:')

        x += w//3

        scr.addstr(y+1, x, 'I/O Wait:')
        scr.addstr(y+2, x, 'IRQ:')
        scr.addstr(y+3, x, 'Soft IRQ:')

        x += w//3

        scr.addstr(y+1, x, 'Guest:')
        scr.addstr(y+2, x, 'Guest Nice:')
    else:
        total = (info.user + info.system + info.idle + info.nice + info.iowait + info.irq + info.softirq + info.guest + info.guest_nice)/100

        user = info.user / total
        system = info.system / total
        idle = info.idle / total
        nice = info.nice / total
        iowait = info.iowait / total
        irq = info.irq / total
        softirq = info.softirq / total
        guest = info.guest / total
        guest_nice = info.guest_nice / total

        scr.addstr(y+1, x+9, f'{idle:6.2f}')
        scr.addstr(y+2, x+9, f'{system:6.2f}')
        scr.addstr(y+3, x+9, f'{user:6.2f}')
        scr.addstr(y+4, x+9, f'{nice:6.2f}')

        x += w//3

        scr.addstr(y+1, x+10, f'{iowait:6.2f}')
        scr.addstr(y+2, x+10, f'{irq:6.2f}')
        scr.addstr(y+3, x+10, f'{softirq:6.2f}')

        x += w//3

        scr.addstr(y+1, x+12, f'{guest:6.2f}')
        scr.addstr(y+2, x+12, f'{guest_nice:6.2f}')

################################################################################

def show_disk_access(scr, first, w, h, x, y):
    """Disk I/O statistics"""

    info = psutil.disk_io_counters()

    x += 2

    if first:
        scr.addstr(y+1, x, 'Read count:')
        scr.addstr(y+2, x, 'Write count:')

        scr.addstr(y+4, x, 'Read bytes:')
        scr.addstr(y+5, x, 'Write bytes:')

        x += w//3

        scr.addstr(y+1, x, 'Read time:')
        scr.addstr(y+2, x, 'Write time:')

        scr.addstr(y+4, x, 'I/O time:')

        x += w//3

        scr.addstr(y+1, x, 'Read merged:')
        scr.addstr(y+2, x, 'Write merged:')
    else:
        scr.addstr(y+1, x+14, f'{info.read_count:12}')
        scr.addstr(y+2, x+14, f'{info.write_count:12}')

        scr.addstr(y+4, x+14, f'{info.read_bytes:12}')
        scr.addstr(y+5, x+14, f'{info.write_bytes:12}')

        x += w//3

        scr.addstr(y+1, x+14, f'{info.read_time:12}')
        scr.addstr(y+2, x+14, f'{info.write_time:12}')

        scr.addstr(y+4, x+14, f'{info.busy_time:12}')

        x += w//3

        scr.addstr(y+1, x+14, f'{info.read_merged_count:12}')
        scr.addstr(y+2, x+14, f'{info.write_merged_count:12}')

################################################################################

def show_processes(scr, first, w, h, x, y):
    """TBD: Process information"""

    pass

################################################################################

def show_memory(scr, first, w, h, x, y):
    """Memory usage"""

    x += 2

    if first:
        scr.addstr(y+1, x, 'Total:')
        scr.addstr(y+2, x, 'Used:')
        scr.addstr(y+3, x, 'Buffers:')
        scr.addstr(y+4, x, 'Free:')

        x += w//3

        scr.addstr(y+1, x, 'Active:')
        scr.addstr(y+2, x, 'Inactive:')

        scr.addstr(y+4, x, 'Usage:')

        x += w//3

        scr.addstr(y+1, x, 'Shared:')
        scr.addstr(y+2, x, 'Slab:')
    else:
        meminfo = psutil.virtual_memory()
        x += 11

        scr.addstr(y+1, x, f'{meminfo.total:12}')
        scr.addstr(y+2, x, f'{meminfo.used:12}')
        scr.addstr(y+3, x, f'{meminfo.buffers:12}')
        scr.addstr(y+4, x, f'{meminfo.free:12}')

        x += w//3

        scr.addstr(y+1, x, f'{meminfo.active:12}')
        scr.addstr(y+2, x, f'{meminfo.inactive:12}')

        scr.addstr(y+4, x, f'{meminfo.percent:6.1f}%')

        x += w//3

        scr.addstr(y+1, x, f'{meminfo.shared:12}')
        scr.addstr(y+2, x, f'{meminfo.slab:12}')

################################################################################

def show_voltages(scr, first, w, h, x, y):
    """TBD: Voltages"""

    pass

################################################################################

def show_cpu_load(scr, first, w, h, x, y):
    """CPU load and frequencies"""

    info = psutil.cpu_percent(percpu=True)
    freq = psutil.cpu_freq(percpu=True)

    stats = psutil.cpu_stats()

    xo = yo = 0
    for n, cpu in enumerate(info):
        if first:
            scr.addstr(y+yo+1, x+xo+5, 'CPU #  :      % at         MHz')
        else:
            scr.addstr(y+yo+1, x+xo+10, f'{n:<2}')
            scr.addstr(y+yo+1, x+xo+14, f'{cpu:5.1f}%')
            scr.addstr(y+yo+1, x+xo+23, f'{freq[n].current:8.2f}')

        yo += 1

        if yo > h-2:
            xo += w//3
            yo = 0

    x += w//2

    if first:
        scr.addstr(y+1, x, 'Context switches:')
        scr.addstr(y+2, x, 'Interrupts:')
        scr.addstr(y+3, x, 'Soft interrupts:')
    else:
        x += 18
        scr.addstr(y+1, x, f'{stats.ctx_switches:12}')
        scr.addstr(y+2, x, f'{stats.interrupts:12}')
        scr.addstr(y+3, x, f'{stats.soft_interrupts:12}')

################################################################################

def show_swappery(scr, first, w, h, x, y):
    """Swap info"""

    x += 2

    if first:
        scr.addstr(y+1, x, 'Swap total:')
        scr.addstr(y+2, x, 'Swap used:')
        scr.addstr(y+3, x, 'Swap free:')

        x += w//3

        scr.addstr(y+1, x, 'Swap used:')

        x += w//3

        scr.addstr(y+1, x, 'Swapped in:')
        scr.addstr(y+2, x, 'Swapped out:')
    else:
        info = psutil.swap_memory()

        x += 14

        scr.addstr(y+1, x, f'{info.total:12}')
        scr.addstr(y+2, x, f'{info.used:12}')
        scr.addstr(y+3, x, f'{info.free:12}')

        x += w//3

        scr.addstr(y+1, x, f'{info.percent:6.2f}%')

        x += w//3

        scr.addstr(y+1, x, f'{info.sin:12}')
        scr.addstr(y+2, x, f'{info.sout:12}')

################################################################################

def show_network(scr, first, w, h, x, y):
    """Network statistics"""

    x += 2

    if first:
        scr.addstr(y+1, x, 'Bytes sent:')
        scr.addstr(y+2, x, 'Bytes received:')

        scr.addstr(y+4, x, 'Packets sent:')
        scr.addstr(y+5, x, 'Packets received:')

        x += w//2

        scr.addstr(y+1, x, 'Send errors:')
        scr.addstr(y+2, x, 'Receive errors:')

        scr.addstr(y+4, x, 'Outgoing dropped:')
        scr.addstr(y+5, x, 'Incoming dropped:')
    else:
        info = psutil.net_io_counters()
        x += 19

        scr.addstr(y+1, x, f'{info.bytes_sent:12}')
        scr.addstr(y+2, x, f'{info.bytes_recv:12}')

        scr.addstr(y+4, x, f'{info.packets_sent:12}')
        scr.addstr(y+5, x, f'{info.packets_recv:12}')

        x += w//2

        scr.addstr(y+1, x, f'{info.errout:12}')
        scr.addstr(y+2, x, f'{info.errin:12}')

        scr.addstr(y+4, x, f'{info.dropout:12}')
        scr.addstr(y+5, x, f'{info.dropin:12}')

################################################################################

def show_temperatures(scr, first, w, h, x, y):
    """TBD: Temperatures"""

    pass

################################################################################

# Panel title and the functions used to update them

BOXES = {
    'System Load': show_system_load,
    'Disk Access': show_disk_access,
    'Processes': show_processes,
    'Memory': show_memory,
    'Voltages': show_voltages,

    'CPU Load': show_cpu_load,
    'Swap and Paging': show_swappery,
    'Temperatures': show_temperatures,
    'Network': show_network,
    'Total CPU Times': show_cpu_times,
}

################################################################################

def main(stdscr):
    """Main function"""

    # Configure curses

    curses.curs_set(0)
    curses.start_color()
    curses.noecho()
    curses.cbreak()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_GREEN, 15)
    curses.init_pair(2, curses.COLOR_BLUE, 15)

    # Set up the display

    stdscr.keypad(1)
    stdscr.nodelay(True)
    stdscr.bkgdset(' ', curses.color_pair(0))

    # Outer loop iterates whenever the console window changes size

    terminate = False

    while not terminate:
        stdscr.clear()

        height, width = stdscr.getmaxyx()

        box_h = height // NUM_BOXES_V
        box_w = width // NUM_BOXES_H

        # Draw the titles and text on the first iteration
        # Just draw the statistics on the subsequent ones

        first_time = True
        window_resize = False

        # Inner loop just updates display until

        while not window_resize and not terminate:
            now = datetime.datetime.now()

            stdscr.addstr(0, 1, now.strftime('%02H:%02M:%02S'), curses.COLOR_BLACK)
            stdscr.addstr(0, width-11, now.strftime('%02Y-%02m-%02d'), curses.COLOR_BLACK)

            for i, box in enumerate(BOXES):
                x, y = divmod(i, NUM_BOXES_V)

                x *= box_w
                y *= box_h

                title_x = x+(box_w - len(box))//2
                stdscr.addstr(y, title_x, box, curses.A_BOLD)

                stdscr.attron(curses.color_pair(1 if first_time else 2))

                BOXES[box](stdscr, first_time, box_w, box_h, x, y+1)

            # Update the display, clear the first-time draw-static-content flag

            stdscr.refresh()
            first_time = False

            # Wait for the next update

            elapsed = (datetime.datetime.now() - now).total_seconds()

            if elapsed < UPDATE_PERIOD:
                time.sleep(UPDATE_PERIOD - elapsed)

            # Check for keypress or window resize

            keyboard = stdscr.getch()

            if keyboard in (ord('Q'), ord('q')):
                terminate = True

            elif keyboard == curses.KEY_RESIZE:
                window_resize = True

################################################################################

def sysmon():
    """Entry point"""

    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == "__main__":
    sysmon()
