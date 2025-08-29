from functools import cached_property
from typing import *

from linter_adapters.common import BaseCategory, Severity, ViolationPrototype
from linter_adapters.parser import BaseViolationParser


try:
    from flake8_rst_docstrings import code_mappings_by_level as rst_docstrings_violations_mapping
except ImportError:
    rst_docstrings_violations_mapping = dict()
    
try:
    from flake8_rst_docstrings import rst_prefix, rst_fail_load, rst_fail_lint
except ImportError:
    rst_prefix = 'RST'
    rst_fail_load = 900
    rst_fail_lint = 903


class Flake8RSTDocstringsCategory(BaseCategory):
    Info            = 100
    Warning         = 200
    Error           = 300
    Severe          = 400
    ParsingError    = 900

@BaseViolationParser.register_decorator('RST')
class Flake8RSTDocstringsViolationParser(BaseViolationParser[Flake8RSTDocstringsCategory]):
    ViolationCategory = Flake8RSTDocstringsCategory
    provider_name = 'flake8-rst-docstrings'
    severity_mapping = \
    {
        Flake8RSTDocstringsCategory.Info:           Severity.Warning,
        Flake8RSTDocstringsCategory.Warning:        Severity.Warning,
        Flake8RSTDocstringsCategory.Error:          Severity.Error,
        Flake8RSTDocstringsCategory.Severe:         Severity.Error,
        Flake8RSTDocstringsCategory.ParsingError:   Severity.Fatal,
    }
    default_severity = Severity.Warning
    
    @override
    def _summary_mapping_gen(self) -> Iterator[Tuple[str, str]]:
        for hundreds, mapping_per_level in rst_docstrings_violations_mapping.items():
            for text, units in mapping_per_level.items():
                yield f'{rst_prefix}{hundreds * self.violation_code_number_base + units :03}', text
        
        yield f'{rst_prefix}{rst_fail_load}', "Failed to load file"
        yield f'{rst_prefix}{rst_fail_lint}', "Failed to lint RST-docstring"


__all__ = \
[
    'Flake8RSTDocstringsCategory',
    'Flake8RSTDocstringsViolationParser',
]
