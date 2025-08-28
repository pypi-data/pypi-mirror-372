"""Vajra plugin implementation."""

from typing import Any, Dict, List

from niti.core.severity import Severity
from niti.plugins.base import NitiPlugin, PluginRuleDefinition

from .rules.forward_declaration_rule import FileIncludeStrategyRule
from .rules.pch_rule import IncludeMissingPchRule


class VajraPlugin(NitiPlugin):
    """Vajra-specific linting rules for C++ projects."""

    @property
    def name(self) -> str:
        return "vajra"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Vajra-specific C++ linting rules including PCH enforcement and forward declaration suggestions"

    @property
    def min_niti_version(self) -> str:
        return "0.1.0"

    def __init__(self):
        self.config = {}

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        self.config = config
        # Pass config to rules that need it
        IncludeMissingPchRule.pch_path = config.get("pch_path", "commons/PrecompiledHeaders.h")

    def get_rules(self) -> List[PluginRuleDefinition]:
        """Return Vajra-specific rules."""
        return [
            PluginRuleDefinition(
                rule_id="include-missing-pch",
                rule_class=IncludeMissingPchRule,
                default_severity=Severity.ERROR,
                default_enabled=True,
                description="Enforce precompiled header inclusion in C++ source files",
            ),
            PluginRuleDefinition(
                rule_id="file-include-strategy",
                rule_class=FileIncludeStrategyRule,
                default_severity=Severity.WARNING,
                default_enabled=False,  # Disabled by default as it can be noisy
                description="Suggest forward declarations instead of includes when possible",
            ),
        ]