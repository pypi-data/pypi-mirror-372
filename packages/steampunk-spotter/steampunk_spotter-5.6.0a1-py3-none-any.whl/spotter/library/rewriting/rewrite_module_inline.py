"""RewriteModuleInline implementation."""

import re
from typing import Optional

from spotter.library.rewriting.models import Replacement, RewriteBase, RewriteSuggestion


class RewriteModuleInline(RewriteBase):
    """RewriteModuleInline implementation."""

    def __init__(self, suggestion: RewriteSuggestion) -> None:
        suggestion_data = suggestion.suggestion_spec["data"]
        self.original_module_name = suggestion_data["original_module_name"]
        super().__init__()

    def get_regex(self, text_before: str) -> str:
        return rf"(\s*-?\s*{self.original_module_name}:.*([ \t]{text_before}\b|\b{text_before}[ \t]).*)"

    def get_replacement(self, content: str, suggestion: RewriteSuggestion) -> Optional[Replacement]:
        suggestion_data = suggestion.suggestion_spec["data"]

        part = self.get_context(content, suggestion)
        before = suggestion_data["module_name"]
        regex = self.get_regex(before)
        match = re.search(regex, part, re.MULTILINE)
        after = ""
        if match is None:
            print(
                f"Applying suggestion {suggestion.suggestion_spec} failed at "
                f"{suggestion.file}:{suggestion.line}:{suggestion.column}: could not find string to replace."
            )
            return None
        replacement = Replacement(content, suggestion, match, after)
        return replacement
