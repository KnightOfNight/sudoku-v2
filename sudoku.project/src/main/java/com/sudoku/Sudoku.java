package com.sudoku;

import java.nio.file.*;
import java.util.Arrays;
import java.util.List;
import java.util.ArrayList;
import software.amazon.awssdk.services.sqs.SqsClient;

public class Sudoku {
    public final static int SIZE = 9;
    public final static int UNIT = SIZE / 3;
    public final static int TOTAL_SIZE = SIZE * SIZE;
    public final static int UNASSIGNED = 0;

    private final static int SAMPLE_GRID[][] = { {5, 3, 0, 0, 7, 0, 0, 0, 0}, {6, 0, 0, 1, 9, 5, 0, 0, 0}, {0, 9, 8, 0, 0, 0, 0, 6, 0}, {8, 0, 0, 0, 6, 0, 0, 0, 3}, {4, 0, 0, 8, 0, 3, 0, 0, 1}, {7, 0, 0, 0, 2, 0, 0, 0, 6}, {0, 6, 0, 0, 0, 0, 2, 8, 0}, {0, 0, 0, 4, 1, 9, 0, 0, 5}, {0, 0, 0, 0, 8, 0, 0, 7, 9} };

    private final static int EMPTY_GRID[][] = { {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0} };

    private static int randIntRange(int mod) {
        int randint = (int)(Math.random() * 1000000) % mod;
        return(randint);
    }

    private static int LONGEST = 0;
    private static boolean solve(int grid[][], int level, boolean verbose) {
        int rc[] = Grid.firstEmptySq(grid);
        if (rc[0] == -1) {
            if (verbose) {
                System.out.printf("solve puzz : %s\n", grid_to_str(grid));
            }
            return(true);
        }
        int row = rc[0];
        int col = rc[1];

        if (level == 0) {
            LONGEST = 0;
        }

        for (int num = 1; num <= SIZE; num++ ) {
            if (! Grid.numPlayable(grid, row, col, num)) {
                continue;
            }

            if (verbose) {
                int len = TOTAL_SIZE - Grid.countEmptySq(grid);
                if (len > LONGEST) {
                    LONGEST = len;
                    System.out.printf("solve puzz : %s\n", grid_to_str(grid));
                }
            }

            grid[row][col] = num;

            if (solve(grid, level + 1, verbose)) {
                return(true);
            }

            grid[row][col] = UNASSIGNED;
        }

        return(false);
    }

    private static int solveUniq(int grid[][], int start_row, int start_col) {
        int row;
        int col;
        int workgrid[][] = new int[SIZE][SIZE];
        int solutions = 0;

        if (start_row == -1 && start_col == -1) {
            int rc[] = Grid.firstEmptySq(grid);
            if (rc[0] == -1) {
                return(1);
            }
            row = rc[0];
            col = rc[1];
        } else {
            row = start_row;
            col = start_col;
        }

        for (int num = 1; num <= SIZE; num++ ) {
            if (! Grid.numPlayable(grid, row, col, num)) {
                continue;
            }

            gridcopy(workgrid, grid);

            workgrid[row][col] = num;

            solutions += solveUniq(workgrid, -1, -1);

            if (solutions > 1) {
                break;
            }
        }

        return(solutions);
    }

    private static int randNum(List<Integer> tried) {
        List<Integer> pool = new ArrayList<Integer>();

        for (int num = 1; num <= SIZE; num++) {
            if (tried.contains(num)) {
                continue;
            }
            pool.add(num);
        }

        if (pool.size() > 0) {
            int randidx = randIntRange(pool.size());
            int num = pool.get(randidx);
            tried.add(num);
            return(num);
        } else {
            return(0);
        }
    }

    private static boolean solveRand(int grid[][], int level) {
        int rc[] = Grid.firstEmptySq(grid);
        if (rc[0] == -1) {
            return(true);
        }
        int row = rc[0];
        int col = rc[1];

        List<Integer> tried = new ArrayList<Integer>();

        while (true) {
            int num = randNum(tried);

            if (num == 0) {
                break;
            }

            if (Grid.numPlayable(grid, row, col, num)) {
                grid[row][col] = num;
                if (solveRand(grid, level + 1)) {
                    return(true);
                }
                grid[row][col] = UNASSIGNED;
            }
        }

        return(false);
    }

