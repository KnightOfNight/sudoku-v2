package main

import (
    "fmt"
    "time"
    "os"
    "strings"
    "io/ioutil"
    "strconv"
)

const SIZE = 9
const UNIT = SIZE / 3
const TOTAL_SIZE = SIZE * SIZE
const UNASSIGNED = 0

func in_row(grid [][]int, r int, num int) bool {
    for c,_ := range grid[r] {
        if grid[r][c] == num {
            return true
        }
    }
    return false
}

func in_col(grid [][]int, c int, num int) bool {
    for r,_ := range grid {
        if grid[r][c] == num {
            return true
        }
    }
    return false
}

func in_unit(grid [][]int, r int, c int, num int) bool {
    unit_row := r - (r % UNIT)
    unit_col := c - (c % UNIT)
    for ur := unit_row; ur < (unit_row + UNIT); ur++ {
        for uc := unit_col; uc < (unit_col + UNIT); uc++ {
            if grid[ur][uc] == num {
                return true
            }
        }
    }
    return false
}

func first_empty_square(grid [][]int) (int, int) {
    for r,row := range grid {
        for c,_ := range row {
            if grid[r][c] == UNASSIGNED {
                return r, c
            }
        }
    }

    return -1, -1
}

func solve(grid [][]int) bool {
    r, c := first_empty_square(grid)

    if r == -1 {
        return true
    }

    for num := 1; num < 10; num++ {
        if in_row(grid, r, num) || in_col(grid, c, num) || in_unit(grid, r, c, num) {
            continue
        }

        grid[r][c] = num

        if solve(grid) {
            return true
        }

        grid[r][c] = UNASSIGNED
    }

    return false
}

func str_to_grid(grid [][]int, grid_str string) {
    r := 0
    c := 0
    for i := 0; i < TOTAL_SIZE; i++ {
        square := string(grid_str[i])
        if square == "." {
            grid[r][c] = UNASSIGNED
        } else {
            num,_ := strconv.Atoi(square)
            grid[r][c] = num
        }
        c += 1
        if c == SIZE {
            c = 0
            r += 1
        }
    }
}

func grid_to_str(grid [][]int) string {
    var grid_str string
    for r := 0; r < SIZE; r++ {
        for c := 0; c < SIZE; c++ {
            square := grid[r][c]
            if square == UNASSIGNED {
                grid_str += "."
            } else {
                grid_str += strconv.Itoa(square)
            }
        }
    }
    return grid_str
}

func read_grid_strs(filename string) []string {
    bytes,_ := ioutil.ReadFile(filename)

    line := strings.TrimSpace(string(bytes))

    lines := strings.Split(line, "\n")

    for l := 0; l < len(lines); l++ {
        line := lines[l]

        if len(line) != TOTAL_SIZE {
            fmt.Printf("ERROR: incorrect length %d, invalid line '%s'\n", len(line), line)
            os.Exit(1)
        }

        for i := 0; i < TOTAL_SIZE; i++ {
            square := string(line[i])

            if square == "." {
                continue
            }

            num,_ := strconv.Atoi(square)
            if num == 0 {
                fmt.Printf("ERROR: incorrect character '%s' at index %d, invalid line '%s'\n", square, i, line)
                os.Exit(1)
            }
        }
    }

    return lines
}

func nanotime() float64 {
    return float64(time.Now().UnixNano()) / 1000000000.0
}

func timed_solve(grid [][]int, quiet bool) {
    if ! quiet {
        fmt.Printf("puzz : %s\n", grid_to_str(grid))
    }

    start := nanotime()

    solved := solve(grid)

    end := nanotime()

    diff := end - start

    if ! quiet {
        if solved {
            fmt.Printf("solu : %s\n", grid_to_str(grid))
        } else {
            fmt.Printf("stat : not solved\n")
        }
        fmt.Printf("time : %.6f\n", diff)
    }
}

func main() {
    sample_grid := [][]int { {5, 3, 0, 0, 7, 0, 0, 0, 0}, {6, 0, 0, 1, 9, 5, 0, 0, 0}, {0, 9, 8, 0, 0, 0, 0, 6, 0}, {8, 0, 0, 0, 6, 0, 0, 0, 3}, {4, 0, 0, 8, 0, 3, 0, 0, 1}, {7, 0, 0, 0, 2, 0, 0, 0, 6}, {0, 6, 0, 0, 0, 0, 2, 8, 0}, {0, 0, 0, 4, 1, 9, 0, 0, 5}, {0, 0, 0, 0, 8, 0, 0, 7, 9}, }
    empty_grid := [][]int { {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, }

    args := os.Args[1:]
    sample := false;
    quiet := false;
    if len(args) > 0 {
        if args[0] == "--sample" {
            sample = true;
        } else if args[0] == "--quiet" {
            quiet = true;
        }
    }

    if sample {
        grid := sample_grid
        timed_solve(grid, false)
        os.Exit(0)
    }

    grid_strs := read_grid_strs("puzzles.txt")

    count := len(grid_strs)

    start := nanotime()

    for _,line := range grid_strs {
        grid := empty_grid
        str_to_grid(grid, line)
        timed_solve(grid, quiet)
    }

    end := nanotime()

    diff := end - start;

    fmt.Printf("total puzz : %d\n", count);
    fmt.Printf("total time : %.6f\n", diff);

    os.Exit(0)
}
