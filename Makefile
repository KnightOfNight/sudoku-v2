
# default - binaries
default: binaries

# all binaries
binaries: bin/csudoku bin/gsudoku bin/jsudoku bin/psudoku

# maven project
project :
	@echo "building project"
	@cd sudoku.project && make

# Docker image

# variables
log := last-build.txt
serial := $(shell docker/serial.sh)

# targets
docker : $(log)
$(log) : Dockerfile project
	@echo "building image"
	@echo $(serial) | tee $(log)
	@docker build --no-cache -t knightofnight/sudoku:$(serial) . 2>&1 | tee -a $(log)
	@docker tag knightofnight/sudoku:$(serial) knightofnight/sudoku:latest 2>&1 | tee -a $(log)

# single binary
bin/csudoku : src/sudoku.c
	@echo "compiling csudoku"
	@cc -o bin/csudoku -Wall src/sudoku.c

# single binary
bin/gsudoku: src/sudoku.go
	@echo "compiling gsudoku"
	@go build -o bin/gsudoku src/sudoku.go

# alias to sudoku.class
bin/jsudoku: lib/sudoku.class
# single binary
lib/sudoku.class: src/sudoku.java
	@echo "compiling jsudoku"
	@javac -d lib src/sudoku.java

# alias to sudoku python files
bin/psudoku: lib/sudoku.pyc lib/gridutils.pyc lib/config.pyc lib/draw.pyc lib/util.pyc

# single binary
lib/%.pyc : src/python/%.py
	@echo "compiling $@"
	@python3 -c "import py_compile; py_compile.compile('$<', cfile='$@', doraise=True)"

# clean everything
clean: cleanbinaries cleanproject

# clean binaries
cleanbinaries:
	@echo "removing binaries"
	@rm -vf bin/csudoku bin/gsudoku lib/sudoku.class lib/*.pyc 2>/dev/null

# clean project
cleanproject:
	@echo "cleaning project"
	@cd sudoku.project && make clean

# sample test report
sample: binaries
	@echo "sample test report"
	@echo
	@echo "language: c"
	@bin/csudoku --sample
	@echo
	@echo "language: go"
	@bin/gsudoku --sample
	@echo
	@echo "language: python"
	@bin/psudoku --sample

# list make targets
list:
	@egrep -B 1 -e "^[a-zA-Z]" Makefile | cut -f 1 -d : | sed -e "s/--//"
