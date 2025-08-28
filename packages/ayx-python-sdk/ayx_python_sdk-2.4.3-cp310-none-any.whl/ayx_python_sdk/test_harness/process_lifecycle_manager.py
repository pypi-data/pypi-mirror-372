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
"""OS independent process management class."""
import subprocess
import time
from abc import ABC
from pathlib import Path
from typing import Any, List, Optional

import psutil

import typer


class ProcessLifecycleManager(ABC):
    """Class for managing the lifecycle of a process."""

    def __init__(self, args: List[str]) -> None:
        """Construct the process lifecycle manager."""
        self._args = args
        self._process: Optional[subprocess.Popen] = None

    def __enter__(self) -> "ProcessLifecycleManager":
        """Enter the context manager and start the process."""
        self._start_process()

        if not self.process_alive():
            raise RuntimeError("Process didn't start correctly.")

        typer.echo("Plugin process started successfully.\n")

        return self

    def __exit__(self, *_: Any, **__: Any) -> None:
        """Exit the process manager and kill the process."""
        if self.process_alive():
            typer.echo("Attemping to kill plugin process.")
            self._kill_process()

        typer.echo("Plugin process killed successfully.\n")

    def _start_process(self) -> None:
        """Start the process."""
        self._process = subprocess.Popen(
            self._args,
            cwd=str(Path(__file__).parent.parent.parent),
        )

    def _kill_process(self, timeout: float = 10.0) -> None:
        """Kill the process and any subprocesses."""
        if self._process is None:
            raise ValueError("Can't kill before process has started.")

        process = psutil.Process(self._process.pid)
        for subprocess_ in process.children(recursive=True):
            subprocess_.terminate()
        process.terminate()

        start = time.time()
        while self.process_alive():
            if time.time() - start > timeout:
                raise RuntimeError("Timeout reached waiting for process to die.")

    def process_alive(self) -> bool:
        """Check if the process is still running."""
        if self._process is None:
            raise ValueError("Process hasn't been started.")

        return self._process.poll() is None
