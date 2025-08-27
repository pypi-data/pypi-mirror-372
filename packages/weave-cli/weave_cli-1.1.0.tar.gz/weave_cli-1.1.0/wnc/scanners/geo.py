from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List
import asyncio
import time
import math
import subprocess

@dataclass
class LocationEstimate:
    city: str
    country: str
    rtt_ms: float
    estimated_km: float


def _speedtest_best_server() -> Optional[LocationEstimate]:
    try:
        import speedtest
        st = speedtest.Speedtest()
        best = st.get_best_server()
        # best contains: 'sponsor', 'name' (city), 'country', 'lat', 'lon', 'd', 'latency'
        city = best.get('name', 'unknown')
        country = best.get('country', 'unknown')
        rtt = float(best.get('latency', 0.0))
        dist_km = float(best.get('d', 0.0))  # approximate distance to server in km
        return LocationEstimate(city=city, country=country, rtt_ms=rtt, estimated_km=dist_km)
    except Exception:
        return None


async def estimate_location_by_rtt() -> Optional[LocationEstimate]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _speedtest_best_server)


# ----- Multi-host probing via Speedtest server directory -----

@dataclass
class ProbePoint:
    city: str
    country: str
    lat: float
    lon: float
    host: str  # hostname:port


@dataclass
class ProbeResult:
    point: ProbePoint
    rtt_ms: float


async def _tcp_rtt(host: str, timeout: float = 1.0) -> Optional[float]:
    try:
        if ":" in host:
            hostname, port_str = host.rsplit(":", 1)
            port = int(port_str)
        else:
            hostname, port = host, 80
        start = time.perf_counter()
        reader, writer = await asyncio.wait_for(asyncio.open_connection(hostname, port), timeout=timeout)
        rtt = (time.perf_counter() - start) * 1000.0
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        return rtt
    except Exception:
        return None


