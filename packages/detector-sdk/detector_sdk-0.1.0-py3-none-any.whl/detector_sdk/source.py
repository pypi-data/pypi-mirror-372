from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator

from .config import InputConfig, InputLocalDirConfig
from .source_local import LocalDirectorySource


class DetectorSource(ABC):
    @abstractmethod
    def run(self) -> Iterator[Path]:
        """Yield ready file paths according to input configuration."""
        raise NotImplementedError


def create_source(cfg: InputConfig) -> DetectorSource:
    input_type = (cfg.type or "local_dir").lower()
    if input_type == "local_dir":
        local_cfg: InputLocalDirConfig = cfg.local_dir or InputLocalDirConfig()
        return LocalDirectorySource(local_cfg)
    # Future: add s3/gcs/queue implementations
    local_cfg = cfg.local_dir or InputLocalDirConfig()
    return LocalDirectorySource(local_cfg)


