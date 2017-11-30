#!/bin/bash
echo 'RUNNING FOR 60 SECONDS.'
end=$((SECONDS+60))
while [ $SECONDS -lt $end ]; 
do
echo "hello" > /dev/null
done
