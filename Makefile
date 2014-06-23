PYTHON=python3
PREPARE_FLAG=--prepare
OPT=-OO
SOURCEFILES=lexer.py parser.py error.py main.py symbol.py type.py
TESTPATH=./tests/

.PHONY: beauty clean prepare static test

all: clean prepare test

beauty:
	pep8 --ignore=E221 $(SOURCEFILES) $(TESTPATH)

test: clean prepare ptest.sh
	./ptest.sh
	nosetests

static:
	pylint -E $(SOURCEFILES)

prepare:
	$(PYTHON) main.py $(PREPARE_FLAG)

clean:
	$(RM) lextab.py parsetab.py parser.out
