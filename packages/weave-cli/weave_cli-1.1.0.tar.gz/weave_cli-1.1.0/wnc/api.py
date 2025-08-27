from __future__ import annotations

import asyncio
from typing import List, Optional

# Re-export useful result types for typing convenience
from .scanners.ports import PortResult as PortResult
from .scanners.cameras import CameraCandidate as CameraCandidate

from .scanners.network import (
    get_internal_subnets as _get_internal_subnets,
    discover_hosts as _discover_hosts,
)
from .scanners.ports import scan_ports as _scan_ports
from .scanners.cameras import detect_cameras as _detect_cameras
from .wizard import run_wizard as _run_wizard


def _run_async(coro):
    """Run an async coroutine from sync code safely."""
    try:
        return asyncio.run(coro)
    except RuntimeError:
        # Fallback for environments where an event loop is already running
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


# ---- High-level sync helpers ----

def internal_subnets() -> List[str]:
    """Return local internal subnets as strings (e.g., '192.168.1.0/24')."""
    return [str(s) for s in _get_internal_subnets()]


def hosts(subnet: str, limit: Optional[int] = None) -> List[str]:
    """Discover live hosts in a subnet. Uses fast TCP connect probes."""
    return _run_async(_discover_hosts(subnet, limit=limit))


def ports(host: str, top_n: int = 200, ports: Optional[List[int]] = None) -> List[PortResult]:
    """Scan TCP ports on a host. Returns a list of PortResult."""
    return _run_async(_scan_ports(host, top_n=top_n, ports=ports))


def cameras(subnet: str) -> List[CameraCandidate]:
    """Detect likely IP cameras in a subnet. Returns a list of CameraCandidate."""
    return _run_async(_detect_cameras(subnet))


def wizard(
    *,
    extended: Optional[bool] = None,
    speedtest_runs: Optional[int] = None,
    output: Optional[str] = None,
    analyze: bool = True,
    yes: bool = False,
    weak_auth: bool = False,
    creds: Optional[List[str]] = None,
    change_password: bool = False,
    change_user: Optional[str] = None,
    new_password: Optional[str] = None,
    wifi: bool = False,
    lan_speed: bool = False,
) -> None:
    """Run the interactive wizard from code (synchronous wrapper)."""
    return _run_async(
        _run_wizard(
            extended=extended,
            speedtest_runs=speedtest_runs,
            output_path=output,
            analyze=analyze,
            assume_yes=yes,
            weak_auth=weak_auth,
            default_creds=creds,
            change_password=change_password,
            change_user=change_user,
            new_password=new_password,
            wifi=wifi,
            lan_speed=lan_speed,
        )
    )
