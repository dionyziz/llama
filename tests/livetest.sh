#!/bin/bash
fswatch -o compiler/parse.py tests/test_parser.py|while read line; do nosetests tests/test_parser.py; done
