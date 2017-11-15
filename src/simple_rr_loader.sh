#!/bin/bash
echo "Sleeping for 10s, then starting individual CPU loading tests."
sleep 10
echo "Started on core 0."
taskset 0x01 ./load.sh
echo "Done on core 0. Starting core 1 in 10 seconds."
sleep 10
taskset 0x02 ./load.sh
echo "Done on core 1. Starting core 2 in 10 seconds."
sleep 10
taskset 0x04 ./load.sh
echo "Done on core 2. Starting core 3 in 10 seconds."
sleep 10
taskset 0x08 ./load.sh
echo "Done on core 3. Starting core 4 in 10 seconds."
sleep 10
taskset 0x10 ./load.sh
echo "Done on core 4. Starting core 5 in 10 seconds."
sleep 10
taskset 0x20 ./load.sh
echo "Done on core 5. Starting core 6 in 10 seconds."
sleep 10
taskset 0x40 ./load.sh
echo "Done on core 6. Starting core 7 in 10 seconds."
sleep 10
taskset 0x80 ./load.sh
echo "Finished all runs on all 8 cores."
