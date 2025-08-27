from __future__ import annotations

import socket
import time
from dataclasses import dataclass
from typing import List, Dict

SSDP_ADDR = '239.255.255.250'
SSDP_PORT = 1900
MSEARCH = (
    "M-SEARCH * HTTP/1.1\r\n"
    f"HOST: {SSDP_ADDR}:{SSDP_PORT}\r\n"
    "MAN: \"ssdp:discover\"\r\n"
    "MX: 2\r\n"
    "ST: ssdp:all\r\n\r\n"
)

@dataclass
class SsdpDevice:
    ip: str
    st: str
    usn: str
    server: str
    location: str


def discover_ssdp(timeout: float = 3.0) -> List[SsdpDevice]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)
    try:
        # Multiple interfaces may exist; simple unicast send
        sock.sendto(MSEARCH.encode('utf-8'), (SSDP_ADDR, SSDP_PORT))
        devices: Dict[tuple, SsdpDevice] = {}
        t_end = time.time() + timeout
        while time.time() < t_end:
            try:
                data, addr = sock.recvfrom(8192)
            except socket.timeout:
                break
            except Exception:
                break
            ip = addr[0]
            headers = {}
            try:
                text = data.decode(errors='ignore').split('\r\n')
                for line in text[1:]:
                    if ':' in line:
                        k, v = line.split(':', 1)
                        headers[k.strip().lower()] = v.strip()
            except Exception:
                pass
            dev = SsdpDevice(
                ip=ip,
                st=headers.get('st', ''),
                usn=headers.get('usn', ''),
                server=headers.get('server', ''),
                location=headers.get('location', ''),
            )
            key = (ip, dev.usn or dev.st)
            devices[key] = dev
        return list(devices.values())
    finally:
        sock.close()
