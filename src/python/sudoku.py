import argparse
import curses
import math
import subprocess
import sys
import time

import config
import gridutils

_WIN = None
_NODELAY = False
_SLOW = True
_RATE = .5
_ROW_PROMPT = 20
_ROW_MESSAGE = 22
_ROW_COUNTER = 21

_COLOR = 10

_COLOR_UNAVAIL      = _COLOR
_COLOR += 1
_COLOR_POSSIBLE     = _COLOR
_COLOR += 1
_COLOR_FAILED       = _COLOR
_COLOR += 1

_COLOR_NUM_MATCH    = _COLOR
_COLOR += 1
_COLOR_AREA_MATCH   = _COLOR
_COLOR += 1

_COLOR_NORM         = _COLOR
_COLOR += 1
_COLOR_SUCCESS      = _COLOR
_COLOR += 1
_COLOR_WARN         = _COLOR
_COLOR += 1
_COLOR_ERROR        = _COLOR
_COLOR += 1

c_height = 2
c_width = 4

def solve(grid, level=0):
    (r, c) = gridutils.first_empty_square(grid)

    if r is None:
        clear_message()
        draw_puzzle(grid, None, None, solved=True);
        return True

    if level == 0:
        draw_puzzle(grid, None, None);

    for num in range(1, config.SIZE + 1):
        clear_message()

        if gridutils.in_row(grid, r, num):
            grid[r][c] = num
            draw_message("Already found in row", color=_COLOR_WARN)
            draw_puzzle(grid, r, c, highlight="row", color=_COLOR_UNAVAIL, num=num);
            grid[r][c] = config.UNASSIGNED
            continue

        if gridutils.in_col(grid, c, num):
            grid[r][c] = num
            draw_message("Already found in column", color=_COLOR_WARN)
            draw_puzzle(grid, r, c, highlight="col", color=_COLOR_UNAVAIL, num=num);
            grid[r][c] = config.UNASSIGNED
            continue

        if gridutils.in_unit(grid, r, c, num):
            grid[r][c] = num
            draw_message("Already found in unit", color=_COLOR_WARN)
            draw_puzzle(grid, r, c, highlight="unit", color=_COLOR_UNAVAIL, num=num);
            grid[r][c] = config.UNASSIGNED
            continue

        grid[r][c] = num

        draw_message("Number is available", color=_COLOR_SUCCESS)
        draw_puzzle(grid, r, c, color=_COLOR_POSSIBLE, num=num);

        if solve(grid, level=level+1):
            return True

        draw_message("Number failed", color=_COLOR_ERROR)
        draw_puzzle(grid, r, c, color=_COLOR_FAILED, num=num)

        grid[r][c] = config.UNASSIGNED

    return False

def nanotime():
    return time.monotonic_ns() / 1000000000

def timed_solve(grid, quiet=False):
    if not quiet:
        print("puzz : %s" % gridutils.grid_to_str(grid))
        print("empt : %d" % gridutils.count_empty_squares(grid));

    start = nanotime()

    solved = solve(grid)

    end = nanotime()

    diff = end - start

    if not quiet:
        if solved:
            print("solu : %s" % gridutils.grid_to_str(grid))
        else:
            print("solu : none")
        print("time : %.6f" % diff)

