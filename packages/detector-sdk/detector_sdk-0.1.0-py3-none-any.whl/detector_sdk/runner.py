from __future__ import annotations
import json
import shlex
import subprocess
from typing import Callable, Optional
from pathlib import Path

from .client import DetectorClient
from .config import DetectorConfig, InputLocalDirConfig
from .loader import load_config
from .source_local import LocalDirectorySource


Handler = Callable[[Path, DetectorClient, DetectorConfig], None]


def _run_command(command: str, file_path: Path) -> int:
    cmd = command.format(file=str(file_path))
    return subprocess.call(shlex.split(cmd))


class DetectorRunner:
    def __init__(self, handler: Optional[Handler] = None, command: Optional[str] = None):
        self.cfg = load_config()
        self.client = DetectorClient()
        self.handler = handler
        self.command = command

    def handle_file(self, file_path: Path) -> None:
        # Ensure session exists
        self.client.register()
        if self.handler is not None:
            self.handler(file_path, self.client, self.cfg)
        elif self.command is not None:
            code = _run_command(self.command, file_path)
            self.client.send_event(
                "process.exit",
                {"file": str(file_path), "exitCode": code},
            )
        else:
            # Default behavior: emit event only
            self.client.send_event("file.ready", {"file": str(file_path)})

    def run(self) -> None:
        # Only local_dir is implemented initially
        src_cfg = self.cfg.input.local_dir or InputLocalDirConfig()
        local = LocalDirectorySource(src_cfg)
        for path in local.run():
            self.handle_file(path)


