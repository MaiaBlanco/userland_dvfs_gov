sudo /home/odroid/PARSEC/parsec-3.0/bin/parsecmgmt -a run -p bodytrack -i $1 -n $2 -c gcc-openmp -s "sudo taskset --all-tasks $3"