def _pick_probe_points(n: int = 10) -> list[ProbePoint]:
    try:
        import speedtest
        st = speedtest.Speedtest()
        servers = st.get_servers()  # dict distance -> [servers]
        points: list[ProbePoint] = []
        # Flatten and pick first entries across keys until n collected
        for arr in servers.values():
            for s in arr:
                host = s.get('host')  # like 'host:port'
                name = s.get('name', 'unknown')  # city
                country = s.get('country', 'unknown')
                lat = float(s.get('lat', 0.0))
                lon = float(s.get('lon', 0.0))
                if host and lat and lon:
                    points.append(ProbePoint(city=name, country=country, lat=lat, lon=lon, host=host))
        # Simple downsample: take evenly spaced across the list
        if not points:
            return []
        step = max(1, len(points) // n)
        selected = [points[i] for i in range(0, min(len(points), step * n), step)]
        return selected[:n]
    except Exception:
        return []


def _rtt_to_km(rtt_ms: float) -> float:
    """Very rough RTT->distance estimate.
    Assume ~200,000 km/s in fiber and RTT is round-trip => 1 ms ≈ 100 km.
    """
    return max(0.0, rtt_ms * 100.0)


async def estimate_location_by_multihost(n_points: int = 10) -> Optional[LocationEstimate]:
    points = _pick_probe_points(n_points)
    if not points:
        return None
    rtts = await asyncio.gather(*(_tcp_rtt(p.host) for p in points))
    results: list[ProbeResult] = []
    for p, r in zip(points, rtts):
        if r is not None:
            results.append(ProbeResult(point=p, rtt_ms=r))
    if not results:
        return None
    # Choose best (lowest RTT) as nearest city; use its speedtest-provided distance if available via single best server fallback
    best = min(results, key=lambda x: x.rtt_ms)
    return LocationEstimate(city=best.point.city, country=best.point.country, rtt_ms=best.rtt_ms, estimated_km=_rtt_to_km(best.rtt_ms))


# ----- Offline multilateration returning coordinates -----

@dataclass
class MultilatResult:
    lat: float
    lon: float
    nearest_city: str
    nearest_country: str
    confidence: float
    points_used: int


def _proj_setup(points: List[ProbePoint]):
    lat0 = sum(p.lat for p in points) / len(points)
    lon0 = sum(p.lon for p in points) / len(points)
    clat = math.cos(math.radians(lat0))
    return lat0, lon0, clat


def _to_xy(lat: float, lon: float, lat0: float, lon0: float, clat: float) -> tuple[float, float]:
    # Approximate km per deg
    x = (lon - lon0) * 111.32 * clat
    y = (lat - lat0) * 110.57
    return x, y


def _to_ll(x: float, y: float, lat0: float, lon0: float, clat: float) -> tuple[float, float]:
    lat = y / 110.57 + lat0
    lon = x / (111.32 * clat) + lon0 if clat != 0 else lon0
    return lat, lon


async def estimate_location_multilat(n_points: int = 20, max_iters: int = 250) -> Optional[MultilatResult]:
    points = _pick_probe_points(n_points)
    if not points:
        return None
    rtts = await asyncio.gather(*(_tcp_rtt(p.host) for p in points))
    prs: list[tuple[ProbePoint, float]] = []
    for p, r in zip(points, rtts):
        if r is not None and r > 0.0:
            prs.append((p, r))
    if len(prs) < 3:
        return None
    # Setup projection around mean
    sel_pts = [p for p, _ in prs]
    lat0, lon0, clat = _proj_setup(sel_pts)
    xy = [(_to_xy(p.lat, p.lon, lat0, lon0, clat), _rtt_to_km(r)) for p, r in prs]
    # Initial guess: weighted average by 1/d^2
    eps = 1e-6
    wx = wy = ws = 0.0
    for (x, y), d in xy:
        w = 1.0 / max(d * d, 1.0)
        wx += w * x
        wy += w * y
        ws += w
    x = wx / max(ws, eps)
    y = wy / max(ws, eps)
    # Gradient descent
    lr = 0.05
    for _ in range(max_iters):
        grad_x = 0.0
        grad_y = 0.0
        loss = 0.0
        for (xi, yi), di in xy:
            dx = x - xi
            dy = y - yi
            ri = math.hypot(dx, dy) + 1e-9
            diff = (ri - di)
            loss += diff * diff
            # derivative of (ri - di)^2 wrt x,y => 2*(ri-di)*(dx/ri), 2*(ri-di)*(dy/ri)
            grad_x += 2.0 * diff * (dx / ri)
            grad_y += 2.0 * diff * (dy / ri)
        x -= lr * grad_x / len(xy)
        y -= lr * grad_y / len(xy)
    est_lat, est_lon = _to_ll(x, y, lat0, lon0, clat)
    # Nearest server city by Euclidean distance in projection
    nearest = None
    nearest_dist = 1e18
    for (xi, yi), _ in xy:
        d = math.hypot(x - xi, y - yi)
        if d < nearest_dist:
            nearest_dist = d
    # Approximate confidence: inverse of mean absolute residual normalized by typical distance
    mean_res = sum(abs(math.hypot(x - xi, y - yi) - di) for (xi, yi), di in xy) / len(xy)
    typical = max(50.0, sum(di for _, di in xy) / len(xy))
    conf = max(0.0, min(1.0, 1.0 - (mean_res / typical)))
    # Find metadata for nearest
    meta_point = min(prs, key=lambda pr: math.hypot(*_to_xy(pr[0].lat, pr[0].lon, lat0, lon0, clat)) - math.hypot(x, y))
    nearest_city = meta_point[0].city
    nearest_country = meta_point[0].country
    return MultilatResult(lat=est_lat, lon=est_lon, nearest_city=nearest_city, nearest_country=nearest_country, confidence=conf, points_used=len(xy))


# ----- Traceroute POP inference (heuristic) -----

def traceroute_infer(targets: Optional[List[str]] = None, timeout: float = 8.0) -> dict:
    targets = targets or ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
    paths: list[dict] = []
    inferred: list[str] = []
    # simple list of common IATA codes for heuristic mapping
    iata_map = {
        "ams": "Amsterdam",
        "lhr": "London",
        "lon": "London",
        "fra": "Frankfurt",
        "cdg": "Paris",
        "par": "Paris",
        "mad": "Madrid",
        "mia": "Miami",
        "nyc": "New York",
        "ewr": "New York",
        "jfk": "New York",
        "lax": "Los Angeles",
        "sfo": "San Francisco",
        "sea": "Seattle",
        "ord": "Chicago",
        "dfw": "Dallas",
        "iad": "Washington",
        "iad": "Washington",
        "yyz": "Toronto",
        "yul": "Montreal",
        "yvr": "Vancouver",
        "hkg": "Hong Kong",
        "sin": "Singapore",
        "syd": "Sydney",
        "tyo": "Tokyo",
        "nrt": "Tokyo",
        "kix": "Osaka",
        "bom": "Mumbai",
        "del": "Delhi",
        "dub": "Dublin",
        "bru": "Brussels",
        "zrh": "Zurich",
        "waw": "Warsaw",
        "osl": "Oslo",
        "arn": "Stockholm",
        "cph": "Copenhagen",
    }
    for dst in targets:
        try:
            proc = subprocess.run([
                "/usr/sbin/traceroute", "-m", "12", "-n", dst
            ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=timeout, check=False)
        except Exception:
            try:
                proc = subprocess.run(["traceroute", "-m", "12", dst], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=timeout, check=False)
            except Exception:
                continue
        out = proc.stdout.decode("utf-8", errors="replace")
        hops: list[dict] = []
        city_hits: list[str] = []
        for line in out.splitlines():
            line = line.strip()
            if not line or line[0].isdigit() is False:
                continue
            # format typically: hop  ip  rtt ...; since we used -n, we only have IPs. Try again without -n for names if needed
            parts = line.split()
            ip = None
            for tok in parts[1:]:
                if tok.count('.') == 3 or ':' in tok:
                    ip = tok
                    break
            hops.append({"ip": ip or "?", "raw": line})
        # Try one pass with names if we had no hits
        if not hops:
            continue
        try:
            proc2 = subprocess.run([
                "/usr/sbin/traceroute", "-m", "12", dst
            ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=timeout, check=False)
        except Exception:
            proc2 = subprocess.run(["traceroute", "-m", "12", dst], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=timeout, check=False)
        out2 = proc2.stdout.decode("utf-8", errors="replace")
        for line in out2.splitlines():
            l = line.lower()
            for code, city in iata_map.items():
                if f".{code}." in l or f"-{code}-" in l or l.endswith(code) or f".{code}1" in l:
                    city_hits.append(city)
        if city_hits:
            inferred.append(max(set(city_hits), key=city_hits.count))
        paths.append({"target": dst, "hops": hops})
    inferred_city = inferred[0] if inferred else None
    return {"targets": targets, "paths": paths, "inferred_city": inferred_city}


async def estimate_top_locations(n_points: int = 30, top_k: int = 5) -> List[LocationEstimate]:
    """Return top_k nearest cities by RTT from a pool of n_points speedtest servers."""
    points = _pick_probe_points(n_points)
    if not points:
        return []
    rtts = await asyncio.gather(*(_tcp_rtt(p.host) for p in points))
    results: list[ProbeResult] = []
    for p, r in zip(points, rtts):
        if r is not None:
            results.append(ProbeResult(point=p, rtt_ms=r))
    results.sort(key=lambda x: x.rtt_ms)
    ests: List[LocationEstimate] = []
    for pr in results[: max(1, top_k)]:
        ests.append(LocationEstimate(city=pr.point.city, country=pr.point.country, rtt_ms=pr.rtt_ms, estimated_km=_rtt_to_km(pr.rtt_ms)))
    return ests


async def estimate_named_city_rtts(city_names: List[str]) -> List[LocationEstimate]:
    """Probe RTT to at least one server for each requested city name (best-effort fuzzy match)."""
    try:
        import speedtest
        st = speedtest.Speedtest()
        servers = st.get_servers()  # dict distance -> [servers]
        # Build a mapping from lower-cased city to list of ProbePoints
        candidates: dict[str, list[ProbePoint]] = {}
        for arr in servers.values():
            for s in arr:
                host = s.get('host')
                name = s.get('name', 'unknown')
                country = s.get('country', 'unknown')
                lat = float(s.get('lat', 0.0))
                lon = float(s.get('lon', 0.0))
                if host and lat and lon:
                    key = name.lower()
                    candidates.setdefault(key, []).append(ProbePoint(city=name, country=country, lat=lat, lon=lon, host=host))
        # For each requested city, pick first candidate with case-insensitive contains match
        probes: list[tuple[str, ProbePoint]] = []
        for req in city_names:
            req_l = req.lower()
            # exact key match first
            if req_l in candidates and candidates[req_l]:
                probes.append((req, candidates[req_l][0]))
                continue
            # contains match across keys
            found = False
            for k, pts in candidates.items():
                if req_l in k and pts:
                    probes.append((req, pts[0]))
                    found = True
                    break
            if not found:
                # fallback: skip if no match
                continue
        # Measure RTTs
        rtts = await asyncio.gather(*(_tcp_rtt(p.host) for _, p in probes))
        out: List[LocationEstimate] = []
        for (name, p), r in zip(probes, rtts):
            if r is not None:
                out.append(LocationEstimate(city=name, country=p.country, rtt_ms=r, estimated_km=_rtt_to_km(r)))
        return out
    except Exception:
        return []
