"""
# ----------------------------------------------------------------------
# main.py
#
# Main module for the Llama compiler
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Author: Nick Korasidis <Renelvon@gmail.com>
# ----------------------------------------------------------------------
"""

import argparse
import collections
import logging
import sys

from compiler import lex, parse, error

# Compiler invocation options and switches.
# Available to all modules.
OPTS = collections.defaultdict(lambda: None)


def mk_cli_parser():
    """Generate a cli parser for the llama compiler."""

    cli_parser = argparse.ArgumentParser(
        description='Llama compiler.',
        epilog='Use at your own RISC.'
    )

    cli_parser.add_argument(
        '-i',
        '--input',
        help='''
            The input file. If ommitted, input is read from stdin.
            ''',
        nargs='?',
        const=None,
        default='<stdin>'
    )

    cli_parser.add_argument(
        '-o',
        '--output',
        help='''
            The output file. If ommitted, it defaults to a.out.
            ''',
        nargs='?',
        default='a.out'
    )

    cli_parser.add_argument(
        '-pp',
        '--prepare',
        help='''
            Build the lexing and parsing tables and exit.
            ''',
        action='store_true',
        default=False
    )

    cli_parser.add_argument(
        '-lv',
        '--lexer_verbose',
        help='''
            Output the lexed tokens along with their file position to stdout.
            Report any lexing errors to stderr.
            ''',
        action='store_true',
        default=False
    )

    cli_parser.add_argument(
        '-pv',
        '--parser_verbose',
        help='''
            Output the parser state during parsing (token, item, etc).
            Report any parsing errors to stderr.
            ''',
        action='store_true',
        default=False
    )
    return cli_parser


def read_program(input_file):
    """
    Read input from file or stdin (if a file is not provided).
    Return read program as a single string.
    """
    if input_file == '<stdin>':
        sys.stdout.write("Reading from stdin (type <EOF> to end):\n")
        sys.stdout.flush()
        data = sys.stdin.read()
    else:
        try:
            file = open(input_file)
            data = file.read()
            file.close()
        except IOError:
            sys.exit(
                'Could not open file %s for reading. Aborting.'
                % input_file
            )
    return data


def main():
    """One function to invoke them all!"""

    # Parse command line.
    parser = mk_cli_parser()
    args = parser.parse_args()

    # Store options & switches in global dict.
    OPTS['input'] = args.input
    OPTS['output'] = args.output
    OPTS['prepare'] = args.prepare
    OPTS['lexer_verbose'] = args.lexer_verbose
    OPTS['parser_verbose'] = args.parser_verbose

    logger = error.Logger(inputfile=OPTS['input'], level=logging.DEBUG)

    lexer = lex.Lexer(logger=logger, verbose=OPTS['lexer_verbose'])

    parser = parse.Parser(logger=logger, verbose=OPTS['parser_verbose'])

    # Stop here if this a dry run.
    if OPTS['prepare']:
        print('Finished generating lexer and parser tables. Exiting...')
        return

    # Get some input.
    data = read_program(OPTS['input'])

    # Parse and construct the AST.
    ast = parser.parse(data=data, lexer=lexer)

    # On bad program, terminate with error.
    if not logger.success:
        sys.exit(1)

if __name__ == '__main__':
    main()
