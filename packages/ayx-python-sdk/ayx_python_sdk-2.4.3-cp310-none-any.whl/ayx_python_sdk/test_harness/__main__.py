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
"""Entrypoint for the test harness."""
import asyncio
from enum import Enum
from pathlib import Path
from typing import List

from ayx_python_sdk.core import Field, FieldType, Metadata
from ayx_python_sdk.test_harness.plugin_runner import (
    PluginRunner,
    RunMode,
)

import pandas as pd

import typer

pd.set_option("display.max_columns", None)

app = typer.Typer()


class TransportType(Enum):
    """Data serialization formats."""

    ENGINE = "engine"
    ARROW = "arrow"


@app.command()
def version() -> None:
    """Get the version pf the test harness."""
    typer.echo("Version: 1.0.0")


@app.command()
def run_plugin(
    plugin_entrypoint: Path = typer.Argument(
        ..., help="The path to the entrypoint to run."
    ),
    plugins_package: str = typer.Argument(
        ..., help="The package that contains plugins to run."
    ),
    tool_name: str = typer.Argument(..., help="The name of the tool to run."),
    config_xml: Path = typer.Argument(
        ..., help="Config XML file containing input/output anchor config."
    ),
    input_csv: List[Path] = typer.Option(
        "", help="List of CSV files to use as input data."
    ),
    transport_type: str = typer.Option(
        TransportType.ARROW, help="[engine | arrow] which data type to use for the run"
    ),
    run_mode: RunMode = RunMode.full_run,
) -> None:
    """Run a plugin out of process and run data through it."""
    typer.echo(
        f"Running {tool_name} in {'update only' if run_mode == RunMode.update_only else 'full run'} mode.\n"
    )
    input_data = []
    if input_csv:
        for path in input_csv:
            if not path.is_file() or not path.exists():
                raise FileNotFoundError("Could not find input csv data")
            dataframe = pd.read_csv(path)
            input_data.append(dataframe)

    input_metadata = [_get_metadata(df) for df in input_data]

    runner = PluginRunner(
        plugin_entrypoint,
        plugins_package,
        tool_name,
        input_metadata,
        input_data,
        config_xml,
        transport_type,
    )
    asyncio.run(runner.run_plugin_v2(run_mode))

    # Keeping the below as a reminder in case we need to test metadata still.
    # if transport_type == "engine":
    #     output_metadata = runner.get_output_metadata()
    #     typer.echo(f"Output metadata is:\n{output_metadata}\n")

    # if run_mode == RunMode.full_run:
    #     output_data = runner.get_output_data()
    #     typer.echo(f"Output data is:\n{output_data}\n")


def _get_metadata(dataframe: pd.DataFrame) -> Metadata:
    fields = []
    for col in dataframe.columns:
        name, field_type, size = col.split("-")
        fields.append(
            Field(name=name, field_type=FieldType(field_type), size=int(size))
        )

    return Metadata(fields)


def main() -> None:
    """Run the main CLI for the test harness."""
    app()


if __name__ == "__main__":
    main()
