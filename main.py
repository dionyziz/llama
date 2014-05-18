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

import lexer as lex
import parser as p

# Compiler invokation options and switches.
# Available to all modules.
opts = collections.defaultdict(lambda: None)


def mk_CLI_parser():
    '''Generates a CLI parser for the llama compiler'''

    CLI_parser = argparse.ArgumentParser(description='Invoke llama compiler.')

    CLI_parser.add_argument(
        '-i',
        '--input',
        help='''
            The input file. If ommitted, input is read from stdin.
            ''',
        nargs='?'
    )

    CLI_parser.add_argument(
        '-o',
        '--output',
        help='''
            The output file. If ommitted, normal output is written to stdout.
            ''',
        nargs='?'
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
            Output the parser state during parsing (stack, current item, etc).
            Report any parsing errors to stderr.
            ''',
        action='store_true',
        default=0
    )
    return CLI_parser


# One function to invoke them all!
def main():
    # Parse command line
    parser = mk_CLI_parser()
    args = parser.parse_args()

    # Store options & switches in global dict
    opts['input'] = args.input
    opts['output'] = args.output
    opts['lexer_debug'] = args.lexer_debug
    opts['parser_debug'] = args.parser_debug

    lxr = lex.LlamaLexer(debug=opts['lexer_debug'])
    prsr = p.LlamaParser()
    prsr.parse(lexer=lxr, input_file=opts['input'], debug=opts['parser_debug'])

if __name__ == '__main__':
    main()
