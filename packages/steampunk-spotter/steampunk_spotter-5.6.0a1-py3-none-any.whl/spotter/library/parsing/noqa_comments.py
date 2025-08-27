"""Provide methods for parsing YAML comments and constructing noqa objects."""

import re
import sys
from typing import Any, Dict, List, Optional, Union

import ruamel.yaml as ruamel
from pydantic import BaseModel


class SpotterNoqa(BaseModel):
    """Data class with options for skipping checks."""

    event: str
    subevent_code: Optional[str] = None
    fqcn: Optional[str] = None

    @staticmethod
    def _parse_subevent_code(comment_part: str) -> Optional[str]:
        """
        Parse subevent_code part of the comment.

        :param comment_part: Comment part
        :return: Subevent code
        """
        subevent_code_regex = r"subevent_code=([^,\]]+)"
        match = re.search(subevent_code_regex, comment_part)
        if match is not None:
            return match.group(1)
        return None

    @staticmethod
    def _parse_fqcn(comment_part: str) -> Optional[str]:
        """
        Parse FQCN part of the comment.

        :param comment_part: Comment part
        :return: FQCN
        """
        fqcn_regex = r"fqcn=([^,\]]+)"
        match = re.search(fqcn_regex, comment_part)
        if match is not None:
            return match.group(1)
        return None

    @classmethod
    def parse_noqa_comment(cls, comment: str, use_noqa_regex: bool = True) -> List["SpotterNoqa"]:
        """
        Parse noqa comment and construct SpotterNoqa objects.

        :param comment: Comment
        :param use_noqa_regex: Match against noqa regex
        :return: List of SpotterNoqa objects
        """
        noqa_regex = r"#\s*noqa:(.*)"
        comment_parts_regex = r"\s*([EWH]\d+)\s*(\[[^]]+])?"

        matches = [comment]
        if use_noqa_regex:
            matches = re.findall(noqa_regex, comment)
            if not matches:
                return []

        comment_parts = re.findall(comment_parts_regex, matches[0])
        return [
            cls(event=part[0], subevent_code=cls._parse_subevent_code(part[1]), fqcn=cls._parse_fqcn(part[1]))
            for part in comment_parts
        ]


def _construct_noqa_from_comment_list(comment_list: List[Any]) -> List[SpotterNoqa]:
    """
    Construct SpotterNoqa objects from list of comments.

    :param comment_list: List of YAML comments
    :return: List of SpotterNoqa objects
    """
    noqas = []
    for comment_token_item in comment_list:
        if comment_token_item:
            if isinstance(comment_token_item, list):
                for comment_token in comment_token_item:
                    if isinstance(comment_token, ruamel.CommentToken):
                        noqas += SpotterNoqa.parse_noqa_comment(comment_token.value)
            elif isinstance(comment_token_item, ruamel.CommentToken):
                noqas += SpotterNoqa.parse_noqa_comment(comment_token_item.value)

    return noqas


def _construct_noqa_from_commented_item(
    commented_item: Union[ruamel.CommentedSeq, ruamel.CommentedMap]
) -> List[SpotterNoqa]:
    """
    Construct SpotterNoqa objects from commented sequence or map.

    :param commented_item: CommentedSeq or CommentedMap YAML object
    :return: List of SpotterNoqa objects
    """
    noqas = []
    if commented_item.ca and commented_item.ca.items and isinstance(commented_item.ca.items, dict):
        for k, v in commented_item.ca.items.items():
            if k:
                noqas += _construct_noqa_from_comment_list(v)

    return noqas


def _construct_noqa_from_dict_recursive(commented_map: Union[Dict[str, Any], ruamel.CommentedMap]) -> List[SpotterNoqa]:
    """
    Construct SpotterNoqa objects from nested dict recursively.

    :param commented_map: Dict or CommentedMap YAML object
    :return: List of SpotterNoqa objects
    """
    noqas = []
    for v in commented_map.values():
        if isinstance(v, dict):
            if isinstance(v, ruamel.CommentedMap):
                noqas += _construct_noqa_from_commented_item(v)

            noqas += _construct_noqa_from_dict_recursive(v)
        if isinstance(v, list):
            if isinstance(v, ruamel.CommentedSeq):
                noqas += _construct_noqa_from_commented_item(v)

            for e in v:
                if isinstance(e, dict):
                    if isinstance(e, ruamel.CommentedMap):
                        noqas += _construct_noqa_from_commented_item(e)

                    noqas += _construct_noqa_from_dict_recursive(e)

    return noqas


def match_comments_with_task(commented_map: ruamel.CommentedMap) -> None:
    """
    Match YAML comments with Ansible tasks by appending the __noqa__ item to each task.

    :param commented_map: CommentedMap YAML object
    """
    try:
        noqas = _construct_noqa_from_commented_item(commented_map) + _construct_noqa_from_dict_recursive(commented_map)
        commented_map["__noqa__"] = noqas
    except Exception as e:  # noqa: BLE001  # safety catchall
        print(f"Error: mapping YAML comments to tasks failed: {e}", file=sys.stderr)
