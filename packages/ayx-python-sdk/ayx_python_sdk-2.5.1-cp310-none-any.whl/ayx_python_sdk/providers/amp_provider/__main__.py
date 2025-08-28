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
"""Entrypoint for tracer bullet application."""
import asyncio
import logging

from ayx_python_sdk.providers.amp_provider.amp_driver import AMPDriver
from ayx_python_sdk.providers.amp_provider.logger_config import configure_logger
from ayx_python_sdk.providers.amp_provider.plugin_class_loader import load_plugin_class
from ayx_python_sdk.providers.amp_provider.sdk_tool_runner import SdkToolRunner


import typer

app = typer.Typer()


@app.command()
def version() -> None:
    """Get the version of the CLI."""
    typer.echo("Version 1.0.0")


@app.command()
def start_sdk_tool_service(
    plugins_package: str,
    tool_name: str,
    sdk_engine_server_address: str = "localhost:6500",
) -> None:
    """Start the SDK Tool service."""
    configure_logger()
    logger = logging.getLogger()
    try:
        _log_info(f"Starting {tool_name} tool with AMP Provider.")
        driver = AMPDriver()
        # Could conditionally load Plugin V1 or V2 here if found necessary
        plugin_class = load_plugin_class(plugins_package, tool_name)
        driver._plugin_class = plugin_class

        runner = SdkToolRunner(
            sdk_engine_server_address  # SocketAddress.from_address_str(sdk_engine_server_address)
        )
        try:
            asyncio.get_event_loop().run_until_complete(runner.start_service())
        except Exception as e:
            _log_error(f"ERROR: Couldn't start service.")
            logger.exception(e)
            raise typer.Exit(code=1)
        _log_info("Exiting process")
    except Exception as e:
        typer.echo(f"EXCEPTION: {e}")
        logger.exception(e)
        raise


def _log_info(msg: str) -> None:
    logger = logging.getLogger()
    logger.info("INFO: %s", msg)
    typer.echo(f"INFO: {msg}")


def _log_error(msg: str) -> None:
    logger = logging.getLogger()
    logger.error("ERROR: %s", msg)
    typer.echo(f"ERROR: {msg}")


def main() -> None:
    """Entrypoint method for the tracer bullet application."""
    app()


if __name__ == "__main__":
    main()
