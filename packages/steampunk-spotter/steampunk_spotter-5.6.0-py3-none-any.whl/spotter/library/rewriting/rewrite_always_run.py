"""RewriteInline implementation."""

import re
from typing import Optional

from spotter.library.rewriting.models import Replacement, RewriteBase, RewriteSuggestion


class RewriteAlwaysRun(RewriteBase):
    """RewriteAlwaysRun implementation."""

    def get_regex(self, text_before: str) -> str:
        return rf"^(\s*({text_before}\s*:.*))"

    def get_replacement(self, content: str, suggestion: RewriteSuggestion) -> Optional[Replacement]:
        suggestion_dict = suggestion.suggestion_spec
        part = self.get_context(content, suggestion)
        before = suggestion_dict["data"]["before"]
        after = "check_mode: false"

        regex = self.get_regex(before)
        match = re.search(regex, part, re.MULTILINE)

        if match is None:
            print(
                f"Applying suggestion {suggestion.suggestion_spec} failed at "
                f"{suggestion.file}:{suggestion.line}:{suggestion.column}: could not find string to replace."
            )
            return None

        replacement = Replacement(content, suggestion, match, after)
        return replacement
