PYTHON=python3
PREPARE_FLAGS=--prepare -pd
OPT=-OO
SOURCEFILES=main.py ./compiler/*.py
BINPATH=./bin
TESTPATH=./tests/

.PHONY: beauty clean cleanaux functionaltest prepare static test unittest

all: test

beauty:
	pep8 --ignore=E221 $(SOURCEFILES) $(TESTPATH)

test:
	make -B unittest
	make -B functionaltest

unittest: cleanmain prepare $(BINPATH)/utest.sh
	$(BINPATH)/utest.sh

functionaltest: cleanmain prepare $(BINPATH)/ftest.sh
	$(BINPATH)/ftest.sh

static:
	pylint -E $(SOURCEFILES)

prepare:
	$(PYTHON) main.py $(PREPARE_FLAGS)
	$(BINPATH)/ctest.sh

cleanaux:
	$(RM) aux*.py

cleanmain:
	$(RM) lextab.py parsetab.py parser.out

clean: cleanaux cleanmain
