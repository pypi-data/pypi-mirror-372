from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class LogConfig(BaseModel):
    level: str = Field(default="INFO")
    json_enabled: bool = Field(default=True, alias="json")
    destination: Optional[str] = Field(default=None, description="file path or 'stdout'")

class TransportHTTPConfig(BaseModel):
    type: str = Field(default="http")
    url: str = Field(default="http://localhost:8080/detector")
    timeout_seconds: float = Field(default=5.0)
    headers: Dict[str, str] = Field(default_factory=dict)

class TransportStdoutConfig(BaseModel):
    type: str = Field(default="stdout")
    pretty: bool = Field(default=True)

class TransportConfig(BaseModel):
    # Union-like config, chosen by 'type'
    type: str = Field(default="stdout")
    http: Optional[TransportHTTPConfig] = None
    stdout: Optional[TransportStdoutConfig] = None

class InputLocalDirConfig(BaseModel):
    path: str = Field(default="./inbox")
    pattern: str = Field(default="*.mp4")
    poll_interval_sec: float = Field(default=1.0)

class InputConfig(BaseModel):
    type: str = Field(default="local_dir")
    local_dir: Optional[InputLocalDirConfig] = None

class DetectorConfig(BaseModel):
    apikey: str = Field(alias="APIKEY")
    source: str = Field(alias="SOURCE")
    store: Optional[str] = Field(default=None, alias="STORE")
    network: Optional[str] = Field(default=None, alias="NETWORK")
    semver: str = Field(default="0.1.0", alias="SEMVER")
    log: LogConfig = Field(default_factory=LogConfig, alias="LOG")
    extra: Dict[str, Any] = Field(default_factory=dict, alias="EXTRA")
    transport: TransportConfig = Field(default_factory=TransportConfig, alias="TRANSPORT")
    input: InputConfig = Field(default_factory=InputConfig, alias="INPUT")

    class Config:
        populate_by_name = True
        extra = "allow"

