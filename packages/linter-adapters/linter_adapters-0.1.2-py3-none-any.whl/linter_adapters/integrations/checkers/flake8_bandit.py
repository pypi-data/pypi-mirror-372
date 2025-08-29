from __future__ import annotations

import importlib
import re
import typing
from typing import *

from linter_adapters.common import BaseCategory, Severity, ViolationPrototype, error_code_pattern_gen
from linter_adapters.parser import BaseViolationParser


if (typing.TYPE_CHECKING):
    from stevedore.extension import Extension
    
    class BanditBlacklistInfo(TypedDict):
        name: str
        id: str
        cwe: int
        message: str
        qualnames: List[str]
        level: str

try:
    from bandit.core.extension_loader import MANAGER as bandit_mgr
except ImportError:
    class BanditMgr(NamedTuple):
        plugins_by_id: Dict[str, Extension] = {}
        blacklist_by_id: Dict[str, BanditBlacklistInfo] = {}
    bandit_mgr = BanditMgr()


class Flake8BanditCategory(BaseCategory):
    TestCode            = 100
    Misconfiguration    = 200
    BadCalls            = 300
    BadImports          = 400
    Cryptography        = 500
    Injection           = 600
    XSS                 = 700

@BaseViolationParser.register_decorator('S')
class Flake8BanditViolationParser(BaseViolationParser[Flake8BanditCategory]):
    ViolationCategory = Flake8BanditCategory
    provider_name = 'flake8-bandit'
    severity_mapping = \
    {
        Flake8BanditCategory.TestCode:         Severity.Error,
        Flake8BanditCategory.Misconfiguration: Severity.Error,
        Flake8BanditCategory.BadCalls:         Severity.Error,
        Flake8BanditCategory.BadImports:       Severity.Error,
        Flake8BanditCategory.Cryptography:     Severity.Error,
        Flake8BanditCategory.Injection:        Severity.Error,
        Flake8BanditCategory.XSS:              Severity.Error,
    }
    default_severity = Severity.Error
    
    BANDIT_SUMMARY_PATTERN = re.compile(fr'(?P<summary>(?P<id>{error_code_pattern_gen('B', 3).pattern}): +(?P<summary_text>[^\n]+))')
    BANDIT_SUMMARY_DETECTORS = \
    [
        re.compile(rf'^( *=+)\n{BANDIT_SUMMARY_PATTERN.pattern}\n(\1)'),
        re.compile(rf'^\*\*({BANDIT_SUMMARY_PATTERN.pattern})\*\*')
    ]
    
    def get_bandit_doc(self, bandit_error_id: str) -> Optional[str]:
        doc: Optional[str] = None
        if (blacklist_info := bandit_mgr.blacklist_by_id.get(bandit_error_id, None)):
            doc = blacklist_info['message']
        
        elif (plugin_info := bandit_mgr.plugins_by_id.get(bandit_error_id, None)):
            if (plugin_info and plugin_info.plugin.__doc__):
                return plugin_info.plugin.__doc__
            
            module = importlib.import_module(plugin_info.module_name)
            doc: str = module and module.__doc__ or ''
        
        return doc and doc.strip() or None
    
    def parse_bandit_doc(self, bandit_plugin_id: str, doc: str | None) -> Tuple[Optional[str], Optional[str]]:
        if (not doc):
            return None, None
        
        doc, _, _ = doc.partition(':Example:')
        doc = doc.strip()
        doc_lines = doc.splitlines()
        
        for det in self.BANDIT_SUMMARY_DETECTORS:
            if (m := det.match(doc)):
                assert m.group('id') == bandit_plugin_id, "Incorrect docstring detected"
                return m.group('summary'), doc[len(m.group(0)):].strip()
        else:
            if (len(doc_lines) > 1):
                return doc_lines[0], doc
            else:
                return doc, None
    
    def parse_violation_extras(self, violation: ViolationPrototype[Flake8BanditCategory]) -> ViolationPrototype[Flake8BugbearCategory]:
        bandit_plugin_id = f'B{violation.error_code_number}'
        doc = self.get_bandit_doc(bandit_plugin_id)
        violation.summary, violation.details = self.parse_bandit_doc(bandit_plugin_id, doc)
        return violation


__all__ = \
[
    'Flake8BanditCategory',
    'Flake8BanditViolationParser',
]
