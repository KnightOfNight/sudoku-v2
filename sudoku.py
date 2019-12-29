import argparse
import copy
import random
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
        return True

    for num in range(1, _SIZE + 1):
        if in_row(grid, r, num) or in_col(grid, c, num) or in_unit(grid, r, c, num):
            continue

        grid[r][c] = num

        if solve(grid):
            return True

        grid[r][c] = _UNASSIGNED

    return False

def uniqsolve(grid, level=0, solutions=0, start_row=None, start_col=None):
    r = 0
    c = 0
    if start_row and start_col:
        r = start_row
        c = start_col
    else:
        (r, c) = first_empty_square(grid)

    if r is None:
        return 1

    this_solutions = 0
    for num in range(1, _SIZE + 1):
        if in_row(grid, r, num) or in_col(grid, c, num) or in_unit(grid, r, c, num):
            continue

        gridcopy = copy.deepcopy(grid)

        gridcopy[r][c] = num

        this_solutions += uniqsolve(gridcopy, level=level+1, solutions=solutions)

        if this_solutions > 1:
            break

    return this_solutions

def randsolve(grid):
    (r, c) = first_empty_square(grid)

    if r is None:
        return True

    nums_tried = []
    while True:
        num = random.randint(1, _SIZE)

        if num in nums_tried:
            continue

        nums_tried.append(num)

        if not in_row(grid, r, num) and not in_col(grid, c, num) and not in_unit(grid, r, c, num):
            grid[r][c] = num
            if randsolve(grid):
                return True
            grid[r][c] = _UNASSIGNED

        if len(nums_tried) == _SIZE:
            num = 0
            break

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

    solved = uniqsolve(grid)

    end = nanotime()

    diff = end - start

    if not quiet:
        if solved == 1:
            print("solu : %s" % grid_to_str(grid))
        elif solved > 1:
            print("solu : multiple")
        else:
            print("solu : none")
        print("time : %.6f" % diff)

def generate():
    grid = [ [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], ]

    if not randsolve(grid):
        print("ERROR: unable to make grid")
        sys.exit(1)

    orig_sol = grid_to_str(grid)
    print("orig : %s" % (orig_sol))

    count = 0
    max_empty = random.randint(4, 50)
    max_empty = 50
    while True:
        r = random.randrange(_SIZE)
        c = random.randrange(_SIZE)

        if grid[r][c] == _UNASSIGNED:
            continue

        gridcopy = copy.deepcopy(grid)
        gridcopy[r][c] = _UNASSIGNED

        solved = uniqsolve(gridcopy, start_row=r, start_col=c)
        if solved == 1:
            grid[r][c] = _UNASSIGNED
            count += 1

        if count == max_empty:
            break

    print("puzz : %s" % (grid_to_str(grid)))
    solved = uniqsolve(grid)
    if solved > 1:
        print("ERROR: invalid puzzie, multiple solutions")
        sys.exit(1)
    elif solved > 0:
        solve(grid)
        print("solu : %s" % (grid_to_str(grid)))
        if grid_to_str(grid) != orig_sol:
            print("ERROR: invalid puzzle, solutions don't match")
            sys.exit(1)
    else:
        print("solu : none")

    return grid

def main():
    sample_grid = [ [5, 3, 0, 0, 7, 0, 0, 0, 0], [6, 0, 0, 1, 9, 5, 0, 0, 0], [0, 9, 8, 0, 0, 0, 0, 6, 0], [8, 0, 0, 0, 6, 0, 0, 0, 3], [4, 0, 0, 8, 0, 3, 0, 0, 1], [7, 0, 0, 0, 2, 0, 0, 0, 6], [0, 6, 0, 0, 0, 0, 2, 8, 0], [0, 0, 0, 4, 1, 9, 0, 0, 5], [0, 0, 0, 0, 8, 0, 0, 7, 9] ]
    empty_grid = [ [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], ]

    parser = argparse.ArgumentParser(description="Solve sudoku")
    parser.add_argument("--sample", action="store_true", help="Solve a sample puzzle then exit")
    parser.add_argument("--quiet", action="store_true", help="Quiet output")
    parser.add_argument("--generate", action="store_true", help="Generate puzzle")
    args = parser.parse_args()

    if args.sample:
        grid = sample_grid
        timed_solve(grid, False)
        sys.exit(0)

    if args.generate:
        for i in range(10000):
            grid = generate()
#            timed_solve(grid, args.quiet)
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

        if (end - start) > 10:
            break

    end = nanotime()

    diff = end - start

    print("total puzz : %d" % count)
    print("total time : %.6f" % diff)
            
    sys.exit(0)

main()
