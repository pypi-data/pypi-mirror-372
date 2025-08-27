from __future__ import annotations

import plistlib
import re
import shutil
import subprocess
from typing import Any, Dict, List, Optional


AIRPORT = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"


def _run_airport(args: List[str]) -> Optional[str]:
    if not shutil.which(AIRPORT):
        return None
    try:
        out = subprocess.check_output([AIRPORT, *args], stderr=subprocess.DEVNULL)
        return out.decode("utf-8", errors="replace")
    except Exception:
        return None


def _wifi_device() -> Optional[str]:
    """Find the macOS Wi‑Fi device name (e.g., en0 or en1) via networksetup.

    Returns the device string or None if not found.
    """
    try:
        out = subprocess.check_output(["/usr/sbin/networksetup", "-listallhardwareports"], stderr=subprocess.DEVNULL)
        s = out.decode("utf-8", errors="replace")
    except Exception:
        return None
    dev = None
    block = []
    for line in s.splitlines():
        line = line.strip()
        if not line:
            # end of block
            if any(l.lower().startswith("hardware port: wi-fi") or l.lower().startswith("hardware port: wifi") for l in block):
                for l in block:
                    if l.lower().startswith("device:"):
                        dev = l.split(":", 1)[1].strip()
                        break
                if dev:
                    return dev
            block = []
            continue
        block.append(line)
    # tail block
    if any(l.lower().startswith("hardware port: wi-fi") or l.lower().startswith("hardware port: wifi") for l in block):
        for l in block:
            if l.lower().startswith("device:"):
                dev = l.split(":", 1)[1].strip()
                break
    return dev


def _current_via_networksetup() -> Optional[Dict[str, Any]]:
    """Fallback: use networksetup to get current SSID for the Wi‑Fi device.
    BSSID/Channel/RSSI/Noise are not provided here, so we only fill SSID when possible.
    """
    dev = _wifi_device()
    if not dev:
        return None
    try:
        out = subprocess.check_output(["/usr/sbin/networksetup", "-getairportnetwork", dev], stderr=subprocess.DEVNULL)
        s = out.decode("utf-8", errors="replace").strip()
    except Exception:
        return None
    # Example outputs:
    # "Current Wi-Fi Network: MySSID" or "You are not associated with an AirPort network."
    if "not associated" in s.lower():
        return {"ssid": None, "bssid": None, "band": None, "channel": None, "rssi": None, "noise": None, "tx_rate": None, "country": None, "auth": None}
    m = re.search(r":\s*(.*)$", s)
    ssid = m.group(1).strip() if m else None
    return {"ssid": ssid, "bssid": None, "band": None, "channel": None, "rssi": None, "noise": None, "tx_rate": None, "country": None, "auth": None}


def current_info() -> Optional[Dict[str, Any]]:
    # `airport -I` prints key: value pairs
    s = _run_airport(["-I"])
    if s:
        info: Dict[str, Any] = {}
        for line in s.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip()
                info[k] = v
        # Normalize keys
        res = {
            "ssid": info.get("SSID"),
            "bssid": info.get("BSSID"),
            "band": info.get("agrCtlChannel"),
            "channel": _parse_channel(info.get("channel")),
            "rssi": _to_int(info.get("agrCtlRSSI")),
            "noise": _to_int(info.get("agrCtlNoise")),
            "tx_rate": info.get("lastTxRate"),
            "country": info.get("country code"),
            "auth": info.get("link auth"),
        }
        # If airport is present but not associated, SSID may be missing -> fallback to networksetup for SSID
        if not res.get("ssid"):
            via_ns = _current_via_networksetup()
            if via_ns and via_ns.get("ssid") is not None:
                res["ssid"] = via_ns["ssid"]
        return res
    # Fallback if airport not available
    return _current_via_networksetup()


def scan_nearby(limit: int = 30) -> List[Dict[str, Any]]:
    # `airport -s` prints a table
    s = _run_airport(["-s"])
    if not s:
        return []
    lines = s.splitlines()
    if not lines:
        return []
    # Heuristic parse: columns are SSID BSSID RSSI CHANNEL HT CC SECURITY
    out: List[Dict[str, Any]] = []
    for line in lines[1:]:
        line = line.rstrip()
        if not line:
            continue
        # BSSID is MAC-like
        m = re.search(r"([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})", line)
        if not m:
            continue
        bssid = m.group(1)
        ssid = line[: m.start()].strip()
        tail = line[m.end():].strip()
        parts = tail.split()
        rssi = _to_int(parts[0]) if parts else None
        channel = _parse_channel(parts[1]) if len(parts) > 1 else None
        cc = parts[3] if len(parts) > 3 else None
        security = " ".join(parts[4:]) if len(parts) > 4 else None
        out.append({
            "ssid": ssid,
            "bssid": bssid,
            "rssi": rssi,
            "channel": channel,
            "country": cc,
            "security": security,
        })
        if len(out) >= limit:
            break
    return out


def _parse_channel(v: Optional[str]) -> Optional[int]:
    if not v:
        return None
    try:
        return int(str(v).split(",")[0])
    except Exception:
        return None


def _to_int(v: Optional[str]) -> Optional[int]:
    try:
        return int(v) if v is not None else None
    except Exception:
        return None
