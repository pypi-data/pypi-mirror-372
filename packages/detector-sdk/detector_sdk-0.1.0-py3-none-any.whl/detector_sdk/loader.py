from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from .config import DetectorConfig
from .endpoint import DetectorEndpoint


CONFIG_FILES = ("detector.yaml", "detector.yml")
RC_FILES = ("detector.rc",)


def _load_yaml_file(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_rc_file(path: Path) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                data[key.strip()] = value.strip()
    return data


def _find_first(paths: tuple[str, ...]) -> Optional[Path]:
    for name in paths:
        p = Path(name)
        if p.exists():
            return p
    return None


def load_config() -> DetectorConfig:
    yaml_path = _find_first(CONFIG_FILES)
    base: Dict[str, Any] = _load_yaml_file(yaml_path) if yaml_path else {}

    rc_path = _find_first(RC_FILES)
    rc: Dict[str, Any] = _load_rc_file(rc_path) if rc_path else {}

    env_overrides: Dict[str, Any] = {}
    for key in ("APIKEY", "SOURCE", "STORE", "NETWORK", "SEMVER"):
        if key in os.environ:
            env_overrides[key] = os.environ[key]

    log_level = os.environ.get("DETECTOR_LOG_LEVEL")
    log_json = os.environ.get("DETECTOR_LOG_JSON")
    log_dest = os.environ.get("DETECTOR_LOG_DEST")
    log_cfg = dict(base.get("LOG", {}))
    if log_level:
        log_cfg["level"] = log_level
    if log_json is not None:
        log_cfg["json"] = log_json.lower() in ("1", "true", "yes")
    if log_dest:
        log_cfg["destination"] = log_dest

    # Transport overrides
    transport_cfg = dict(base.get("TRANSPORT", {}))
    transport_type_env = os.environ.get("DETECTOR_TRANSPORT_TYPE")
    if transport_type_env:
        transport_cfg["type"] = transport_type_env
    http_url = os.environ.get("DETECTOR_TRANSPORT_HTTP_URL")
    if http_url:
        http_cfg = dict(transport_cfg.get("http", {}))
        http_cfg["url"] = http_url
        transport_cfg["http"] = http_cfg
    stdout_pretty = os.environ.get("DETECTOR_TRANSPORT_STDOUT_PRETTY")
    if stdout_pretty is not None:
        stdout_cfg = dict(transport_cfg.get("stdout", {}))
        stdout_cfg["pretty"] = stdout_pretty.lower() in ("1", "true", "yes")
        transport_cfg["stdout"] = stdout_cfg

    # Input overrides
    input_cfg = dict(base.get("INPUT", {}))
    input_type = os.environ.get("DETECTOR_INPUT_TYPE")
    if input_type:
        input_cfg["type"] = input_type
    inbox = os.environ.get("DETECTOR_INPUT_LOCAL_DIR_PATH")
    if inbox:
        local = dict(input_cfg.get("local_dir", {}))
        local["path"] = inbox
        input_cfg["local_dir"] = local
    pattern = os.environ.get("DETECTOR_INPUT_LOCAL_DIR_PATTERN")
    if pattern:
        local = dict(input_cfg.get("local_dir", {}))
        local["pattern"] = pattern
        input_cfg["local_dir"] = local
    interval = os.environ.get("DETECTOR_INPUT_LOCAL_DIR_POLL_SEC")
    if interval:
        try:
            interval_f = float(interval)
            local = dict(input_cfg.get("local_dir", {}))
            local["poll_interval_sec"] = interval_f
            input_cfg["local_dir"] = local
        except ValueError:
            pass

    merged = {**base, **rc, **env_overrides, "LOG": log_cfg, "TRANSPORT": transport_cfg, "INPUT": input_cfg}

    return DetectorConfig.model_validate(merged)


def build_endpoint(cfg: DetectorConfig) -> DetectorEndpoint:
    return DetectorEndpoint.from_config(cfg)


