import subprocess
import sys
from typing import Any, List, TextIO, Union


class ExecutableRunner:
    @classmethod
    def execute_command(cls, cmd: List[str], passthrough_stdout: bool = False) -> Any:
        """
        Run command with arguments.

        :param cmd: List of arguments
        :param passthrough_stdout: Pass command's standard output through to the standard output of the calling process.
        """
        stdout: Union[int, TextIO] = subprocess.DEVNULL
        stderr: Union[int, TextIO] = subprocess.DEVNULL
        if passthrough_stdout:
            stdout = sys.stdout
            stderr = sys.stderr

        return subprocess.run(cmd, check=True, stdout=stdout, stderr=stderr)
