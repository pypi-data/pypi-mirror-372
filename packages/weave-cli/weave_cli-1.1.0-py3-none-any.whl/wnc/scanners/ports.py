from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import List, Optional

TOP_COMMON_PORTS = [
    80, 443, 22, 21, 25, 110, 143, 53, 123, 135, 139, 445, 3306, 3389, 8080,
    8443, 8000, 1723, 5900, 995, 993, 587, 161, 162, 554, 5060, 8888, 6379,
    11211, 5000, 9000, 1883, 8883, 5432, 27017, 9200, 32400, 32469
]

SERVICE_HINTS = {
    80: ("tcp", "http"),
    443: ("tcp", "https"),
    22: ("tcp", "ssh"),
    21: ("tcp", "ftp"),
    25: ("tcp", "smtp"),
    110: ("tcp", "pop3"),
    143: ("tcp", "imap"),
    53: ("udp/tcp", "dns"),
    123: ("udp", "ntp"),
    135: ("tcp", "rpc"),
    139: ("tcp", "netbios"),
    445: ("tcp", "smb"),
    3306: ("tcp", "mysql"),
    3389: ("tcp", "rdp"),
    8080: ("tcp", "http-alt"),
    8443: ("tcp", "https-alt"),
    8000: ("tcp", "http-alt"),
    1723: ("tcp", "pptp"),
    5900: ("tcp", "vnc"),
    995: ("tcp", "pop3s"),
    993: ("tcp", "imaps"),
    587: ("tcp", "submission"),
    161: ("udp", "snmp"),
    162: ("udp", "snmp-trap"),
    554: ("tcp", "rtsp"),
    5060: ("udp/tcp", "sip"),
    6379: ("tcp", "redis"),
    11211: ("tcp", "memcached"),
    5000: ("tcp", "http-alt"),
    9000: ("tcp", "http-alt"),
    1883: ("tcp", "mqtt"),
    8883: ("tcp", "mqtts"),
    5432: ("tcp", "postgres"),
    27017: ("tcp", "mongodb"),
    9200: ("tcp", "elasticsearch"),
    32400: ("tcp", "plex"),
    32469: ("tcp", "plex-dlna"),
}

CONNECT_TIMEOUT = 0.6
SEM_LIMIT = 500


@dataclass
class PortResult:
    port: int
    proto: str
    service: Optional[str]


async def _check_port(host: str, port: int, sem: asyncio.Semaphore) -> Optional[PortResult]:
    async with sem:
        try:
            fut = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(fut, timeout=CONNECT_TIMEOUT)
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            proto, svc = SERVICE_HINTS.get(port, ("tcp", None))
            return PortResult(port=port, proto=proto, service=svc)
        except Exception:
            return None


async def scan_ports(host: str, top_n: int = 200, ports: Optional[List[int]] = None) -> List[PortResult]:
    """Scan TCP ports on a host using async connect. Returns list of open ports with hints.

    - If `ports` is provided, scan exactly those ports.
    - Else scan the first `top_n` from TOP_COMMON_PORTS (bounded by list length).
    """
    if ports is None:
        to_scan = TOP_COMMON_PORTS[: min(top_n, len(TOP_COMMON_PORTS))]
    else:
        to_scan = list(dict.fromkeys(ports))  # dedupe keep order

    sem = asyncio.Semaphore(SEM_LIMIT)
    results = await asyncio.gather(*(_check_port(host, p, sem) for p in to_scan))
    open_ports = [r for r in results if r is not None]
    open_ports.sort(key=lambda r: r.port)
    return open_ports
