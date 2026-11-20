"""
DNS Utilities for Antigravity Reels Engine
Ensures fast, non-blocking DNS resolution against local systemd-resolved (127.0.0.53)
when external nameservers (like 8.8.8.8) in /etc/resolv.conf drop outbound UDP packets.
"""

import socket
import struct
from typing import List, Dict

_fast_dns_enabled = False

def enable_fast_dns():
    """Patches socket.getaddrinfo to query 127.0.0.53 directly with an in-memory cache."""
    global _fast_dns_enabled
    if _fast_dns_enabled:
        return

    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_sock.settimeout(0.4)
        test_sock.sendto(
            b"\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01",
            ("127.0.0.53", 53),
        )
        resp, _ = test_sock.recvfrom(512)
        test_sock.close()
        if not resp:
            return
    except Exception:
        return

    _orig_getaddrinfo = socket.getaddrinfo
    _cache: Dict[str, str] = {}

    def _dns_query(host: str, dns_ip: str = "127.0.0.53") -> List[str]:
        header = struct.pack(">HHHHHH", 0x1234, 0x0100, 1, 0, 0, 0)
        query = b""
        for part in host.split("."):
            query += struct.pack("B", len(part)) + part.encode()
        query += b"\x00"
        query += struct.pack(">HH", 1, 1)
        packet = header + query

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.2)
        sock.sendto(packet, (dns_ip, 53))
        data, _ = sock.recvfrom(1024)
        sock.close()

        offset = len(packet)
        ips = []
        ancount = struct.unpack(">H", data[6:8])[0]
        for _ in range(ancount):
            if offset >= len(data):
                break
            if data[offset] & 0xC0 == 0xC0:
                offset += 2
            else:
                while data[offset] != 0:
                    offset += 1 + data[offset]
                offset += 1
            rtype, rclass, ttl, rdlength = struct.unpack(">HHIH", data[offset : offset + 10])
            offset += 10
            if rtype == 1 and rdlength == 4:
                ips.append(socket.inet_ntoa(data[offset : offset + 4]))
            offset += rdlength
        return ips

    def fast_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        if isinstance(host, str) and not host.replace(".", "").isdigit() and host not in ("localhost", "127.0.0.1"):
            if host not in _cache:
                try:
                    ips = _dns_query(host)
                    if ips:
                        _cache[host] = ips[0]
                except Exception:
                    pass
            if host in _cache:
                return _orig_getaddrinfo(_cache[host], port, family, type, proto, flags)
        return _orig_getaddrinfo(host, port, family, type, proto, flags)

    socket.getaddrinfo = fast_getaddrinfo
    _fast_dns_enabled = True

enable_fast_dns()
