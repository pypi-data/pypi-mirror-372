"""Add and remove kernel specifications for Jupyter."""

from __future__ import annotations

import enum
import importlib.util
import json
import shutil
import sys
from pathlib import Path

from jupyter_client.kernelspec import KernelSpec, _is_valid_kernel_name  # pyright: ignore[reportPrivateUsage]

# path to kernelspec resources
RESOURCES = Path(__file__).parent.joinpath("resources")


__all__ = ["Backend", "KernelName", "get_kernel_dir", "make_argv", "write_kernel_spec"]


class Backend(enum.StrEnum):
    asyncio = "asyncio"
    if importlib.util.find_spec("trio"):
        trio = "trio"


class KernelName(enum.StrEnum):
    asyncio = "async"
    trio = "async-trio"


def make_argv(
    *,
    connection_file="{connection_file}",
    kernel_name: KernelName | str = KernelName.asyncio,
    kernel_factory="async_kernel.Kernel",
    fullpath=True,
    **kwargs,
) -> list[str]:
    """Constructs the argument vector (argv) for launching a Python kernel module.

    The backend is determined from the kernel_name. If the kernel_name contains 'trio'
    (case-insensitive)a trio backend will be used otherwise an 'asyncio' backend is used.

    Args:
        connection_file: The path to the connection file.
        kernel_factory: The string import path to a callable that creates the kernel.
        kernel_name: The name of the kernel to use.
        fullpath: If True the full path to the executable is used, otherwise 'python' is used.

    kwargs:
        Additional settings to use on the instance of the Kernel.
        kwargs are converted to key/value pairs, keys will be prefixed with '--'.
        The kwargs should correspond to settings to set prior to starting. kwargs
        are set on the
        instance by eval on the value.
        keys that correspond to an attribute on the kernel instance are not used.

    Returns:
        list: A list of command-line arguments to launch the kernel module.
    """
    python = sys.executable if fullpath else "python"
    argv = [python, "-m", "async_kernel", "-f", connection_file]
    for k, v in ({"kernel_factory": kernel_factory, "kernel_name": kernel_name} | kwargs).items():
        argv.extend((f"--{k}", str(v)))
    return argv


def write_kernel_spec(
    path: Path | str | None = None,
    *,
    kernel_factory="async_kernel.Kernel",
    connection_file="{connection_file}",
    kernel_name: KernelName | str = KernelName.asyncio,
    fullpath=False,
    display_name="",
    **kwargs,
) -> Path:
    """
    Write a kernel spec directory to `path` for launching a kernel.

    The kernel spec always calls the 'python -m async_kernel' which calls
    [][async_kernel.command.command_line][] [as a python module](https://docs.python.org/3/using/cmdline.html#command-line)).


    Args:
        connection_file: The path to the connection file.
        kernel_factory: The string import path to a callable that creates the Kernel.
        kernel_name: The name of the kernel to use.
        fullpath: If True the full path to the executable is used, otherwise 'python' is used.
        display_name: The display name for Jupyter to use for the kernel. The default is `"Python ({kernel_name})"`.

    kwargs:
        Additional settings to use on the instance of the Kernel.
        kwargs are converted to key/value pairs, keys will be prefixed with '--'.
        The kwargs should correspond to settings to set prior to starting. kwargs
        are set on the
        instance by eval on the value.
        keys that correspond to an attribute on the kernel instance are not used.
    """
    assert _is_valid_kernel_name(kernel_name)
    path = Path(path) if path else get_kernel_dir() / kernel_name
    # stage resources
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(RESOURCES, path, dirs_exist_ok=True)
    spec = KernelSpec()
    spec.argv = make_argv(
        kernel_factory=kernel_factory,
        connection_file=connection_file,
        kernel_name=kernel_name,
        fullpath=fullpath,
        **kwargs,
    )
    spec.name = kernel_name
    spec.display_name = display_name or f"Python ({kernel_name})"
    spec.language = "python"
    spec.interrupt_mode = "message"
    spec.metadata = {"debugger": True}

    # write kernel.json
    with path.joinpath("kernel.json").open("w") as f:
        json.dump(spec.to_dict(), f, indent=1)
    return path


def get_kernel_dir() -> Path:
    "The path to where kernel specs are stored for Jupyter."
    return Path(sys.prefix) / "share/jupyter/kernels"
