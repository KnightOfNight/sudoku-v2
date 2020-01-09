import curses
import sys
import time

import config
import gridutils
import util


_WIN = None
_NODELAY = False
_AUTO = False
_SLOW = True
_RATE = 1
_RATE_FACTOR = 5.0
_ROW_PROMPT = 20


_COLOR = 10

COLOR_UNAVAIL      = _COLOR
_COLOR += 1
COLOR_POSSIBLE     = _COLOR
_COLOR += 1
COLOR_FAILED       = _COLOR
_COLOR += 1

COLOR_NUM_MATCH    = _COLOR
_COLOR += 1
COLOR_AREA_MATCH   = _COLOR
_COLOR += 1

COLOR_NORM         = _COLOR
_COLOR += 1
COLOR_INVERSE      = _COLOR
_COLOR += 1
COLOR_SUCCESS      = _COLOR
_COLOR += 1
COLOR_WARN         = _COLOR
_COLOR += 1
COLOR_ERROR        = _COLOR
_COLOR += 1


_CELL_HEIGHT = 2
_CELL_WIDTH = 4


_SIDE_BOX_WIDTH = 30
_SIDE_BOX_HEIGHT = 10
_SIDE_BOX_START_COL = 38


_INFO_COL = _SIDE_BOX_START_COL + 2
_INFO_DATA_COL = _SIDE_BOX_START_COL + 7
_INFO_LEN_MAX = _SIDE_BOX_WIDTH - 8


_MSG_LEN_MAX = _SIDE_BOX_WIDTH - 3


