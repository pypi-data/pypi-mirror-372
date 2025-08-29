import textwrap
from functools import cached_property
from typing import *

from linter_adapters.common import BaseCategory, Severity, ViolationPrototype
from linter_adapters.parser import BaseViolationParser

try:
    from pycodestyle import _checks as pycodestyle_checks, tabs_or_spaces
except ImportError:
    pycodestyle_checks = dict()
    tabs_or_spaces = object()

class PycodestyleCategory(BaseCategory):
    Indentation = 100
    Whitespace  = 200
    BlankLines  = 300
    Imports     = 400
    LineLength  = 500
    Deprecation = 600
    Statements  = 700
    Comments    = 800   # comes from flake8-eradicate
    SyntaxError = 900

class PycodestyleCheck(NamedTuple):
    category_name: str
    error_codes: List[str]
    args: List[str]
    obj: Any
    docstring: str

@BaseViolationParser.register_decorator('E', 'W')
class PycodestyleViolationParser(BaseViolationParser[PycodestyleCategory]):
    provider_name = 'pycodestyle'
    ViolationCategory = PycodestyleCategory
    severity_mapping = \
    {
        PycodestyleCategory.Indentation:    Severity.Error,
        PycodestyleCategory.Whitespace:     Severity.Error,
        PycodestyleCategory.BlankLines:     Severity.Convention,
        PycodestyleCategory.Imports:        Severity.Convention,
        PycodestyleCategory.LineLength:     Severity.Convention,
        PycodestyleCategory.Deprecation:    Severity.Warning,
        PycodestyleCategory.Statements:     Severity.Warning,
        PycodestyleCategory.Comments:       Severity.Error,
        PycodestyleCategory.SyntaxError:    Severity.Fatal,
    }
    default_severity = Severity.Warning
    
    def _pycodestyle_checks_gen(self) -> Iterator[PycodestyleCheck]:
        for category_name, category_checks in pycodestyle_checks.items():
            for check_fn, (error_codes, args) in category_checks.items():
                if (not error_codes or error_codes == [ '' ]):
                    if (check_fn is tabs_or_spaces):
                        error_codes = [ 'E101' ]
                
                doc = getattr(check_fn, '__doc__', '')
                doc = textwrap.dedent(doc).strip()
                
                yield PycodestyleCheck \
                (
                    category_name = category_name,
                    error_codes = error_codes,
                    args = args,
                    obj = check_fn,
                    docstring = doc,
                )
    
    @cached_property
    def pycodestyle_checks(self) -> Dict[str, PycodestyleCheck]:
        return { code: check for check in self._pycodestyle_checks_gen() for code in check.error_codes }
    
    @override
    def _summary_mapping_gen(self) -> Iterator[Tuple[str, str]]:
        for error_code, pycodestyle_check in self.pycodestyle_checks.items():
            yield (error_code, pycodestyle_check.docstring.splitlines()[0].strip() or None)
    
    @override
    def _details_mapping_gen(self) -> Iterator[Tuple[str, str]]:
        for error_code, pycodestyle_check in self.pycodestyle_checks.items():
            yield (error_code, pycodestyle_check.docstring or None)
    
    def parse_violation_extras(self, violation: ViolationPrototype[PycodestyleCategory]) -> ViolationPrototype[PycodestyleCategory]:
        if (violation.category == PycodestyleCategory.Comments):
            violation.provider = 'flake8-eradicate'
        elif ((pycodestyle_check := self.pycodestyle_checks.get(violation.error_code, None)) is not None):
            violation.string_id = getattr(pycodestyle_check.obj, '__name__', None)
        return violation


__all__ = \
[
    'PycodestyleCategory',
    'PycodestyleCheck',
    'PycodestyleViolationParser',
]
