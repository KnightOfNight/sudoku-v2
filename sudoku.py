import argparse
import subprocess
import sys
import time

_SIZE = 9
_UNIT = int(_SIZE / 3)
_TOTAL_SIZE = _SIZE * _SIZE
_UNASSIGNED = 0

def in_row(grid, row, num):
    return num in grid[row]

def in_col(grid, col, num):
    return num in [ x[col] for x in grid ]

def in_unit(grid, row, col, num):
    unit_row = row - (row % _UNIT)
    unit_col = col - (col % _UNIT)
    for r in range(unit_row, unit_row + _UNIT):
        if num in grid[r][unit_col:unit_col + _UNIT]:
            return True
    return False

def first_empty_square(grid):
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == _UNASSIGNED:
                return (r, c)
    return (None, None)

def count_empty_squares(grid):
    count = 0
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == _UNASSIGNED:
                count += 1
    return count

def solve(grid):
    (r, c) = first_empty_square(grid)

    if r is None:
        print_grid(grid);
        return True

    for num in range(1, _SIZE + 1):
        if in_row(grid, r, num):
            grid[r][c] = num
            print_grid(grid, hrow=r, hcol=c, affect=red, hentrow=True);
            grid[r][c] = _UNASSIGNED
            continue

        if in_col(grid, c, num):
            grid[r][c] = num
            print_grid(grid, hrow=r, hcol=c, affect=red, hentcol=True);
            grid[r][c] = _UNASSIGNED
            continue

        if in_unit(grid, r, c, num):
            grid[r][c] = num
            print_grid(grid, hrow=r, hcol=c, affect=red, hentunit=True);
            grid[r][c] = _UNASSIGNED
            continue

#        if in_row(grid, r, num) or in_col(grid, c, num) or in_unit(grid, r, c, num):
#            continue

        grid[r][c] = num

        print_grid(grid, hrow=r, hcol=c);

        if solve(grid):
            return True

        print_grid(grid, hrow=r, hcol=c, affect=red);

        grid[r][c] = _UNASSIGNED

    return False

def str_to_grid(grid, grid_str):
    r = 0
    c = 0
    for i in range(_TOTAL_SIZE):
        square = grid_str[i]
        if square == ".":
            grid[r][c] = _UNASSIGNED
        else:
            grid[r][c] = int(square)
        c += 1
        if c == _SIZE:
            c = 0
            r += 1

def grid_to_str(grid):
    grid_str = ""
    for r in range(_SIZE):
        for c in range(_SIZE):
            square = grid[r][c]
            if square == _UNASSIGNED: 
                grid_str += "."
            else:
                grid_str += str(square)
    return grid_str

def read_grid_strs(filename):
    lines = []

    with open(filename, "r") as f:
        lines = [ l.strip() for l in f.readlines() ]

    for line in lines:
        if len(line) != _TOTAL_SIZE:
            print("ERROR: incorrect length %d, invalid line '%s'" % (len(line), line))
            sys.exit(1)

        for i in range(_TOTAL_SIZE):
            square = line[i]
            if square == ".":
                continue
            try:
                num = int(square)
                continue
            except ValueError:
                print("ERROR: incorrect character '%s' at index %d, invalid line '%s'" % (square, i, line))
                sys.exit(1)

    return lines

def nanotime():
    return time.monotonic_ns() / 1000000000

def timed_solve(grid, quiet=False):
    if not quiet:
        print("puzz : %s" % grid_to_str(grid))
        print("empt : %d" % count_empty_squares(grid));

    start = nanotime()

    solved = solve(grid)

    end = nanotime()

    diff = end - start

    if not quiet:
        if solved:
            print("solu : %s" % grid_to_str(grid))
        else:
            print("solu : none")
        print("time : %.6f" % diff)

def colorize(s, style=0, fg=30, bg=40):
    if style not in range(8):
        print("ERROR: style %d not in range(%d)" % (style, 8))
        sys.exit(1)

    if fg not in range(30, 38):
        print("ERROR: fg %d not in range(%d, %d)" % (fg, 30, 38))
        sys.exit(1)

    if bg not in range(40, 48):
        print("ERROR: bg %d not in range(%d, %d)" % (bg, 40, 48))
        sys.exit(1)

    ss = "\x1b[%d;%d;%dm%s\x1b[0m" % (style, fg, bg, s)

    return ss

def yellow(s):
    return colorize(s, style=0, fg=33, bg=40)

def white(s):
    return colorize(s, style=1, fg=37, bg=40)

def blue(s):
    return colorize(s, style=1, fg=34, bg=40)

def redonred(s):
    return colorize(s, style=1, fg=31, bg=41)

def whiteonred(s):
    return colorize(s, style=1, fg=31, bg=41)

def print_grid(grid, hrow=None, hcol=None, clear=True, sleep=0.01, affect=blue, hentrow=False, hentcol=False, hentunit=False):
    if clear:
        subprocess.run("clear")

    xy = len(grid)
    for r in range(xy):
        row = grid[r]
        sys.stdout.write("%s\n" % (white("+" + "---+" * xy)))
        sys.stdout.write("%s" % white("|"))
        for c in range(xy):
            i = grid[r][c]
            s = str(i)
            if i == _UNASSIGNED:
                s = " "
            if hrow is not None and hcol is not None and hrow == r and hcol == c:
                s = affect(s)
            else:
                s = white(s)
            sys.stdout.write(" %s %s" % (s, white("|")))
        sys.stdout.write("\n")

    sys.stdout.write("%s\n" % (white("+" + "---+" * xy)))

    if sleep > 0:
        time.sleep(sleep)

def main():
    sample_grid = [ [5, 3, 0, 0, 7, 0, 0, 0, 0], [6, 0, 0, 1, 9, 5, 0, 0, 0], [0, 9, 8, 0, 0, 0, 0, 6, 0], [8, 0, 0, 0, 6, 0, 0, 0, 3], [4, 0, 0, 8, 0, 3, 0, 0, 1], [7, 0, 0, 0, 2, 0, 0, 0, 6], [0, 6, 0, 0, 0, 0, 2, 8, 0], [0, 0, 0, 4, 1, 9, 0, 0, 5], [0, 0, 0, 0, 8, 0, 0, 7, 9] ]

    empty_grid = [ [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], ]

    parser = argparse.ArgumentParser(description="Solve sudoku")
    parser.add_argument("--sample", action="store_true", help="Solve a sample puzzle then exit")
    parser.add_argument("--quiet", action="store_true", help="Quiet output")
    args = parser.parse_args()

    if args.sample:
        grid = sample_grid
        timed_solve(grid, False)
        sys.exit(0)

    grid_strs = read_grid_strs("puzzles.txt")

    count = len(grid_strs)

    start = nanotime()

    count = 0
    for grid_str in grid_strs:
        grid = empty_grid
        str_to_grid(grid, grid_str)
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

main()
