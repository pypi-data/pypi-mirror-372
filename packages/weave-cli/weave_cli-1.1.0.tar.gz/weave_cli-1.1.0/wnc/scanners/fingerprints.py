from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class FingerprintResult:
    ip: str
    vendor: Optional[str]
    product: Optional[str]
    type: Optional[str]
    confidence: float
    evidence: List[str]


def _match_hue(ev: Dict[str, Any]) -> Optional[FingerprintResult]:
    title = (ev.get("http_title") or "").lower()
    http_server = (ev.get("http_server") or "").lower()
    ssdp_model = (ev.get("ssdp_model") or "").lower()
    ssdp_server = (ev.get("ssdp_server") or "").lower()
    ssdp_usn = (ev.get("ssdp_usn") or "").lower()
    mdns_services = ev.get("mdns_services") or []

    is_hue_http = (
        "hue personal wireless" in title or
        "philips hue" in title or
        "ipbridge" in http_server or
        "hue" in http_server
    )
    is_hue_ssdp = (
        "ipbridge" in ssdp_model or
        "ipbridge" in ssdp_server or
        "hue" in ssdp_server or
        ssdp_usn.startswith("uuid:2f402f80")
    )
    is_hue_mdns = any(svc == "_hue._tcp.local" for svc in mdns_services)

    if is_hue_http or is_hue_ssdp or is_hue_mdns:
        evidence: List[str] = []
        if ev.get('http_title'):
            evidence.append(f"http.title={ev.get('http_title')}")
        if ev.get('http_server'):
            evidence.append(f"http.server={ev.get('http_server')}")
        if ev.get('ssdp_model'):
            evidence.append(f"ssdp.model={ev.get('ssdp_model')}")
        if ev.get('ssdp_server'):
            evidence.append(f"ssdp.server={ev.get('ssdp_server')}")
        if ev.get('ssdp_usn'):
            evidence.append(f"ssdp.usn={ev.get('ssdp_usn')}")
        if mdns_services:
            evidence.append(f"mdns.services={','.join(mdns_services[:5])}")
        return FingerprintResult(
            ip=ev["ip"], vendor="Philips", product="Hue Bridge", type="iot-bridge", confidence=0.97,
            evidence=evidence
        )
    return None


def _match_topsvision(ev: Dict[str, Any]) -> Optional[FingerprintResult]:
    rtsp_server = (ev.get("rtsp_server") or "").lower()
    http_server = (ev.get("http_server") or "").lower()
    title = (ev.get("http_title") or "").lower()
    if "topsvision" in rtsp_server:
        return FingerprintResult(
            ip=ev["ip"], vendor="TopsVision/HiSilicon", product=None, type="camera", confidence=0.85,
            evidence=[f"rtsp.server={ev.get('rtsp_server')}", f"http.server={ev.get('http_server')}", f"http.title={ev.get('http_title')}"]
        )
    if "uc-httpd" in http_server and title in ("index", "web client"):
        return FingerprintResult(
            ip=ev["ip"], vendor="HiSilicon OEM", product=None, type="camera", confidence=0.6,
            evidence=[f"http.server={ev.get('http_server')}", f"http.title={ev.get('http_title')}"]
        )
    return None


def _match_onvif(ev: Dict[str, Any]) -> Optional[FingerprintResult]:
    manuf = (ev.get("onvif_manufacturer") or "").strip()
    model = (ev.get("onvif_model") or "").strip()
    if manuf or model:
        vendor = manuf or None
        product = model or None
        return FingerprintResult(
            ip=ev["ip"], vendor=vendor, product=product, type="camera", confidence=0.9,
            evidence=[f"onvif.manufacturer={manuf}", f"onvif.model={model}"]
        )
    return None


def _match_unifi(ev: Dict[str, Any]) -> Optional[FingerprintResult]:
    server = (ev.get("http_server") or "").lower()
    title = (ev.get("http_title") or "").lower()
    ssdp_server = (ev.get("ssdp_server") or "").lower()
    if "ubnt" in server or "unifi" in title or "ubiquiti" in ssdp_server:
        return FingerprintResult(
            ip=ev["ip"], vendor="Ubiquiti", product=None, type="router/ap", confidence=0.7,
            evidence=[f"http.server={ev.get('http_server')}", f"http.title={ev.get('http_title')}", f"ssdp.server={ev.get('ssdp_server')}"]
        )
    return None


_RULES = [_match_onvif, _match_hue, _match_topsvision, _match_unifi]


def classify_device(evidence: Dict[str, Any]) -> FingerprintResult:
    """Return best-effort classification with confidence.

    evidence keys expected per IP:
      - ip, http_server, http_title, rtsp_server, ssdp_model, ssdp_server, mdns_services (list), onvif_manufacturer, onvif_model
    """
    best: Optional[FingerprintResult] = None
    for rule in _RULES:
        try:
            res = rule(evidence)
        except Exception:
            res = None
        if res and (best is None or res.confidence > best.confidence):
            best = res
    if best is None:
        best = FingerprintResult(ip=evidence["ip"], vendor=None, product=None, type=None, confidence=0.0, evidence=[])
    return best
