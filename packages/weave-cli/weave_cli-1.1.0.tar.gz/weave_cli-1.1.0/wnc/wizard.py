import asyncio
from dataclasses import dataclass, asdict
import json
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel

from .scanners.network import get_internal_subnets, discover_hosts
from .scanners.ports import scan_ports
from .scanners.cameras import detect_cameras, check_weak_auth_for_ip
from .scanners.udp import probe_udp_services
from .scanners.speed import run_speedtest
from .scanners.geo import (
    estimate_location_by_rtt,
    estimate_location_by_multihost,
    estimate_top_locations,
    estimate_named_city_rtts,
    estimate_location_multilat,
    traceroute_infer,
)
from .scanners.onvif import ws_discover
from .scanners.ssdp import discover_ssdp
from .scanners.arp import read_arp_table
from .scanners.mdns import discover_mdns
from .scanners.banners import grab_banners
from .scanners.onvif_client import get_device_information, change_onvif_password
from .analyzers.risk import analyze as analyze_risk
from .scanners.fingerprints import classify_device
from .scanners import wifi as wifi_scan
from .scanners.lan import lan_latency

console = Console()

@dataclass
class WizardState:
    subnet: str | None = None
    target_host: str | None = None
    total_hosts: int = 0
    total_cameras: int = 0
    total_onvif: int = 0
    total_ssdp: int = 0
    scanned_subnets: list[str] = None
    port_samples: dict[str, list[int]] = None
    udp_samples: dict[str, list[str]] = None
    hosts_map: dict[str, list[str]] = None
    cameras_map: dict[str, list[dict]] = None
    onvif_devices: list[dict] = None
    ssdp_devices: list[dict] = None
    speedtest: dict | None = None
    location: dict | None = None
    location_top: list[dict] | None = None
    location_targets: list[dict] | None = None
    location_multilat: dict | None = None
    location_traceroute: dict | None = None
    arp_entries: list[dict] = None
    mdns_records: list[dict] = None
    banners: list[dict] = None
    port_open: dict[str, list[int]] = None
    onvif_info: list[dict] = None
    weak_auth_findings: list[dict] | None = None
    onvif_password_change: list[dict] | None = None
    devices: list[dict] | None = None
    wifi: dict | None = None
    lan_speed: dict | None = None

