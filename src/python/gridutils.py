import config

def in_row(grid, row, num):
    return num in grid[row]

def in_col(grid, col, num):
    return num in [ x[col] for x in grid ]

def in_unit(grid, row, col, num):
    (rows, cols) = get_unit(row, col)

    for r in rows:
        for c in cols:
            if grid[r][c] == num:
                return True

    return False

def get_unit(row, col):
    unit_row = row - (row % config.UNIT)
    unit_col = col - (col % config.UNIT)

    rows = range(unit_row, unit_row + config.UNIT)
    cols = range(unit_col, unit_col + config.UNIT)

    return (rows, cols)

def first_empty_square(grid):
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == config.UNASSIGNED:
                return (r, c)
    return (None, None)

def count_empty_squares(grid):
    count = 0
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == config.UNASSIGNED:
                count += 1
    return count

def str_to_grid(grid, grid_str):
    r = 0
    c = 0
    for i in range(config.TOTAL_SIZE):
        square = grid_str[i]
        if square == ".":
            grid[r][c] = config.UNASSIGNED
        else:
            grid[r][c] = int(square)
        c += 1
        if c == config.SIZE:
            c = 0
            r += 1

def grid_to_str(grid):
    grid_str = ""
    for r in range(config.SIZE):
        for c in range(config.SIZE):
            square = grid[r][c]
            if square == config.UNASSIGNED: 
                grid_str += "."
            else:
                grid_str += str(square)
    return grid_str

def read_grid_strs(filename):
    lines = []

    with open(filename, "r") as f:
        lines = [ l.strip() for l in f.readlines() ]

    for line in lines:
        if len(line) != config.TOTAL_SIZE:
            print("ERROR: incorrect length %d, invalid line '%s'" % (len(line), line))
            sys.exit(1)

        for i in range(config.TOTAL_SIZE):
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
