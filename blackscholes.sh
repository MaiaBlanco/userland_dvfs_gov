sudo ./parsecmgmt -a run -p blackscholes -n 4 -c gcc-openmp -s 'sudo perf stat -aA -C 4-7 taskset --all-tasks 0xf0' -i native
./parsecmgmt -a build -p blackscholes -c gcc-openmp
