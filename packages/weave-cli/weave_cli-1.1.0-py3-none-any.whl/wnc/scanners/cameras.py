from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import List, Optional, Tuple

import httpx

from .network import discover_hosts
from .ports import scan_ports

CANDIDATE_PORTS = [80, 8080, 8000, 8443, 554, 8554]
HTTP_PORTS = [80, 8080, 8000, 8443]
RTSP_PORTS = [554, 8554]
HTTP_TIMEOUT = 2.0
CONNECT_TIMEOUT = 0.6
SEM_LIMIT = 200

BRAND_HINTS = [
    "onvif", "rtsp", "ip camera", "hikvision", "dahua", "axis", "amcrest",
    "reolink", "uniview", "ezviz", "foscam", "ycc365", "tplink", "unifi", "wyze",
]

VENDOR_FPS = {
    "Hikvision": ["Hikvision", "Hik", "App-webs", "Basic realm=\"hikvision\""],
    "Dahua": ["Dahua", "General", "realm=\"Login to Web\""],
    "Axis": ["Axis", "AXIS", "realm=\"AXIS"],
    "Amcrest": ["Amcrest", "Sricam", "Ambarella"],
    "Reolink": ["Reolink"],
    "Uniview": ["Uniview", "UNV"],
    "EZVIZ": ["EZVIZ"],
    "Foscam": ["Foscam"],
    "Ubiquiti": ["UniFi", "Ubiquiti"],
}


@dataclass
class CameraCandidate:
    ip: str
    evidence: List[str]
    vendor: str | None = None


async def _http_probe(ip: str, port: int) -> List[str]:
    url = f"http://{ip}:{port}/"
    evidence: List[str] = []
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=HTTP_TIMEOUT, verify=False) as client:
            r = await client.get(url)
            server = r.headers.get("Server")
            if server:
                evidence.append(f"Server={server}")
            wa = r.headers.get("WWW-Authenticate")
            if wa:
                evidence.append(f"WWW-Authenticate={wa}")
            title = None
            text = r.text[:4096].lower()
            for h in BRAND_HINTS:
                if h in text:
                    evidence.append(f"html~{h}")
            # rough title extraction
            start = r.text.lower().find("<title>")
            if start != -1:
                end = r.text.lower().find("</title>", start)
                if end != -1:
                    title = r.text[start+7:end].strip()
            if title:
                evidence.append(f"title={title[:80]}")
    except Exception as e:
        # Non-fatal; ignore connection errors
        pass
    return evidence


async def _rtsp_probe(ip: str, port: int) -> List[str]:
    evidence: List[str] = []
    try:
        fut = asyncio.open_connection(ip, port)
        reader, writer = await asyncio.wait_for(fut, timeout=CONNECT_TIMEOUT)
        # Send minimal OPTIONS request (RTSP)
        try:
            writer.write(b"OPTIONS rtsp://%b:%d/ RTSP/1.0\r\nCSeq: 1\r\n\r\n" % (ip.encode(), port))
            await writer.drain()
            data = await asyncio.wait_for(reader.read(128), timeout=0.5)
            if b"RTSP/1.0" in data:
                evidence.append("rtsp-handshake")
        except Exception:
            # Even a successful TCP connect on RTSP port is a good hint
            evidence.append("rtsp-tcp-open")
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
    except Exception:
        pass
    return evidence


async def _rtsp_describe(ip: str, port: int) -> List[str]:
    evidence: List[str] = []
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=CONNECT_TIMEOUT)
        try:
            req = (
                f"DESCRIBE rtsp://{ip}:{port}/ RTSP/1.0\r\n"
                f"CSeq: 2\r\n"
                f"Accept: application/sdp\r\n\r\n"
            ).encode()
            writer.write(req)
            await writer.drain()
            data = await asyncio.wait_for(reader.read(2048), timeout=1.0)
            if data:
                text = data.decode(errors="ignore")
                lines = text.splitlines()
                # capture headers and first lines of SDP
                for ln in lines[:20]:
                    if ln.lower().startswith("server:"):
                        evidence.append(f"rtsp-server={ln.split(':',1)[1].strip()}")
                    if ln.lower().startswith("www-authenticate"):
                        evidence.append(f"rtsp-auth={ln.split(':',1)[1].strip()}")
                    if ln.lower().startswith("s="):
                        evidence.append(f"sdp-s={ln[2:].strip()}")
                    if ln.lower().startswith("a=tool:"):
                        evidence.append(f"sdp-tool={ln.split(':',1)[1].strip()}")
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
    except Exception:
        pass
    return evidence


def _infer_vendor(evidence: List[str]) -> str | None:
    ev_text = " | ".join(evidence)
    for vendor, hints in VENDOR_FPS.items():
        for h in hints:
            if h.lower() in ev_text.lower():
                return vendor
    return None


