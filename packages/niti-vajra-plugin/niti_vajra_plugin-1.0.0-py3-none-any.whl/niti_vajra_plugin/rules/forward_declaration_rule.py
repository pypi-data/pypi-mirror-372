"""Forward declaration suggestion rule."""

import re
from typing import Any, List

from niti.core.issue import LintIssue
from niti.core.severity import Severity
from niti.rules.base import RegexRule


class FileIncludeStrategyRule(RegexRule):
    """Rule to enforce include strategy vs forward declarations.

    Headers should prefer forward declarations when possible to reduce
    compilation dependencies.
    """

    def __init__(self):
        # Plugin rules don't use RuleId enum
        super().__init__(rule_id=None, severity=Severity.WARNING)
        # Store the plugin rule ID
        self.plugin_rule_id = "vajra/file-include-strategy"

    def __str__(self) -> str:
        """String representation of the rule."""
        return self.plugin_rule_id

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if f"// vajra-lint-disable {self.plugin_rule_id}" in content:
            return self.issues

        # Only check header files
        if not file_path.endswith((".h", ".hpp", ".hxx")):
            return self.issues

        # Find includes that could be forward declarations
        violations = self._find_forward_declaration_opportunities(content)

        for violation in violations:
            line_num, include_path, suggestion = violation
            self.add_issue(
                file_path=file_path,
                line_number=line_num,
                column=1,
                message=f"Consider forward declaration instead of including '{include_path}'",
                suggested_fix=suggestion,
            )

        return self.issues

    def _find_forward_declaration_opportunities(
        self, content: str
    ) -> List[tuple]:
        """Find includes that could be replaced with forward declarations."""
        violations = []
        lines = content.split("\n")

        include_pattern = re.compile(r'^\\s*#include\\s+["\']([^"\']+)["\']')

        for line_num, line in enumerate(lines, 1):
            match = include_pattern.match(line)
            if not match:
                continue

            include_path = match.group(1)

            # Skip system includes and certain types
            if self._should_skip_include(include_path):
                continue

            # Check if this include is only used for pointers/references
            if self._could_use_forward_declaration(include_path, content):
                class_name = self._extract_class_name_from_path(include_path)
                if class_name:
                    suggestion = f"Add 'class {class_name};' forward declaration and move include to .cpp file"
                    violations.append((line_num, include_path, suggestion))

        return violations

    def _should_skip_include(self, include_path: str) -> bool:
        """Check if include should be skipped from forward declaration checking."""
        skip_patterns = [
            "std",  # Standard library
            "vector",  # STL containers
            "string",
            "memory",
            "functional",
            "type_traits",
            "utility",
            "algorithm",
            "iostream",
            "fstream",
            "sstream",
            "cassert",
            "cstdint",
            "cmath",
            "commons/",  # Commons headers often needed for macros/inline functions
            "PrecompiledHeaders.h",
        ]

        for pattern in skip_patterns:
            if pattern in include_path:
                return True

        return False

    def _could_use_forward_declaration(
        self, include_path: str, content: str
    ) -> bool:
        """Check if include could be replaced with forward declaration."""
        # Extract potential class name
        class_name = self._extract_class_name_from_path(include_path)
        if not class_name:
            return False

        # Look for usage patterns in the content
        # This is a simple heuristic - only suggest if used in pointer/reference contexts

        # Pattern for pointer/reference usage
        pointer_patterns = [
            f"std::shared_ptr<{class_name}>",
            f"std::unique_ptr<{class_name}>",
            f"{class_name}*",
            f"{class_name}&",
            f"const {class_name}*",
            f"const {class_name}&",
        ]

        # Pattern for value usage (suggests forward declaration won't work)
        value_patterns = [
            f"{class_name} ",  # Value declaration
            f"new {class_name}",  # Direct instantiation
            f"{class_name}(",  # Constructor call
            f"::{class_name}",  # Method call
        ]

        has_pointer_usage = any(
            pattern in content for pattern in pointer_patterns
        )
        has_value_usage = any(pattern in content for pattern in value_patterns)

        # Suggest forward declaration only if used as pointer/reference and not as value
        return has_pointer_usage and not has_value_usage

    def _extract_class_name_from_path(self, include_path: str) -> str:
        """Extract likely class name from include path."""
        # Simple heuristic: take filename without extension and capitalize
        if "/" in include_path:
            filename = include_path.split("/")[-1]
        else:
            filename = include_path

        if "." in filename:
            name = filename.split(".")[0]
        else:
            name = filename

        # Convert to CamelCase
        if "_" in name:
            parts = name.split("_")
            return "".join(part.capitalize() for part in parts)
        else:
            return name.capitalize()