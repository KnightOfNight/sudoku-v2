import java.nio.file.*;

public class sudoku {
    private final static int SIZE = 9;
    private final static int UNIT = SIZE / 3;
    private final static int TOTAL_SIZE = SIZE * SIZE;
    private final static int UNASSIGNED = 0;

    private final static int SAMPLE_GRID[][] = { {5, 3, 0, 0, 7, 0, 0, 0, 0}, {6, 0, 0, 1, 9, 5, 0, 0, 0}, {0, 9, 8, 0, 0, 0, 0, 6, 0}, {8, 0, 0, 0, 6, 0, 0, 0, 3}, {4, 0, 0, 8, 0, 3, 0, 0, 1}, {7, 0, 0, 0, 2, 0, 0, 0, 6}, {0, 6, 0, 0, 0, 0, 2, 8, 0}, {0, 0, 0, 4, 1, 9, 0, 0, 5}, {0, 0, 0, 0, 8, 0, 0, 7, 9} };

    private final static int EMPTY_GRID[][] = { {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0}, {0,0,0,0,0,0,0,0,0} };

    private static int randintmod(int mod) {
        int randint = (int)(Math.random() * 1000000) % mod;
        return(randint);
    }

    private static boolean in_row(int grid[][], int row, int num) {
        for (int col = 0; col < SIZE; col++) {
            if (grid[row][col] == num) {
                return(true);
            }
        }
        return(false);
    }

    private static boolean in_col(int grid[][], int col, int num) {
       for (int row = 0; row < SIZE; row++) {
            if (grid[row][col] == num) {
                return(true);
            }
        }
        return(false);
    }

    private static boolean in_unit(int grid[][], int row, int col, int num) {
        int start_row = row - (row % UNIT);
        int end_row = start_row + UNIT;
        int start_col = col - (col % UNIT);
        int end_col = start_col + UNIT;

        for (int r = start_row; r < end_row; r++) {
            for (int c = start_col; c < end_col; c++) {
                if (grid[r][c] == num) {
                    return(true);
                }
            }
        }

        return(false);
    }

    private static boolean num_available(int grid[][], int row, int col, int num) {
        return(! in_row(grid, row, num) && ! in_col(grid, col, num) && ! in_unit(grid, row, col, num));
    }

    private static int[] first_empty_square(int grid[][]) {
        for (int row = 0; row < SIZE; row++) {
            for (int col = 0; col < SIZE; col++) {
                if (grid[row][col] == UNASSIGNED) {
                    int rc[] = { row, col };
                    return rc;
                }
            }
        }

        int rc[] = { -1, -1 };
        return rc;
    }

    private static int count_empty_squares(int grid[][]) {
        int count = 0;

        for (int row = 0; row < SIZE; row++) {
            for (int col = 0; col < SIZE; col++) {
                if (grid[row][col] == UNASSIGNED) {
                    count++;
                }
            }
        }

        return count;
    }

    private static int[] rand_square(int grid[][], boolean empty) {
        int found[][] = new int[0][0];

        for (int r = 0; r < SIZE; r++) {
            for (int c = 0; c < SIZE; c++) {
                int square = grid[r][c];
                if (((square == UNASSIGNED) && empty) || ((square != UNASSIGNED) && ! empty)) {
                    int len = found.length;
                    int newfound[][];
                    newfound = new int[len + 1][2];

                    for (int i = 0; i < len; i++) {
                        newfound[i][0] = found[i][0];
                        newfound[i][1] = found[i][1];
                    }

                    newfound[len][0] = r;
                    newfound[len][1] = c;

                    len++;

                    found = newfound;
                }
            }
        }

        if (found.length > 0) {
            return(found[randintmod(found.length)]);
        } else {
            int rc[] = { -1, -1 };
            return(rc);
        }
    }

    private static int longest = 0;

    private static boolean solve(int grid[][], int level) {
        int rc[] = first_empty_square(grid);
        if (rc[0] == -1) {
            System.out.printf("solve puzz : %s\n", grid_to_str(grid));
            return(true);
        }
        int row = rc[0];
        int col = rc[1];

        if (level == 0) {
            longest = 0;
        }

        for (int num = 1; num <= SIZE; num++ ) {
            if (! num_available(grid, row, col, num)) {
                continue;
            }

            int len = TOTAL_SIZE - count_empty_squares(grid);

            if (len > longest) {
                longest = len;
                System.out.printf("solve puzz : %s\n", grid_to_str(grid));
            }

            grid[row][col] = num;

            if (solve(grid, level + 1)) {
                return(true);
            }

            grid[row][col] = UNASSIGNED;
        }

        return(false);
    }

