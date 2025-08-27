"""Base class for whole inline rewriting."""

import itertools
import sys
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from re import Match
from typing import Any, Dict, Iterator, List, Optional, Tuple

from colorama import Back, Fore, Style
from pydantic import BaseModel

from spotter.library.scanning.display_level import DisplayLevel


class RewriteResult(BaseModel):
    """Rewrite Result."""

    content: str
    diff_size: int


class CheckType(Enum):
    """Enum that holds different check types for check result."""

    TASK = "task"
    PLAY = "play"
    REQUIREMENTS = "requirements"
    ANSIBLE_CFG = "ansible_cfg"
    INVENTORY = "inventory"
    VARIABLE = "variable"
    OTHER = "other"

    def __str__(self) -> str:
        """
        Convert CheckType to lowercase string.

        :return: String in lowercase
        """
        return str(self.name.lower())

    @classmethod
    def from_string(cls, check_type: str) -> "CheckType":
        """
        Convert string level to CheckType object.

        :param check_type: Check type
        :return: CheckType object
        """
        try:
            return cls[check_type.upper()]
        except KeyError:
            print(
                f"Warning: nonexistent check result type: {check_type}, "
                f"valid values are: {[str(e) for e in CheckType]}.",
                file=sys.stderr,
            )
            return CheckType.OTHER


class RewriteSuggestion(BaseModel):
    """Suggestion for rewriting Ansible task or play."""

    check_type: CheckType
    item_args: Dict[str, Any]
    file: Path
    file_parent: Path
    line: int
    column: int
    start_mark: int
    end_mark: int
    suggestion_spec: Dict[str, Any]
    display_level: DisplayLevel

    # used so classes are compared by reference
    def __hash__(self) -> int:
        return id(self)

    @classmethod
    def from_item(
        cls,
        check_type: CheckType,
        item: Dict[str, Any],
        suggestion_spec: Optional[Dict[str, Any]],
        display_level: DisplayLevel,
    ) -> Optional["RewriteSuggestion"]:
        """Create Suggestion object for rewriting Ansible task or play."""
        if not suggestion_spec:
            return None

        if check_type == CheckType.TASK:
            item_args = item["task_args"]
        elif check_type == CheckType.PLAY:
            item_args = item["play_args"]
        elif check_type == CheckType.INVENTORY:
            item_args = item["dynamic_inventory_args"]
        else:
            item_args = None

        file_path = Path(item["spotter_metadata"]["file"])

        return cls(
            check_type=check_type,
            item_args=item_args,
            file=file_path,
            file_parent=file_path.parent,
            line=item["spotter_metadata"]["line"],
            column=item["spotter_metadata"]["column"],
            start_mark=item["spotter_metadata"]["start_mark_index"],
            end_mark=item["spotter_metadata"]["end_mark_index"],
            suggestion_spec=suggestion_spec,
            display_level=display_level,
        )

    @property
    def is_fix_requirements(self) -> bool:
        """Is suggestion of type FIX_REQUIREMENTS."""
        return self.suggestion_spec.get("action") == "FIX_REQUIREMENTS"


class Replacement:
    """
    Replacement object that holds the entire context of replacement.

    Implemented as a separate object because, after matching, we still want to have multiple
    options of what to do with the match.
    One scenario is to show the diff first and only apply changes after user conformation.
    """

    def __init__(
        self,
        content: str,
        suggestion: RewriteSuggestion,
        match: Match,  # type: ignore[type-arg]  # type not generic in Python <=3.8
        replacement: str,
    ) -> None:
        """
        Construct Replacement object.

        :param content: Text to which we will apply rewritng
        :param suggestion: Suggestion object from which we calculated match
        :param match: Regex match, that was found inside content.
        :param replacement: New value for span(2) inside match.
        """
        self.content = content
        self.suggestion = suggestion
        self.s_bounding_index, self.e_bounding_index = match.span(1)
        self.s_index, self.e_index = match.span(2)
        self.after = replacement

    def apply(self) -> RewriteResult:
        """
        Apply the suggestion to the text.

        :return: Rewrite result.
        """
        content = self.content
        suggestion = self.suggestion

        content_before = content[: suggestion.start_mark + self.s_index]
        content_after = content[suggestion.start_mark + self.e_index :]
        end_content = content_before + self.after + content_after

        len_before = self.e_index - self.s_index
        return RewriteResult(content=end_content, diff_size=len(self.after) - len_before)

    def get_diff(self) -> Tuple[str, str]:
        """
        Calculate a string diff that may be shown to the user.

        :return: Tuple with content before and after.
        """
        moved = self.content[self.suggestion.start_mark :]
        bounding_before = moved[self.s_bounding_index : self.e_bounding_index]
        bounding_after = (
            moved[self.s_bounding_index : self.s_index] + self.after + moved[self.e_index : self.e_bounding_index]
        )
        return bounding_before, bounding_after


