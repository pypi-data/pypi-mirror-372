import re
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import *


class Severity(StrEnum):
    """ Basically, severity from Pylint. It just makes sense. """
    
    Refactor = 'refactor'
    """ For a "good practice" metric violation """
    
    Convention = 'convention'
    """ For coding standard violation """
    
    Warning = 'warning'
    """ For stylistic problems, or minor programming issues """
    
    Error = 'error'
    """ For important programming issues (i.e. most probably bug) """
    
    Fatal = 'fatal'
    """ For errors which prevented further processing """
    
    Informational = 'info'
    """ Messages that linter emits (do not contribute to your analysis score) """


class BaseCategory(IntEnum):
    pass


@dataclass
class ViolationPrototype[C: BaseCategory]:
    error_code: str
    error_code_class: str
    error_code_number: int
    
    severity: Severity = None # will be present after pre-parsing
    provider: str | None = None
    string_id: str | None = None
    category: C | None = None
    summary: str | None = None
    details: Any = None


def error_code_pattern_gen(prefix: str, code_length: int) -> Pattern[str]:
    return re.compile(f'(?:{prefix}{{{code_length}}})')


__all__ = \
[
    'Severity',
    'BaseCategory',
    'ViolationPrototype',
    
    'error_code_pattern_gen',
]