async def _probe_ip(ip: str, sem: asyncio.Semaphore) -> CameraCandidate | None:
    async with sem:
        ev: List[str] = []
        # Check which candidate ports are open
        open_ports = await scan_ports(ip, ports=CANDIDATE_PORTS)
        port_set = {r.port for r in open_ports}
        if not port_set:
            return None
        # HTTP clues
        http_tasks = []
        for p in HTTP_PORTS:
            if p in port_set:
                http_tasks.append(_http_probe(ip, p))
        if http_tasks:
            for res in await asyncio.gather(*http_tasks):
                ev.extend(res)
        # RTSP clues
        rtsp_tasks = []
        for p in RTSP_PORTS:
            if p in port_set:
                rtsp_tasks.append(_rtsp_probe(ip, p))
                rtsp_tasks.append(_rtsp_describe(ip, p))
        if rtsp_tasks:
            for res in await asyncio.gather(*rtsp_tasks):
                ev.extend(res)
        # Heuristic: if any HTTP brand hints or RTSP evidence exists, likely camera
        if ev:
            ev = sorted(set(ev))
            # Exclude known non-camera IoT bridges like Philips Hue (IpBridge)
            ev_l = " | ".join(ev).lower()
            if ("hue personal wireless" in ev_l) or ("ipbridge" in ev_l) or (" hue/" in ev_l):
                return None
            vendor = _infer_vendor(ev)
            return CameraCandidate(ip=ip, evidence=ev, vendor=vendor)
        return None


async def detect_cameras(subnet: str) -> List[CameraCandidate]:
    hosts = await discover_hosts(subnet)
    if not hosts:
        return []
    sem = asyncio.Semaphore(SEM_LIMIT)
    results = await asyncio.gather(*(_probe_ip(h, sem) for h in hosts))
    cams = [c for c in results if c is not None]
    return cams


# ---- Weak default credential checks (safe, read-only) ----

DEFAULT_CREDS = [
    ("admin", "admin"),
    ("admin", "12345"),
    ("admin", "123456"),
    ("admin", "password"),
    ("root", "root"),
    ("root", "pass"),
]


async def _try_http_auth(ip: str, port: int, creds: List[Tuple[str, str]]) -> Optional[Tuple[str, str, int]]:
    base = f"http://{ip}:{port}/"
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=HTTP_TIMEOUT, verify=False) as client:
            # First, check if auth is required
            r0 = await client.get(base)
            if r0.status_code in (200, 301, 302):
                # No auth needed, but not a cred issue; we won't treat as weak-auth
                return None
            # Try supplied credentials
            for u, p in creds:
                try:
                    r = await client.get(base, auth=(u, p))
                    if r.status_code in (200, 204):
                        return (u, p, r.status_code)
                except Exception:
                    continue
    except Exception:
        return None
    return None


async def _try_rtsp_auth(ip: str, port: int, creds: List[Tuple[str, str]]) -> Optional[Tuple[str, str]]:
    # Simple TCP connect with embedded creds in RTSP URL, check for 200/401 in response
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=CONNECT_TIMEOUT)
        try:
            # First unauthenticated DESCRIBE
            req = (
                f"DESCRIBE rtsp://{ip}:{port}/ RTSP/1.0\r\n"
                f"CSeq: 1\r\nAccept: application/sdp\r\n\r\n"
            ).encode()
            writer.write(req)
            await writer.drain()
            data = await asyncio.wait_for(reader.read(512), timeout=0.8)
            # If unauthorized, try creds
            if b"401" in data or b"Unauthorized" in data or data:
                for u, p in creds:
                    try:
                        req2 = (
                            f"DESCRIBE rtsp://{u}:{p}@{ip}:{port}/ RTSP/1.0\r\n"
                            f"CSeq: 2\r\nAccept: application/sdp\r\n\r\n"
                        ).encode()
                        writer.write(req2)
                        await writer.drain()
                        data2 = await asyncio.wait_for(reader.read(512), timeout=0.8)
                        if b"200" in data2 or b"OK" in data2:
                            return (u, p)
                    except Exception:
                        continue
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
    except Exception:
        return None
    return None


async def check_weak_auth_for_ip(ip: str, open_ports: List[int], cred_pairs: Optional[List[str]] = None) -> dict | None:
    """Try common default credentials on HTTP/RTSP ports.
    Returns a dict with findings if any credential works, else None.
    """
    # Build credential list
    creds: List[Tuple[str, str]] = []
    if cred_pairs:
        for c in cred_pairs:
            if ":" in c:
                u, p = c.split(":", 1)
                creds.append((u, p))
    if not creds:
        creds = DEFAULT_CREDS

    http_ports = [p for p in open_ports if p in HTTP_PORTS]
    rtsp_ports = [p for p in open_ports if p in RTSP_PORTS]

    findings: dict = {"ip": ip, "http": None, "rtsp": None}

    # Try HTTP
    for p in http_ports:
        res = await _try_http_auth(ip, p, creds)
        if res:
            u, pw, code = res
            findings["http"] = {"port": p, "username": u, "password": pw, "status": code}
            break

    # Try RTSP
    if not findings["http"]:
        for p in rtsp_ports:
            res2 = await _try_rtsp_auth(ip, p, creds)
            if res2:
                u, pw = res2
                findings["rtsp"] = {"port": p, "username": u, "password": pw}
                break

    if findings["http"] or findings["rtsp"]:
        return findings
    return None
