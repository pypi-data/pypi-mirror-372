from __future__ import annotations
import json
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple
import urllib.request
import urllib.error

from .config import TransportConfig, TransportHTTPConfig, TransportStdoutConfig


class Transport(ABC):
    @abstractmethod
    def send(self, path: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


class StdoutTransport(Transport):
    def __init__(self, cfg: TransportStdoutConfig):
        self.cfg = cfg

    def send(self, path: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        data = json.dumps({"path": path, "payload": payload, "headers": headers or {}}, indent=2 if self.cfg.pretty else None)
        sys.stdout.write(data + "\n")
        return None


class HTTPTransport(Transport):
    def __init__(self, cfg: TransportHTTPConfig):
        self.cfg = cfg

    def send(self, path: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        url = self.cfg.url.rstrip("/") + "/" + path.lstrip("/")
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        for k, v in (self.cfg.headers or {}).items():
            req.add_header(k, v)
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=self.cfg.timeout_seconds) as resp:
                body = resp.read()
                ctype = resp.headers.get("Content-Type", "")
                if body:
                    try:
                        return json.loads(body.decode("utf-8"))
                    except Exception:
                        return {"raw": body.decode("utf-8", errors="ignore"), "contentType": ctype}
                return None
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP error {e.code}: {e.reason}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"HTTP transport error: {e.reason}") from e


def create_transport(cfg: TransportConfig) -> Transport:
    t = (cfg.type or "stdout").lower()
    if t == "http":
        http_cfg = cfg.http or TransportHTTPConfig()
        return HTTPTransport(http_cfg)
    return StdoutTransport(cfg.stdout or TransportStdoutConfig())


