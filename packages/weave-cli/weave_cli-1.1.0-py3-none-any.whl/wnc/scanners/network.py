from __future__ import annotations

import asyncio
from typing import List, Dict
import socket

import psutil
from netaddr import IPNetwork, IPAddress

COMMON_HOST_PROBE_PORTS = [80, 443, 22, 53, 3389, 8080, 8443, 8000, 139, 445]
CONNECT_TIMEOUT = 0.5
SEM_LIMIT = 500


def get_interfaces() -> Dict[str, List[str]]:
    """Return a map of interface name -> list of IPv4 addresses."""
    if_addrs = psutil.net_if_addrs()
    out: Dict[str, List[str]] = {}
    for name, addrs in if_addrs.items():
        v4s = []
        for a in addrs:
            if getattr(a, 'family', None) == socket.AF_INET:
                ip = a.address
                if ip and not ip.startswith("169.254.") and ip != "127.0.0.1":
                    v4s.append(ip)
        if v4s:
            out[name] = v4s
    return out


def get_internal_subnets() -> List[IPNetwork]:
    """Infer internal subnets from interface addresses and netmasks."""
    subnets: List[IPNetwork] = []
    for name, addrs in psutil.net_if_addrs().items():
        for a in addrs:
            if getattr(a, 'family', None) == socket.AF_INET and a.address and a.netmask:
                try:
                    # Build CIDR from ip + netmask
                    cidr = IPNetwork(f"{a.address}/{a.netmask}")
                    # Skip loopback and link-local
                    if IPAddress(a.address).is_loopback() or str(cidr).startswith("169.254."):
                        continue
                    # Skip /32 and very small masks
                    if cidr.prefixlen >= 31:
                        continue
                    # Deduplicate
                    if all(cidr != s for s in subnets):
                        subnets.append(cidr)
                except Exception:
                    continue
    return subnets


async def _probe_host(ip: str, sem: asyncio.Semaphore) -> bool:
    async with sem:
        for port in COMMON_HOST_PROBE_PORTS:
            try:
                fut = asyncio.open_connection(ip, port)
                reader, writer = await asyncio.wait_for(fut, timeout=CONNECT_TIMEOUT)
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:
                    pass
                return True
            except Exception:
                continue
        return False


async def discover_hosts(subnet: str, limit: int | None = None) -> List[str]:
    """Return list of IPs that responded to a fast TCP connect on common ports."""
    net = IPNetwork(subnet)
    ips = [str(ip) for ip in net.iter_hosts()]
    if limit:
        ips = ips[:limit]
    sem = asyncio.Semaphore(SEM_LIMIT)
    results = await asyncio.gather(*(_probe_host(ip, sem) for ip in ips), return_exceptions=True)
    live = [ip for ip, ok in zip(ips, results) if ok is True]
    return live
