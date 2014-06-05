PYTHON=python3
PREPARE_FLAG=--prepare
OPT=-OO

.PHONY: clean prepare test

all: clean prepare test

test: clean prepare ptest.sh
	./ptest.sh

prepare:
	$(PYTHON) main.py $(PREPARE_FLAG)

clean:
	$(RM) lextab.py parsetab.py parser.out
