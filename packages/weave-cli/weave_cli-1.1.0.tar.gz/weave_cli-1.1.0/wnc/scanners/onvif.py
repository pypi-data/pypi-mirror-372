from __future__ import annotations

import socket
import uuid
import re
from dataclasses import dataclass
from typing import Dict, List

MCAST_GRP = '239.255.255.250'
MCAST_PORT = 3702

# Minimal WS-Discovery Probe for ONVIF devices
PROBE_TEMPLATE = (
    "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    "<e:Envelope xmlns:e=\"http://www.w3.org/2003/05/soap-envelope\""
    " xmlns:w=\"http://schemas.xmlsoap.org/ws/2004/08/addressing\""
    " xmlns:d=\"http://schemas.xmlsoap.org/ws/2005/04/discovery\""
    " xmlns:dn=\"http://www.onvif.org/ver10/network/wsdl\">"
    " <e:Header>"
    "  <w:MessageID>uuid:{uuid}</w:MessageID>"
    "  <w:To e:mustUnderstand=\"true\">urn:schemas-xmlsoap-org:ws:2005:04:discovery</w:To>"
    "  <w:Action e:mustUnderstand=\"true\">"
    "   http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe"
    "  </w:Action>"
    " </e:Header>"
    " <e:Body>"
    "  <d:Probe>"
    "   <d:Types>dn:NetworkVideoTransmitter</d:Types>"
    "  </d:Probe>"
    " </e:Body>"
    "</e:Envelope>"
)

@dataclass
class OnvifDevice:
    ip: str
    xaddrs: List[str]
    scopes: List[str]


def ws_discover(timeout: float = 2.5) -> Dict[str, OnvifDevice]:
    """Broadcast a WS-Discovery Probe and collect ONVIF responses.
    Returns a mapping ip -> OnvifDevice.
    """
    msg = PROBE_TEMPLATE.format(uuid=str(uuid.uuid4()))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
        ttl = 2
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        sock.sendto(msg.encode('utf-8'), (MCAST_GRP, MCAST_PORT))
        devices: Dict[str, OnvifDevice] = {}
        while True:
            try:
                data, addr = sock.recvfrom(8192)
            except socket.timeout:
                break
            except Exception:
                break
            ip = addr[0]
            text = data.decode(errors='ignore')
            # Extract XAddrs and Scopes
            xaddrs = re.findall(r"<wsa:Address>(.*?)</wsa:Address>|<XAddrs>(.*?)</XAddrs>", text)
            flat_xaddrs: List[str] = []
            for a, b in xaddrs:
                if a:
                    flat_xaddrs.append(a.strip())
                if b:
                    flat_xaddrs.extend(b.strip().split())
            scopes = re.findall(r"<Scopes>(.*?)</Scopes>", text)
            scope_items: List[str] = []
            for s in scopes:
                scope_items.extend(s.split())
            d = devices.get(ip)
            if d:
                d.xaddrs = list(sorted(set(d.xaddrs + flat_xaddrs)))
                d.scopes = list(sorted(set(d.scopes + scope_items)))
            else:
                devices[ip] = OnvifDevice(ip=ip, xaddrs=flat_xaddrs, scopes=scope_items)
        return devices
    finally:
        sock.close()
