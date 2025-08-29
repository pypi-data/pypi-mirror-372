from __future__ import annotations
import time
from pathlib import Path
from typing import Iterator
import fnmatch

from .config import InputLocalDirConfig


class LocalDirectorySource:
    def __init__(self, cfg: InputLocalDirConfig):
        self.cfg = cfg
        self.root = Path(cfg.path)
        self.seen: set[str] = set()
        self.root.mkdir(parents=True, exist_ok=True)

    def poll(self) -> Iterator[Path]:
        pattern = self.cfg.pattern
        for p in self.root.iterdir():
            if not p.is_file():
                continue
            if p.name in self.seen:
                continue
            if not fnmatch.fnmatch(p.name, pattern):
                continue
            # Simple stabilization: wait one poll cycle for new files
            self.seen.add(p.name)
            yield p

    def run(self) -> Iterator[Path]:
        interval = self.cfg.poll_interval_sec
        while True:
            yield from self.poll()
            time.sleep(interval)


