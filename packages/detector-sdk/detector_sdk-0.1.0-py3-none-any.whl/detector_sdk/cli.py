from __future__ import annotations
import os
import sys
import json
from pathlib import Path
from typing import Any, Dict
import click
import yaml
from .config import DetectorConfig, LogConfig
from .endpoint import DetectorEndpoint
from .loader import load_config, build_endpoint
from .logging_setup import configure_logging
from .client import DetectorClient
from .runner import DetectorRunner
from .echo_server import run_echo_server

DEFAULT_YAML = {
    "APIKEY": "YOUR_API_KEY",
    "SOURCE": "example/source",
    "STORE": "s3://bucket/path",
    "NETWORK": "public",
    "SEMVER": "0.1.0",
    "LOG": {
        "level": "INFO",
        "json": True,
        "destination": "stdout"
    },
    "TRANSPORT": {
        "type": "stdout",
        "stdout": {"pretty": True}
    },
    "INPUT": {
        "type": "local_dir",
        "local_dir": {"path": "./inbox", "pattern": "*.mp4", "poll_interval_sec": 1.0}
    }
}

CONFIG_FILES = ["detector.yaml", "detector.yml"]
RC_FILES = ["detector.rc"]


def load_yaml_file(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_rc_file(path: Path) -> Dict[str, Any]:
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


def find_first(paths):
    for name in paths:
        p = Path(name)
        if p.exists():
            return p
    return None


def resolve_config() -> DetectorConfig:
    yaml_path = find_first(CONFIG_FILES)
    base: Dict[str, Any] = load_yaml_file(yaml_path) if yaml_path else {}

    rc_path = find_first(RC_FILES)
    rc: Dict[str, Any] = load_rc_file(rc_path) if rc_path else {}

    env_overrides: Dict[str, Any] = {}
    for key in ["APIKEY", "SOURCE", "STORE", "NETWORK", "SEMVER"]:
        if key in os.environ:
            env_overrides[key] = os.environ[key]

    log_level = os.environ.get("DETECTOR_LOG_LEVEL")
    log_json = os.environ.get("DETECTOR_LOG_JSON")
    log_dest = os.environ.get("DETECTOR_LOG_DEST")
    log_cfg = base.get("LOG", {})
    if log_level:
        log_cfg["level"] = log_level
    if log_json is not None:
        log_cfg["json"] = log_json.lower() in ("1", "true", "yes")
    if log_dest:
        log_cfg["destination"] = log_dest

    merged = {**base, **rc, **env_overrides, "LOG": log_cfg}

    return DetectorConfig.model_validate(merged)


def make_endpoint(cfg: DetectorConfig) -> DetectorEndpoint:
    return DetectorEndpoint.from_config(cfg)


@click.group()
def main():
    """Detector SDK CLI"""


@main.command()
@click.option("--force", is_flag=True, help="Overwrite existing files")
def init(force: bool):
    """Create a starter detector.yaml and detector.rc"""
    yaml_path = Path("detector.yaml")
    rc_path = Path("detector.rc")
    if yaml_path.exists() and not force:
        click.echo("detector.yaml already exists. Use --force to overwrite.")
    else:
        with yaml_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(DEFAULT_YAML, f, sort_keys=False)
        click.echo("Created detector.yaml")
    if rc_path.exists() and not force:
        click.echo("detector.rc already exists. Use --force to overwrite.")
    else:
        with rc_path.open("w", encoding="utf-8") as f:
            f.write("# key=value overrides\n")
        click.echo("Created detector.rc")


@main.command("validate")
def validate_cmd():
    """Validate configuration files"""
    try:
        cfg = resolve_config()
    except Exception as e:
        click.echo(f"Invalid config: {e}")
        sys.exit(1)
    click.echo("OK")


@main.command("show-endpoint")
@click.option("--format", "fmt", type=click.Choice(["json", "yaml"]) , default="json")
def show_endpoint(fmt: str):
    cfg = load_config()  # uses same resolution as resolve_config
    configure_logging(cfg.log)
    ep = build_endpoint(cfg)
    data = ep.to_dict()
    if fmt == "json":
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(yaml.safe_dump(data, sort_keys=False))


@main.command("register")
def register_cmd():
    cfg = load_config()
    configure_logging(cfg.log)
    client = DetectorClient()
    detector_id, token = client.register()
    click.echo(json.dumps({"detectorId": detector_id, "sessionToken": token}))


@main.command("heartbeat")
@click.option("--metric", multiple=True, help="key=value metric pairs")
def heartbeat_cmd(metric: list[str]):
    cfg = load_config()
    configure_logging(cfg.log)
    metrics = {}
    for m in metric:
        if "=" in m:
            k, v = m.split("=", 1)
            metrics[k] = v
    client = DetectorClient()
    client.heartbeat(metrics or None)
    click.echo("OK")


@main.command("send-event")
@click.option("--type", "event_type", required=True)
@click.option("--data", "data_json", default="{}", help="JSON payload")
def send_event_cmd(event_type: str, data_json: str):
    cfg = load_config()
    configure_logging(cfg.log)
    try:
        data = json.loads(data_json)
    except Exception:
        click.echo("Invalid JSON for --data", err=True)
        sys.exit(1)
    client = DetectorClient()
    client.send_event(event_type, data)
    click.echo("OK")


@main.command("run")
@click.option("--command", "command", default=None, help="Shell command template, use {file} placeholder")
def run_cmd(command: str | None):
    cfg = load_config()
    configure_logging(cfg.log)
    runner = DetectorRunner(command=command)
    runner.run()


@main.command("echo-server")
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=8080, type=int)
def echo_server_cmd(host: str, port: int):
    click.echo(f"Echo server on http://{host}:{port}")
    run_echo_server(host, port)

