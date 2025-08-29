from __future__ import annotations

import typing
from typing import *

from linter_adapters.common import BaseCategory, Severity, ViolationPrototype
from linter_adapters.parser import BaseViolationParser


try:
    from flake8.plugins.pyflakes import FLAKE8_PYFLAKES_CODES
    from pyflakes import messages as pyflakes_messages
except ImportError:
    FLAKE8_PYFLAKES_CODES = dict()
    pyflakes_messages = object()

if (typing.TYPE_CHECKING):
    from pyflakes.messages import Message


class PyflakesCategory(BaseCategory):
    Imports = 400
    FormatStrings = 500
    Misuses = 600
    Statements = 700
    Variables = 800
    CommonMistakes = 900


@BaseViolationParser.register_decorator('F')
class PyflakesViolationParser(BaseViolationParser[PyflakesCategory]):
    provider_name = 'pyflakes'
    ViolationCategory = PyflakesCategory
    severity_mapping = \
    {
        PyflakesCategory.Imports:           Severity.Error,
        PyflakesCategory.FormatStrings:     Severity.Error,
        PyflakesCategory.Misuses:           Severity.Error,
        PyflakesCategory.Statements:        Severity.Error,
        PyflakesCategory.Variables:         Severity.Warning,
        PyflakesCategory.CommonMistakes:    Severity.Error,
    }
    default_severity = Severity.Error
    
    pyflakes_reverse_mapping: Dict[str, str] = { value: key for key, value in FLAKE8_PYFLAKES_CODES.items() }
    def get_pyflakes_message_summary(self, violation: ViolationPrototype) -> Optional[str]:
        msg_cls: Optional[Message] = getattr(pyflakes_messages, violation.string_id or '', None)
        return msg_cls and msg_cls.message or None
    
    def parse_violation_extras(self, violation: ViolationPrototype[PyflakesCategory]) -> ViolationPrototype[PyflakesCategory]:
        violation.string_id = self.pyflakes_reverse_mapping.get(violation.error_code)
        violation.summary = self.get_pyflakes_message_summary(violation)
        return violation


__all__ = \
[
    'PyflakesCategory',
    'PyflakesViolationParser',
]
