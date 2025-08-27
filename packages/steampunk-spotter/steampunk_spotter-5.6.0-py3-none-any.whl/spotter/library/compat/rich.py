"""Rich compatibility shims."""

from inspect import signature
from typing import Optional

from rich.progress import Progress


def compat_progress_total(progress: Progress) -> Optional[float]:
    """
    Compatibility shim for progress total.

    Setting total=None is supported in rich >= 12.3.0 because total parameter is of type Optional[float].
    Here we check if the function signature for total parameter allows None, otherwise we set a starting float.

    :param progress: Progress object
    :return: Total value
    """
    progress_starting_total: Optional[float] = 100.0
    progress_add_task_signature = signature(progress.add_task)
    total_parameter = progress_add_task_signature.parameters.get("total", None)
    if total_parameter and total_parameter.annotation == Optional[float]:
        progress_starting_total = None

    return progress_starting_total
