WARN= -Wall -Werror -Wall
CFLAGS=

omprelease:CFLAGS+=-fopenmp -DOMP_COMPILE
omprelease: release

ompdebug:CFLAGS+=-fopenmp -DOMP_COMPILE
ompdebug: debug

release:CFLAGS+=-O3
release: all

debug:CFLAGS+=-g -O0
debug: all

all: main.o
	gcc main.o -o omp_convolve.out $(WARN) $(CFLAGS)

main.o: main.cpp net_specs.h convolve.h
	gcc -c main.cpp $(WARN) $(CFLAGS)

clean:
	$(rm *.o *.out 2> /dev/null)
	echo Removed all .o and .out files.
