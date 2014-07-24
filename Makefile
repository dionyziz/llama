PYTHON=python3
PREPARE_FLAGS=--prepare -pd
OPT=-OO
SOURCEFILES=main.py ./compiler/*.py
BINPATH=./bin
TESTPATH=./tests/

.PHONY: beauty clean cleanaux functionaltest prepare static test unittest

all: clean prepare test

beauty:
	pep8 --ignore=E221 $(SOURCEFILES) $(TESTPATH)

test: unittest functionaltest

unittest: $(BINPATH)/utest.sh
	$(BINPATH)/utest.sh

functionaltest: $(BINPATH)/ftest.sh
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
