from linter_adapters.common import BaseCategory, Severity
from linter_adapters.parser import BaseViolationParser


class Flake8StringFormatCategory(BaseCategory):
    ImplicitParameters  = 100
    MissingValues       = 200
    UnusedValues        = 300

@BaseViolationParser.register_decorator('FMT')
class Flake8StringFormatViolationParser(BaseViolationParser[Flake8StringFormatCategory]):
    ViolationCategory = Flake8StringFormatCategory
    provider_name = 'flake8-string-format'
    severity_mapping = \
    {
        Flake8StringFormatCategory.ImplicitParameters:  Severity.Error,
        Flake8StringFormatCategory.MissingValues:       Severity.Error,
        Flake8StringFormatCategory.UnusedValues:        Severity.Warning,
    }
    default_severity = Severity.Warning


__all__ = \
[
    'Flake8StringFormatCategory',
    'Flake8StringFormatViolationParser',
]