def draw_screen():
    start_row = 0
    start_col = 0

    height = config.SIZE * c_height
    width = config.SIZE * c_width

    # lines
    for i in range(0, config.SIZE + 1):
        _WIN.hline(start_row + (i * c_height), start_col, curses.ACS_HLINE, width)
        _WIN.vline(start_row, start_col + (i * c_width), curses.ACS_VLINE, height)

    # corners
    _WIN.addch(start_row, start_col, curses.ACS_ULCORNER)
    _WIN.addch(start_row, start_col + width, curses.ACS_URCORNER)
    _WIN.addch(start_row + height, start_col, curses.ACS_LLCORNER)
    _WIN.addch(start_row + height, start_col + width, curses.ACS_LRCORNER)

    # tees
    for i in range(1, config.SIZE):
        _WIN.addch(start_row, start_col + (i * c_width), curses.ACS_TTEE)
        _WIN.addch(start_row + height, start_col + (i * c_width), curses.ACS_BTEE)
        _WIN.addch(start_row + (i * c_height), start_col, curses.ACS_LTEE)
        _WIN.addch(start_row + (i * c_height), start_col + width, curses.ACS_RTEE)

    # pluses
    for r in range(1, config.SIZE):
        for c in range(1, config.SIZE):
            _WIN.addch(start_row + (r * c_height), start_col + (c * c_width), curses.ACS_PLUS)

    # side box
    start_row = 0
    start_col = 38
    width = 30
    height = 10
    _WIN.hline(start_row, start_col, curses.ACS_HLINE, width)
    _WIN.hline(start_row + height, start_col, curses.ACS_HLINE, width)
    _WIN.vline(start_row, start_col, curses.ACS_VLINE, height)
    _WIN.vline(start_row, start_col + width, curses.ACS_VLINE, height)

    _WIN.addch(start_row, start_col, curses.ACS_ULCORNER)
    _WIN.addch(start_row, start_col + width, curses.ACS_URCORNER)
    _WIN.addch(start_row + height, start_col, curses.ACS_LLCORNER)
    _WIN.addch(start_row + height, start_col + width, curses.ACS_LRCORNER)

    attrs = curses.A_BOLD | curses.color_pair(_COLOR_NORM)
    _WIN.addstr(1, 40, "Loc:", attrs)
    _WIN.addstr(2, 40, "Num:", attrs)
    _WIN.addstr(3, 40, "Aut:", attrs)
    _WIN.addstr(4, 40, "Slo:", attrs)
    _WIN.addstr(5, 40, "Rat:", attrs)
    _WIN.addstr(6, 40, "Tim:", attrs)

def draw_prompt(color=_COLOR_NORM, message=None):
    attrs = curses.A_BOLD | curses.color_pair(color)
    _WIN.move(_ROW_PROMPT, 0)
    _WIN.clrtoeol()
    if not message:
        message = "Sudoku [ (a)uto, (s)low, (r)ate, (q)uit ] : "
    _WIN.addstr(_ROW_PROMPT, 0, message, attrs)

def draw_info(row, col, num):
    attrs = curses.A_BOLD | curses.color_pair(_COLOR_NORM)
    if row is not None and col is not None:
        _WIN.addstr(1, 45, "%d,%d" % (row + 1, col + 1), attrs)
    else:
        _WIN.addstr(1, 45, "   ", attrs)

    if num is not None:
        _WIN.addstr(2, 45, "%d" % (num), attrs)
    else:
        _WIN.addstr(2, 45, " ", attrs)

    _WIN.addstr(3, 45, "%s " % _NODELAY, attrs)
    _WIN.addstr(4, 45, "%s " % _SLOW, attrs)
    _WIN.addstr(5, 45, "%.1fs" % _RATE, attrs)

def draw_timer(num):
    attrs = curses.A_BOLD | curses.color_pair(_COLOR_NORM)
    _WIN.addstr(6, 45, "%.6f" % num, attrs)

def draw_message(message, color=_COLOR_ERROR):
    attrs = curses.A_BOLD | curses.color_pair(color)
    clear_message()
    _WIN.addstr(7, 40, message, attrs)

def clear_message():
    _WIN.addstr(7, 40, " " * 28)

def draw_puzzle(grid, row, col, highlight=None, color=_COLOR_NORM, num=None, solved=False):
    assert (row is None and col is None) or (row is not None and col is not None)
    if highlight:
        assert num

    global _NODELAY
    global _SLOW
    global _RATE

