"""Code quality rules for C++ code."""

import re
from typing import Any, List, Set

from ..core.issue import LintIssue
from .base import ASTRule


class QualityMagicNumbersRule(ASTRule):
    """Rule to detect magic numbers in code.

    Magic numbers are numeric literals that appear in code without explanation.
    They should be replaced with named constants that explain their purpose.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Find all numeric literals in the code
        numeric_nodes = self.find_nodes_by_type(tree, "number_literal")

        for node in numeric_nodes:
            if self.is_inside_comment(node, content):
                continue

            value = self.get_text_from_node(node, content)

            # Skip acceptable numbers
            if self._is_acceptable_number(value, node, content):
                continue

            line_num = self.get_line_from_byte(node.start_byte, content)
            column = node.start_byte - content.rfind("\n", 0, node.start_byte)

            self.add_issue(
                file_path=file_path,
                line_number=line_num,
                column=column,
                message=f"Magic number '{value}' should be replaced with a named constant",
                suggested_fix=f"const auto kSomeDescriptiveName = {value};",
            )

        return self.issues

    def _is_acceptable_number(
        self, value: str, node: Any, content: str
    ) -> bool:
        """Check if a number is acceptable (not a magic number)."""
        # Common acceptable numbers (only very basic ones)
        if value in ["0", "1", "-1", "2"]:
            return True

        # Boolean literals (true/false should be handled separately)
        if value in ["true", "false"]:
            return True

        # Numbers in array/vector sizing contexts (be more restrictive)
        if self._is_in_sizing_context(node, content):
            return True

        # Float literals for common values
        if value in ["0.0", "0.0f", "1.0", "1.0f", "2.0", "2.0f"]:
            return True

        # Numbers in const/constexpr declarations are acceptable
        if self._is_in_const_declaration(node, content):
            return True

        return False

    def _is_in_sizing_context(self, node: Any, content: str) -> bool:
        """Check if number is used in array sizing or similar context."""
        parent_context = self._get_parent_context(node, content, 50)
        sizing_patterns = [
            r"std::array<[^>]*,\s*\d+",
            r"\[\s*\d+\s*\]",
            r"\.resize\s*\(\s*\d+",
            r"\.reserve\s*\(\s*\d+",
        ]

        for pattern in sizing_patterns:
            if re.search(pattern, parent_context):
                return True

        return False

    def _get_parent_context(
        self, node: Any, content: str, context_size: int = 30
    ) -> str:
        """Get surrounding context of a node."""
        start = max(0, node.start_byte - context_size)
        end = min(len(content), node.end_byte + context_size)
        return content[start:end]

    def _is_in_const_declaration(self, node: Any, content: str) -> bool:
        """Check if number is part of a named constant declaration."""
        # Look for const/constexpr keywords in the line
        line_start = content.rfind("\n", 0, node.start_byte) + 1
        line_end = content.find("\n", node.start_byte)
        if line_end == -1:
            line_end = len(content)

        line_content = content[line_start:line_end]

        # Only accept const/constexpr if it's a named constant (has 'k' prefix)
        if any(keyword in line_content for keyword in ["const ", "constexpr "]):
            # Check if variable name starts with 'k' (naming convention for constants)
            import re

            # Look for pattern like "const type kVariableName" or "constexpr type kVariableName"
            pattern = r"\b(?:const|constexpr)\s+\w+\s+k\w+"
            return bool(re.search(pattern, line_content))

        return False



