#!/bin/sh

for i in $( ls ./test/correct ); do
    echo ".: Testing: $i"
    python3 main.py -i ./test/correct/$i
done
