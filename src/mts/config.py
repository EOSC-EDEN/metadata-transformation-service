"""Application settings; the core has no dependency on Flask."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """Operator settings. Paths are relative to the working directory by default."""

    resource_path: Path = Path("resources")
    max_metadata_bytes: int = 1_000_000
    max_request_bytes: int = 2_000_000

    @classmethod
    def from_env(cls):
        """Read optional deployment overrides without mutating module globals."""
        return cls(
            resource_path=Path(os.getenv("MTS_RESOURCE_PATH", "resources")),
            max_metadata_bytes=int(os.getenv("MTS_MAX_METADATA_BYTES", "1000000")),
            max_request_bytes=int(os.getenv("MTS_MAX_REQUEST_BYTES", "2000000")),
        )

    def __post_init__(self):
        if self.max_metadata_bytes <= 0 or self.max_request_bytes <= 0:
            raise ValueError("Size limits must be positive")
