sudo /home/odroid/PARSEC/parsec-3.0/bin/parsecmgmt -a run -p blackscholes -n 4 -c gcc-openmp -s "sudo perf stat -I 200 -aA -C 4-7 -e cycles -e instructions -e page-faults -e LLC-load-misses -e branch-misses -e branches -o $1 taskset --all-tasks 0xf0" -i native
#./parsecmgmt -a build -p blackscholes -c gcc-openmp
