import functools
from typing import *

from linter_adapters.common import BaseCategory, Severity, ViolationPrototype
from linter_adapters.parser import BaseViolationParser


try:
    import bugbear
except ImportError:
    bugbear = None


class Flake8BugbearCategory(BaseCategory):
    ProbablyErrors  = 000
    Optimizations   = 900

@BaseViolationParser.register_decorator('B')
class Flake8BugbearViolationParser(BaseViolationParser[Flake8BugbearCategory]):
    ViolationCategory = Flake8BugbearCategory
    provider_name = 'flake8-bugbear'
    severity_mapping = \
    {
        Flake8BugbearCategory.ProbablyErrors:   Severity.Error,
        Flake8BugbearCategory.Optimizations:    Severity.Refactor,
    }
    default_severity = Severity.Error
    
    def get_bugbear_violation_info(self, violation: ViolationPrototype) -> Optional[str]:
        partial: Optional[functools.partial] = violation and getattr(bugbear, violation.error_code, None)
        msg: Optional[str] = partial and partial.keywords.get('message')
        return msg
    
    def parse_violation_extras(self, violation: ViolationPrototype[Flake8BugbearCategory]) -> ViolationPrototype[Flake8BugbearCategory]:
        violation.details = self.get_bugbear_violation_info(violation)
        return violation


__all__ = \
[
    'Flake8BugbearCategory',
    'Flake8BugbearViolationParser',
]
