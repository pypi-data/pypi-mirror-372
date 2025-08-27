from __future__ import annotations

from typing import Dict, List, Any

Risk = Dict[str, Any]

RISKY_TCP_PORTS = {
    23: ("Telnet", "Disable Telnet; use SSH with keys"),
    21: ("FTP", "Disable FTP; use SFTP/FTPS"),
    445: ("SMB", "Restrict SMB; patch and segment"),
    139: ("NetBIOS", "Restrict legacy NetBIOS"),
    3389: ("RDP", "Restrict RDP; use VPN and MFA"),
    5900: ("VNC", "Disable/secure VNC with strong auth and tunnel"),
    80: ("HTTP", "Prefer HTTPS; enforce auth and updates"),
}

RISKY_UDP_SERVICES = {
    "snmp": ("SNMP", "Disable or enforce v3 with strong creds"),
    "ntp": ("NTP", "Ensure no public exposure; restrict to LAN"),
    "dns": ("DNS", "Avoid open resolvers; restrict queries"),
}


def _sev(level: str) -> int:
    return {"low": 1, "medium": 2, "high": 3}.get(level, 1)


def analyze(report_data: Dict[str, Any]) -> Dict[str, Any]:
    risks: List[Risk] = []

    port_open: Dict[str, List[int]] = report_data.get("port_open", {})
    banners: List[Dict[str, Any]] = report_data.get("banners", [])
    cameras = report_data.get("cameras", {})
    udp_samples = report_data.get("udp_samples", {})
    onvif = report_data.get("onvif", [])
    onvif_info = report_data.get("onvif_info", [])

    # Risky TCP ports
    for host, ports in port_open.items():
        for p in ports:
            if p in RISKY_TCP_PORTS:
                name, rec = RISKY_TCP_PORTS[p]
                risks.append({
                    "severity": "high" if p in (23, 21, 3389, 5900) else "medium",
                    "category": "exposed_service",
                    "target": host,
                    "evidence": f"TCP/{p} ({name}) open",
                    "recommendation": rec,
                })

    # UDP services
    for subnet, entries in udp_samples.items():
        for e in entries:
            host = e.get("ip")
            for s in e.get("services", []):
                name = s.get("service")
                if name in RISKY_UDP_SERVICES:
                    svc, rec = RISKY_UDP_SERVICES[name]
                    risks.append({
                        "severity": "medium",
                        "category": "udp_service",
                        "target": host,
                        "evidence": f"UDP/{s.get('port')} ({svc}) responded",
                        "recommendation": rec,
                    })

    # Cameras & ONVIF
    total_cams = sum(len(v) for v in cameras.values()) if isinstance(cameras, dict) else 0
    if total_cams:
        risks.append({
            "severity": "medium",
            "category": "iot_camera",
            "target": "network",
            "evidence": f"{total_cams} camera candidates detected",
            "recommendation": "Isolate cameras on VLAN; change default creds; update firmware",
        })
    if onvif:
        risks.append({
            "severity": "medium",
            "category": "onvif_exposure",
            "target": "network",
            "evidence": f"{len(onvif)} ONVIF devices responding to discovery",
            "recommendation": "Restrict ONVIF access; enforce auth; segment from untrusted hosts",
        })
    for info in onvif_info:
        man = (info.get("Manufacturer") or "").lower()
        if man and any(v in man for v in ("hikvision", "dahua", "reolink", "uniview", "foscam")):
            risks.append({
                "severity": "medium",
                "category": "camera_vendor",
                "target": info.get("ip"),
                "evidence": f"ONVIF device: {info.get('Manufacturer')} {info.get('Model')} ({info.get('FirmwareVersion')})",
                "recommendation": "Audit camera security settings; disable unused services; update firmware",
            })

    # Banners (very light heuristics)
    for b in banners:
        svc = (b.get("service") or "").lower()
        info = (b.get("info") or "").lower()
        if svc == "http" and ("apache/2.2" in info or "nginx/0." in info):
            risks.append({
                "severity": "medium",
                "category": "outdated_http",
                "target": f"{b.get('host')}:{b.get('port')}",
                "evidence": b.get("info"),
                "recommendation": "Update web server; place behind reverse proxy; enforce HTTPS",
            })
        if svc == "ssh" and "openssh" in info:
            # informational
            risks.append({
                "severity": "low",
                "category": "ssh_banner",
                "target": f"{b.get('host')}:{b.get('port')}",
                "evidence": b.get("info"),
                "recommendation": "Disable password auth; use keys; restrict access",
            })

    # Score (very rough)
    score = sum(_sev(r["severity"]) for r in risks)
    return {"risks": risks, "score": score}
