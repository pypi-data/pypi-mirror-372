from __future__ import annotations

import re
import subprocess
import shutil
from dataclasses import dataclass
from typing import Dict, Optional

# Minimal OUI map (expandable). Prefixes are upper-case without separators.
OUI_MAP: Dict[str, str] = {
    "BC305B": "Hikvision",
    "D4C1C8": "Dahua",
    "00408C": "Axis Communications",
    "F0B0E7": "Ubiquiti Networks",
    "18E829": "Ubiquiti Networks",
    "FCECDA": "Ubiquiti Networks",
    "A4DA22": "Reolink",
    "BCADAB": "TP-Link",
    "ACF2C5": "Amazon Technologies",
    "84742A": "Google",
    "001132": "Cisco",
    "000C29": "VMware",
}

@dataclass
class ArpEntry:
    ip: str
    mac: str
    iface: Optional[str] = None
    vendor: Optional[str] = None


def _normalize_mac(mac: str) -> str:
    return re.sub(r"[^0-9A-Fa-f]", "", mac).upper()


def _lookup_vendor(mac: str) -> Optional[str]:
    nm = _normalize_mac(mac)
    for l in (6, 7, 8):  # try 24-bit and some longer OUIs if present
        p = nm[:l]
        if p in OUI_MAP:
            return OUI_MAP[p]
    p24 = nm[:6]
    return OUI_MAP.get(p24)


def read_arp_table() -> Dict[str, ArpEntry]:
    """Parse system ARP table using `arp -an` (macOS/Linux) if available.
    Returns mapping ip -> ArpEntry.
    """
    cmd = shutil.which("arp")
    if not cmd:
        return {}
    try:
        out = subprocess.check_output([cmd, "-an"], text=True, timeout=3)
    except Exception:
        return {}
    entries: Dict[str, ArpEntry] = {}
    # macOS/Linux typical line: ? (192.168.1.10) at dc:a6:32:12:34:56 on en0 ifscope [ethernet]
    # or: ? (192.168.1.10) at dc-a6-32-12-34-56 on en0 [ethernet]
    pat = re.compile(r"\((?P<ip>\d+\.\d+\.\d+\.\d+)\) at (?P<mac>[0-9a-fA-F:\-]{11,}) on (?P<iface>\S+)")
    for line in out.splitlines():
        m = pat.search(line)
        if not m:
            continue
        ip = m.group("ip")
        mac = m.group("mac").replace('-', ':')
        iface = m.group("iface")
        vendor = _lookup_vendor(mac)
        entries[ip] = ArpEntry(ip=ip, mac=mac, iface=iface, vendor=vendor)
    return entries
