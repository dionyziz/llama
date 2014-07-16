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
	make -B unittest
	make -B functionaltest

unittest: clean prepare $(BINPATH)/utest.sh
	$(BINPATH)/utest.sh

functionaltest: clean prepare $(BINPATH)/ftest.sh
	$(BINPATH)/ftest.sh

static:
	pylint -E $(SOURCEFILES)

prepare:
	$(PYTHON) main.py $(PREPARE_FLAG)

clean:
	$(RM) lextab.py parsetab.py parser.out
