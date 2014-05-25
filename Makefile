PYTHON=python3
PREPARE_FLAG=--prepare
OPT=-OO

.PHONY: clean prepare

all:

prepare:
	$(PYTHON) main.py $(PREPARE_FLAG)

clean:
	$(RM) lextab.py parsetab.py parser.out
