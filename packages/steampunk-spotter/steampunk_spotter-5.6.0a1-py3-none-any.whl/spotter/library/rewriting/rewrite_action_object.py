"""RewriteLocalActionInline implementation."""

import re
from io import StringIO
from typing import Optional, Tuple

import ruamel.yaml as ruamel

from spotter.library.rewriting.models import Replacement, RewriteBase, RewriteSuggestion
from spotter.library.rewriting.rewrite_module_object import RewriteModuleObject


class RewriteActionObject(RewriteBase):
    """RewriteActionObject implementation."""

    def get_regex(self, text_before: str) -> str:
        return rf"^(\s*({text_before}\s*):)"

    def remove_module_row(self, content: str, suggestion: RewriteSuggestion) -> Tuple[str, RewriteSuggestion]:
        """
        Remove module line from content.

        :param content: Content that we want to rewrite
        :param suggestion: Suggestion object
        """
        module_replacement = RewriteModuleObject().get_replacement(content, suggestion)
        if module_replacement is None:
            module_name = suggestion.suggestion_spec["data"]["module_name"]
            print(f'Applying suggestion failed: could not find "{module_name}" to replace.')
            raise TypeError()
        rewrite_result = module_replacement.apply()
        suggestion.end_mark += rewrite_result.diff_size
        return rewrite_result.content, suggestion

    def get_replacement(self, content: str, suggestion: RewriteSuggestion) -> Optional[Replacement]:
        # 1. Remove line "module: ..." from task arguments
        suggestion_data = suggestion.suggestion_spec["data"]
        content, suggestion = self.remove_module_row(content, suggestion)
        part = self.get_context(content, suggestion)

        # 2. Add "delegate_to": localhost
        if suggestion_data["additional"]:
            index = self.get_indent_index(content, suggestion.start_mark)
            additional_suggestion_data = StringIO()
            ruamel.YAML(typ="rt").dump(suggestion_data["additional"][0], additional_suggestion_data)
            additional = " " * index + additional_suggestion_data.getvalue()
            new_content = content[: suggestion.end_mark] + additional + content[suggestion.end_mark]
        else:
            new_content = content

        # 3. Replace "action:" with "<module_name>:"
        before = suggestion_data["original_module_name"]
        after = suggestion_data["module_name"]
        regex = self.get_regex(before)
        match = re.search(regex, part, re.MULTILINE)
        if match is None:
            print(
                f"Applying suggestion {suggestion.suggestion_spec} failed at "
                f"{suggestion.file}:{suggestion.line}:{suggestion.column}: could not find string to replace."
            )
            return None
        replacement = Replacement(new_content, suggestion, match, after)
        return replacement
