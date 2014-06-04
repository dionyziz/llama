PYTHON=python3
PREPARE_FLAG=--prepare
OPT=-OO

.PHONY: clean prepare test alltest

all: clean prepare test

test:
	$(PYTHON) main.py -i test/correct/fibonacci.lla

alltest: clean prepare ptest.sh
	./ptest.sh

prepare:
	$(PYTHON) main.py $(PREPARE_FLAG)

clean:
	$(RM) lextab.py parsetab.py parser.out
