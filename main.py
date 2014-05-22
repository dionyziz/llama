# ----------------------------------------------------------------------
# main.py
#
# Main module for the Llama language
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Author: Nick Korasidis <Renelvon@gmail.com>
# ----------------------------------------------------------------------

import argparse
import collections
import sys

import error as err
import lexer as lex
import parser as prs

# Compiler invokation options and switches.
# Available to all modules.
opts = collections.defaultdict(lambda: None)


def mk_CLI_parser():
    """Generate a CLI parser for the llama compiler."""

    CLI_parser = argparse.ArgumentParser(
        description='Invoke llama compiler.',
        epilog='Use at your own RISC.'
    )

    CLI_parser.add_argument(
        '-i',
        '--input',
        help='''
            The input file. If ommitted, input is read from stdin.
            ''',
        nargs='?',
        const=None,
        default=None
    )

    CLI_parser.add_argument(
        '-o',
        '--output',
        help='''
            The output file. If ommitted, it defaults to a.out.
            ''',
        nargs='?',
        default='a.out'
    )

    CLI_parser.add_argument(
        '-ld',
        '--lexer_debug',
        help='''
            Output the lexed tokens along with their file position to stdout.
            Report any lexing errors to stderr.
            ''',
        action='store_true',
        default=False
    )

    CLI_parser.add_argument(
        '-pd',
        '--parser_debug',
        help='''
            Output the parser state during parsing (token, item, etc).
            Report any parsing errors to stderr.
            ''',
        action='store_true',
        default=0
    )
    return CLI_parser


def input(input_file=None):
    """
    Read input from file or stdin (if a file is not provided).
    Return read input as a single string.
    """
    if input_file:
        try:
            fd = open(input_file)
            data = fd.read()
            fd.close()
        except IOError as e:
            sys.exit(
                'Could not open file %s for reading. Aborting.'
                % input_file
            )
    else:
        opts['input'] = '<stdin>'
        sys.stdout.write("Reading from stdin (type <EOF> to end):\n")
        sys.stdout.flush()
        data = sys.stdin.read()
    return data


# One function to invoke them all!
def main():
    # Parse command line.
    parser = mk_CLI_parser()
    args = parser.parse_args()

    # Store options & switches in global dict.
    opts['input'] = args.input
    opts['output'] = args.output
    opts['lexer_debug'] = args.lexer_debug
    opts['parser_debug'] = args.parser_debug

    # Make a lexer.
    lexer = lex.LlamaLexer(debug=opts['lexer_debug'])
    lexer.build()

    # Make a parser.
    parser = prs.LlamaParser()

    # Get some input.
    data = input(opts['input'])

    # Initiaize the error logger
    err.init_logger(opts['input'])

    # Parse.
    parser.parse(
        lexer=lexer,
        data=data,
        debug=opts['parser_debug'])

    # Output all errors and warnings to stderr.
    for msg in err.get_all_signals():
        print(msg, file=sys.stderr)

if __name__ == '__main__':
    main()
