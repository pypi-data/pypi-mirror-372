"""RewriteInline implementation."""

import re
import textwrap
from io import StringIO
from typing import Any, Dict, Optional

import ruamel.yaml as ruamel
from ruamel.yaml.scalarstring import LiteralScalarString

from spotter.library.parsing.parsing import SafeLineConstructor
from spotter.library.rewriting.models import Replacement, RewriteBase, RewriteSuggestion


class MultilineSafeLineConstructor(SafeLineConstructor):
    """Custom constructor to handle multiline strings."""

    def construct_scalar(self, node: ruamel.nodes.ScalarNode) -> Any:
        scalar = super().construct_scalar(node)
        if not isinstance(scalar, str):
            return scalar
        if node.start_mark.line == node.end_mark.line:
            return scalar

        meta = {
            "__start_mark_index__": node.start_mark.index,
            "__end_mark_index__": node.end_mark.index,
        }
        return {"__metadata__": meta}


class RewriteInline(RewriteBase):
    """RewriteInline implementation."""

    def get_regex(self, text_before: str) -> str:
        return rf"^(\s*{text_before}\s*:(\s+.*))"

    def get_final_regex(self, yaml_text: str, before: str) -> Optional[str]:
        yaml = ruamel.YAML(typ="rt")
        yaml.Constructor = MultilineSafeLineConstructor
        yaml.version = (1, 1)
        parsed = yaml.load(yaml_text)

        for key, value in parsed[0].items():
            if key != before:
                continue
            if isinstance(value, str):
                break

            # Check if the item has metadata and if it matches the before text
            start_mark = value["__metadata__"]["__start_mark_index__"]
            end_mark = value["__metadata__"]["__end_mark_index__"]
            text = yaml_text[start_mark:end_mark]
            if text[0] == "|" and text[-1] == "\n":
                text = text.rstrip("\n")
            value_part = re.escape(text)
            return rf"^(\s*{before}\s*:(\s+{value_part}))"
        return self.get_regex(before)

    def get_indent_block(self, content: str, indent_index: int, split_by: str) -> str:
        """
        Get content block with each line indented.

        :param content: content block (usually a whole task)
        :param indent_index: number of empty spaces before first letter
        :param split_by: character to split by
        """
        indent = "\n" + " " * indent_index
        content_split = list(filter(None, content.split(split_by)))
        i_content = [indent + content for content in content_split]
        return "".join(i_content)

    def create_multiline_markers(self, content: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in content.items():
            if not isinstance(value, str):
                continue
            if "\n" not in value:
                continue
            content[key] = LiteralScalarString(textwrap.dedent(value))
        return content

    def get_replacement(self, content: str, suggestion: RewriteSuggestion) -> Optional[Replacement]:
        suggestion_dict = suggestion.suggestion_spec
        part = self.get_context(content, suggestion)
        before = suggestion_dict["data"]["module_name"]

        regex = self.get_final_regex(content, before)
        match = re.search(regex, part, re.MULTILINE) if regex else None
        if match is None:
            print(
                f"Applying suggestion {suggestion.suggestion_spec} failed at "
                f"{suggestion.file}:{suggestion.line}:{suggestion.column}: could not find string to replace."
            )
            return None

        offset = 2
        yaml = ruamel.YAML(typ="rt")
        args = ""
        variables = ""
        if "args" in suggestion_dict["data"] and suggestion_dict["data"]["args"]:
            content_args = StringIO()
            task_args = self.create_multiline_markers(suggestion_dict["data"]["args"])
            yaml.dump(task_args, content_args)
            args = self.get_indent_block(content_args.getvalue(), offset, "\n")
        if "vars" in suggestion_dict["data"] and suggestion_dict["data"]["vars"]:
            content_vars = StringIO()
            yaml.dump({"vars": suggestion_dict["data"]["vars"]}, content_vars)
            variables = "\n" + content_vars.getvalue()

        indent = self.get_indent_index(content, suggestion.start_mark)
        after = self.get_indent_block(f"{args}{variables}", indent, "\n").rstrip("\n")
        replacement = Replacement(content, suggestion, match, after)
        return replacement
