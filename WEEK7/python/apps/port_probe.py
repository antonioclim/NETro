"""Sondare defensivă de porturi (TCP connect și UDP probe).

Scop: să înțelegi diferența dintre un port TCP „deschis” (acceptă conexiuni) și un port „închis”
(refuză sau expiră), respectiv comportamentul tipic UDP (nu există handshake, deci multe cazuri
se manifestă ca timeout).

Atenție: folosește acest script doar pe rețeaua locală de laborator.
"""

from __future__ import annotations

import argparse
import socket
import time
from typing import Iterable, Tuple


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Sondează porturi TCP și UDP pentru o țintă (didactic, defensiv).")
    p.add_argument("--host", required=True, help="Host-ul țintă (IP sau nume)")
    p.add_argument("--tcp", default="9090", help="Porturi TCP (ex: 80,443 sau 9000-9010)")
    p.add_argument("--udp", default="9091", help="Porturi UDP (ex: 53 sau 9000-9010)")
    p.add_argument("--timeout", type=float, default=0.6, help="Timeout per probă (secunde)")
    return p


def parse_ports(spec: str) -> list[int]:
    ports: list[int] = []
    for part in (spec or "").split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            ports.extend(list(range(int(a), int(b) + 1)))
        else:
            ports.append(int(part))
    return sorted(set(ports))


def tcp_probe(host: str, port: int, timeout: float) -> Tuple[int, str]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return (port, "deschis")
    except (ConnectionRefusedError, OSError) as e:
        return (port, f"închis ({e.__class__.__name__})")
    except socket.timeout:
        return (port, "timeout")
    finally:
        try:
            sock.close()
        except Exception:
            pass


def udp_probe(host: str, port: int, timeout: float) -> Tuple[int, str]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(b"ping", (host, port))
        # În UDP, de obicei nu primești răspuns. Încerc totuși o recepție.
        data, _ = sock.recvfrom(2048)
        if data:
            return (port, "răspuns")
        return (port, "fără date")
    except socket.timeout:
        return (port, "timeout")
    except OSError as e:
        return (port, f"eroare ({e.__class__.__name__})")
    finally:
        try:
            sock.close()
        except Exception:
            pass


def log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"[probe {ts}] {msg}", flush=True)


def run_probes(host: str, tcp_ports: Iterable[int], udp_ports: Iterable[int], timeout: float) -> int:
    log(f"Sondez {host} cu timeout {timeout:.2f}s")

    if tcp_ports:
        log(f"TCP: {', '.join(map(str, tcp_ports))}")
        for p in tcp_ports:
            port, status = tcp_probe(host, p, timeout)
            log(f"TCP {port}: {status}")

    if udp_ports:
        log(f"UDP: {', '.join(map(str, udp_ports))}")
        for p in udp_ports:
            port, status = udp_probe(host, p, timeout)
            log(f"UDP {port}: {status}")

    log("Gata")
    return 0


def main() -> int:
    args = build_parser().parse_args()
    tcp_ports = parse_ports(args.tcp)
    udp_ports = parse_ports(args.udp)
    return run_probes(args.host, tcp_ports, udp_ports, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
