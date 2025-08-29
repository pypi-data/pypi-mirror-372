from typing import Dict

from linter_adapters.common import BaseCategory, Severity, ViolationPrototype
from linter_adapters.parser import BaseViolationParser


class Flake8CCategory(BaseCategory):
    Comprehensions      = 400
    CommasPlacement     = 800
    McCabeComplexity    = 900

@BaseViolationParser.register_decorator('C')
class Flake8ComprehensionOrMcCabeViolationParser(BaseViolationParser[Flake8CCategory]):
    """ Both use error class 'C' """
    
    provider_name = 'comprehensions-or-commas-or-mccabe'
    ViolationCategory = Flake8CCategory
    severity_mapping = \
    {
        Flake8CCategory.Comprehensions:     Severity.Refactor,
        Flake8CCategory.CommasPlacement:    Severity.Convention,
        Flake8CCategory.McCabeComplexity:   Severity.Refactor,
    }
    default_severity = Severity.Warning
    
    provider_names_mapping: Dict[Flake8CCategory, str] = \
    {
        Flake8CCategory.Comprehensions:     'flake8-comprehensions',
        Flake8CCategory.CommasPlacement:    'flake8-commas',
        Flake8CCategory.McCabeComplexity:   'mccabe',
    }
    
    def parse_violation_extras(self, violation: ViolationPrototype[Flake8CCategory]) -> ViolationPrototype[Flake8CCategory]:
        if (violation.category in self.provider_names_mapping):
            violation.provider = self.provider_names_mapping[violation.category]
        
        return violation


__all__ = \
[
    'Flake8CCategory',
    'Flake8ComprehensionOrMcCabeViolationParser',
]
