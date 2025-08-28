# Copyright (C) 2022 Alteryx, Inc. All rights reserved.
#
# Licensed under the ALTERYX SDK AND API LICENSE AGREEMENT;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.alteryx.com/alteryx-sdk-and-api-license-agreement
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Alteryx Python SDK: Main program."""
import filecmp
import importlib.util
import json
import logging
import os
import re
import shutil
import subprocess
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, List

from ayx_python_sdk.cli.utilities import get_install_dir
from ayx_python_sdk.cli.workspace import (
    WorkspaceError,
    remove_whitespace,
)
from ayx_python_sdk.providers.file_provider import FileProvider
from ayx_python_sdk.providers.file_provider.tool_input import ToolInput
from ayx_python_sdk.version import short_version

import deprecation

import typer

logger = logging.getLogger(__name__)
app = typer.Typer(
    help="Run a tool using file inputs and outputs in a pure Python environment."
)

REQ_LOCAL = "requirements-local.txt"
REQ_THIRDPARTY = "requirements-thirdparty.txt"


class TemplateToolTypes(str, Enum):
    """Installation Type of Designer."""

    Input = "input"
    MultipleInputs = "multiple-inputs"
    MultipleOutputs = "multiple-outputs"
    Optional = "optional"
    Output = "output"
    SingleInputSingleOutput = "single-input-single-output"
    MultipleInputConnections = "multi-connection-input-anchor"


name_to_tool = {
    TemplateToolTypes.Input: "AyxSdkInput",
    TemplateToolTypes.MultipleInputs: "AyxSdkMultipleInputAnchors",
    TemplateToolTypes.MultipleOutputs: "AyxSdkMultipleOutputAnchors",
    TemplateToolTypes.Optional: "AyxSdkOptionalInputAnchor",
    TemplateToolTypes.Output: "AyxSdkOutput",
    TemplateToolTypes.SingleInputSingleOutput: "AyxSdkPassThrough",
    TemplateToolTypes.MultipleInputConnections: "AyxSdkMultiConnectionsMultiOutputAnchor",
}


@app.command()
def init_workspace(
    workspace_directory: str = typer.Option(
        ...,
        help="Directory to create a workspace in. "
        "If the directory doesn't exist, it will be created.",
    ),
    yes_to_all: bool = typer.Option(False, "--y", help="Confirm all"),
) -> None:
    """Initialize a plugin workspace with a python backend."""
    backend_directory = Path(workspace_directory) / "backend"
    plugins_directory = backend_directory / "ayx_plugins"
    assets_directory = (
        Path(os.path.realpath(__file__)).parent / "assets" / "workspace_files"
    )

    typer.echo(f"Creating {plugins_directory}")
    plugins_directory.mkdir(parents=True, exist_ok=True)

    files_to_create = {
        (assets_directory / REQ_LOCAL)
        .resolve(): (backend_directory / REQ_LOCAL)
        .resolve(),
        (assets_directory / REQ_THIRDPARTY)
        .resolve(): (backend_directory / REQ_THIRDPARTY)
        .resolve(),
        (assets_directory / "setup.py")
        .resolve(): (backend_directory / "setup.py")
        .resolve(),
        (assets_directory / "__init__.py")
        .resolve(): (plugins_directory / "__init__.py")
        .resolve(),
    }
    new_files = []
    files_to_overwrite = []
    for source_path, dest_path in files_to_create.items():
        if not dest_path.exists():
            new_files.append((source_path, dest_path))
        else:
            files_to_overwrite.append((source_path, dest_path))
    for source_path, dest_path in new_files:
        typer.echo(f"Creating file {dest_path}")
        shutil.copy(source_path, dest_path)
    pin_ayx_version_to_requirements((backend_directory / REQ_THIRDPARTY).resolve())

    if not files_to_overwrite:
        return
    output_paths = [str(path[1]) for path in files_to_overwrite]
    if yes_to_all or typer.confirm(
        "\nThe following files will be overwritten:\n\t"
        + "\n\t".join(output_paths)
        + "\n\nConfirm that it is okay to remove these paths.\n"
    ):
        for source_path, dest_path in files_to_overwrite:
            typer.echo(f"Overwriting file {dest_path}")
            shutil.copy(source_path, dest_path)
        pin_ayx_version_to_requirements((backend_directory / REQ_THIRDPARTY).resolve())
    else:
        typer.echo(f"{', '.join(output_paths)} will not be overwritten")


def pin_ayx_version_to_requirements(requirements_path: Path) -> None:
    """Pins the plugin SDK to third-party requirements."""
    with open(requirements_path, "r") as req_file:
        lines = req_file.readlines()
        for line_num in range(len(lines)):
            if re.match(r"^ayx_python_sdk$", lines[line_num]):
                lines[line_num] = f"ayx_python_sdk=={short_version}"
        req_file = open(requirements_path, "w")
        req_file.writelines(lines)


@deprecation.deprecated(
    deprecated_in="1.0.3",
    removed_in="2.0.0",
    details="Use the Plugin CLI's test harness instead.",
)  # type: ignore
@app.command(
    deprecated=True,
    short_help="(DEPRECATED) Run a tool using file inputs and outputs in a pure Python environment.",
)
def run_tool_with_file_provider(
    configuration_file: str = typer.Option(
        ...,
        help="JSON file that specifies the input and output "
        "information needed for the file provider to run",
    ),
) -> None:
    """
    Run a tool using file inputs and outputs in a pure Python environment.

    Parameters
    ----------
    configuration_file
        Specifies the path to the JSON file that contains the tool plugin,
        configuration files, input files, and output files.
    """
    try:
        with open(configuration_file) as fd:
            json_dict = json.load(fd)
    except FileNotFoundError:
        raise RuntimeError(f"Couldn't find tool information file {configuration_file}.")

    tool_input = ToolInput(**json_dict)
    tool_classname = tool_input.tool.plugin
    tool_path = Path(tool_input.tool.path)

    file_provider = FileProvider(
        tool_input.tool_config.resolve(),
        tool_input.workflow_config.resolve(),
        inputs=tool_input.inputs or [],
        outputs=tool_input.outputs or [],
        update_tool_config=tool_input.update_tool_config,
    )

    tool_class = _load_user_plugin_class(tool_classname, tool_path)

    # Initialize and run the plugin
    plugin = tool_class(file_provider)
    for input_anchor in file_provider.input_anchors:
        for input_anchor_connection in input_anchor.connections:
            plugin.on_input_connection_opened(input_anchor_connection)
            # TODO Support multiple calls to on_record_packet
            plugin.on_record_packet(input_anchor_connection)
    plugin.on_complete()


def _load_user_plugin_class(tool_classname: str, tool_path: Path) -> Any:
    """Load the plugin and get a reference to its class."""
    root = Path(os.getcwd())
    tool_full_path = (root / tool_path).resolve()
    original_cwd = os.getcwd()

    try:
        os.chdir(tool_full_path.parent)
        spec: Any = importlib.util.spec_from_file_location("main", "main.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, tool_classname)
    finally:
        os.chdir(original_cwd)


def handle_workspace_errors(function: Callable) -> Callable:
    """Handle any workspace errors that occur."""

    @wraps(function)
    def decorator(*args: Any, **kwargs: Any) -> None:
        try:
            function(*args, **kwargs)
        except WorkspaceError as e:
            typer.echo(f"ERROR: {e}")
            raise typer.Exit(code=1)

    return decorator


@app.command()
@handle_workspace_errors
def create_ayx_plugin(
    name: str = typer.Option(
        ..., prompt="Tool Name", help="Name of the tool to create."
    ),
    workspace_directory: Path = typer.Option(
        ..., prompt="Workspace directory", help="Directory to put the new tool in."
    ),
    tool_type: TemplateToolTypes = typer.Option(
        ...,
        prompt="Tool type",
        help=f"The type of tool to create. Must be one of: {', '.join(name_to_tool.keys())}",
    ),
) -> None:
    """Create a new plugin for Alteryx Designer."""
    typer.echo("Creating Alteryx Plugin...")
    plugin_directory = workspace_directory / "backend" / "ayx_plugins"
    if not plugin_directory.is_dir():
        raise WorkspaceError(f"Plugin directory doesn't exist: {plugin_directory}")

    if plugin_directory.is_file():
        raise WorkspaceError(
            f"Plugin directory path is a file, not a directory: {plugin_directory}"
        )

    if not (plugin_directory / "__init__.py").exists():
        raise WorkspaceError(
            "__init__.py not found in the specified directory. "
            "Make sure that you've entered the correct path."
        )

    new_tool_name = remove_whitespace(name)
    new_tool_file_name = re.sub(r"(?<!^)(?=[A-Z])", "_", new_tool_name).lower()
    new_tool_path = plugin_directory / f"{new_tool_file_name}.py"

    if not new_tool_name.replace("_", "").isalnum() or not new_tool_name[0].isalpha():
        raise WorkspaceError(
            f"The name of the tool {new_tool_name} must be alpha-numeric, "
            "cannot start with a number, and cannot contain any special characters."
        )

    if new_tool_path.exists():
        raise WorkspaceError(
            "There is already another tool with this name in the directory."
        )

    example_tool_name = name_to_tool[tool_type]
    example_tool_dir = get_install_dir() / "examples" / example_tool_name

    shutil.copy(
        example_tool_dir / "main.py",
        new_tool_path,
    )
    typer.echo(f"Copying example tool to {plugin_directory}...")

    _update_main_py(new_tool_path, example_tool_name, new_tool_name)
    _update_init_py(plugin_directory, new_tool_file_name, new_tool_name)

    typer.echo(f"Added new tool to package directory: {new_tool_path}")


def _update_main_py(
    plugin_path: Path,
    example_tool_name: str,
    new_tool_name: str,
) -> None:
    try:
        with open(str(plugin_path), "r") as f:
            content = f.read()

        content = content.replace(example_tool_name, new_tool_name)
        with open(str(plugin_path), "w") as f:
            f.write(content)
    except IOError:
        raise WorkspaceError(f"Error updating {plugin_path}")


def _update_init_py(
    plugin_directory: Path, new_tool_file_name: str, new_tool_name: str
) -> None:
    import_line = f"from .{new_tool_file_name} import {new_tool_name}\n"
    try:
        with open(str(Path(plugin_directory) / "__init__.py"), "a") as f:
            f.write(import_line)
    except IOError:
        raise WorkspaceError("Error opening the __init__.py file")


@app.command()
@handle_workspace_errors
def install_deps(
    dependency_cache_dir: Path = typer.Option(
        default=Path(".doit_cache"),
        prompt="Distribution directory",
        help="Creates a distribution directory",
    ),
    output_path: Path = typer.Option(
        ...,
        prompt="Output path including filename",
        help="The path to save the .pyz bootstrap artifact, example: './bootstrap.pyz'",
    ),
) -> None:
    """Install any dependencies for the current workspace tools."""
    typer.echo("Installing dependencies...")
    logger.info("install_deps called...")
    dist_dir = (dependency_cache_dir / "dist").resolve()
    dist_dir.mkdir(exist_ok=True, parents=True)
    curr_dir = Path(".")
    backend_dir = curr_dir / "backend"

    if (
        not (backend_dir / REQ_LOCAL).exists()
        or not (backend_dir / REQ_THIRDPARTY).exists()
    ):
        raise WorkspaceError(
            "Missing requirements files. Please make sure that both 'requirements-thirdparty.txt' and 'requirements-local.txt' exist in the backend folder."
        )
    install_local_dependencies = [
        "python",
        "-m",
        "pip",
        "install",
        "-r",
        REQ_LOCAL,
        "--upgrade",
        "--target",
        str(dist_dir),
    ]
    result = _run_build_artifact_command(
        install_local_dependencies, "Installing local dependencies", backend_dir
    )
    if result != 0:
        raise WorkspaceError(
            "Installing local dependencies failed, aborting YXI generation."
        )
    requirements_changed = _check_requirements_changed(
        dist_dir / REQ_THIRDPARTY,
        backend_dir / REQ_THIRDPARTY,
    )

    if requirements_changed:
        typer.echo("Installing new dependencies...")
        install_third_party_dependencies = [
            "python",
            "-m",
            "pip",
            "install",
            "-r",
            REQ_THIRDPARTY,
            "--upgrade",
            "--target",
            str(dist_dir),
        ]

        result = _run_build_artifact_command(
            install_third_party_dependencies,
            "Installing third party dependencies",
            backend_dir,
        )

        if result != 0:
            Path(dist_dir / REQ_THIRDPARTY).unlink(missing_ok=True)
            raise WorkspaceError(
                "Installing third party dependencies failed, aborting YXI generation."
            )


def _run_build_artifact_command(cmd: List[str], label: str, cwd: Path) -> int:
    try:
        typer.echo(f"[{label}]: {' '.join(cmd)} ")
        process = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd
        )
        if process.returncode != 0:
            typer.echo(
                f"Process [{label}] failed with error code{process.returncode}\nPlease check log for details"
            )
            logger.error(
                "Process returned with non-zero exit code: %s",
                process.stderr,
                exc_info=True,
            )
        return process.returncode
    except subprocess.CalledProcessError as e:
        typer.echo(
            f"Process [{label}] failed with {process.returncode}\nPlease check log for details"
        )
        logger.error(
            "Exception occured during execution of subprocess: %s",
            e.__traceback__,
            exc_info=True,
        )
        return -1


def _check_requirements_changed(
    dist_requirements: Path, backend_requirements: Path
) -> bool:
    try:
        if not dist_requirements.exists():
            shutil.copy(backend_requirements, dist_requirements)
            return True
        else:
            file_changed = not filecmp.cmp(dist_requirements, backend_requirements)
            if file_changed:
                shutil.copy(backend_requirements, dist_requirements)
            return file_changed

    except Exception:
        raise WorkspaceError(
            "Could not find /requirements-thirdparty.txt in the specified directories"
        )


@app.command()
def docs() -> None:
    """Open the ayx-plugin-sdk documentation in a browser."""
    import webbrowser

    docs_index_html = Path(os.path.dirname(__file__)) / "docs" / "index.html"
    webbrowser.open_new_tab(str(docs_index_html))


def _log_info(msg: str) -> None:
    logger.info("INFO: %s", msg)
    typer.echo(f"INFO: {msg}")


def _log_error(msg: str) -> None:
    logger.error("ERROR: %s", msg)
    typer.echo(f"ERROR: {msg}")


def main() -> None:
    """Define the main entry point to typer."""
    app()


if __name__ == "__main__":
    main()
