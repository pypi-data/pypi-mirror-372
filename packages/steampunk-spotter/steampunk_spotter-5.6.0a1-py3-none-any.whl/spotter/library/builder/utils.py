from spotter.library.runner import ExecutableRunner


def is_ansible_galaxy_installed() -> bool:
    """Check if ansible-galaxy is installed."""
    try:
        ExecutableRunner.execute_command(["ansible-galaxy", "--version"])
        return True
    except FileNotFoundError:
        return False


def is_ansible_builder_installed() -> bool:
    """Check if ansible-galaxy is installed."""
    try:
        ExecutableRunner.execute_command(["ansible-builder", "--version"])
        return True
    except FileNotFoundError:
        return False
