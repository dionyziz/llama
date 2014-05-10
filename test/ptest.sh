#!/bin/sh

CDIR="../c/"
OCAMLDIR="../OCaml"
PYTHONDIR=="../python"
case $1 in
    OCaml)
        make -C $OCAMLDIR depend
        make -C $OCAMLDIR spit
        for i in $( ls ./correct ); do
            echo ".: Testing: $i"
            ../OCaml/spit ../test/correct/$i
        done
    ;;
    c)
        make -C $CDIR
        for i in $( ls ./correct ); do
            echo ".: Testing: $i"
            ../c/spit < ../test/correct/$i
        done
    ;;
    python)
        make -C $PYTHONDIR all
        for i in $( ls ./correct ); do
            echo ".: Testing: $i"
            python3 ../python/lexer.py ../test/correct/$i
        done
esac
