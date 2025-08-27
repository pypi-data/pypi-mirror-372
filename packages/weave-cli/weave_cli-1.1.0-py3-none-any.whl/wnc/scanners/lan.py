from __future__ import annotations

import subprocess
import sys
import time
import socket
from typing import List, Optional, Dict, Tuple

DEFAULT_PORTS = [53, 80, 443]
CONNECT_TIMEOUT = 0.6


def _run(cmd: List[str]) -> str:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        return out
    except Exception:
        return ""


def get_default_gateway() -> Optional[str]:
    """Best-effort default gateway detection (macOS/Linux)."""
    if sys.platform == "darwin":
        out = _run(["route", "-n", "get", "default"])
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("gateway: "):
                gw = line.split(" ", 1)[1].strip()
                if gw:
                    return gw
        # Fallback to netstat
        out = _run(["netstat", "-nr"])
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[0] == "default":
                return parts[1]
    else:
        # Linux
        out = _run(["ip", "route", "show", "default"]) or _run(["ip", "r"])
        for line in out.splitlines():
            parts = line.split()
            if parts and parts[0] == "default":
                # default via 192.168.1.1 dev ...
                try:
                    idx = parts.index("via")
                    return parts[idx + 1]
                except Exception:
                    continue
        # Fallback to netstat
        out = _run(["netstat", "-rn"]) or _run(["route", "-n"])
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 2 and (parts[0] == "0.0.0.0" or parts[0] == "default"):
                return parts[1]
    return None


def get_dns_servers() -> List[str]:
    """Best-effort DNS resolver list (macOS/Linux)."""
    servers: List[str] = []
    if sys.platform == "darwin":
        out = _run(["scutil", "--dns"])  # contains 'nameserver[0] : 192.168.1.1'
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("nameserver[") and ":" in line:
                ip = line.split(":", 1)[1].strip()
                if ip and ip not in servers:
                    servers.append(ip)
    else:
        try:
            with open("/etc/resolv.conf", "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("nameserver "):
                        ip = line.split()[1]
                        if ip and ip not in servers:
                            servers.append(ip)
        except Exception:
            pass
    return servers[:3]


def measure_tcp_rtts(ip: str, ports: List[int] | None = None, attempts: int = 5, timeout: float = CONNECT_TIMEOUT) -> Tuple[List[float], List[int]]:
    """Measure TCP connect RTTs to ip over the first port that accepts connections; if none accept, still record attempts per port.
    Returns (rtts_ms, open_ports).
    """
    ports = ports or DEFAULT_PORTS
    rtts: List[float] = []
    open_ports: List[int] = []
    # Try all ports per attempt to find at least one that connects
    for _ in range(attempts):
        connected = False
        for p in ports:
            s = None
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(timeout)
                t0 = time.perf_counter()
                s.connect((ip, p))
                dt = (time.perf_counter() - t0) * 1000.0
                rtts.append(dt)
                if p not in open_ports:
                    open_ports.append(p)
                connected = True
                break
            except Exception:
                continue
            finally:
                try:
                    if s:
                        s.close()
                except Exception:
                    pass
        if not connected:
            # No open ports; sleep a little to avoid tight loop
            time.sleep(0.02)
    return rtts, open_ports


def summarize(values: List[float]) -> Dict[str, float] | None:
    if not values:
        return None
    vs = sorted(values)
    n = len(vs)
    p50 = vs[n // 2]
    p95 = vs[min(n - 1, int(n * 0.95))]
    avg = sum(vs) / n
    return {"p50": p50, "p95": p95, "avg": avg}


def lan_latency(attempts: int = 5) -> Dict:
    """Return latency measurements to default gateway and primary DNS via TCP connect RTTs."""
    gw = get_default_gateway()
    dns = get_dns_servers()
    result: Dict = {
        "gateway": None,
        "dns": [],
    }
    if gw:
        rtts, open_ports = measure_tcp_rtts(gw, attempts=attempts)
        result["gateway"] = {
            "ip": gw,
            "open_ports": open_ports,
            "rtts": rtts,
            "summary": summarize(rtts),
        }
    for ip in dns:
        rtts, open_ports = measure_tcp_rtts(ip, attempts=attempts)
        result["dns"].append({
            "ip": ip,
            "open_ports": open_ports,
            "rtts": rtts,
            "summary": summarize(rtts),
        })
    return result
