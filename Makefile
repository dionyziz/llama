PYTHON=python3
PREPARE_FLAGS=--prepare -pd
OPT=-OO
SOURCEFILES=main.py ./compiler/*.py
BINPATH=./bin
TESTPATH=./tests

.PHONY: check clean cleanaux flake8check functionaltest prepare pylintcheck test unittest

all: clean prepare check test

pylintcheck:
	pylint --rcfile .pylintrc $(SOURCEFILES) $(TESTPATH)

flake8check:
	flake8 --ignore=E221 ./compiler/lex.py
	flake8 --ignore=E501 ./compiler/parse.py
	flake8 --exclude=lex.py,parse.py $(SOURCEFILES)
	flake8 --exclude=__init__.py $(TESTPATH)/*.py

check: flake8check pylintcheck

test: unittest functionaltest

unittest:
	nosetests --with-coverage --cover-package=compiler --cover-inclusive

functionaltest: $(BINPATH)/ftest.sh
	$(BINPATH)/ftest.sh

prepare:
	$(PYTHON) main.py $(PREPARE_FLAGS)
	$(BINPATH)/ctest.sh

cleanaux:
	$(RM) aux*.py

cleanmain:
	$(RM) lextab.py parsetab.py parser.out .coverage

clean: cleanaux cleanmain
