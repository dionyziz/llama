#!/bin/sh

TEST_PATH=tests

for i in `find tests -iname 'test_*.py'`; do
    echo ".: Unit Testing: $i"
    nosetests $i --nocapture || exit 2
    echo
done
