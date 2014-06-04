#!/bin/sh

for i in $( ls ./test/correct ); do
    echo ".: Testing: $i"
    python3 -OO main.py -i ./test/correct/$i
done
