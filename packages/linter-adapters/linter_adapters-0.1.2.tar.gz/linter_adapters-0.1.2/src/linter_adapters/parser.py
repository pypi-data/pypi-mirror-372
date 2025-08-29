from __future__ import annotations

import math
import re
import typing
from abc import ABC
from functools import cached_property, lru_cache
from pathlib import Path
from typing import *

from .common import BaseCategory, Severity, ViolationPrototype
from .common import error_code_pattern_gen
from .types import AnyPath


if (typing.TYPE_CHECKING):
    from flake8.violation import Violation as Flake8Violation, Violation

AnyViolation: TypeAlias = Union[str, 'Flake8Violation', ViolationPrototype[Any]]

class BaseViolationParser[C: BaseCategory]:
    REGISTRY: ClassVar[Dict[str, BaseViolationParser]] = dict()
    
    provider_name: str
    ViolationCategory: Type[C]
    severity_mapping: Dict[C, Severity]
    
    default_prefix: str | None = None
    default_severity: Severity = Severity.Warning
    violation_code_number_base: int = 100
    
    @classmethod
    def parse_module_name(cls, filename: AnyPath):
        return Path(filename) \
            .absolute() \
            .relative_to(Path('.').absolute()) \
            .with_suffix('') \
            .as_posix() \
            .replace('/', '.') \
    
    def parse_violation_base(self, error_code: str) -> ViolationPrototype[None] | None:
        parsed = re.fullmatch(r'(?P<provider>\w+?)(?P<number>\d+)', error_code)
        if not parsed:
            return None
        
        result: ViolationPrototype[None] = ViolationPrototype(error_code, parsed.group('provider'), int(parsed.group('number')))
        return result
    
    def parse_violation_category(self, violation: ViolationPrototype[Any]) -> ViolationPrototype[C]:
        violation.provider = self.provider_name
        
        try:
            violation.category = self.ViolationCategory(violation.error_code_number // self.violation_code_number_base * self.violation_code_number_base)
        except (ValueError, LookupError):
            violation.category = None
        
        violation.severity = self.severity_mapping.get(violation.category, self.default_severity)
        
        return violation
    
    def _summary_mapping_gen(self) -> Iterator[Tuple[str, str]]:
        # noinspection PyTypeChecker
        yield None, None
    
    @cached_property
    def summary_mapping(self) -> Dict[str, str]:
        return dict(self._summary_mapping_gen())
    
    def _details_mapping_gen(self) -> Iterator[Tuple[str, str]]:
        # noinspection PyTypeChecker
        yield None, None
    
    @cached_property
    def details_mapping(self) -> Dict[str, str]:
        return dict(self._details_mapping_gen())
    
    def parse_violation_details(self, violation: ViolationPrototype[C]) -> ViolationPrototype[C]:
        violation.summary = self.summary_mapping.get(violation.error_code, None)
        violation.details = self.details_mapping.get(violation.error_code, None)
        if (violation.string_id is None and violation.category is not None and len(self.ViolationCategory) > 1):
            violation.string_id = violation.category.name
        
        return violation
    
    def parse_violation_extras(self, violation: ViolationPrototype[C]) -> ViolationPrototype[C]:
        return violation
    
    def parse_violation_code(self, violation: AnyViolation | None) -> str | None:
        match violation:
            case str(code):
                error_code = code
            case ViolationPrototype(error_code=code):
                error_code = code
            case flake8_violation if flake8_violation.__class__.__name__ == 'Violation':  # type: Flake8Violation
                error_code = flake8_violation.code
            case None:
                return None
            case _:
                error_code = str(violation)
        
        error_code = error_code and error_code.rstrip(':')
        return error_code
    
    def parse_violation(self, violation: AnyViolation) -> ViolationPrototype[C] | None:
        error_code = self.parse_violation_code(violation)
        return self._parse_violation_impl(error_code)
    
    @lru_cache(maxsize=None)
    def _parse_violation_impl(self, error_code: str) -> ViolationPrototype[C] | None:
        violation = error_code and self.parse_violation_base(error_code)
        violation = violation and self.parse_violation_category(violation)
        violation = violation and self.parse_violation_details(violation)
        violation = violation and self.parse_violation_extras(violation)
        return violation
    
    @classmethod
    def parse_using_registry(cls, violation: AnyViolation, *, optimistic: bool = True) -> ViolationPrototype[Any] | None:
        parser = SimpleViolationParser.INSTANCE
        error_code  = parser.parse_violation_code(violation)
        violation   = parser.parse_violation_base(error_code)
        parser      = BaseViolationParser.REGISTRY.get(violation.error_code_class, parser if (optimistic) else None)
        violation   = parser and parser.parse_violation(violation)
        return violation
    
    @classmethod
    def register(cls, *error_classes: str):
        if (not error_classes and cls.default_prefix is not None):
            error_classes = [ cls.default_prefix ]
        
        instance = cls()
        instance.register_violation_class(*error_classes)
    
    @classmethod
    def register_decorator[T: BaseViolationParser](cls, *error_classes: str) -> Callable[[Type[T]], Type[T]]:
        def decorator(parser_cls: Type[T]) -> Type[T]:
            parser_cls.register(*error_classes)
            return parser_cls
        return decorator
    
    def register_violation_class(self, *error_classes: str) -> None:
        for error_class in error_classes:
            assert error_class not in self.REGISTRY, f"Cannot re-register error class '{error_class}'"
            BaseViolationParser.REGISTRY[error_class] = self
        
        if (len(error_classes) == 1 and self.default_prefix is None):
            self.default_prefix = error_classes[0]
    
    def error_code_pattern(self, prefix: str = None) -> Pattern[str]:
        if (prefix is None):
            prefix = self.default_prefix
        if (prefix is None):
            prefix = r'[A-Z]+'
        
        return error_code_pattern_gen(prefix, int(math.log10(self.violation_code_number_base)))


class SingleCategoryViolationParser[C: BaseCategory](BaseViolationParser, ABC):
    category_name: str
    category_number: int
    
    @classmethod
    def make_enum(cls) -> Type[C]:
        enum_name = cls.__name__.replace('ViolationParser', '') + 'Category'
        enum_cls = BaseCategory(enum_name, { cls.category_name: cls.category_number })
        return cast(Type[C], enum_cls)
    
    def __init_subclass__(cls, **kwargs):
        if (not hasattr(cls, 'ViolationCategory')):
            cls.ViolationCategory = cls.make_enum()
        if (not hasattr(cls, 'severity_mapping')):
            cls.severity_mapping = { cls.ViolationCategory[cls.category_name]: cls.default_severity }
        
        super().__init_subclass__()


class SimpleViolationParser(SingleCategoryViolationParser):
    provider_name = 'linter-adapters'
    category_name = 'Violation'
    category_number = 000

SimpleViolationParser.INSTANCE = SimpleViolationParser()


__all__ = \
[
    'BaseViolationParser',
    'SingleCategoryViolationParser',
    'SimpleViolationParser',
]
