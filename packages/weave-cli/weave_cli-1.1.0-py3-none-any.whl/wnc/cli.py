import asyncio
import typer
from rich.console import Console
from rich.panel import Panel
from typing import Optional

from . import __version__
from .wizard import run_wizard
from .scanners.network import get_interfaces, get_internal_subnets, discover_hosts
from .scanners.ports import scan_ports
from .scanners.cameras import detect_cameras

app = typer.Typer(help="Weave Network CLI (WNC)")
console = Console()

@app.callback()
def main(version: Optional[bool] = typer.Option(None, "--version", help="Show version and exit", is_eager=True)):
    if version:
        console.print(f"WNC v{__version__}")
        raise typer.Exit(code=0)

@app.command()
def wizard(
    extended: bool = typer.Option(True, "--extended/--no-extended", help="Run extended tasks (UDP probes, speedtest, rough location)"),
    speedtest_runs: Optional[int] = typer.Option(None, "--speedtest-runs", min=1, max=3, help="Number of speedtest runs (1-3)"),
    output: Optional[str] = typer.Option(None, "--output", help="Write JSON report to this path"),
    analyze: bool = typer.Option(True, "--analyze/--no-analyze", help="Run risk analyzer and include in report"),
    yes: bool = typer.Option(False, "--yes", help="Run non-interactively and auto-accept prompts"),
    weak_auth: bool = typer.Option(True, "--weak-auth/--no-weak-auth", help="Test common default credentials on detected cameras (safe, read-only)"),
    creds: Optional[str] = typer.Option(None, "--creds", help="Comma-separated username:password pairs to try for weak-auth (e.g. 'admin:admin,admin:12345')"),
    change_password: bool = typer.Option(False, "--change-password", help="Attempt ONVIF password change if weak creds are found (DANGEROUS)"),
    change_user: Optional[str] = typer.Option(None, "--change-user", help="Username to change password for (defaults to the weak-cred username)"),
    new_password: Optional[str] = typer.Option(None, "--new-password", help="New password to set (required with --change-password)"),
    wifi: bool = typer.Option(False, "--wifi", help="Collect Wi‑Fi info on macOS (SSID/BSSID/channel/RSSI)"),
    lan_speed: bool = typer.Option(False, "--lan-speed", help="Measure LAN latency to default gateway and DNS"),
):
    """Run the interactive scanning wizard."""
    # Parse creds string to list
    cred_list = None
    if creds:
        parts = [p.strip() for p in creds.split(",") if p.strip()]
        cred_list = [p for p in parts if ":" in p]
    if change_password and not new_password:
        console.print("[red]--new-password is required when using --change-password[/red]")
        raise typer.Exit(code=2)
    asyncio.run(run_wizard(
        extended=extended,
        speedtest_runs=speedtest_runs,
        output_path=output,
        analyze=analyze,
        assume_yes=yes,
        weak_auth=weak_auth,
        default_creds=cred_list,
        change_password=change_password,
        change_user=change_user,
        new_password=new_password,
        wifi=wifi,
        lan_speed=lan_speed,
    ))

scan_app = typer.Typer(help="Scanning commands")
app.add_typer(scan_app, name="scan")

@scan_app.command("internal")
def scan_internal():
    """Discover local interfaces, subnets, and live hosts."""
    subnets = get_internal_subnets()
    console.print(Panel.fit("Discovered subnets:\n" + "\n".join(str(s) for s in subnets), title="Internal Subnets"))
    for subnet in subnets:
        hosts = asyncio.run(discover_hosts(str(subnet)))
        console.print(Panel.fit("\n".join(hosts) or "No hosts found", title=f"Live hosts in {subnet}"))

@scan_app.command("ports")
def scan_ports_cmd(target: str = typer.Option(..., "--target", help="Target IPv4 address"), top: int = typer.Option(200, "--top", help="Top N common ports to scan")):
    """Scan ports on a single host."""
    results = asyncio.run(scan_ports(target, top_n=top))
    from rich.table import Table
    table = Table(title=f"Open ports on {target}")
    table.add_column("Port", justify="right")
    table.add_column("Proto")
    table.add_column("Service")
    for r in results:
        table.add_row(str(r.port), r.proto, r.service or "?")
    console.print(table)

@scan_app.command("cameras")
def scan_cameras(subnet: str = typer.Option(..., "--subnet", help="CIDR subnet to search for cameras, e.g. 192.168.1.0/24")):
    """Detect likely IP cameras on a subnet."""
    cams = asyncio.run(detect_cameras(subnet))
    if not cams:
        console.print("No cameras detected.")
    else:
        from rich.table import Table
        table = Table(title=f"Potential Cameras in {subnet}")
        table.add_column("IP")
        table.add_column("Vendor")
        table.add_column("Evidence")
        for cam in cams:
            table.add_row(cam.ip, cam.vendor or "?", ", ".join(cam.evidence)[:200])
        console.print(table)
