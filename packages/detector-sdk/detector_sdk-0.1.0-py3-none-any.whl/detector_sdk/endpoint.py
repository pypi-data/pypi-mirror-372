from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class DetectorEndpoint(BaseModel):
    kind: str = Field(default="detector")
    name: Optional[str] = None
    version: str = Field(default="0.1.0")
    properties: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_none=True)

    @classmethod
    def from_config(cls, cfg: "DetectorConfig") -> "DetectorEndpoint":
        from .config import DetectorConfig as _DetectorConfig
        assert isinstance(cfg, _DetectorConfig)
        properties: Dict[str, Any] = {
            "APIKEY": cfg.apikey,
            "SOURCE": cfg.source,
            "STORE": cfg.store,
            "NETWORK": cfg.network,
            "SEMVER": cfg.semver,
            "LOG": cfg.log.model_dump(by_alias=True),
            "EXTRA": cfg.extra,
        }
        return cls(name=cfg.source, version=cfg.semver, properties=properties)

