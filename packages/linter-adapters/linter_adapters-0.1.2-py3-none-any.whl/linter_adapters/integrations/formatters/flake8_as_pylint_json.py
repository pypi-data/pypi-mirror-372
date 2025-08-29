"""
Inspired by `flake8_for_pycharm` package.
Original authors:
* Copyright (C) 2017-2018 Ian Stapleton Cordasco <graffatcolmingov@gmail.com> - license holder
* Ramast Magdy - publisher

Author of this module: Peter Zaitcev / USSX-Hares, 2025
"""

import json

from flake8.formatting.base import BaseFormatter
from flake8.violation import Violation

from linter_adapters.common import Severity
from linter_adapters.parser import BaseViolationParser
from .pylint import PylintMessage


_END_OF_OUTPUT = PylintMessage \
(
    type = Severity.Informational.value,
    module = '',
    obj = '',
    line = 1,
    column = 0,
    endColumn = None,
    endLine = None,
    path = '/dev/null',
    symbol = 'eof',
    message = "This is end of file",
    message_id = 'I000',
)

_PYFLAKES_MAP: dict[str, str] | None = None


class PylintJson(BaseFormatter):
    def __init__(self, options):
        self.first_error: bool = True
        super(PylintJson, self).__init__(options)
    
    def write_line(self, line):
        """Override write for convenience."""
        self.write(line, None)
    
    def start(self):
        self.newline = '\n'
        self.write_line('[')
    
    def stop(self):
        if (self.newline != '\n'):
            self.newline = '\n'
            self.write_line(self.format_pylint_message(_END_OF_OUTPUT))
        self.newline = '\n'
        self.write_line(']')
    
    def format_pylint_message(self, message: PylintMessage) -> str:
        indent = ' ' * 4
        formatted = json.dumps(message.asdict(), indent=indent)
        formatted = indent + formatted.replace('\n', '\n' + indent)
        return formatted
    
    def format(self, violation: Violation) -> str:
        """ Format a violation. """
        
        formatted = Flake8ToPylint.convert_violation(violation)
        
        max_line_length = 999
        if (violation.physical_line):
            max_line_length = len(violation.physical_line)
        if (violation.column_number >= max_line_length):
            formatted = formatted._replace(column=max_line_length - 1)
        
        return self.format_pylint_message(formatted)
    
    def handle(self, error: Violation):
        self.newline = ',\n'
        self.write_line(self.format(error))


class Flake8ToPylint:
    @classmethod
    def convert_violation(cls, error: Violation) -> PylintMessage:
        violation_prototype = BaseViolationParser.parse_using_registry(error)
        formatted = PylintMessage \
        (
            type = (violation_prototype.severity or Severity.Convention).value,
            module = BaseViolationParser.parse_module_name(error.filename),
            obj = "",
            line = error.line_number,
            column = error.column_number,
            endColumn = None,
            endLine = None,
            path = error.filename,
            symbol = violation_prototype.string_id or error.code,
            message = f"[{error.code}] {error.text}",
            message_id = error.code,
        )
        
        return formatted


__all__ = \
[
    'PylintJson',
    'Flake8ToPylint',
]