def setup_screen(scr):
    global _WIN

    _WIN = scr

    _WIN.clear()

    _WIN.nodelay(True)

    curses.init_pair(COLOR_UNAVAIL, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(COLOR_POSSIBLE, curses.COLOR_YELLOW, curses.COLOR_WHITE)
    curses.init_pair(COLOR_FAILED, curses.COLOR_RED, curses.COLOR_WHITE)

    curses.init_pair(COLOR_NUM_MATCH, curses.COLOR_RED, curses.COLOR_RED)
    curses.init_pair(COLOR_AREA_MATCH, curses.COLOR_WHITE, curses.COLOR_RED)

    curses.init_pair(COLOR_NORM, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(COLOR_INVERSE, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(COLOR_SUCCESS, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_WARN, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(COLOR_ERROR, curses.COLOR_RED, curses.COLOR_BLACK)


def draw_screen():
    start_row = 0
    start_col = 0

    height = config.SIZE * _CELL_HEIGHT
    width = config.SIZE * _CELL_WIDTH

    # lines
    for i in range(0, config.SIZE + 1):
        _WIN.hline(start_row + (i * _CELL_HEIGHT), start_col, curses.ACS_HLINE, width)
        _WIN.vline(start_row, start_col + (i * _CELL_WIDTH), curses.ACS_VLINE, height)

    # corners
    _WIN.addch(start_row, start_col, curses.ACS_ULCORNER)
    _WIN.addch(start_row, start_col + width, curses.ACS_URCORNER)
    _WIN.addch(start_row + height, start_col, curses.ACS_LLCORNER)
    _WIN.addch(start_row + height, start_col + width, curses.ACS_LRCORNER)

    # tees
    for i in range(1, config.SIZE):
        _WIN.addch(start_row, start_col + (i * _CELL_WIDTH), curses.ACS_TTEE)
        _WIN.addch(start_row + height, start_col + (i * _CELL_WIDTH), curses.ACS_BTEE)
        _WIN.addch(start_row + (i * _CELL_HEIGHT), start_col, curses.ACS_LTEE)
        _WIN.addch(start_row + (i * _CELL_HEIGHT), start_col + width, curses.ACS_RTEE)

    # pluses
    for r in range(1, config.SIZE):
        for c in range(1, config.SIZE):
            _WIN.addch(start_row + (r * _CELL_HEIGHT), start_col + (c * _CELL_WIDTH), curses.ACS_PLUS)

    # side box
    start_row = 0
    start_col = _SIDE_BOX_START_COL
    width = _SIDE_BOX_WIDTH
    height = _SIDE_BOX_HEIGHT

    _WIN.hline(start_row, start_col, curses.ACS_HLINE, width)
    _WIN.hline(start_row + height, start_col, curses.ACS_HLINE, width)
    _WIN.vline(start_row, start_col, curses.ACS_VLINE, height)
    _WIN.vline(start_row, start_col + width, curses.ACS_VLINE, height)

    _WIN.addch(start_row, start_col, curses.ACS_ULCORNER)
    _WIN.addch(start_row, start_col + width, curses.ACS_URCORNER)
    _WIN.addch(start_row + height, start_col, curses.ACS_LLCORNER)
    _WIN.addch(start_row + height, start_col + width, curses.ACS_LRCORNER)

    attrs = curses.color_pair(COLOR_INVERSE)
    _WIN.addstr(1, _INFO_COL, "Loc:", attrs)
    _WIN.addstr(2, _INFO_COL, "Num:", attrs)
    _WIN.addstr(3, _INFO_COL, "Aut:", attrs)
    _WIN.addstr(4, _INFO_COL, "Slo:", attrs)
    _WIN.addstr(5, _INFO_COL, "Rat:", attrs)
    _WIN.addstr(6, _INFO_COL, "Tim:", attrs)


def draw_content(grid, row, col, highlight=None, color=COLOR_NORM, num=None, solved=False, message=None, message_color=None):
    assert (row is None and col is None) or (row is not None and col is not None)
    if highlight:
        assert num
    if message:
        assert message_color
        assert not solved

    global _AUTO
    global _SLOW
    global _RATE

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
                attrs = curses.A_BOLD | curses.color_pair(COLOR_NORM)

            elif r == row and c == col:
                # matching cell
                attrs = curses.A_BOLD | curses.color_pair(color)

            elif highlight == "row" and r == row:
                # matching row
                if grid[r][c] == num:
                    attrs = curses.A_BOLD | curses.color_pair(COLOR_NUM_MATCH)
                else:
                    attrs = curses.A_BOLD | curses.color_pair(COLOR_AREA_MATCH)

            elif highlight == "col" and c == col:
                # matching col
                if grid[r][c] == num:
                    attrs = curses.A_BOLD | curses.color_pair(COLOR_NUM_MATCH)
                else:
                    attrs = curses.A_BOLD | curses.color_pair(COLOR_AREA_MATCH)

            elif highlight == "unit":
                (unitr, unitc) = gridutils.get_unit(row, col)
                if r in unitr and c in unitc:
                    # matching unit
                    if grid[r][c] == num:
                        attrs = curses.A_BOLD | curses.color_pair(COLOR_NUM_MATCH)
                    else:
                        attrs = curses.A_BOLD | curses.color_pair(COLOR_AREA_MATCH)

            else:
                # cell not matched
                attrs = curses.A_BOLD | curses.color_pair(COLOR_NORM)
                
            _WIN.addstr(start_row + (r * _CELL_HEIGHT), start_col + (c * _CELL_WIDTH), s, attrs)

    if message:
        draw_message(message, color=message_color)
    else:
        clear_message()

    if solved:
        draw_info(row, col, num)
        draw_prompt(message="Finished - hit any key to exit... ", color=COLOR_SUCCESS)
        anykey()
        return

    start = util.nanotime()

    while True:
        draw_info(row, col, num)

        draw_prompt()

        ch = _WIN.getch()

        end = util.nanotime()

        diff = end - start

        if ch == -1:
            # timed out waiting for key
            if _AUTO and not _SLOW:
                break
            elif _AUTO and (diff > (_RATE / _RATE_FACTOR)):
                break
            else:
                time.sleep(.1)
                continue

        elif ch == 32 or ch == 10:
            # '<space>' or '<enter>'
            if not _AUTO:
                break

        elif ch == 97:
            # 'a'
            _AUTO = not _AUTO

        elif ch == 115:
            # 's'
            if _AUTO:
                _SLOW = not _SLOW

        elif ch == 114:
            # 'r'
            if not _AUTO or not _SLOW:
                continue
            if _RATE < 10:
                _RATE += 1
            elif _RATE < 30:
                _RATE += 5
            else:
                _RATE += 10
            if _RATE > 50:
                _RATE = 50

        elif ch == 82:
            # 'R'
            if not _AUTO or not _SLOW:
                continue
            if _RATE <= 10:
                _RATE -= 1
            elif _RATE <= 30:
                _RATE -= 5
            else:
                _RATE -= 10
            if _RATE < 1:
                _RATE = 1

        elif ch == 113:
            # 'q'
            sys.exit(0)

        else:
            draw_prompt(message="Invalid command - hit any key to continue... ", color=COLOR_ERROR)
            anykey()


def draw_info(row, col, num):
    attrs = curses.A_BOLD | curses.color_pair(COLOR_NORM)
#    attrs = curses.color_pair(COLOR_INVERSE)

    if row is not None and col is not None:
        s = "%d,%d" % (row + 1, col + 1)
    else:
        s = "None"
    _WIN.addstr(1, _INFO_DATA_COL, fmt_info(s), attrs)

    if num is not None:
        s = str(num)
    else:
        s = "None"
    _WIN.addstr(2, _INFO_DATA_COL, fmt_info(s), attrs)

    s = "%s" % _AUTO
    _WIN.addstr(3, _INFO_DATA_COL, fmt_info(s), attrs)

    if _AUTO:
        s = "%s" % _SLOW
    else:
        s = "N/A"
    _WIN.addstr(4, _INFO_DATA_COL, fmt_info(s), attrs)

    if _AUTO and _SLOW:
        s = "%d (%.2f)" % (_RATE, _RATE / _RATE_FACTOR)
    else:
        s = "N/A"
    _WIN.addstr(5, _INFO_DATA_COL, fmt_info(s), attrs)

    s = "%.6f" % util.nanotime()
    _WIN.addstr(6, _INFO_DATA_COL, fmt_info(s), attrs)


def draw_prompt(color=COLOR_NORM, message=None):
    attrs = curses.A_BOLD | curses.color_pair(color)
    _WIN.move(_ROW_PROMPT, 0)
    _WIN.clrtoeol()
    if not message:
        message = "Sudoku [ (a)uto, (s)low, (r)ate, (q)uit ] : "
    _WIN.addstr(_ROW_PROMPT, 0, message, attrs)


def draw_message(message, color=COLOR_ERROR):
    attrs = curses.A_BOLD | curses.color_pair(color)
#    attrs = curses.color_pair(COLOR_INVERSE)
    clear_message()
    _WIN.addstr(8, _INFO_COL, fmt_info(message, maxlen=_MSG_LEN_MAX), attrs)


def clear_message(color=COLOR_NORM):
    attrs = curses.A_BOLD | curses.color_pair(color)
#    attrs = curses.color_pair(COLOR_INVERSE)
    s = ""
    _WIN.addstr(8, _INFO_COL, fmt_info(s, maxlen=_MSG_LEN_MAX), attrs)


def anykey():
    _WIN.nodelay(False)
    _WIN.getch()
    _WIN.nodelay(True)


def fmt_info(content, maxlen=_INFO_LEN_MAX):
    s = content[:maxlen]
    s += " " * (maxlen - len(s))
    return s
