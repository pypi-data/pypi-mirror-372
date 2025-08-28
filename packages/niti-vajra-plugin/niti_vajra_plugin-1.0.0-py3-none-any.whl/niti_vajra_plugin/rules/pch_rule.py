"""Precompiled header enforcement rule."""

from typing import Any, List

from niti.core.issue import LintIssue
from niti.core.severity import Severity
from niti.rules.base import AutofixResult, RegexRule


class IncludeMissingPchRule(RegexRule):
    """Rule to detect missing PrecompiledHeaders.h inclusion."""

    # Class variable to store PCH path from config
    pch_path = "commons/PrecompiledHeaders.h"

    def __init__(self):
        # Plugin rules don't use RuleId enum
        super().__init__(rule_id=None, severity=Severity.ERROR)
        self.supports_autofix = True
        # Store the plugin rule ID
        self.plugin_rule_id = "vajra/include-missing-pch"

    def __str__(self) -> str:
        """String representation of the rule."""
        return self.plugin_rule_id

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []
        if (
            not file_path.endswith((".cpp", ".cc", ".cxx"))
            or "/test/" in file_path
        ):
            return self.issues

        lines = content.split("\n")
        first_include_line, pch_include_line = None, None

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith(("//", "/*")):
                continue
            if stripped.startswith("#include"):
                if first_include_line is None:
                    first_include_line = i + 1
                if self._get_pch_filename() in stripped:
                    pch_include_line = i + 1
                    break
            elif not stripped.startswith("#"):
                break

        if pch_include_line is None:
            line = first_include_line or 1
            msg = (
                f"{self._get_pch_filename()} should be the first include"
                if first_include_line
                else f"Missing {self._get_pch_filename()} inclusion"
            )
            fix = f'#include "{self.pch_path}"'
            self.add_issue(file_path, line, 1, msg, fix)
        elif first_include_line != pch_include_line:
            self.add_issue(
                file_path,
                pch_include_line,
                1,
                f"{self._get_pch_filename()} should be the first include",
                f"Move {self._get_pch_filename()} include to the top",
            )

        return self.issues

    def _get_pch_filename(self) -> str:
        """Extract filename from PCH path."""
        return self.pch_path.split("/")[-1]

    def autofix(
        self,
        file_path: str,
        content: str,
        tree: Any,
        config: Any,
        issues: List[LintIssue],
    ) -> AutofixResult:
        if not issues:
            return AutofixResult(success=False)

        lines = content.split("\n")
        pch_include = f'#include "{self.pch_path}"'

        # Remove existing PCH include if it's not in the right place
        existing_pch_index = -1
        for i, line in enumerate(lines):
            if self._get_pch_filename() in line:
                existing_pch_index = i
                break
        if existing_pch_index != -1:
            lines.pop(existing_pch_index)

        # Find the correct insertion point
        insert_pos = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith(("//", "/*")):
                insert_pos = i + 1
            elif stripped.startswith("#pragma once"):
                insert_pos = i + 1
            else:
                break

        lines.insert(insert_pos, pch_include)
        new_content = "\n".join(lines)
        return AutofixResult(
            success=True,
            new_content=new_content,
            message=f"Added/Moved {self._get_pch_filename()} to the correct position.",
            issues_fixed=1,
        )