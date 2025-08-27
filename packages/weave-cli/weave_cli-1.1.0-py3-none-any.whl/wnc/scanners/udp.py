from __future__ import annotations

import socket
import struct
import time
from dataclasses import dataclass
from typing import List, Optional

# Basic UDP service probes that yield responses without special privileges.
# - DNS (53): standard query for A record of example.com
# - NTP (123): client request; many servers respond
# - SNMP (161): try a simple GET sysDescr with 'public' (may be blocked)

DNS_QUERY = bytes.fromhex(
    "abcd01000001000000000000076578616d706c6503636f6d0000010001"
)

# NTP request: all zero except first byte 0x1b (LI=0, VN=3, Mode=3)
NTP_QUERY = b"\x1b" + b"\x00" * 47

# Minimal SNMPv1 GET for 1.3.6.1.2.1.1.1.0 with community 'public'
SNMP_PUBLIC_SYS_DESCR = bytes.fromhex(
    "303902010004067075626c6963a02c02044a4b4c4d020100020100301e300c06082b060102010101000500300e06082b06010201010100020100"
)

SOCK_TIMEOUT = 0.8

@dataclass
class UdpService:
    port: int
    service: str
    detail: Optional[str] = None


def _probe_dns(ip: str) -> Optional[UdpService]:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(SOCK_TIMEOUT)
            s.sendto(DNS_QUERY, (ip, 53))
            data, _ = s.recvfrom(512)
            if data and data[:2] == DNS_QUERY[:2]:
                return UdpService(port=53, service="dns", detail="dns-response")
    except Exception:
        pass
    return None


def _probe_ntp(ip: str) -> Optional[UdpService]:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(SOCK_TIMEOUT)
            s.sendto(NTP_QUERY, (ip, 123))
            data, _ = s.recvfrom(48)
            if data and len(data) >= 48:
                return UdpService(port=123, service="ntp", detail="ntp-response")
    except Exception:
        pass
    return None


def _probe_snmp(ip: str) -> Optional[UdpService]:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(SOCK_TIMEOUT)
            s.sendto(SNMP_PUBLIC_SYS_DESCR, (ip, 161))
            data, _ = s.recvfrom(1024)
            if data:
                return UdpService(port=161, service="snmp", detail="community=public")
    except Exception:
        pass
    return None


def probe_udp_services(ip: str) -> List[UdpService]:
    found: List[UdpService] = []
    for fn in (_probe_dns, _probe_ntp, _probe_snmp):
        svc = fn(ip)
        if svc:
            found.append(svc)
    return found
