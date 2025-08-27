# Weave Network CLI (WNC)

Modular Python CLI for network discovery, port/protocol scanning, and device (e.g., IP camera) detection, guided by an interactive wizard with live progress.

## Quickstart

1. Create virtualenv and install deps:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the wizard (basic):

```
python -m wnc wizard
```

3. Full extended scan with JSON report and risk analysis:

```
python -m wnc wizard --yes --output scan_report.json --analyze
```

4. Or run commands directly:

```
python -m wnc scan internal
python -m wnc scan ports --target 192.168.1.10 --top 1000
python -m wnc scan cameras --subnet 192.168.1.0/24
```

## Features

- Interactive wizard with Rich progress bars
- Internal network discovery (interfaces, subnets)
- Host discovery (TCP connect checks)
- Async port scan and banner grabbing (HTTP/HTTPS/SSH/Redis/Memcached) with HTTP title extraction
- Camera heuristics (HTTP/RTSP), ONVIF WS-Discovery, optional ONVIF SOAP info, optional ONVIF password change
- Device fingerprinting from HTTP/RTSP/SSDP/mDNS/ONVIF evidence with confidence scoring
- LAN latency to default gateway and DNS (median/p95 via TCP connect RTTs)
- SSDP/UPnP discovery; mDNS service discovery
- Passive ARP table parsing with MAC OUI vendor hints (no ARP sweep)
- Speedtest and RTT-based rough location
- Risk analyzer that scores and summarizes findings
- Modular scanners in `wnc/scanners/`

## CLI Flags (wizard)

- `--extended/--no-extended` run extended tasks (default: on)
- `--weak-auth/--no-weak-auth` test common default credentials for HTTP/RTSP on camera-like hosts (safe, read-only) (default: on)
- `--creds "u1:p1,u2:p2"` custom username:password pairs to try for weak-auth
- `--change-password` attempt ONVIF password change when weak creds found (DANGEROUS; modifies device)
- `--change-user <user>` target username for ONVIF password change (defaults to the weak-cred username)
- `--new-password <pw>` new password to set (required with `--change-password`)
- `--wifi` collect Wi‑Fi info (macOS) including current SSID/BSSID/channel/RSSI and nearby APs
- `--lan-speed` measure LAN latency to default gateway and DNS (RTT med/p95)
- `--speedtest-runs <1-3>` number of speedtest runs
- `--output <path>` write full JSON report to path
- `--analyze/--no-analyze` run risk analyzer and include results in report (default: on)
- `--yes` non-interactive; auto-accept prompts

## Report (JSON)

When `--output` is provided, the wizard writes a JSON file including:

- `subnets`, `hosts`, `port_sample_hosts`, `port_open`
- `udp_samples` (labeled UDP services per sampled host)
- `cameras`, `onvif`, `onvif_info`, `weak_auth_findings`, `onvif_password_change`
- `ssdp`, `mdns_records`, `arp`, `banners`
- `devices` (fingerprinted vendor/product/type with confidence)
- `wifi` (macOS current network and nearby APs)
- `lan_speed` (gateway and DNS RTT stats, open ports tried)
- `speedtest`, `location`, `location_top`, `location_targets`, `risk`, `summary`

## Docker

Build image:

```bash
docker build -t weave-network-cli:latest .
```

Run the wizard (save report locally):

```bash
# Linux: host networking gives best local LAN visibility
# macOS/Windows: --network host is not supported the same way; container can still reach LAN via bridged networking

docker run --rm \
  --name wnc \
  --network host \
  -v "$PWD:/data" \
  weave-network-cli:latest wizard --yes --extended --output /data/scan_report.json
```

Other commands:

```bash
docker run --rm --network host weave-network-cli:latest scan internal

docker run --rm --network host weave-network-cli:latest scan ports --target 192.168.1.10 --top 200

docker run --rm --network host weave-network-cli:latest scan cameras --subnet 192.168.1.0/24
```

Limitations in container:

- `--wifi` (macOS Wi‑Fi details) will not work inside Docker.
- Host network mode is recommended on Linux for local discovery.

## npm (Node wrapper)

You can use an npm wrapper to invoke WNC without installing Python. It prefers Docker (and falls back to local Python if available).

Run via npx:

```bash
npx @thephotocodegrapher/wnc wizard --yes --extended --output ./scan_report.json
```

Or install globally:

```bash
npm i -g @thephotocodegrapher/wnc
wnc wizard --yes --extended --output ./scan_report.json
```

Notes:

- Requires Docker for best experience; on Linux, host networking is used automatically when available.
- On macOS/Windows, Docker networking differs; discovery still works via bridged networking.

## Python API

Use WNC programmatically without packaging to PyPI. Import sync helpers from `wnc`:

```python
from wnc import internal_subnets, hosts, ports, cameras, wizard

subs = internal_subnets()
print("Subnets:", subs)

if subs:
    live = hosts(subnet=subs[0])
    print("Live hosts:", live[:10])

    if live:
        open_ports = ports(live[0], top_n=100)
        print("Open ports:", [(r.port, r.service) for r in open_ports])

    cams = cameras(subs[0])
    for c in cams[:5]:
        print("Camera:", c.ip, c.vendor, c.evidence[:3])

# Run the interactive wizard non-interactively and save a JSON report
wizard(yes=True, extended=True, output="scan_report.json")
```

Available helpers in `wnc`:

- `internal_subnets() -> List[str]`
- `hosts(subnet, limit=None) -> List[str]`
- `ports(host, top_n=200, ports=None) -> List[PortResult]`
- `cameras(subnet) -> List[CameraCandidate]`
- `wizard(...same flags as CLI...) -> None`

## Notes

- ICMP ping typically requires elevated privileges. This tool uses fast TCP connect checks to infer live hosts.
- Scans are best-effort and may miss hosts with strict firewalls.
- ONVIF SOAP device information is unauthenticated by default and best-effort (short timeouts).
- ONVIF password change is disabled by default; only runs with `--change-password` and requires `--new-password`. Behavior varies by vendor.

## License

This project is released under the PolyForm Noncommercial License 1.0.0. You may use, copy, modify, and redistribute the software for noncommercial purposes.

- Noncommercial means not intended for or directed toward commercial advantage or monetary compensation.
- For commercial use, please contact the authors to obtain a commercial license.

See the full text in `LICENSE`.

## Maintainer

- [Kai Gartner](https://linkedin.com/in/kaigartner)

## Project Meta

- [Contributing](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [Third-Party Notices](THIRD_PARTY.md)
