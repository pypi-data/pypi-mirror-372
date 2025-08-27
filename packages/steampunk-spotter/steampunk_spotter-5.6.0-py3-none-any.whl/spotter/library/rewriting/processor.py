"""Entry point of rewriting functionality."""

import sys
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Type, cast

from spotter.library.rewriting.models import INodeSuggestion, Replacement, RewriteBase, RewriteResult, RewriteSuggestion
from spotter.library.rewriting.rewrite_action_inline import RewriteActionInline
from spotter.library.rewriting.rewrite_action_object import RewriteActionObject
from spotter.library.rewriting.rewrite_always_run import RewriteAlwaysRun
from spotter.library.rewriting.rewrite_fqcn import RewriteFqcn
from spotter.library.rewriting.rewrite_inline import RewriteInline
from spotter.library.rewriting.rewrite_local_action_inline import RewriteLocalActionInline
from spotter.library.rewriting.rewrite_local_object import RewriteLocalActionObject
from spotter.library.rewriting.rewrite_requirements import update_requirements
from spotter.library.scanning.display_level import DisplayLevel


class RewriteProcessor:
    """Factory that will use correct implementation depending on 'action' inside 'suggestion'."""

    rewriter_mapping: ClassVar[Dict[str, Type[RewriteBase]]] = {
        "FIX_FQCN": RewriteFqcn,
        "FIX_REDIRECT": RewriteFqcn,
        "FIX_INLINE": RewriteInline,
        "FIX_ALWAYS_RUN": RewriteAlwaysRun,
        "FIX_ACTION_INLINE": RewriteActionInline,
        "FIX_ACTION_OBJECT": RewriteActionObject,
        "FIX_LOCAL_ACTION_OBJECT": RewriteLocalActionObject,
        "FIX_LOCAL_ACTION_INLINE": RewriteLocalActionInline,
    }

    @classmethod
    def execute(cls, content: str, suggestion: RewriteSuggestion) -> Optional[RewriteResult]:
        """
        Update task content.

        :param content: Old task content
        :param suggestion: Suggestion object for a specific task
        :return: Tuple with updated content and content length difference, or none if matching failed.
        """
        replacement = cls.get_replacement(content, suggestion)
        if not replacement:
            return RewriteResult(content=content, diff_size=0)

        return replacement.apply()

    @classmethod
    def multi_execute(
        cls, content: str, suggestions: List[RewriteSuggestion], display_level: DisplayLevel
    ) -> RewriteResult:
        """
        Update task content with multiple suggestions.

        :param content: Old task content
        :param suggestions: List of suggestions of specific tasks
        :return: List of tuples with updated content and content length difference, or none if matching failed
        """
        suggestion_start_position = -1
        previous_suggestion = None
        cut_all = False
        length_diff = 0
        for suggestion in suggestions:
            len_before = len(content)
            if suggestion_start_position == suggestion.start_mark and previous_suggestion:
                suggestion.end_mark = previous_suggestion.end_mark
                if suggestion.display_level.value < display_level.value or cut_all:
                    cut_all = True
                    continue
            cut_all = False
            suggestion_start_position = suggestion.start_mark
            previous_suggestion = suggestion

            replacement = cls.get_replacement(content, suggestion)
            if replacement is None:
                raise TypeError()
            rewrite_result = replacement.apply()
            new_content, _ = rewrite_result.content, rewrite_result.diff_size
            length_diff = len(new_content) - len_before
            suggestion.end_mark = suggestion.end_mark + length_diff
            content = new_content

        return RewriteResult(content=content, diff_size=length_diff)

    @classmethod
    def get_replacement(cls, content: str, suggestion: RewriteSuggestion) -> Optional[Replacement]:
        """
        Get replacement according to action.

        :param content: Old task content
        :param suggestion: Suggestion object for a specific task
        """
        suggestion_dict = suggestion.suggestion_spec
        action = cast(str, suggestion_dict.get("action"))

        rewriter_class = cls.rewriter_mapping.get(action)
        if not rewriter_class:
            print(f"Unknown mapping: {action}")
            return None

        rewriter = rewriter_class()  # we assume the mapping only contains implementations
        replacement = rewriter.get_replacement(content, suggestion)
        return replacement


def update_files(
    suggestions: List[RewriteSuggestion], display_level: DisplayLevel, scan_paths: List[Path]
) -> List[RewriteSuggestion]:
    """
    Update files by following suggestions.

    :param suggestions: List of suggestions as Suggestion objects
    :param display_level: DisplayLevel object
    :return: List of suggestion that cannot be applied due to some error
    """
    inodes = INodeSuggestion.from_suggestions(suggestions)
    update_requirements(inodes, display_level, scan_paths)
    applied_suggestions = []

    for inode in inodes:
        # python sort is stable, so items with same start mark, should stay in same order
        suggestions_reversed = sorted(inode.suggestions, key=lambda x: -x.start_mark)
        suggestions_items = [x for x in suggestions_reversed if not x.is_fix_requirements]

        with inode.file.open("r", encoding="utf-8") as f:
            content = f.read()

        end_content = content
        try:
            rewrite_result = RewriteProcessor.multi_execute(end_content, suggestions_items, display_level)
            if rewrite_result is None:
                continue
            end_content = rewrite_result.content

            if end_content != content:
                with inode.file.open("w", encoding="utf-8") as f:
                    f.write(end_content)

            applied_suggestions.extend(inode.suggestions)
        except Exception as e:  # noqa: BLE001  # safety catchall
            print(f"Error: rewriting {inode.file} failed: {e}", file=sys.stderr)

    return applied_suggestions
