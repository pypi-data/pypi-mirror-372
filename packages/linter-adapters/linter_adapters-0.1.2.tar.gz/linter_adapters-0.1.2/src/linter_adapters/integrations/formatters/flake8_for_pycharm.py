import sys
import textwrap
from argparse import ArgumentParser, Namespace
from typing import *

from flake8.main.cli import main as flake8_main

from linter_adapters.integrations import register_all
from linter_adapters.parser import BaseViolationParser
from linter_adapters.types import ImportableFunction


MainFunction: TypeAlias = Callable[[Sequence[str]], int | None]

class ArgumentsNamespace(Namespace):
    output_format: Literal['text', 'json'] = 'text'
    paths: Sequence[str] | None = None
    help_msg: Sequence[str] | None = None
    flake8_main: ImportableFunction[MainFunction] | None = None

def explain(*error_codes: str) -> int:
    for error_code in error_codes:
        try:
            violation_prototype = BaseViolationParser.parse_using_registry(error_code, optimistic=False)
        except (ImportError, AttributeError, ValueError, LookupError, AssertionError):
            violation_prototype = None
        
        if (violation_prototype is None):
            print(f"No such message id or symbol '{error_code}'.")
        else:
            if (violation_prototype.string_id):
                print(f":{violation_prototype.string_id} ({violation_prototype.error_code})", end=' ')
            else:
                print(violation_prototype.error_code, end=' ')
            print(f"from {violation_prototype.provider}")
            
            if (violation_prototype.summary):
                print(textwrap.indent(violation_prototype.summary, ' ' * 2))
            if (violation_prototype.details and len(error_codes) == 1):
                print(textwrap.indent(violation_prototype.details, ' ' * 4))
        
        print()
    
    return 0

def run(argv: Sequence[str], *, parsed_args: ArgumentsNamespace = None) -> int:
    argv = list(argv)
    parsed_args = parsed_args or ArgumentsNamespace()
    
    match parsed_args.output_format:
        case 'text':
            fmt = 'pylint'
        case 'json':
            fmt = 'pylint-json'
        case _:
            fmt = None
    
    if (fmt is not None):
        argv.insert(0, f'--format={fmt}')
    
    argv.extend(parsed_args.paths or ())
    
    run_flake8 = parsed_args.flake8_main.func if (parsed_args.flake8_main) else flake8_main
    return run_flake8(argv) or 0


def make_argument_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('--help-msg', type=lambda s: cast(str, s).split(','), default=ArgumentsNamespace.help_msg)
    parser.add_argument('--output-format', '-f', choices=[ 'text', 'json' ], default=ArgumentsNamespace.output_format)
    parser.add_argument('--flake8-main', '-F', type=ImportableFunction[MainFunction], default=ArgumentsNamespace.flake8_main)
    parser.add_argument('paths', type=str, nargs='*', default=ArgumentsNamespace.paths)
    return parser


def main(argv: Sequence[str] = None) -> int:
    if (argv is None):
        argv = sys.argv[1:]
    
    parser = make_argument_parser()
    parsed, unparsed = parser.parse_known_args(argv, namespace=ArgumentsNamespace())
    
    register_all()
    
    if (parsed.help_msg is not None):
        return explain(*parsed.help_msg)
    else:
        return run(unparsed, parsed_args=parsed)

if (__name__ == '__main__'):
    main()


__all__ = \
[
    'ArgumentsNamespace',
    
    'explain',
    'main',
    'make_argument_parser',
    'run',
]
