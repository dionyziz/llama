#!/bin/sh

for i in $( ls ./test/correct ); do
    echo ".: Testing: $i"
    python3 main.py -i ./test/correct/$i
    if [ $? -ne 0 ]; then
        exit 1
    fi
done
