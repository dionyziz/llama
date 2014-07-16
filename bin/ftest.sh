#!/bin/sh

TEST_PATH=tests/correct

for i in $(ls $TEST_PATH); do
    echo ".: Testing: $i"
    python3 main.py -i $TEST_PATH/$i
    if [ $? -ne 0 ]; then
        exit 1
    fi
done