    private static int uniqsolve(int grid[][], int start_row, int start_col) {
        int row;
        int col;

        if (start_row == -1 && start_col == -1) {
            int rc[] = first_empty_square(grid);
            if (rc[0] == -1) {
                return(1);
            }
            row = rc[0];
            col = rc[1];
        } else {
            row = start_row;
            col = start_col;
        }

        int solutions = 0;
        int workgrid[][] = new int[SIZE][SIZE];

        for (int num = 1; num <= SIZE; num++ ) {
            if (! num_available(grid, row, col, num)) {
                continue;
            }

            gridcopy(workgrid, grid);

            workgrid[row][col] = num;

            solutions += uniqsolve(workgrid, -1, -1);

            if (solutions > 1) {
                break;
            }
        }

        return(solutions);
    }

    private static boolean randsolve(int grid[][], int level) {
        int rc[] = first_empty_square(grid);
        if (rc[0] == -1) {
            return(true);
        }
        int row = rc[0];
        int col = rc[1];

        int nums_tried[] = new int[SIZE];

        while (true) {
            int num = randintmod(SIZE) + 1;

            int idx = num - 1;

            if (nums_tried[idx] > 0) {
//                System.out.printf("level:%d num:%d - CACHE HIT\n", level, num);
                continue;
            }

//            System.out.printf("level:%d num:%d - TRYING\n", level, num);

            nums_tried[idx] = num;

            if (num_available(grid, row, col, num)) {
                grid[row][col] = num;
                if (randsolve(grid, level + 1)) {
//                    System.out.printf("level:%d num:%d - SOLVED\n", level, num);
                    return(true);
                }
                grid[row][col] = UNASSIGNED;
//                System.out.printf("level:%d num:%d - NO SOLUTION\n", level, num);
//            } else {
//                System.out.printf("level:%d num:%d - NOT AVAILABLE\n", level, num);
            }

            int available = 0;
            for (int i = 0; i < SIZE; i++) {
                if (nums_tried[i] == 0) {
                    available++;
                    break;
                }
            }

            if (available == 0) {
//                System.out.printf("level:%d NO SOLUTION\n", level);
                break;
//            } else {
//                System.out.printf("level:%d TRYING MORE\n", level);
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
            System.out.printf("empt : %d\n", count_empty_squares(grid));
        }

        if (checkuniq) {
            start = nanotime();
            solutions = uniqsolve(grid, -1, -1);
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
            boolean solved = solve(grid, 0);
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
                    System.out.printf("diff : uniqsolve was faster by a factor of %.3f\n", fastdiff / uniqdiff);
                }
            }
        } else {
            if (! quiet) {
                System.out.printf("solu : none\n");
            }
        }

        return(solutions);
    }

    private static int[][] generate() {
        int tried[][] = new int[SIZE][SIZE];
        int grid[][] = new int[SIZE][SIZE];
        int workgrid[][] = new int[SIZE][SIZE];
        double start;
        double end;
        double diff;

        start = nanotime();
        randsolve(grid, 0);
        end = nanotime();
        diff = end - start;

        System.out.printf("generate solu : %s\n", grid_to_str(grid));
        System.out.printf("generate time : %.6f\n", diff);

        int count_empty = 0;
        int max_empty = 61;

        start = nanotime();

        while (true) {
            int r = randintmod(SIZE);
            int c = randintmod(SIZE);

            if (tried[r][c] > 0) {
//                System.out.printf("%d,%d already checked\n", r, c);
                continue;
            }

            tried[r][c] = 1;

            if (grid[r][c] == UNASSIGNED) {
//                System.out.printf("%d,%d unassigned\n", r, c);
                continue;
            }

            gridcopy(workgrid, grid);
            workgrid[r][c] = UNASSIGNED;

            int solutions = uniqsolve(workgrid, r, c);

            if (solutions == 1) {
                grid[r][c] = UNASSIGNED;
                count_empty++;
//                System.out.printf("prune puzz : %s\n", grid_to_str(grid));
//                System.out.printf("%d,%d is now empty\n", r, c);
            }

            if (count_empty == max_empty) {
//                System.out.printf("%d,%d hit max empty\n", r, c);
                break;
            }

            int rc[] = first_empty_square(tried);
            if (rc[0] == -1) {
//                System.out.printf("%d,%d all squares checked\n", r, c);
                break;
            }
        }

        end = nanotime();
        diff = end - start;

        System.out.printf("prune time : %.6f\n", diff);

        System.out.printf("generate puzz : %s\n", grid_to_str(grid));

        System.out.printf("generate empt : %d (%d)\n", count_empty, max_empty);

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
            double start = nanotime();
            for (int num = 0; num < generate_count; num++) {
                generate();
            }
            double end = nanotime();
            double diff = end - start;
            System.out.printf("total time : %.6f\n", diff);
            System.out.printf("total rate : %.6f puzz/s\n", generate_count / diff);
            System.out.printf("total puzz : %d\n", generate_count);

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
            timed_solve(grid, true, quiet);
        }

        double end = nanotime();

        double diff = end - start;

        System.out.printf("total puzz : %d\n", count);
        System.out.printf("total time : %.6f\n", diff);

        return;
    }
}