#    if gridutils.count_empty_squares(grid) < 3:
#        _NODELAY = False
#        _WIN.nodelay(_NODELAY)

    draw_info(row, col, num)

    start_row = 1
    start_col = 1

    for r in range(config.SIZE):
        for c in range(config.SIZE):
            if grid[r][c]:
                s = " %d " % grid[r][c]
            else:
                s = "   "

            attrs = 0

            if row is None and col is None:
                # no cell specified
                attrs = curses.A_BOLD | curses.color_pair(_COLOR_NORM)

            elif r == row and c == col:
                # matching cell
                attrs = curses.A_BOLD | curses.color_pair(color)

            elif highlight == "row" and r == row:
                # matching row
                if grid[r][c] == num:
                    attrs = curses.A_BOLD | curses.color_pair(_COLOR_NUM_MATCH)
                else:
                    attrs = curses.A_BOLD | curses.color_pair(_COLOR_AREA_MATCH)

            elif highlight == "col" and c == col:
                # matching col
                if grid[r][c] == num:
                    attrs = curses.A_BOLD | curses.color_pair(_COLOR_NUM_MATCH)
                else:
                    attrs = curses.A_BOLD | curses.color_pair(_COLOR_AREA_MATCH)

            elif highlight == "unit":
                (unitr, unitc) = gridutils.get_unit(row, col)
                if r in unitr and c in unitc:
                    # matching unit
                    if grid[r][c] == num:
                        attrs = curses.A_BOLD | curses.color_pair(_COLOR_NUM_MATCH)
                    else:
                        attrs = curses.A_BOLD | curses.color_pair(_COLOR_AREA_MATCH)

            else:
                # cell not matched
                attrs = curses.A_BOLD | curses.color_pair(_COLOR_NORM)
                
            _WIN.addstr(start_row + (r * c_height), start_col + (c * c_width), s, attrs)

    if solved:
        draw_prompt(message="Finished - hit any key to exit... ", color=_COLOR_SUCCESS)
        anykey()
        return

    start = nanotime()
    while True:
        draw_prompt()

        ch = _WIN.getch()

        end = nanotime()
        diff = end - start

        draw_timer(end)

        if ch == -1:
            # timed out waiting for key
            if (_SLOW and (diff > _RATE)) or not _SLOW:
                break
            else:
                time.sleep(.1)
    
        elif ch == 113:
            # 'q'
            sys.exit(0)

        elif ch == 32 or ch == 10:
            # '<space>' or '<enter>'
            break

        elif ch == 114:
            # 'r'
            _RATE += .5
            if _RATE > 5:
                _RATE = .5
            draw_info(row, col, num)

        elif ch == 82:
            # 'R'
            _RATE -= .5
            if _RATE < .5:
                _RATE = .5
            draw_info(row, col, num)

        elif ch == 97:
            # 'a'
            _NODELAY = not _NODELAY
            _WIN.nodelay(_NODELAY)
            draw_info(row, col, num)

        elif ch == 115:
            # 's'
            _SLOW = not _SLOW
            draw_info(row, col, num)

        else:
            draw_prompt(message="Invalid command - hit any key to continue... ", color=_COLOR_ERROR)
            anykey()

def anykey():
    _WIN.nodelay(False)
    _WIN.getch()
    _WIN.nodelay(_NODELAY)

def main(stdscr):
    sample_grid = [ [5, 3, 0, 0, 7, 0, 0, 0, 0], [6, 0, 0, 1, 9, 5, 0, 0, 0], [0, 9, 8, 0, 0, 0, 0, 6, 0], [8, 0, 0, 0, 6, 0, 0, 0, 3], [4, 0, 0, 8, 0, 3, 0, 0, 1], [7, 0, 0, 0, 2, 0, 0, 0, 6], [0, 6, 0, 0, 0, 0, 2, 8, 0], [0, 0, 0, 4, 1, 9, 0, 0, 5], [0, 0, 0, 0, 8, 0, 0, 7, 9] ]

    empty_grid = [ [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], ]

    parser = argparse.ArgumentParser(description="Solve sudoku")
    parser.add_argument("--sample", action="store_true", help="Solve a sample puzzle then exit")
    parser.add_argument("--quiet", action="store_true", help="Quiet output")
    args = parser.parse_args()

    global _WIN
    _WIN = stdscr

    curses.init_pair(_COLOR_UNAVAIL, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(_COLOR_POSSIBLE, curses.COLOR_YELLOW, curses.COLOR_WHITE)
    curses.init_pair(_COLOR_FAILED, curses.COLOR_RED, curses.COLOR_WHITE)

    curses.init_pair(_COLOR_NUM_MATCH, curses.COLOR_RED, curses.COLOR_RED)
    curses.init_pair(_COLOR_AREA_MATCH, curses.COLOR_WHITE, curses.COLOR_RED)

    curses.init_pair(_COLOR_NORM, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(_COLOR_SUCCESS, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(_COLOR_WARN, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(_COLOR_ERROR, curses.COLOR_RED, curses.COLOR_BLACK)

    _WIN.clear()

    _WIN.nodelay(_NODELAY)

    draw_screen()

    if args.sample:
        grid = sample_grid
        timed_solve(grid, True)
        sys.exit(0)

    grid_strs = gridutils.read_grid_strs("etc/puzzles.txt")

    count = len(grid_strs)

    start = nanotime()

    count = 0
    for grid_str in grid_strs:
        grid = empty_grid
        gridutils.str_to_grid(grid, grid_str)
        timed_solve(grid, args.quiet)

        end = nanotime()

        count += 1

        if (end - start) >= 1:
            break

    end = nanotime()

    diff = end - start

    print("total puzz : %d" % count)
    print("total time : %.6f" % diff)
            
    sys.exit(0)

if __name__ == '__main__':
    curses.wrapper(main)