class RewriteBase(ABC):
    """Base class with all common logic for inplace rewriting."""

    def get_context(self, content: str, suggestion: RewriteSuggestion) -> str:
        """
        Get a block of content that has all context that needs to be rewriten, usually a complete task.

        :param content: Old task content
        :param suggestion: Suggestion object for a specific task
        :return: Block of text that is relevant.
        """
        part = content[suggestion.start_mark : suggestion.end_mark]
        return part

    def get_indent_index(self, content: str, start_mark: int) -> int:
        """
        Get index of first character.

        :param content: content block (usually a whole task).
        :param start_mark: starting mark index of task in content
        """
        l_content = content[:start_mark]
        index = l_content.rfind("\n") + 1
        return start_mark - index

    def _color_print(self, content: str, suggestion: RewriteSuggestion) -> None:
        before = content[: suggestion.start_mark]
        item = content[suggestion.start_mark : suggestion.end_mark]
        after = content[suggestion.end_mark :]
        print(f"{before}{Fore.RED}{Back.GREEN}{item}{Style.RESET_ALL}{after}")

    def shorten_match(self, content: str, suggestion: RewriteSuggestion) -> Tuple[RewriteSuggestion, str]:
        """
        Shorted a match for all whitespaces.

        Missing part is to also skip all comments.
        """
        # self._color_print(content, suggestion)
        part = self.get_context(content, suggestion)
        suggestion.end_mark -= len(part) - len(part.rstrip())
        if suggestion.end_mark < len(content) and content[suggestion.end_mark] == "\n":
            suggestion.end_mark += 1
            start_char = ""
        else:
            start_char = "\n"
        # self._color_print(content, suggestion)
        return suggestion, start_char

    @abstractmethod
    def get_replacement(self, content: str, suggestion: RewriteSuggestion) -> Optional[Replacement]:
        """
        Retrieve a replacement object for the inline rewriting action.

        :param content: The content that we want to rewrite
        :param suggestion: The suggestion
        :return: a replacement object that contains all logic for rewriting.
        """

    @abstractmethod
    def get_regex(self, text_before: str) -> str:
        """
        Construct a simple regex in which we are able to replace only one constant.

        The first match group will be used as a block of text with context, which will be
        shown to the user to inspect what will change.
        The second match group is the text that we will actually replace.

        :param text_before: Exact text that will be replaced with new value
        :return: A regex string that can be compiled into a regex.
        """


class INodeSuggestion:
    """
    Helper class for removing duplicate suggestions.

    In case of soft and hard links, we can get multiple results for one error. This class
    helps to remove duplicates. It does it by mathing and grouping files by theirs inode values.
    """

    def __init__(self, file: Path, suggestions: Iterator[RewriteSuggestion]) -> None:
        """
        Construct INodeSuggestion object.

        :param file: Path of file, that is listed inside suggestions
        :param suggestions: Suggestions that should be applied
        """
        self.file = file
        self.suggestions = list(suggestions)

    @staticmethod
    def _get_file(rewrite_suggestion: RewriteSuggestion) -> Path:
        return rewrite_suggestion.file

    @staticmethod
    def _get_inode(suggestion: "INodeSuggestion") -> int:
        return suggestion.file.stat().st_ino

    @classmethod
    def from_suggestions(cls, suggestions: List[RewriteSuggestion]) -> List["INodeSuggestion"]:
        """
        Construct list of INodeSuggestion objects.

        :param suggestions: Suggestions that should be used
        """
        files = [INodeSuggestion(file, suggests) for file, suggests in itertools.groupby(suggestions, cls._get_file)]
        inodes = [next(group) for _, group in itertools.groupby(sorted(files, key=cls._get_inode), cls._get_inode)]
        return inodes
