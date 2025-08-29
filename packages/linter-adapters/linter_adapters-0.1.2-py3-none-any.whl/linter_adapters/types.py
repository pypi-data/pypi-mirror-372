import os
from dataclasses import dataclass, field
from functools import cached_property
from importlib.metadata import EntryPoint
from typing import *


AnyPath = str | os.PathLike[str]

@dataclass
class ImportableObject[T]:
    _entry_point: EntryPoint = field(init=False, repr=False)
    
    def __init__(self, name: str):
        self._entry_point = EntryPoint(name=None, group=None, value=name)
    
    @cached_property
    def obj(self) -> T:
        return self._entry_point.load()


class ImportableFunction[C: Callable](ImportableObject[C]):
    @property
    def func(self) -> C:
        return self.obj


__all__ = \
[
    'AnyPath',
    'ImportableFunction',
    'ImportableObject',
]
