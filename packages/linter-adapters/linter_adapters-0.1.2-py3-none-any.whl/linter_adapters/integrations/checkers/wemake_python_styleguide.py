from __future__ import annotations

import textwrap
import typing
from typing import *

from linter_adapters.common import BaseCategory, Severity, ViolationPrototype
from linter_adapters.parser import BaseViolationParser


if (typing.TYPE_CHECKING):
    from wemake_python_styleguide.cli.commands.explain.violation_loader import ViolationInfo

try:
    from wemake_python_styleguide.cli.commands.explain.violation_loader import get_violation
except ImportError:
    get_violation = lambda code: None


class WemakePythonStyleguideCategory(BaseCategory):
    System = 000
    """
    These checks ensures that our internal checks passes.
    
    For example, we can report violations from this group
    when some exception occur during the linting process
    or some dependencies are missing.
    """
    
    Naming = 100
    """
    Naming is hard! It is, in fact, one of the two hardest problems.

    These checks are required to make your application
    easier to read and understand by multiple people over the long period of time.
    """
    
    Complexity = 200
    """
    These checks find flaws in your application design.
    
    We try to stick to “the magical 7 ± 2 number” when counting things.
    https://en.wikipedia.org/wiki/The_Magical_Number_Seven,_Plus_or_Minus_Two
    
    That’s how many objects we can keep in our memory at a time.
    We try hard not to exceed the memory capacity limit.
    
    You can also find interesting reading about “Cognitive complexity”:
    https://www.sonarsource.com/docs/CognitiveComplexity.pdf
    """
    
    Consistency = 300
    """
    These checks limit Python’s inconsistencies.
    
    We can do the same things differently in Python.
    For example, there are three ways to format a string.
    There are several ways to write the same number.
    
    We like our code to be consistent.
    It is easier to work with your code base if you follow these rules.
    
    So, we choose a single way to do things.
    It does not mean that we choose the best way to do it.
    But, we value consistency more than being 100% right
    and we are ready to suffer all trade-offs that might come.
    
    Once again, these rules are highly subjective, but we love them.
    """
    
    BestPractices = 400
    """
    These checks ensure that you follow the best practices.
    
    The source for these best practices is countless hours
    we have spent debugging software or reviewing it.
    
    How do we find inspiration for new rules?
    We find some ugly code during code reviews and audits,
    then we forbid the use of code like it forever.
    """
    
    Refactoring = 500
    """
    These checks ensure that you don’t have patterns that can be refactored.
    
    There are so many ways of doing the same thing in Python.
    Here we collect know patterns that can be rewritten
    into much easier or just more pythonic version.
    """
    
    OOP = 600
    """
    These checks ensures that you use Python’s version of OOP correctly.
    
    There are different gotchas in Python to write beautiful classes and using objects correctly.
    That’s the place we collect these kind of rules.
    """


@BaseViolationParser.register_decorator('WPS')
class WemakePythonStyleguideViolationParser(BaseViolationParser[WemakePythonStyleguideCategory]):
    provider_name = 'wemake-python-styleguide'
    ViolationCategory = WemakePythonStyleguideCategory
    severity_mapping = \
    {
        WemakePythonStyleguideCategory.System:          Severity.Fatal,
        WemakePythonStyleguideCategory.Naming:          Severity.Convention,
        WemakePythonStyleguideCategory.Complexity:      Severity.Refactor,
        WemakePythonStyleguideCategory.Consistency:     Severity.Warning,
        WemakePythonStyleguideCategory.BestPractices:   Severity.Convention,
        WemakePythonStyleguideCategory.Refactoring:     Severity.Refactor,
        WemakePythonStyleguideCategory.OOP:             Severity.Warning,
    }
    default_severity = Severity.Convention
    
    def get_wemake_python_violation_info(self, violation: ViolationPrototype) -> Optional[ViolationInfo]:
        return get_violation(violation.error_code_number)
    
    def parse_violation_extras(self, violation: ViolationPrototype[WemakePythonStyleguideCategory]) -> ViolationPrototype[WemakePythonStyleguideCategory]:
        violation_info = self.get_wemake_python_violation_info(violation)
        violation.string_id = violation_info and violation_info.identifier
        docstring           = violation_info and textwrap.dedent(violation_info.docstring or '').strip()
        violation.summary   = docstring and docstring.splitlines()[0] or None
        violation.details   = docstring and docstring[len(violation.summary or ''):].strip()
        
        return violation


__all__ = \
[
    'WemakePythonStyleguideCategory',
    'WemakePythonStyleguideViolationParser',
]
