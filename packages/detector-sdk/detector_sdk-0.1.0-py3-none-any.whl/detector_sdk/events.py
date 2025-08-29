from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class RegisterRequest(BaseModel):
    endpoint: Dict[str, Any]


class RegisterResponse(BaseModel):
    detector_id: str = Field(alias="detectorId")
    session_token: str = Field(alias="sessionToken")


class HeartbeatRequest(BaseModel):
    detector_id: str = Field(alias="detectorId")
    session_token: str = Field(alias="sessionToken")
    metrics: Optional[Dict[str, Any]] = None


class Event(BaseModel):
    detector_id: str = Field(alias="detectorId")
    session_token: str = Field(alias="sessionToken")
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)


