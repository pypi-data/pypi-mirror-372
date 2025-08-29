from functools import cached_property
from typing import *

from linter_adapters.common import BaseCategory, Severity, ViolationPrototype
from linter_adapters.parser import SingleCategoryViolationParser


@SingleCategoryViolationParser.register_decorator()
class Flake8DebuggerViolationParser(SingleCategoryViolationParser):
    provider_name = 'flake8-debugger'
    category_name = 'DebuggerUsage'
    category_number = 100
    default_prefix = 'T'
    default_severity = Severity.Error


@SingleCategoryViolationParser.register_decorator()
class Flake8ImportSortViolationParser(SingleCategoryViolationParser):
    provider_name = 'flake8-isort'
    category_name = 'ImportsPositioning'
    category_number = 000
    default_prefix = 'I'
    default_severity = Severity.Convention
    
    @override
    def _summary_mapping_gen(self) -> Iterator[Tuple[str, str]]:
        try:
            from flake8_isort import Flake8Isort
        except ImportError:
            Flake8Isort = object()
        
        pat = self.error_code_pattern()
        for name, value in Flake8Isort.__dict__.items():
            if (isinstance(value, str) and ('isort' in name or 'msg' in name) and (m := pat.match(value))):
                code = m.group(0)
                yield code, value


@SingleCategoryViolationParser.register_decorator()
class Flake8BrokenLineViolationParser(SingleCategoryViolationParser):
    provider_name = 'flake8-broken-line'
    category_name = 'Linebreaks'
    category_number = 400
    default_prefix = 'N'
    default_severity = Severity.Convention


@SingleCategoryViolationParser.register_decorator()
class Flake8DateTimeZoneViolationParser(SingleCategoryViolationParser):
    provider_name = 'flake8-datetimez'
    category_name = 'Timezone'
    category_number = 000
    default_prefix = 'DTZ'
    default_severity = Severity.Error


@SingleCategoryViolationParser.register_decorator()
class Flake8QuotesViolationParser(SingleCategoryViolationParser):
    provider_name = 'flake8-quotes'
    category_name = 'Quotes'
    category_number = 000
    default_prefix = 'Q'
    default_severity = Severity.Convention


__all__ = \
[
    'Flake8BrokenLineViolationParser',
    'Flake8DateTimeZoneViolationParser',
    'Flake8DebuggerViolationParser',
    'Flake8ImportSortViolationParser',
    'Flake8QuotesViolationParser',
]
