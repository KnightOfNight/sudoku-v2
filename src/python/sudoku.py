import argparse
import curses
import sys
import time

import config
import gridutils
import draw
import util


def solve(grid, level=0):
    (r, c) = gridutils.first_empty_square(grid)

    if r is None:
        draw.draw_content(grid, None, None, solved=True);
        return True

    if level == 0:
        draw.draw_content(grid, None, None);

    for num in range(1, config.SIZE + 1):
        if gridutils.in_row(grid, r, num):
            grid[r][c] = num
            draw.draw_content(grid, r, c, highlight="row", color=draw.COLOR_UNAVAIL, num=num, message="Already found in row", message_color=draw.COLOR_WARN);
            grid[r][c] = config.UNASSIGNED
            continue

        if gridutils.in_col(grid, c, num):
            grid[r][c] = num
            draw.draw_content(grid, r, c, highlight="col", color=draw.COLOR_UNAVAIL, num=num, message="Already found in col", message_color=draw.COLOR_WARN);
            grid[r][c] = config.UNASSIGNED
            continue

        if gridutils.in_unit(grid, r, c, num):
            grid[r][c] = num
            draw.draw_content(grid, r, c, highlight="unit", color=draw.COLOR_UNAVAIL, num=num, message="Already found in unit", message_color=draw.COLOR_WARN);
            grid[r][c] = config.UNASSIGNED
            continue

        grid[r][c] = num

        draw.draw_content(grid, r, c, color=draw.COLOR_POSSIBLE, num=num, message="Number is available", message_color=draw.COLOR_SUCCESS);

        if solve(grid, level=level+1):
            return True

        draw.draw_content(grid, r, c, color=draw.COLOR_FAILED, num=num, message="Number failed", message_color=draw.COLOR_ERROR);

        grid[r][c] = config.UNASSIGNED

    return False


def timed_solve(grid, quiet=False):
    if not quiet:
        print("puzz : %s" % gridutils.grid_to_str(grid))
        print("empt : %d" % gridutils.count_empty_squares(grid));

    start = util.nanotime()

    solved = solve(grid)

    end = util.nanotime()

    diff = end - start

    if not quiet:
        if solved:
            print("solu : %s" % gridutils.grid_to_str(grid))
        else:
            print("solu : none")
        print("time : %.6f" % diff)


def main(stdscr):
    sample_grid = [ [5, 3, 0, 0, 7, 0, 0, 0, 0], [6, 0, 0, 1, 9, 5, 0, 0, 0], [0, 9, 8, 0, 0, 0, 0, 6, 0], [8, 0, 0, 0, 6, 0, 0, 0, 3], [4, 0, 0, 8, 0, 3, 0, 0, 1], [7, 0, 0, 0, 2, 0, 0, 0, 6], [0, 6, 0, 0, 0, 0, 2, 8, 0], [0, 0, 0, 4, 1, 9, 0, 0, 5], [0, 0, 0, 0, 8, 0, 0, 7, 9] ]

    empty_grid = [ [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], ]

    parser = argparse.ArgumentParser(description="Solve sudoku")
    parser.add_argument("--sample", action="store_true", help="Solve a sample puzzle then exit")
    parser.add_argument("--quiet", action="store_true", help="Quiet output")
    args = parser.parse_args()

    draw.setup_screen(stdscr)

    draw.draw_screen()

    if args.sample:
        grid = sample_grid
        timed_solve(grid, True)
        sys.exit(0)

    grid_strs = gridutils.read_grid_strs("etc/puzzles.txt")

    count = len(grid_strs)

    start = util.nanotime()

    count = 0
    for grid_str in grid_strs:
        grid = empty_grid
        gridutils.str_to_grid(grid, grid_str)
        timed_solve(grid, args.quiet)

        end = util.nanotime()

        count += 1

        if (end - start) >= 1:
            break

    end = util.nanotime()

    diff = end - start

    print("total puzz : %d" % count)
    print("total time : %.6f" % diff)
            
    sys.exit(0)

if __name__ == '__main__':
    curses.wrapper(main)
