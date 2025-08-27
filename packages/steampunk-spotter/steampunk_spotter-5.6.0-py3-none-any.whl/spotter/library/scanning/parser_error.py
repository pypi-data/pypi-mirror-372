from pathlib import Path

from pydantic import BaseModel
from ruamel.yaml.error import StringMark


class YamlErrorDetails(BaseModel):
    """A class representing details of errors encountered while parsing YAML files."""

    column: int
    index: int
    line: int
    description: str
    file_path: Path

    @classmethod
    def create_object(cls, problem_mark: StringMark, description: str, file_path: Path) -> "YamlErrorDetails":
        """
        A class method to create a YamlErrorDetails object

        :param problem_mark: An instance of StringMark representing the position of the error.
        :param description: A description of the error.
        :param file_path: The path to the YAML file where the error occurred.
        :return: An instance of YamlParserHandler class initialized with the error details.
        """
        return cls(
            column=problem_mark.column,
            index=problem_mark.index,
            line=problem_mark.line,
            description=description,
            file_path=file_path,
        )
