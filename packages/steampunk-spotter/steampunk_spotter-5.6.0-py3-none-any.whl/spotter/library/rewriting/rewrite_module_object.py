"""RewriteModuleObject implementation."""

import re
from typing import Optional

from spotter.library.rewriting.models import Replacement, RewriteBase, RewriteSuggestion


class RewriteModuleObject(RewriteBase):
    """RewriteModuleObject implementation."""

    def get_regex(self, text_before: str) -> str:
        return rf"((\n\s+{text_before}:\s[^\n]+))"

    def get_replacement(self, content: str, suggestion: RewriteSuggestion) -> Optional[Replacement]:
        part = self.get_context(content, suggestion)
        before = "module"
        regex = self.get_regex(before)
        match = re.search(regex, part)
        after = ""
        if match is None:
            print(
                f"Applying suggestion {suggestion.suggestion_spec} failed at "
                f"{suggestion.file}:{suggestion.line}:{suggestion.column}: could not find string to replace."
            )
            return None
        replacement = Replacement(content, suggestion, match, after)
        return replacement
