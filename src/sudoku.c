#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>

#define SIZE 9
#define UNIT (SIZE / 3)
#define TOTAL_SIZE (SIZE * SIZE)
#define UNASSIGNED 0

int in_row(int grid[SIZE][SIZE], int row, int num) {
    for (int col = 0; col < SIZE; col++) {
        if (grid[row][col] == num) {
            return(1);
        }
    }
    return(0);
}

int in_col(int grid[SIZE][SIZE], int col, int num) {
    for (int row = 0; row < SIZE; row++) {
        if (grid[row][col] == num) {
            return(1);
        }
    }
    return(0);
}

int in_unit(int grid[SIZE][SIZE], int row, int col, int num) {
    int start_row = row - (row % UNIT);
    int end_row = start_row + UNIT;
    int start_col = col - (col % UNIT);
    int end_col = start_col + UNIT;

    for (int r = start_row; r < end_row; r++) {
        for (int c = start_col; c < end_col; c++) {
            if (grid[r][c] == num) {
                return(1);
            } 
        }
    }
    return(0);
}

int first_empty_square(int grid[SIZE][SIZE], int *row, int *col) {
    for (*row = 0; *row < SIZE; (*row)++) {
        for (*col = 0; *col < SIZE; (*col)++) {
            if (grid[*row][*col] == UNASSIGNED) {
                return(1);
            }
        }
    }
    return(0);
}

int solve(int grid[SIZE][SIZE]) {
    int row = 0;
    int col = 0;
    
    if (! first_empty_square(grid, &row, &col)) {
        return(1);
    }
    
    for (int num = 1; num <= SIZE; num++ ) {
        if (in_row(grid, row, num) || in_col(grid, col, num) || in_unit(grid, row, col, num)) {
            continue;
        }

        grid[row][col] = num;
            
        if (solve(grid)) {
            return(1);
        }
            
        grid[row][col] = UNASSIGNED;
    }
    
    return(0);
}

void str_to_grid(int grid[SIZE][SIZE], char grid_str[256]) {
    int r = 0;
    int c = 0;
    char square;

    for (int i = 0; i < TOTAL_SIZE; i++) {
        square = grid_str[i];
        if (square == '.') {
            grid[r][c] = UNASSIGNED;
        } else {
            grid[r][c] = square - '0';
        }
        c++;
        if (c == SIZE) {
            c = 0;
            r++;
        }
    }
}

void grid_to_str(char grid_str[256], int grid[SIZE][SIZE]) {
    int square;
    for (int r = 0; r < SIZE; r++) {
        for (int c = 0; c < SIZE; c++) {
            square = grid[r][c];
            if (square == UNASSIGNED) {
                grid_str[(r * SIZE) + c] = '.';
            } else {
                grid_str[(r * SIZE) + c] = square + '0';
            }
        }
    }
    grid_str[TOTAL_SIZE] = '\0';
}

char** read_grid_strs(char *filename, int *count) {
    FILE *file = NULL;
    char line[256];
    char **lines = NULL;
    char **new_lines = NULL;
    char square;
    int num = 0;
    int ct = 0;

    lines = malloc(0);

    file = fopen(filename, "r");
    if (file == NULL) {
        printf("ERROR: unable to open file '%s'\n", filename);
        return(NULL);
    }

    ct = 0;
    while (fgets(line, 256, file)) {
        if (line[strlen(line) - 1] == '\n') {
            line[strlen(line) - 1] = '\0';
        }

        if (strlen(line) != TOTAL_SIZE) {
            printf("ERROR: incorrect length %lu, invalid line '%s'\n", strlen(line), line);
            exit(1);
        }

        for (int i = 0; i < TOTAL_SIZE; i++) {
            square = line[i];

            if (square == '.') {
                continue;
            }

            num = square - '0';
            if ((num < 1) || (num > SIZE)) {
                printf("ERROR: incorrect character '%c' at index %d, invalid line '%s'\n", square, i, line);
                exit(1);
            }
        }

        new_lines = realloc(lines, (ct + 1) * sizeof(char*));
        lines = new_lines;
        lines[ct] = malloc((TOTAL_SIZE + 1) * sizeof(char));
        strcpy(lines[ct], line);

        ct++;
    }

    (*count) = ct;

    return(lines);
}

double nanotime() {
    struct timespec tsp;
    double secs;

    clock_gettime(CLOCK_MONOTONIC, &tsp);

    secs = (double)tsp.tv_sec + ((double)tsp.tv_nsec / 1000000000.0);

    return(secs);
}

void timed_solve(int grid[SIZE][SIZE], int quiet) {
    double start, end, diff;
    int solved = 0;
    char grid_str[256];

    if (! quiet) {
        grid_to_str(grid_str, grid);
        printf("puzz : %s\n", grid_str);
    }

    start = nanotime();

    solved = solve(grid);

    end = nanotime();

    diff = end - start;

    if (! quiet) {
        if (solved) {
            grid_to_str(grid_str, grid);
            printf("solu : %s\n", grid_str);
        } else {
            printf("stat : not solved\n");
        }
        printf("time : %.6f\n", diff);
    }
}

int main(int argc, char *argv[]) {
    int sample_grid[SIZE][SIZE] = { {5, 3, 0, 0, 7, 0, 0, 0, 0}, {6, 0, 0, 1, 9, 5, 0, 0, 0}, {0, 9, 8, 0, 0, 0, 0, 6, 0}, {8, 0, 0, 0, 6, 0, 0, 0, 3}, {4, 0, 0, 8, 0, 3, 0, 0, 1}, {7, 0, 0, 0, 2, 0, 0, 0, 6}, {0, 6, 0, 0, 0, 0, 2, 8, 0}, {0, 0, 0, 4, 1, 9, 0, 0, 5}, {0, 0, 0, 0, 8, 0, 0, 7, 9} };
    int empty_grid[SIZE][SIZE] = { {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0} };
    int grid[SIZE][SIZE];
    int sample = 0;
    int quiet = 0;
    int count = 0;
    char **grid_strs = NULL;
    char *grid_str = NULL;
    double start, end, diff;

    if (argc > 1) {
        if (! strcmp(argv[1], "--sample")) {
            sample = 1;
        } else if (! strcmp(argv[1], "--quiet")) {
            quiet = 1;
        }
    }

    if (sample) {
        for (int r = 0; r < SIZE; r++) {
            for (int c = 0; c < SIZE; c++) {
                grid[r][c] = sample_grid[r][c];
            }
        }
        timed_solve(grid, 0);
        return(0);
    }

    grid_strs = read_grid_strs("puzzles.txt", &count);
    if (grid_strs == NULL) {
        exit(1);
    };

    start = nanotime();

    for (int i = 0; i < count; i++) {
        for (int r = 0; r < SIZE; r++) {
            for (int c = 0; c < SIZE; c++) {
                grid[r][c] = empty_grid[r][c];
            }
        }
        grid_str = grid_strs[i];
        str_to_grid(grid, grid_str);
        timed_solve(grid, quiet);
    }

    end = nanotime();

    diff = end - start;

    printf("total puzz : %d\n", count);
    printf("total time : %.6f\n", diff);

    return(0);
}