    private static void str_to_grid(int grid[][], String grid_str) {
        int r = 0;
        int c = 0;

        for (int i = 0; i < TOTAL_SIZE; i++) {
            char square = grid_str.charAt(i);
            if (square == '.') {
                grid[r][c] = UNASSIGNED;
            } else {
                grid[r][c] = Character.getNumericValue(square);
            }
            c++;
            if (c == SIZE) {
                c = 0;
                r++;
            }
        }
    }

    private static String grid_to_str(int grid[][]) {
        String grid_str = "";
        for (int r = 0; r < SIZE; r++) {
            for (int c = 0; c < SIZE; c++) {
                int square = grid[r][c];
                if (square == UNASSIGNED) {
                    grid_str = grid_str.concat(".");
                } else {
                    grid_str = grid_str.concat(Integer.toString(square));
                }
            }
        }
        return(grid_str);
    }

    private static String[] read_grid_strs(String filename) throws Exception {
        String line = new String(Files.readAllBytes(Paths.get(filename)));

        line = line.trim();

        String lines[] = line.split("\n");

        for (int l = 0; l < lines.length; l++) {
            line = lines[l];

            if (line.length() != TOTAL_SIZE) {
                System.out.printf("ERROR: incorrect length %d, invalid line '%s'\n", line.length(), line);
                System.exit(1);
            }

            for (int i = 0; i < TOTAL_SIZE; i++) {
                char square = line.charAt(i);

                if (square == '.') {
                    continue;
                }

                int num = Character.getNumericValue(square);
                if ((num < 1) || (num > SIZE)) {
                    System.out.printf("ERROR: incorrect character '%c' at index %d, invalid line '%s'\n", square, i, line);
                    System.exit(1);
                }
            }
        }

        return(lines);
    }

    private static void gridcopy(int dest[][], int src[][]) {
        for (int r = 0; r < SIZE; r++) {
            for (int c = 0; c < SIZE; c++) {
                dest[r][c] = src[r][c];
            }
        }
    }

    private static double nanotime() {
        long time = System.nanoTime();

        double seconds = time / 1000000000.0;

        return(seconds);
    }

    private static int timed_solve(int grid[][], boolean checkuniq, boolean quiet) {
        double start;
        double end;
        double diff;
        double uniqdiff = 0;
        double fastdiff = 0;
        int solutions;

        if (! quiet) {
            System.out.printf("puzz : %s\n", grid_to_str(grid));
            System.out.printf("empt : %d\n", Grid.countEmptySq(grid));
        }

        if (checkuniq) {
            start = nanotime();
            solutions = solveUniq(grid, -1, -1);
            if (! quiet) {
                end = nanotime();
                uniqdiff = end - start;
                System.out.printf("uniq sols : %d\n", solutions);
                System.out.printf("uniq time : %.6f\n", uniqdiff);
            }
        } else {
            solutions = 1;
        }

        if (solutions > 1) {
            System.out.printf("solu : multiple\n");
            System.out.printf("ERROR\n");
            System.exit(1);
        } else if (solutions == 1) {
            start = nanotime();
            boolean solved = solve(grid, 0, false);
            if (! quiet) {
                end = nanotime();
                fastdiff = end - start;
                if (solved) {
                    System.out.printf("solu : %s\n", grid_to_str(grid));
                } else {
                    System.out.printf("solu : failed\n");
                    System.out.printf("ERROR\n");
                    System.exit(1);
                }
                System.out.printf("time : %.6f\n", fastdiff);
                if ((uniqdiff > 0) && (uniqdiff < fastdiff)) {
                    System.out.printf("diff : solveUniq was faster by a factor of %.3f\n", fastdiff / uniqdiff);
                }
            }
        } else {
            if (! quiet) {
                System.out.printf("solu : none\n");
            }
        }

        return(solutions);
    }

