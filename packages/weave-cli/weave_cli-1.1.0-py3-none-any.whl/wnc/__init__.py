__app_name__ = "wnc"
__version__ = "1.1.0"

# Public library API
from .api import (
    internal_subnets,
    hosts,
    ports,
    cameras,
    wizard,
    PortResult,
    CameraCandidate,
)

__all__ = [
    "__app_name__",
    "__version__",
    # API
    "internal_subnets",
    "hosts",
    "ports",
    "cameras",
    "wizard",
    # Types
    "PortResult",
    "CameraCandidate",
]