async def run_wizard(*, extended: bool | None = None, speedtest_runs: int | None = None, output_path: str | None = None, analyze: bool = True, assume_yes: bool = False, weak_auth: bool = False, default_creds: list[str] | None = None, change_password: bool = False, change_user: str | None = None, new_password: str | None = None, wifi: bool = False, lan_speed: bool = False):
    console.rule("WNC Wizard")
    console.print("Let's explore your network. Answer a few questions, and I'll do the rest.")

    subnets = get_internal_subnets()
    if not subnets:
        console.print("No local subnets detected.")
    else:
        console.print(Panel.fit("\n".join(str(s) for s in subnets), title="Detected subnets"))

    do_full = True if assume_yes else typer.confirm("Do you want a full internal scan (discover hosts, ports, and cameras)?", default=True)

    if do_full:
        state = WizardState(scanned_subnets=[], port_samples={}, udp_samples={}, hosts_map={}, cameras_map={}, onvif_devices=[], ssdp_devices=[], arp_entries=[], mdns_records=[], banners=[], port_open={}, onvif_info=[], weak_auth_findings=[], onvif_password_change=[], devices=[], wifi=None, lan_speed=None)
        for subnet in subnets:
            await _scan_full_subnet(str(subnet), state, weak_auth=weak_auth, default_creds=default_creds)

        # Extended?
        do_ext = extended if extended is not None else (True if assume_yes else typer.confirm("Run extended tasks (UDP probes, speedtest, rough location)?", default=False))
        if do_ext:
            # UDP probe a sample of discovered hosts from each subnet
            console.rule("Extended: UDP Probing")
            for subnet in state.scanned_subnets:
                sample_hosts = state.port_samples.get(subnet, [])
                # If we have no port sample keys, we cannot infer hosts here; skip handled inside
                await _udp_probe_sample(subnet, state)

            # ONVIF WS-Discovery
            console.rule("Extended: ONVIF Discovery")
            onvifs = ws_discover()
            state.total_onvif = len(onvifs)
            if onvifs:
                # store for JSON report
                state.onvif_devices = [
                    {"ip": ip, "scopes": dev.scopes, "xaddrs": dev.xaddrs}
                    for ip, dev in onvifs.items()
                ]
                from rich.table import Table
                table = Table(title="ONVIF devices")
                table.add_column("IP")
                table.add_column("Scopes")
                table.add_column("XAddrs")
                for ip, dev in onvifs.items():
                    table.add_row(ip, "\n".join(dev.scopes)[:120], "\n".join(dev.xaddrs)[:120])
                console.print(table)

                # Try ONVIF SOAP DeviceInformation (best-effort)
                info_rows = []
                for ip, dev in onvifs.items():
                    for x in dev.xaddrs[:1]:  # try first XAddr per device
                        try:
                            dinfo = get_device_information(x)
                        except Exception:
                            dinfo = None
                        if dinfo:
                            rec = {"ip": ip, "xaddr": x}
                            rec.update(dinfo)
                            state.onvif_info.append(rec)
                            info_rows.append((ip, dinfo.get("Manufacturer") or "", dinfo.get("Model") or "", dinfo.get("FirmwareVersion") or ""))
                        break
                if info_rows:
                    it = Table(title="ONVIF Device Information (best-effort)")
                    it.add_column("IP")
                    it.add_column("Manufacturer")
                    it.add_column("Model")
                    it.add_column("Firmware")
                    for ip, man, mod, fw in info_rows[:15]:
                        it.add_row(ip, man[:24], mod[:24], fw[:20])
                    console.print(it)
            else:
                console.print("No ONVIF devices discovered.")

            # Optionally change password via ONVIF for devices where weak creds were found
            if change_password and state.weak_auth_findings:
                console.rule("Attempting ONVIF password change (requested)")
                changed: list[dict] = []
                # Build IP->xaddr map
                ip_xaddr = {}
                for rec in (state.onvif_devices or []):
                    ip_xaddr.setdefault(rec.get("ip"), rec.get("xaddrs", []) or [])
                from rich.table import Table
                t = Table(title="ONVIF password change results")
                t.add_column("IP")
                t.add_column("Result")
                t.add_column("Detail")
                for f in state.weak_auth_findings:
                    ip = f.get("ip")
                    xaddrs = ip_xaddr.get(ip) or []
                    if not xaddrs:
                        t.add_row(ip, "skipped", "No ONVIF endpoint discovered")
                        continue
                    # pick first xaddr
                    x = xaddrs[0]
                    svc = f.get("http") or f.get("rtsp")
                    if not svc:
                        t.add_row(ip, "skipped", "No working weak creds")
                        continue
                    user = (change_user or svc.get("username"))
                    pw = svc.get("password")
                    if not user or not pw or not new_password:
                        t.add_row(ip, "skipped", "Missing credentials/new_password")
                        continue
                    try:
                        ok = change_onvif_password(x, user, pw, user, new_password)
                    except Exception as e:
                        ok = False
                    if ok:
                        changed.append({"ip": ip, "xaddr": x, "username": user, "changed": True})
                        t.add_row(ip, "changed", f"user={user}")
                    else:
                        changed.append({"ip": ip, "xaddr": x, "username": user, "changed": False})
                        t.add_row(ip, "failed", f"user={user}")
                if changed:
                    console.print(t)

            # Traceroute POP inference
            try:
                tr = traceroute_infer()
            except Exception:
                tr = {"error": "traceroute failed"}
            # Only record and display if a city was inferred
            if isinstance(tr, dict) and tr.get("inferred_city"):
                state.location_traceroute = tr
                console.print(Panel.fit(
                    f"Inferred nearby POP (traceroute): {tr.get('inferred_city')}",
                    title="Traceroute Inference"
                ))
            else:
                state.location_traceroute = None

            # SSDP discovery
            console.rule("Extended: SSDP Discovery")
            ssdp_devices = discover_ssdp()
            state.total_ssdp = len(ssdp_devices)
            if ssdp_devices:
                # store for JSON report
                state.ssdp_devices = [
                    {"ip": d.ip, "st": d.st, "usn": d.usn, "server": d.server, "location": d.location}
                    for d in ssdp_devices
                ]
                from rich.table import Table
                table = Table(title="SSDP devices (sample)")
                table.add_column("IP")
                table.add_column("ST")
                table.add_column("USN")
                table.add_column("Server")
                for d in ssdp_devices[:15]:
                    table.add_row(d.ip, d.st[:40], d.usn[:40], d.server[:30])
                console.print(table)
            else:
                console.print("No SSDP devices discovered.")

            # ARP Table (passive, safe)
            console.rule("Extended: ARP Table (passive)")
            arp = read_arp_table()
            if arp:
                state.arp_entries = [
                    {"ip": e.ip, "mac": e.mac, "iface": e.iface, "vendor": e.vendor}
                    for e in arp.values()
                ]
                from rich.table import Table
                table = Table(title="ARP entries (sample)")
                table.add_column("IP")
                table.add_column("MAC")
                table.add_column("Vendor")
                table.add_column("Iface")
                for e in list(arp.values())[:20]:
                    table.add_row(e.ip, e.mac, (e.vendor or "?")[:24], e.iface or "-")
                console.print(table)
            else:
                console.print("No ARP entries available or command not found.")

            # mDNS discovery (passive multicast queries)
            console.rule("Extended: mDNS Discovery")
            try:
                mdns = discover_mdns()
            except Exception:
                mdns = []
            if mdns:
                state.mdns_records = [{"name": r.name, "rtype": r.rtype, "data": r.data} for r in mdns]
                from rich.table import Table
                table = Table(title="mDNS records (sample)")
                table.add_column("Name")
                table.add_column("Type")
                table.add_column("Data")
                for r in mdns[:20]:
                    table.add_row(r.name[:40], str(r.rtype), r.data[:60])
                console.print(table)
            else:
                console.print("No mDNS responses received.")

            # Banner grabbing on known open ports (best-effort)
            console.rule("Extended: Banner Grabbing")
            from rich.table import Table
            btable = Table(title="Service banners (sample)")
            btable.add_column("Host")
            btable.add_column("Port")
            btable.add_column("Service")
            btable.add_column("Info")
            count = 0
            for subnet in state.scanned_subnets:
                for h in state.port_samples.get(subnet, [])[:5]:
                    ports = state.port_open.get(h) or [22,80,443,8080,8443,6379,11211]
                    try:
                        banners = grab_banners(h, ports[:8])
                    except Exception:
                        banners = []
                    for b in banners:
                        state.banners.append({"host": h, "port": b.port, "service": b.service, "info": b.info})
                        if count < 20:
                            btable.add_row(h, str(b.port), b.service or "?", (b.info or "")[:60])
                            count += 1
            if count:
                console.print(btable)
            else:
                console.print("No banners collected.")

            # Device fingerprinting using collected evidence
            console.rule("Extended: Device Fingerprinting")
            # Build per-IP evidence
            evidence_map: dict[str, dict] = {}
            # Start from hosts we touched (port_samples + cameras + ssdp + onvif)
            ips = set()
            for subnet in state.scanned_subnets:
                ips.update(state.port_samples.get(subnet, []) or [])
                for c in state.cameras_map.get(subnet, []) or []:
                    ips.add(c.get("ip"))
            for d in (state.ssdp_devices or []):
                ips.add(d.get("ip"))
            for o in (state.onvif_info or []):
                ips.add(o.get("ip"))
            # Fill from banners
            for b in state.banners:
                if b.get("service") == "http":
                    ip = b.get("host")
                    ev = evidence_map.setdefault(ip, {"ip": ip})
                    info = b.get("info") or ""
                    # Parse simple key=value tokens we produced (Server=..., title=...)
                    for part in info.split(";"):
                        part = part.strip()
                        if part.lower().startswith("server="):
                            ev["http_server"] = part.split("=",1)[1].strip()
                        if part.lower().startswith("title="):
                            ev["http_title"] = part.split("=",1)[1].strip()
            # RTSP server evidence from camera detection strings
            for subnet in state.scanned_subnets:
                for c in state.cameras_map.get(subnet, []) or []:
                    ip = c.get("ip")
                    ev = evidence_map.setdefault(ip, {"ip": ip})
                    for e in c.get("evidence", []):
                        if e.lower().startswith("rtsp-server="):
                            ev["rtsp_server"] = e.split("=",1)[1]
            # SSDP server and rough model from ST/USN
            for s in (state.ssdp_devices or []):
                ip = s.get("ip")
                ev = evidence_map.setdefault(ip, {"ip": ip})
                if s.get("server"):
                    ev["ssdp_server"] = s.get("server")
                # heuristic model from USN or ST strings
                if s.get("usn"):
                    ev["ssdp_model"] = s.get("usn")
            # ONVIF info
            for o in (state.onvif_info or []):
                ip = o.get("ip")
                ev = evidence_map.setdefault(ip, {"ip": ip})
                if o.get("Manufacturer"):
                    ev["onvif_manufacturer"] = o.get("Manufacturer")
                if o.get("Model"):
                    ev["onvif_model"] = o.get("Model")

            from rich.table import Table
            dt = Table(title="Classified devices (sample)")
            dt.add_column("IP")
            dt.add_column("Vendor")
            dt.add_column("Product")
            dt.add_column("Type")
            dt.add_column("Conf")
            shown = 0
            for ip in sorted(ips):
                ev = evidence_map.get(ip) or {"ip": ip}
                res = classify_device(ev)
                state.devices.append({
                    "ip": res.ip,
                    "vendor": res.vendor,
                    "product": res.product,
                    "type": res.type,
                    "confidence": res.confidence,
                    "evidence": res.evidence,
                })
                if shown < 15 and (res.vendor or res.type or res.product):
                    dt.add_row(ip, str(res.vendor or "-"), str(res.product or "-"), str(res.type or "-"), f"{res.confidence:.2f}")
                    shown += 1
            if shown:
                console.print(dt)
            else:
                console.print("No confident device classifications.")

            # Wi‑Fi information (macOS)
            if wifi:
                console.rule("Extended: Wi‑Fi (macOS)")
                try:
                    cur = wifi_scan.current_info()
                except Exception:
                    cur = None
                try:
                    nearby = wifi_scan.scan_nearby()
                except Exception:
                    nearby = []
                state.wifi = {"current": cur, "nearby": nearby}
                if cur:
                    console.print(Panel.fit(
                        f"SSID: {cur.get('ssid') or '-'}\nBSSID: {cur.get('bssid') or '-'}\nChannel: {cur.get('channel') or '-'}\nRSSI: {cur.get('rssi') or '-'} dBm\nNoise: {cur.get('noise') or '-'} dBm",
                        title="Current Wi‑Fi"
                    ))
                if nearby:
                    nt = Table(title="Nearby APs (sample)")
                    nt.add_column("SSID")
                    nt.add_column("BSSID")
                    nt.add_column("Ch")
                    nt.add_column("RSSI")
                    for ap in nearby[:15]:
                        nt.add_row(ap.get("ssid") or "", ap.get("bssid") or "", str(ap.get("channel") or ""), str(ap.get("rssi") or ""))
                    console.print(nt)

            # LAN latency (gateway and DNS)
            if lan_speed:
                console.rule("Extended: LAN latency (gateway/DNS)")
                try:
                    ls = lan_latency(attempts=6)
                except Exception:
                    ls = {"error": "failed"}
                state.lan_speed = ls
                if isinstance(ls, dict) and (ls.get("gateway") or ls.get("dns")):
                    from rich.table import Table
                    lt = Table(title="LAN latency summary")
                    lt.add_column("Target")
                    lt.add_column("IP")
                    lt.add_column("Median (ms)")
                    lt.add_column("p95 (ms)")
                    # Gateway
                    gw = ls.get("gateway")
                    if gw and gw.get("summary"):
                        lt.add_row("gateway", gw.get("ip") or "", f"{gw['summary'].get('p50', 0):.1f}", f"{gw['summary'].get('p95', 0):.1f}")
                    # First DNS
                    for idx, d in enumerate(ls.get("dns") or []):
                        if d.get("summary"):
                            lt.add_row(f"dns[{idx}]", d.get("ip") or "", f"{d['summary'].get('p50', 0):.1f}", f"{d['summary'].get('p95', 0):.1f}")
                    console.print(lt)

            # Speedtest
            if speedtest_runs is None:
                if assume_yes:
                    runs = 1
                else:
                    runs = typer.prompt("Speedtest runs (1-3)", default=1)
                    try:
                        runs = max(1, min(int(runs), 3))
                    except Exception:
                        runs = 1
            else:
                runs = max(1, min(int(speedtest_runs), 3))
            console.rule("Extended: Speedtest")
            st = await run_speedtest(runs=runs)
            if st:
                console.print(Panel.fit(
                    f"Download: {st.download_mbps:.1f} Mbps\nUpload: {st.upload_mbps:.1f} Mbps\nPing: {st.ping_ms:.1f} ms\nServer: {st.server_name}",
                    title="Speedtest"
                ))
                state.speedtest = {"download_mbps": st.download_mbps, "upload_mbps": st.upload_mbps, "ping_ms": st.ping_ms, "server": st.server_name}
            else:
                console.print("Speedtest not available or failed.")

            # Rough geolocation: multilateration + RTT fallback
            console.rule("Extended: Rough Location (RTT-based)")
            mlat = await estimate_location_multilat(24)
            # Only display/store multilateration if confidence is reasonably high
            if mlat and getattr(mlat, "confidence", 0) >= 0.6:
                console.print(Panel.fit(
                    f"Estimated coordinates: {mlat.lat:.4f}, {mlat.lon:.4f}\nNearest city: {mlat.nearest_city} ({mlat.nearest_country})\nConfidence: {mlat.confidence:.2f}",
                    title="Multilateration Estimate"
                ))
                state.location_multilat = {
                    "lat": mlat.lat,
                    "lon": mlat.lon,
                    "nearest_city": mlat.nearest_city,
                    "nearest_country": mlat.nearest_country,
                    "confidence": mlat.confidence,
                    "points_used": mlat.points_used,
                }
            else:
                state.location_multilat = None
            # Also show nearest-by-RTT city for context
            mloc = await estimate_location_by_multihost(10)
            if mloc:
                console.print(Panel.fit(
                    f"Nearest city by RTT (multi-host): {mloc.city} ({mloc.country})\nRTT: {int(mloc.rtt_ms)} ms",
                    title="Nearest by RTT"
                ))
                state.location = {"city": mloc.city, "country": mloc.country, "rtt_ms": mloc.rtt_ms}
            else:
                loc = await estimate_location_by_rtt()
                if loc:
                    console.print(Panel.fit(
                        f"Nearest city by RTT: {loc.city} ({loc.country})\nEstimated distance: ~{int(loc.estimated_km)} km\nRTT: {int(loc.rtt_ms)} ms",
                        title="Nearest by RTT"
                    ))
                    state.location = {"city": loc.city, "country": loc.country, "rtt_ms": loc.rtt_ms, "estimated_km": loc.estimated_km}
                else:
                    console.print("Could not estimate location via RTT.")

            # Show top-N nearest cities by RTT with ~km
            try:
                top = await estimate_top_locations(n_points=40, top_k=5)
            except Exception:
                top = []
            if top:
                from rich.table import Table
                t = Table(title="Nearest cities by RTT (top 5)")
                t.add_column("City")
                t.add_column("Country")
                t.add_column("RTT (ms)")
                t.add_column("~Distance (km)")
                state.location_top = []
                for e in top:
                    t.add_row(e.city, e.country, str(int(e.rtt_ms)), str(int(e.estimated_km)))
                    state.location_top.append({"city": e.city, "country": e.country, "rtt_ms": e.rtt_ms, "estimated_km": e.estimated_km})
                console.print(t)

            # Compare to specific cities requested
            targets = [
                "Amsterdam", "New York", "Los Angeles", "Tokyo", "Beijing", "Bangkok", "Mumbai", "Dubai",
            ]
            try:
                comps = await estimate_named_city_rtts(targets)
            except Exception:
                comps = []
            if comps:
                from rich.table import Table
                ct = Table(title="City comparison (RTT and ~km)")
                ct.add_column("City")
                ct.add_column("Country")
                ct.add_column("RTT (ms)")
                ct.add_column("~Distance (km)")
                state.location_targets = []
                # Keep original target order
                order = {name: i for i, name in enumerate(targets)}
                comps.sort(key=lambda e: order.get(e.city, 999))
                for e in comps:
                    ct.add_row(e.city, e.country, str(int(e.rtt_ms)), str(int(e.estimated_km)))
                    state.location_targets.append({"city": e.city, "country": e.country, "rtt_ms": e.rtt_ms, "estimated_km": e.estimated_km})
                console.print(ct)

        # Final overview
        console.rule("Scan Overview")
        console.print(Panel.fit(
            f"Subnets scanned: {len(state.scanned_subnets)}\n"
            f"Total hosts discovered: {state.total_hosts}\n"
            f"Total camera candidates: {state.total_cameras}\n"
            f"ONVIF devices: {state.total_onvif}\n"
            f"SSDP devices: {state.total_ssdp}",
            title="Summary"
        ))
        # Risk analysis (optional)
        risk_report = None
        if analyze:
            console.rule("Risk Analysis")
            try:
                risk_input = {
                    "port_open": state.port_open,
                    "banners": state.banners,
                    "cameras": state.cameras_map,
                    "udp_samples": state.udp_samples,
                    "onvif": state.onvif_devices,
                    "onvif_info": state.onvif_info,
                }
                risk_report = analyze_risk(risk_input)
            except Exception as e:
                risk_report = {"error": str(e), "risks": [], "score": 0}
            # print concise table
            from rich.table import Table
            rtable = Table(title="Top Risks (sample)")
            rtable.add_column("Severity")
            rtable.add_column("Category")
            rtable.add_column("Target")
            rtable.add_column("Evidence")
            if risk_report and risk_report.get("risks"):
                for r in risk_report["risks"][:15]:
                    rtable.add_row(r.get("severity","-"), r.get("category","-"), str(r.get("target","-"))[:24], str(r.get("evidence",""))[:60])
                console.print(rtable)
                console.print(f"Risk score: {risk_report.get('score')}")
            else:
                console.print("No notable risks identified.")
        # Write JSON report if requested
        if output_path:
            report = {
                "subnets": state.scanned_subnets,
                "hosts": state.hosts_map,
                "port_sample_hosts": state.port_samples,
                "port_open": state.port_open,
                "udp_samples": state.udp_samples,
                "cameras": state.cameras_map,
                "onvif": state.onvif_devices,
                "onvif_info": state.onvif_info,
                "ssdp": state.ssdp_devices,
                "arp": state.arp_entries,
                "mdns_records": state.mdns_records,
                "banners": state.banners,
                "weak_auth_findings": state.weak_auth_findings,
                "onvif_password_change": state.onvif_password_change,
                "devices": state.devices,
                "wifi": state.wifi,
                "lan_speed": state.lan_speed,
                "speedtest": state.speedtest,
                "location": state.location,
                "location_multilat": state.location_multilat,
                "location_traceroute": state.location_traceroute,
                "location_top": state.location_top,
                "location_targets": state.location_targets,
                "risk": risk_report,
                "summary": {
                    "subnets": len(state.scanned_subnets),
                    "hosts": state.total_hosts,
                    "cameras": state.total_cameras,
                    "onvif": state.total_onvif,
                    "ssdp": state.total_ssdp,
                },
            }
            # Omit empty/None optional location sections
            for k in ["location_multilat", "location_traceroute", "location_top", "location_targets"]:
                v = report.get(k)
                if not v:
                    report.pop(k, None)
            try:
                with open(output_path, "w") as f:
                    json.dump(report, f, indent=2)
                console.print(f"Saved report to {output_path}")
            except Exception as e:
                console.print(f"[red]Failed to write report:[/red] {e}")
        return

    # Partial flow
    subnet = (str(subnets[0]) if subnets else "192.168.1.0/24") if assume_yes else typer.prompt("Enter a subnet to scan (CIDR)", default=str(subnets[0]) if subnets else "192.168.1.0/24")
    console.print(f"Selected subnet: [bold]{subnet}[/bold]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("Discovering hosts", total=None)
        hosts = await discover_hosts(subnet)
        progress.update(task, description=f"Discovered {len(hosts)} hosts")

    if not hosts:
        console.print("No hosts found.")
        return

    console.print(Panel.fit("\n".join(hosts), title=f"Live hosts in {subnet}"))

    do_cam = True if assume_yes else typer.confirm("Scan this subnet for IP cameras?", default=True)
    if do_cam:
        cams = await detect_cameras(subnet)
        if cams:
            from rich.table import Table
            table = Table(title=f"Potential Cameras in {subnet}")
            table.add_column("IP")
            table.add_column("Vendor")
            table.add_column("Evidence")
            for cam in cams:
                table.add_row(cam.ip, cam.vendor or "?", ", ".join(cam.evidence)[:200])
            console.print(table)
        else:
            console.print("No cameras detected.")

    do_ports = True if assume_yes else typer.confirm("Port-scan one of the hosts?", default=True)
    if do_ports:
        target = hosts[0] if assume_yes else typer.prompt("Enter host IP", default=hosts[0])
        results = await scan_ports(target)
        from rich.table import Table
        table = Table(title=f"Open ports on {target}")
        table.add_column("Port")
        table.add_column("Proto")
        table.add_column("Service")
        for r in results:
            table.add_row(str(r.port), r.proto, r.service or "?")
        console.print(table)

async def _scan_full_subnet(subnet: str, state: WizardState, *, weak_auth: bool = False, default_creds: list[str] | None = None):
    console.rule(f"Full scan: {subnet}")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        transient=False,
    ) as progress:
        t_hosts = progress.add_task("Discovering hosts", total=None)
        hosts = await discover_hosts(subnet)
        progress.update(t_hosts, description=f"Found {len(hosts)} hosts")
        progress.stop_task(t_hosts)

        if not hosts:
            console.print("No hosts found.")
            return

        state.scanned_subnets.append(subnet)
        state.total_hosts += len(hosts)
        state.hosts_map[subnet] = hosts

        # Camera sweep
        t_cam = progress.add_task("Scanning for cameras", total=None)
        cams = await detect_cameras(subnet)
        progress.stop_task(t_cam)

        if cams:
            from rich.table import Table
            table = Table(title=f"Potential Cameras in {subnet}")
            table.add_column("IP")
            table.add_column("Vendor")
            table.add_column("Evidence")
            cam_list = []
            for cam in cams:
                table.add_row(cam.ip, cam.vendor or "?", ", ".join(cam.evidence)[:200])
                cam_list.append({"ip": cam.ip, "vendor": cam.vendor, "evidence": cam.evidence})
            console.print(table)
            state.total_cameras += len(cams)
            state.cameras_map[subnet] = cam_list
        else:
            console.print("No cameras detected.")

        # Ports on first N hosts
        t_ports = progress.add_task("Port scanning sample hosts", total=None)
        sample = hosts[: min(10, len(hosts))]
        state.port_samples[subnet] = []
        for h in sample:
            results = await scan_ports(h, top_n=200)
            open_ports = ", ".join(str(r.port) for r in results)
            console.print(f"[bold]{h}[/bold]: {open_ports}")
            state.port_samples[subnet].append(h)
            state.port_open[h] = [r.port for r in results]
        progress.stop_task(t_ports)

        # Optional: weak default credential checks (safe)
        if weak_auth:
            console.rule("Weak default credential checks (HTTP/RTSP)")
            # Candidates: detected cameras in this subnet and scanned sample hosts
            cam_ips = [c.get("ip") for c in state.cameras_map.get(subnet, [])]
            targets = list({*cam_ips, *state.port_samples.get(subnet, [])})
            tasks = []
            for ip in targets:
                ports = state.port_open.get(ip, [])
                if ports:
                    tasks.append(check_weak_auth_for_ip(ip, ports, default_creds))
            if tasks:
                results = await asyncio.gather(*tasks)
                findings = [r for r in results if r]
                if findings:
                    state.weak_auth_findings.extend(findings)
                    from rich.table import Table
                    w = Table(title="Weak credentials found")
                    w.add_column("IP")
                    w.add_column("Service")
                    w.add_column("Port")
                    w.add_column("Username")
                    w.add_column("Password")
                    for f in findings:
                        if f.get("http"):
                            h = f["http"]
                            w.add_row(f["ip"], "HTTP", str(h.get("port")), h.get("username",""), h.get("password",""))
                        if f.get("rtsp"):
                            r = f["rtsp"]
                            w.add_row(f["ip"], "RTSP", str(r.get("port")), r.get("username",""), r.get("password",""))
                    console.print(w)
                else:
                    console.print("No weak default credentials found on sampled hosts.")

async def _udp_probe_sample(subnet: str, state: WizardState):
    hosts = state.port_samples.get(subnet) or []
    if not hosts:
        return
    from rich.table import Table
    table = Table(title=f"UDP services (sample) in {subnet}")
    table.add_column("IP")
    table.add_column("Services")
    for h in hosts[:5]:
        svcs = probe_udp_services(h)
        if svcs:
            svc_str = ", ".join(f"{s.service}:{s.port}" for s in svcs)
            # Ensure list container for subnet
            if subnet not in state.udp_samples or not isinstance(state.udp_samples.get(subnet), list):
                state.udp_samples[subnet] = []
            state.udp_samples[subnet].append({
                "ip": h,
                "services": [{"service": s.service, "port": s.port, "detail": s.detail} for s in svcs],
            })
        else:
            svc_str = "-"
        table.add_row(h, svc_str)
    console.print(table)
