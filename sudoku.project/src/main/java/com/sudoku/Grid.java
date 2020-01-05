package com.sudoku;

public class Grid {
    private static boolean numInRow(int grid[][], int row, int num) {
        for (int col = 0; col < Sudoku.SIZE; col++) {
            if (grid[row][col] == num) {
                return(true);
            }
        }
        return(false);
    }

    private static boolean numInCol(int grid[][], int col, int num) {
       for (int row = 0; row < Sudoku.SIZE; row++) {
            if (grid[row][col] == num) {
                return(true);
            }
        }
        return(false);
    }

    private static boolean numInUnit(int grid[][], int row, int col, int num) {
        int start_row = row - (row % Sudoku.UNIT);
        int end_row = start_row + Sudoku.UNIT;
        int start_col = col - (col % Sudoku.UNIT);
        int end_col = start_col + Sudoku.UNIT;

        for (int r = start_row; r < end_row; r++) {
            for (int c = start_col; c < end_col; c++) {
                if (grid[r][c] == num) {
                    return(true);
                }
            }
        }

        return(false);
    }

    public static boolean numPlayable(int grid[][], int row, int col, int num) {
        return(! numInRow(grid, row, num) && ! numInCol(grid, col, num) && ! numInUnit(grid, row, col, num));
    }

    public static int[] firstEmptySq(int grid[][]) {
        for (int row = 0; row < Sudoku.SIZE; row++) {
            for (int col = 0; col < Sudoku.SIZE; col++) {
                if (grid[row][col] == Sudoku.UNASSIGNED) {
                    int rc[] = { row, col };
                    return rc;
                }
            }
        }

        int rc[] = { -1, -1 };

        return rc;
    }

    public static int countEmptySq(int grid[][]) {
        int count = 0;

        for (int row = 0; row < Sudoku.SIZE; row++) {
            for (int col = 0; col < Sudoku.SIZE; col++) {
                if (grid[row][col] == Sudoku.UNASSIGNED) {
                    count++;
                }
            }
        }

        return count;
    }
}
