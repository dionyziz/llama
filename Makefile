PYTHON=python3
PREPARE_FLAG=--prepare
OPT=-OO
SOURCEFILES=main.py ./compiler/*.py
BINPATH=./bin
TESTPATH=./tests/

.PHONY: beauty clean functionaltest prepare static test unittest

all: test

beauty:
	pep8 --ignore=E221 $(SOURCEFILES) $(TESTPATH)

test:
	make clean
	make prepare
	make unittest
	make clean
	make prepare
	make functionaltest

unittest:
	for i in `find tests -iname 'test_*.py'`; do echo "\n\nRunning $$i"; nosetests $$i || exit 2; done

functionaltest: $(BINPATH)/ptest.sh
	$(BINPATH)/ptest.sh

static:
	pylint -E $(SOURCEFILES)

prepare:
	$(PYTHON) main.py $(PREPARE_FLAG)

clean:
	$(RM) lextab.py parsetab.py parser.out
