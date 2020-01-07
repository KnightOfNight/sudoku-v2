FROM knightofnight/aws-java
WORKDIR /
COPY sudoku.class .
COPY jsudoku .
ENTRYPOINT ["/jsudoku", "--generate", "10"]
