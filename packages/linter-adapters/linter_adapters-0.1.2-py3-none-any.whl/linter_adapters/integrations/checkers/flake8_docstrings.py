from __future__ import annotations

import functools
import typing
from typing import *

from linter_adapters.common import BaseCategory, Severity, ViolationPrototype
from linter_adapters.parser import BaseViolationParser


try:
    from pydocstyle import violations as pydocstyle_violations
except ImportError:
    pydocstyle_violations = object


if (typing.TYPE_CHECKING):
    from pydocstyle.violations import ErrorParams


class Flake8DocstringsCategory(BaseCategory):
    MissingDocstrings       = 100
    WhitespaceIssues        = 200
    QuotesIssues            = 300
    DocstringContentIssues  = 400
    DocstringParsingError   = 900

@BaseViolationParser.register_decorator('D')
class Flake8DocstringsViolationParser(BaseViolationParser[Flake8DocstringsCategory]):
    ViolationCategory = Flake8DocstringsCategory
    provider_name = 'flake8-docstrings'
    severity_mapping = \
    {
        Flake8DocstringsCategory.MissingDocstrings:         Severity.Warning,
        Flake8DocstringsCategory.WhitespaceIssues:          Severity.Warning,
        Flake8DocstringsCategory.QuotesIssues:              Severity.Warning,
        Flake8DocstringsCategory.DocstringContentIssues:    Severity.Error,
        Flake8DocstringsCategory.DocstringParsingError:     Severity.Fatal,
    }
    default_severity = Severity.Warning
    
    def get_pydocstyle_violation_info(self, violation: ViolationPrototype) -> Optional[str]:
        partial: Optional[functools.partial] = violation and getattr(pydocstyle_violations, violation.error_code, None)
        info: Optional[ErrorParams] = partial and partial()
        msg: Optional[str] = info and info.short_desc
        return msg
    
    def parse_violation_extras(self, violation: ViolationPrototype[Flake8DocstringsCategory]) -> ViolationPrototype[Flake8DocstringsCategory]:
        violation.summary = self.get_pydocstyle_violation_info(violation)
        return violation


__all__ = \
[
    'Flake8DocstringsCategory',
    'Flake8DocstringsViolationParser',
]