    private static int[] randSq(int grid[][], int tried[][], boolean empty) {
        List<int[]> found = new ArrayList<int[]>();

        for (int r = 0; r < SIZE; r++) {
            for (int c = 0; c < SIZE; c++) {
                if (tried[r][c] > 0) {
                    continue;
                }

                if (((grid[r][c] == UNASSIGNED) && ! empty) || ((grid[r][c] != UNASSIGNED) && empty)) {
                    continue;
                }

                int rc[] = new int[2];
                rc[0] = r;
                rc[1] = c;

                found.add(rc);
            }
        }

        if (found.size() > 0) {
            int randidx = randIntRange(found.size());
            int rc[] = found.get(randidx);
            int r = rc[0];
            int c = rc[1];
            tried[r][c] = 1;
            return(rc);
        } else {
            int rc[] = { -1, -1 };
            return(rc);
        }
    }

    private static int[][] generate() {
        int tried[][] = new int[SIZE][SIZE];
        int grid[][] = new int[SIZE][SIZE];
        int workgrid[][] = new int[SIZE][SIZE];
        double start;
        double end;
        double diff;
        int solutions = 0;
        int count_empty = 0;
        int max_empty = 61;

        start = nanotime();
        solveRand(grid, 0);
        end = nanotime();
        diff = end - start;
        System.out.printf("generate solu : %s\n", grid_to_str(grid));
        System.out.printf("generate time : %.6f (stage 1)\n", diff);

        start = nanotime();
        while (true) {
            int rc[] = randSq(grid, tried, false);
            if (rc[0] == -1) {
                break;
            }

            int r = rc[0];
            int c = rc[1];

            gridcopy(workgrid, grid);
            workgrid[r][c] = UNASSIGNED;

            solutions = solveUniq(workgrid, r, c);

            if (solutions == 1) {
                grid[r][c] = UNASSIGNED;
                count_empty++;
            } else if (solutions == 0) {
                System.out.printf("%d,%d ERROR - no solution found\n", r, c);
                System.exit(1);
            }

            if (count_empty == max_empty) {
                break;
            }
        }
        end = nanotime();
        diff = end - start;
        System.out.printf("generate puzz : %s\n", grid_to_str(grid));
        System.out.printf("generate coun : %d (%d)\n", count_empty, max_empty);
        System.out.printf("generate time : %.6f (stage 2)\n", diff);

        return(grid);
    }

    public static void main(String args[]) {
        int grid[][] = new int[SIZE][SIZE];
        boolean sample = false;
        boolean quiet = false;
        boolean generate = false;
        String filename = "puzzles.txt";
        int generate_count = 1;

        if (args.length > 0) {
            if (args[0].equals("--sample")) {
                sample = true;
            } else if (args[0].equals("--quiet")) {
                quiet = true;
            } else if (args[0].equals("--generate")) {
                generate = true;
                if (args.length > 1) {
                    generate_count = Integer.parseInt(args[1]);
                    if (generate_count < 1) {
                        System.out.printf("ERROR: invalid count %d\n", generate_count);
                        System.exit(1);
                    }
                }
            } else if (args[0].equals("--solve")) {
                if (args.length > 1) {
                    filename = args[1];
                }
            }
        }

        if (sample) {
            gridcopy(grid, SAMPLE_GRID);
            timed_solve(grid, true, false);
            return;
        }

        if (generate) {
            SqsClient sqs = Sqs.connect();
            List<String> puzzles = new ArrayList<String>();
            double start = nanotime();
            for (int num = 0; num < generate_count; num++) {
                int puzzle_grid[][] = generate();
                String puzzle_str = grid_to_str(puzzle_grid);
                puzzles.add(puzzle_str);
            }
            double end = nanotime();
            double diff = end - start;
            System.out.printf("total puzz : %d\n", generate_count);
            System.out.printf("total rate : %.6f puzz/s\n", generate_count / diff);
            System.out.printf("total time : %.6f\n", diff);

            Sqs.sendPuzzles(sqs, puzzles);

           return;
        }

        String grid_strs[];
        try {
            grid_strs = read_grid_strs(filename);
        } catch(Exception e) {
            return;
        }

        int count = grid_strs.length;

        double start = nanotime();

        for (int i = 0; i < grid_strs.length; i++) {
            gridcopy(grid, EMPTY_GRID);
            String line = grid_strs[i];
            str_to_grid(grid, line);
            timed_solve(grid, false, quiet);
        }

        double end = nanotime();

        double diff = end - start;

        System.out.printf("total puzz : %d\n", count);
        System.out.printf("total time : %.6f\n", diff);

        return;
    }
}
