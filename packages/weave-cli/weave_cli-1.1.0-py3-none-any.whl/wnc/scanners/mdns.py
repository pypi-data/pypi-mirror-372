from __future__ import annotations

import socket
import struct
import time
from dataclasses import dataclass
from typing import List, Dict

MADDR = '224.0.0.251'
MPORT = 5353

# Common services to query
COMMON_PTRS = [
    "_services._dns-sd._udp.local.",
    "_http._tcp.local.",
    "_rtsp._tcp.local.",
    "_ipp._tcp.local.",
    "_printer._tcp.local.",
    "_airplay._tcp.local.",
    "_raop._tcp.local.",
    "_spotify-connect._tcp.local.",
    "_ssh._tcp.local.",
    "_hue._tcp.local.",
]

@dataclass
class MdnsRecord:
    name: str
    rtype: int
    rclass: int
    ttl: int
    data: str

@dataclass
class MdnsService:
    service: str
    instance: str
    target: str | None
    txt: Dict[str, str]


def _encode_name(name: str) -> bytes:
    parts = name.strip('.').split('.')
    out = b''
    for p in parts:
        b = p.encode('utf-8')
        out += struct.pack('B', len(b)) + b
    return out + b'\x00'


def _build_query(qname: str, qtype: int = 12, qclass: int = 1) -> bytes:
    # qtype 12 = PTR
    tid = 0
    flags = 0x0000
    qdcount = 1
    ancount = nscount = arcount = 0
    header = struct.pack('!HHHHHH', tid, flags, qdcount, ancount, nscount, arcount)
    q = _encode_name(qname) + struct.pack('!HH', qtype, qclass)
    return header + q


def _parse_name(packet: bytes, offset: int):
    labels = []
    jumped = False
    orig_offset = offset
    while True:
        if offset >= len(packet):
            return ('.'.join(labels), offset)
        length = packet[offset]
        if length == 0:
            offset += 1
            break
        if (length & 0xC0) == 0xC0:
            # pointer
            if offset + 1 >= len(packet):
                break
            pointer = ((length & 0x3F) << 8) | packet[offset + 1]
            offset += 2
            name, _ = _parse_name(packet, pointer)
            labels.append(name)
            jumped = True
            break
        else:
            offset += 1
            label = packet[offset:offset + length]
            labels.append(label.decode('utf-8', errors='ignore'))
            offset += length
    name = '.'.join(labels)
    if jumped:
        return (name, orig_offset + 2)
    return (name, offset)


def _parse_answers(packet: bytes) -> List[MdnsRecord]:
    if len(packet) < 12:
        return []
    _tid, flags, qdcount, ancount, nscount, arcount = struct.unpack('!HHHHHH', packet[:12])
    offset = 12
    # skip questions
    for _ in range(qdcount):
        _, offset = _parse_name(packet, offset)
        offset += 4  # qtype+qclass
    records: List[MdnsRecord] = []
    total = ancount + nscount + arcount
    for _ in range(total):
        name, offset = _parse_name(packet, offset)
        if offset + 10 > len(packet):
            break
        rtype, rclass, ttl, rdlength = struct.unpack('!HHIH', packet[offset:offset + 10])
        offset += 10
        rdata = packet[offset:offset + rdlength]
        offset += rdlength
        data_str = ''
        if rtype in (12, 33):  # PTR or SRV
            try:
                target, _ = _parse_name(packet, offset - rdlength)
                data_str = target
            except Exception:
                data_str = ''
        elif rtype == 16:  # TXT
            # simple TXT parse
            txts: Dict[str, str] = {}
            i = 0
            while i < len(rdata):
                l = rdata[i]
                i += 1
                s = rdata[i:i + l].decode('utf-8', errors='ignore')
                i += l
                if '=' in s:
                    k, v = s.split('=', 1)
                    txts[k] = v
            data_str = ';'.join(f'{k}={v}' for k, v in txts.items())
        else:
            data_str = rdata.decode('utf-8', errors='ignore')
        records.append(MdnsRecord(name=name, rtype=rtype, rclass=rclass, ttl=ttl, data=data_str))
    return records


def discover_mdns(timeout: float = 3.0) -> List[MdnsRecord]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
        # join multicast group
        mreq = struct.pack("=4sl", socket.inet_aton(MADDR), socket.INADDR_ANY)
        try:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except OSError:
            # best effort
            pass
        # bind ephemeral port; many OSes restrict binding 5353 without root
        sock.bind(("0.0.0.0", 0))
        # send queries
        for q in COMMON_PTRS:
            pkt = _build_query(q)
            try:
                sock.sendto(pkt, (MADDR, MPORT))
            except Exception:
                continue
        # collect
        end = time.time() + timeout
        packets: List[bytes] = []
        while time.time() < end:
            try:
                data, _ = sock.recvfrom(9000)
                packets.append(data)
            except socket.timeout:
                break
            except Exception:
                break
        records: List[MdnsRecord] = []
        for p in packets:
            records.extend(_parse_answers(p))
        return records
    finally:
        sock.close()
