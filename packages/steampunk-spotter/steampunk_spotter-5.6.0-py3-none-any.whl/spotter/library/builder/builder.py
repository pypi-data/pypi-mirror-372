import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import ruamel.yaml as ruamel
from pydantic import BaseModel
from pydantic_core import to_jsonable_python
from ruamel.yaml import CommentedMap

from spotter.library.runner import ExecutableRunner


class BuildFileContent(BaseModel):
    src: str
    dest: str


class SpotterBuilder:
    def __init__(self, file: Path, args: List[str], project_root: Path):
        self.project_root = project_root
        self.args = args
        self.file = file

    def _get_ee_modified_file_path(self, tmp_dir: Path) -> Path:
        """
        Get modified execution_environment.yml path.

        :param tmp_dir: Path to modified execution_environment.yml
        """
        return Path(f"{tmp_dir.absolute()}/ee.yml")

    @classmethod
    def _collection_path(cls, project_root: Path) -> Path:
        """
        Get spotter collection path.

        :param : Project root path
        """
        return Path(f"{project_root.absolute()}/builder/extras/collection")

    @classmethod
    def _resource_path(cls, project_root: Path) -> Path:
        """Get script resource path.

        :param project_root: Project root path
        """
        return Path(f"{project_root}/builder/extras/scripts")

    @staticmethod
    def _get_extra_build_steps() -> List[str]:
        """Get build steps for execution environment."""
        # TODO: path changes depending on version. Update this method corresponding to ansible builder version
        return [
            "COPY _build/scripts/entrypoint_hook.sh /opt/builder/bin/entrypoint_hook.sh",
            "COPY _build/tars/xlab_steampunk-spotter-1.0.0.tar.gz /tmp/xlab_steampunk-spotter-1.0.0.tar.gz",
            "RUN pip3 install steampunk-spotter && "
            "sed -i '$ d' /opt/builder/bin/entrypoint && "
            "echo 'exec /opt/builder/bin/entrypoint_hook.sh \"${@}\"' >> /opt/builder/bin/entrypoint && "
            "ansible-galaxy collection install /tmp/xlab_steampunk-spotter-1.0.0.tar.gz -p /runner/.ansible/collections && "
            "chown -c 1000 -hR /runner/.ansible && "
            "chmod ug+r /opt/builder/bin/entrypoint && "
            "chmod ug+r /opt/builder/bin/entrypoint_hook.sh",
        ]

    @classmethod
    def _get_build_files_content(cls, tmp_dir: Path, project_root: Path) -> List[BuildFileContent]:
        """Get build file content.

        :param tmp_dir: Temporary directory path
        :param project_root: Project root path
        """
        return [
            BuildFileContent(src=f"{tmp_dir.absolute()}/xlab_steampunk-spotter-1.0.0.tar.gz", dest="tars"),
            BuildFileContent(src=f"{cls._resource_path(project_root.absolute())}/entrypoint_hook.sh", dest="scripts"),
        ]

    @classmethod
    def _create_collection(cls, tmp_dir: Path, project_root: Path) -> None:
        """Build spotter ansible-galaxy collection"""
        collection_path = str(cls._collection_path(project_root).absolute())
        output_path = str(tmp_dir.absolute())
        cmd = ["ansible-galaxy", "collection", "build", collection_path, "--output-path", output_path, "--force"]
        try:
            ExecutableRunner.execute_command(cmd, True)
        except Exception as e:  # noqa: BLE001  # safety catchall
            print(f"Something went wrong when zipping steampunk spotter collection:\n {e}")
            sys.exit(1)

    @classmethod
    def _validate_ee(cls, file: Path, ee: Any) -> None:
        """Validate that EE definition file uses v3 format"""
        if ee is None:
            print(f"Execution environment definition file {file} is invalid.")
            sys.exit(1)
        if not isinstance(ee, dict):
            print(f"Execution environment definition file {file} should be a dict.")
            sys.exit(1)
        if "version" not in ee:
            print(f"Execution environment definition file {file} should have version defined.")
            sys.exit(1)

        version = ee["version"]
        supported_version = 3
        if version != supported_version:
            msg = (
                f"Execution environment definition file {file} is in format version {version}. "
                f"Supported version is {supported_version}."
            )
            print(msg)
            sys.exit(1)

    @classmethod
    def _load_ee(cls, file_path: Path) -> Any:
        """
        Load execution_environment.yml

        :param file_path: Execution environment file path
        """
        yaml_text = file_path.read_text(encoding="utf-8")
        yaml = ruamel.YAML()
        return yaml.load(yaml_text)

    @classmethod
    def _modify_ee(cls, ee: Dict[Any, Any], tmp_dir: Path, project_root: Path) -> CommentedMap:
        """
        Modify execution_environment.yml to implement spotter inside Execution environment.

        :param ee: Original execution environment file
        :param tmp_dir: Temporary directory path
        :param project_root: Project root path
        """
        extra_build_steps = cls._get_extra_build_steps()
        build_content = cls._get_build_files_content(tmp_dir, project_root)

        # Modify additional_build_steps
        append_list_content = to_jsonable_python(extra_build_steps)
        build_files = to_jsonable_python(build_content)
        if "additional_build_steps" not in ee:
            ee["additional_build_steps"] = {}
        if "append_final" in ee["additional_build_steps"]:
            append_final = ee["additional_build_steps"]["append_final"]
            if isinstance(append_final, list):
                append_final.extend(append_list_content)
            else:
                ee["additional_build_steps"]["append_final"] = [
                    append_final,
                    *append_list_content,
                ]
        else:
            ee["additional_build_steps"]["append_final"] = append_list_content

        # Modify additional build files
        if "additional_build_files" not in ee:
            ee["additional_build_files"] = []
        _ = [ee["additional_build_files"].append(x) for x in build_files]
        return ee

    @classmethod
    def _create_tmp_ee(cls, tmp_dir: Path, ee_modified: Dict[str, Any]) -> None:
        """
        Save modified execution environment file to temporary directory.

        :param tmp_dir: Temporary directory path
        :param ee_modified: Modified execution environment content
        """
        with open(
            str(tmp_dir.absolute()),
            "wb",
        ) as f:
            yaml = ruamel.YAML()
            yaml.indent(mapping=4, sequence=6, offset=3)
            yaml.dump(ee_modified, f)

    @classmethod
    def _get_cmd(cls, ee_modified_path: Path, flags: List[str]) -> List[str]:
        """
        Get command for ansible builder execution

        :param ee_modified_path: Modified execution environment file path
        :param flags: Extra ansible builder flags
        """
        return ["ansible-builder", "build", "--file", str(ee_modified_path.absolute()), *flags]

    def build(self, *, create_only: bool = False) -> None:
        """Spotter builder execution."""
        file_path = Path(self.file)
        ee = self._load_ee(file_path)
        self._validate_ee(file_path, ee)

        tmp_path = Path()

        with tempfile.NamedTemporaryFile(dir=tmp_path) as ee_file:
            print("Creating modified execution environment.")
            ee_modified = self._modify_ee(ee, tmp_path, self.project_root)
            print("Creating Steampunk spotter collection.")
            self._create_collection(tmp_path, self.project_root)
            self._create_tmp_ee(Path(ee_file.name), ee_modified)
            cmd = self._get_cmd(Path(ee_file.name), self.args)

            if create_only:
                return

            print("Build execution environment.")
            ExecutableRunner.execute_command(cmd, True)
            print("Done.")
