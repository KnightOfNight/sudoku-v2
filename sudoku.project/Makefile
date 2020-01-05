
jar := target/sudoku-1.0.jar
log4j := deps/slf4j-simple-1.7.9.jar
rundir := run

default : build

all: build gen sol sam

build : deps $(jar)

$(jar) : src/main/java/com/sudoku/*.java pom.xml
	@mvn package
	@mkdir -p $(rundir)
	@cp target/*.jar target/lib/*.jar deps/*.jar $(rundir)

deps: $(log4j)

$(log4j) :
	@mkdir -p deps
	@cd deps && wget http://repo2.maven.org/maven2/org/slf4j/slf4j-simple/1.7.9/slf4j-simple-1.7.9.jar

clean :
	@mvn clean
	@rm -vfr deps
	@rm -vfr $(rundir)

gen : build
	@./jsudoku --generate 15

sol : build
	@./jsudoku --solve

sam : build
	@./jsudoku --sample
