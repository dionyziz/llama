PYTHON=python3
PREPARE_FLAGS=--prepare -pd
OPT=-OO
SOURCEFILES=main.py ./compiler/*.py
BINPATH=./bin
TESTPATH=./tests

.PHONY: check clean cleanaux functionaltest prepare test unittest

all: clean prepare test

check:
	flake8 --ignore=E221 ./compiler/lex.py
	flake8 --ignore=E501 ./compiler/parse.py
	flake8 --exclude=lex.py,parse.py $(SOURCEFILES)
	flake8 --exclude=__init__.py $(TESTPATH)/*.py
	pylint -E --ignore=test_lexer.py $(SOURCEFILES) $(TESTPATH)
	pylint -E -d E1101 $(TESTPATH)/test_lexer.py

test: unittest functionaltest

unittest: $(BINPATH)/utest.sh
	$(BINPATH)/utest.sh

functionaltest: $(BINPATH)/ftest.sh
	$(BINPATH)/ftest.sh

prepare:
	$(PYTHON) main.py $(PREPARE_FLAGS)
	$(BINPATH)/ctest.sh

cleanaux:
	$(RM) aux*.py

cleanmain:
	$(RM) lextab.py parsetab.py parser.out

clean: cleanaux cleanmain
