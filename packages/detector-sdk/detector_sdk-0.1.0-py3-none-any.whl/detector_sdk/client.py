from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from .loader import load_config, build_endpoint
from .transport import Transport, create_transport
from .session import SessionStore
from .events import RegisterRequest, RegisterResponse, HeartbeatRequest, Event


class DetectorClient:
    def __init__(self, transport: Optional[Transport] = None, session_store: Optional[SessionStore] = None):
        self.cfg = load_config()
        self.transport = transport or create_transport(self.cfg.transport)
        self.session_store = session_store or SessionStore()

    def register(self) -> Tuple[str, str]:
        ep = build_endpoint(self.cfg).to_dict()
        req = RegisterRequest(endpoint=ep)
        headers = {"X-API-Key": self.cfg.apikey}
        resp = self.transport.send("register", req.model_dump(by_alias=True), headers)
        # Prefer transport response if present
        if isinstance(resp, dict) and "detectorId" in resp and "sessionToken" in resp:
            detector_id = str(resp["detectorId"])
            session_token = str(resp["sessionToken"])
            self.session_store.save(detector_id, session_token)
            return detector_id, session_token
        # Otherwise use existing or synthesize
        existing = self.session_store.load()
        if existing:
            return existing
        detector_id = f"{self.cfg.source}:{self.cfg.semver}"
        session_token = "local-session"
        self.session_store.save(detector_id, session_token)
        return detector_id, session_token

    def heartbeat(self, metrics: Optional[Dict[str, Any]] = None) -> None:
        session = self.session_store.load()
        if not session:
            session = self.register()
        detector_id, session_token = session
        req = HeartbeatRequest(detectorId=detector_id, sessionToken=session_token, metrics=metrics)
        headers = {"X-API-Key": self.cfg.apikey}
        self.transport.send("heartbeat", req.model_dump(by_alias=True), headers)

    def send_event(self, event_type: str, data: Dict[str, Any]) -> None:
        session = self.session_store.load()
        if not session:
            session = self.register()
        detector_id, session_token = session
        evt = Event(detectorId=detector_id, sessionToken=session_token, type=event_type, data=data)
        headers = {"X-API-Key": self.cfg.apikey}
        self.transport.send("event", evt.model_dump(by_alias=True), headers)


