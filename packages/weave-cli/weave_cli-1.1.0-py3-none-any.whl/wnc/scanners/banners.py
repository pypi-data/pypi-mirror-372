from __future__ import annotations

import socket
import ssl
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Banner:
    port: int
    service: Optional[str]
    info: str

SOCK_TIMEOUT = 1.5


def _connect(host: str, port: int) -> Optional[socket.socket]:
    try:
        s = socket.create_connection((host, port), timeout=SOCK_TIMEOUT)
        s.settimeout(SOCK_TIMEOUT)
        return s
    except Exception:
        return None


def _recv_some(s: socket.socket, n: int = 256) -> str:
    try:
        data = s.recv(n)
        return data.decode('utf-8', errors='ignore')
    except Exception:
        return ''


def grab_http(host: str, port: int) -> Optional[Banner]:
    s = _connect(host, port)
    if not s:
        return None
    try:
        req = b"HEAD / HTTP/1.0\r\nHost: %b\r\nUser-Agent: WNC\r\nConnection: close\r\n\r\n" % host.encode()
        s.sendall(req)
        data = s.recv(2048).decode('utf-8', errors='ignore')
        server = ''
        title = ''
        for line in data.split('\r\n'):
            if line.lower().startswith('server:'):
                server = line.split(':', 1)[1].strip()
        # Try to glean a title; if not present, do a tiny GET
        low = data.lower()
        if '<title>' in low:
            try:
                start = low.index('<title>') + 7
                end = low.index('</title>', start)
                title = data[start:end].strip()
            except Exception:
                title = ''
        if not title:
            try:
                # issue a tiny GET to capture title if possible
                req = b"GET / HTTP/1.0\r\nHost: %b\r\nUser-Agent: WNC\r\nConnection: close\r\n\r\n" % host.encode()
                s.sendall(req)
                gdata = s.recv(4096).decode('utf-8', errors='ignore')
                glow = gdata.lower()
                if '<title>' in glow:
                    gs = glow.index('<title>') + 7
                    ge = glow.find('</title>', gs)
                    if ge != -1:
                        title = gdata[gs:ge].strip()
                if not server:
                    for line in gdata.split('\r\n'):
                        if line.lower().startswith('server:'):
                            server = line.split(':', 1)[1].strip()
            except Exception:
                pass
        info = server
        if title:
            info = (server + ' | ' if server else '') + f"title={title[:80]}"
        if not info:
            info = (data.split('\r\n', 1)[0] if data else '')
        return Banner(port=port, service='http', info=info)
    except Exception:
        return None
    finally:
        s.close()


def grab_https(host: str, port: int) -> Optional[Banner]:
    s = _connect(host, port)
    if not s:
        return None
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ss = ctx.wrap_socket(s, server_hostname=host)
        ss.settimeout(SOCK_TIMEOUT)
        req = b"HEAD / HTTP/1.0\r\nHost: %b\r\nUser-Agent: WNC\r\nConnection: close\r\n\r\n" % host.encode()
        ss.sendall(req)
        data = ss.recv(2048).decode('utf-8', errors='ignore')
        server = ''
        for line in data.split('\r\n'):
            if line.lower().startswith('server:'):
                server = line.split(':', 1)[1].strip()
        return Banner(port=port, service='https', info=server or (data.split('\r\n', 1)[0] if data else ''))
    except Exception:
        return None
    finally:
        try:
            ss.close()
        except Exception:
            pass


def grab_ssh(host: str, port: int) -> Optional[Banner]:
    s = _connect(host, port)
    if not s:
        return None
    try:
        data = _recv_some(s, 256)
        if data.startswith('SSH-'):
            return Banner(port=port, service='ssh', info=data.strip())
        return None
    finally:
        s.close()


def grab_redis(host: str, port: int) -> Optional[Banner]:
    s = _connect(host, port)
    if not s:
        return None
    try:
        s.sendall(b"PING\r\n")
        data = _recv_some(s)
        if 'PONG' in data:
            return Banner(port=port, service='redis', info='PONG')
        return None
    finally:
        s.close()


def grab_memcached(host: str, port: int) -> Optional[Banner]:
    s = _connect(host, port)
    if not s:
        return None
    try:
        s.sendall(b"version\r\n")
        data = _recv_some(s)
        if 'VERSION' in data.upper():
            return Banner(port=port, service='memcached', info=data.strip())
        return None
    finally:
        s.close()


def grab_generic(host: str, port: int) -> Optional[Banner]:
    s = _connect(host, port)
    if not s:
        return None
    try:
        data = _recv_some(s)
        if data:
            return Banner(port=port, service=None, info=data.strip())
        return None
    finally:
        s.close()


COMMON_SERVICE_PORTS = {
    80: 'http', 8080: 'http', 8000: 'http', 8888: 'http',
    443: 'https', 8443: 'https',
    22: 'ssh',
    6379: 'redis',
    11211: 'memcached',
}


def grab_banners(host: str, ports: List[int]) -> List[Banner]:
    banners: List[Banner] = []
    for p in ports:
        svc = COMMON_SERVICE_PORTS.get(p)
        b: Optional[Banner] = None
        if svc == 'http':
            b = grab_http(host, p)
        elif svc == 'https':
            b = grab_https(host, p)
        elif svc == 'ssh':
            b = grab_ssh(host, p)
        elif svc == 'redis':
            b = grab_redis(host, p)
        elif svc == 'memcached':
            b = grab_memcached(host, p)
        else:
            # small generic peek
            b = grab_generic(host, p)
        if b:
            banners.append(b)
    return banners
