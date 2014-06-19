#!/bin/sh

TEST_PATH=tests/correct

for i in $(ls $TEST_PATH); do
    echo ".: Testing: $i"
    python3 main.py -i $TEST_PATH/$i
done
