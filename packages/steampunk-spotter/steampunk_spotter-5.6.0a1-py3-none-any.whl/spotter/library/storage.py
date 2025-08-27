"""Provide local storage for saving data."""

import json
import shutil
import sys
from pathlib import Path, PurePath
from typing import Any, Dict


class Storage:
    """A storage class for saving data to local storage."""

    DEFAULT_PATH = Path.home() / ".config/steampunk-spotter"

    def __init__(self, path: Path):
        """
        Construct Storage object.

        :param path: Storage path
        """
        try:
            self.path = path.absolute()
            path.mkdir(exist_ok=True, parents=True)
        except OSError as e:
            print(f"Error: could not create directory: {e!s}", file=sys.stderr)
            sys.exit(2)

    def write(self, content: str, *path: str) -> None:
        """
        Write content to storage.

        :param content: Content
        :param path: Path inside storage to save the content to
        """
        try:
            *subpath, name = path
            dir_path = self.path / PurePath(*subpath)
            dir_path.mkdir(exist_ok=True, parents=True)
            (dir_path / name).write_text(content)
        except OSError as e:
            print(f"Error: unable to write content to storage: {e!s}", file=sys.stderr)
            sys.exit(2)

    def write_json(self, data: Dict[Any, Any], *path: str) -> None:
        """
        Write JSON data to storage.

        :param data: JSON data as dict
        :param path: Path inside storage to save the data to
        """
        try:
            self.write(json.dumps(data, indent=2), *path)
        except TypeError as e:
            print(f"Error: unable to serialize the object to JSON: {e!s}", file=sys.stderr)
            sys.exit(2)

    def update_json(self, update_data: Dict[Any, Any], *path: str) -> None:
        """
        Update JSON data to storage.

        :param update_data: JSON data as dict that will update the existing JSON from storage
        :param path: Path inside storage to save the data to
        """
        try:
            data = self.read_json(*path) if self.exists(*path) else {}
            data.update(update_data)
            self.write_json(data, *path)
        except TypeError as e:
            print(f"Error: unable to serialize the object to JSON: {e!s}", file=sys.stderr)
            sys.exit(2)

    def read(self, *path: str) -> str:
        """
        Read content from storage.

        :param path: Path inside storage to read the content from
        :return: Content as string
        """
        try:
            return (self.path / PurePath(*path)).read_text()
        except OSError as e:
            print(f"Error: unable to read content from storage: {e!s}", file=sys.stderr)
            sys.exit(2)

    def read_json(self, *path: str) -> Dict[Any, Any]:
        """
        Read JSON data from storage.

        :param path: Path inside storage to read the data from
        :return: JSON object as dict
        """
        try:
            data = json.loads(self.read(*path))
            if not isinstance(data, dict):
                print(
                    f"Error: could not read JSON data from storage: not a JSON object, is {type(data)}", file=sys.stderr
                )
                sys.exit(2)
            return data
        except json.JSONDecodeError as e:
            print(f"Error: could not read JSON data from storage: {e!s}", file=sys.stderr)
            sys.exit(2)

    def exists(self, *path: str) -> bool:
        """
        Check if path inside storage exists.

        :param path: Path inside storage to check existence for
        :return: True if exists, else False
        """
        try:
            return (self.path / PurePath(*path)).exists()
        except (OSError, ValueError) as e:
            print(f"Error: could check if file exists: {e!s}", file=sys.stderr)
            sys.exit(2)

    def remove(self, *path: str) -> None:
        """
        Remove file from storage.

        :param path: Path inside storage to be removed
        """
        try:
            (self.path / PurePath(*path)).unlink(missing_ok=True)
        except OSError as e:
            print(f"Error: could not remove file from storage: {e!s}", file=sys.stderr)
            sys.exit(2)

    def remove_all(self, keep_root_dir: bool = False) -> None:
        """
        Remove all files from storage (this will also remove the storage dir).

        :param keep_root_dir: Keep root storage dir after the content gets deleted
        """
        try:
            shutil.rmtree(self.path)
            if keep_root_dir:
                Path(self.path).mkdir(exist_ok=True)
        except OSError as e:
            print(f"Error: could not remove all files from storage: {e!s}", file=sys.stderr)
            sys.exit(2)

    def copy_file(self, source: str, destination: str) -> None:
        """
        Copy source to destination file within storage.

        :param source: Path inside storage to be copied
        :param destination: Path inside storage to be copied to
        """
        try:
            content = self.read(source)
            self.write(content, destination)
        except OSError as e:
            print(f"Error: unable to copy file within storage: {e!s}", file=sys.stderr)
            sys.exit(2)

    def move_file(self, source: str, destination: str) -> None:
        """
        Move source to destination file within storage.

        :param source: Path inside storage to be moved
        :param destination: Path inside storage to move to
        """
        try:
            self.copy_file(source, destination)
            self.remove(source)
        except OSError as e:
            print(f"Error: unable to move file within storage: {e!s}", file=sys.stderr)
            sys.exit(2)
