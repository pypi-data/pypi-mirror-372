from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional

@dataclass
class SpeedResult:
    download_mbps: float
    upload_mbps: float
    ping_ms: float
    server_name: str


def _run_speedtest_once() -> Optional[SpeedResult]:
    try:
        import speedtest  # from speedtest-cli
        st = speedtest.Speedtest()
        st.get_best_server()
        dl = st.download() / 1e6  # bits per second to Mbps
        ul = st.upload() / 1e6
        ping = st.results.ping
        srv = st.results.server.get('sponsor', 'unknown')
        return SpeedResult(download_mbps=dl, upload_mbps=ul, ping_ms=ping, server_name=str(srv))
    except Exception:
        return None


async def run_speedtest(runs: int = 1) -> Optional[SpeedResult]:
    runs = max(1, min(int(runs), 3))
    loop = asyncio.get_running_loop()
    results: list[SpeedResult] = []
    for _ in range(runs):
        res = await loop.run_in_executor(None, _run_speedtest_once)
        if res:
            results.append(res)
    if not results:
        return None
    # Average results
    dl = sum(r.download_mbps for r in results) / len(results)
    ul = sum(r.upload_mbps for r in results) / len(results)
    ping = sum(r.ping_ms for r in results) / len(results)
    srv = results[-1].server_name
    return SpeedResult(download_mbps=dl, upload_mbps=ul, ping_ms=ping, server_name=srv)
