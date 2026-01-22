#!/usr/bin/env python3
"""
================================================================================
Exercițiul 1: Scanner TCP Avansat
================================================================================
S13 - IoT și Securitate în Rețele de Calculatoare

OBIECTIVE PEDAGOGICE:
1. Înțelegerea funcționării socketurilor TCP
2. Diferențierea între porturi open/closed/filtered
3. Implementarea scanării concurente cu ThreadPoolExecutor
4. Exportul rezultatelor în format JSON structurat

ATENȚIE ETICĂ:
- Acest instrument este destinat EXCLUSIV laboratorului controlat
- NU utilizați pe sisteme fără autorizare explicită
- Încălcarea acestei reguli constituie infracțiune conform legii

UTILIZARE:
    # Scanare de bază
    python3 ex_01_port_scanner.py --target 10.0.13.11 --ports 1-1024
    
    # Scanare specifică cu export JSON
    python3 ex_01_port_scanner.py --target 10.0.13.11 --ports 22,80,443,8080 --json-out scan.json
    
    # Descoperire hosturi în rețea
    python3 ex_01_port_scanner.py --target 10.0.13.1-15 --mode discovery
    
    # Scanare cu paralelism ridicat
    python3 ex_01_port_scanner.py --target 10.0.13.11 --ports 1-65535 --workers 200 --timeout 0.1
================================================================================
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ==============================================================================
# CONSTANTE ȘI CONFIGURĂRI
# ==============================================================================

# Porturi cunoscute și serviciile asociate (subset relevant)
KNOWN_PORTS = {
    20: "FTP-Data",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    993: "IMAPS",
    995: "POP3S",
    1883: "MQTT",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
    8883: "MQTT-TLS",
    27017: "MongoDB",
}

# Culori ANSI pentru output
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


# ==============================================================================
# STRUCTURI DE DATE
# ==============================================================================

@dataclass
class ScanResult:
    """Rezultatul scanării unui singur port."""
    port: int
    state: str  # "open", "closed", "filtered"
    service: Optional[str] = None
    banner: Optional[str] = None
    response_time_ms: Optional[float] = None


@dataclass
class HostScanResult:
    """Rezultatul scanării complete a unui host."""
    target: str
    scan_time: str
    total_ports: int
    open_ports: List[ScanResult]
    closed_ports: int
    filtered_ports: int
    duration_seconds: float


# ==============================================================================
# FUNCȚII DE SCANARE
# ==============================================================================

def tcp_connect_scan(
    host: str,
    port: int,
    timeout: float = 0.5,
    grab_banner: bool = True
) -> ScanResult:
    """
    Realizează un TCP connect scan pe un singur port.
    
    EXPLICAȚIE TEHNICĂ:
    - Creează un socket TCP și încearcă conexiunea completă (3-way handshake)
    - Rezultatul depinde de răspunsul sistemului țintă:
        * Conexiune reușită → port OPEN
        * Connection refused → port CLOSED
        * Timeout → port FILTERED (firewall drop)
    
    Args:
        host: Adresa IP sau hostname
        port: Numărul portului (1-65535)
        timeout: Timeout în secunde pentru conexiune
        grab_banner: Dacă încearcă să citească banner-ul serviciului
    
    Returns:
        ScanResult cu starea portului și informații suplimentare
    """
    start_time = time.perf_counter()
    result = ScanResult(port=port, state="unknown")
    
    # Creăm socketul TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        # ========================================
        # SECȚIUNEA STUDENT - TCP Connect
        # ========================================
        # Încercăm conexiunea la (host, port)
        # connect_ex() returnează 0 pentru succes, altfel cod eroare
        error_code = sock.connect_ex((host, port))
        
        if error_code == 0:
            # Conexiune reușită - port deschis
            result.state = "open"
            result.service = KNOWN_PORTS.get(port, "unknown")
            
            # Opțional: citim banner-ul serviciului
            if grab_banner:
                try:
                    sock.settimeout(0.5)
                    # Trimitem un newline pentru a stimula răspunsul
                    sock.sendall(b"\r\n")
                    banner = sock.recv(1024).decode("utf-8", errors="replace").strip()
                    if banner:
                        result.banner = banner[:100]  # Limităm lungimea
                except Exception:
                    pass  # Banner grab eșuat - nu e critic
        else:
            # Conexiune refuzată - port închis
            result.state = "closed"
    
    except socket.timeout:
        # Timeout - probabil filtrat de firewall
        result.state = "filtered"
    
    except ConnectionRefusedError:
        # Explicit refuzat - port închis
        result.state = "closed"
    
    except OSError as e:
        # Alte erori de rețea
        result.state = f"error:{e.__class__.__name__}"
    
    finally:
        sock.close()
    
    # Calculăm timpul de răspuns
    result.response_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
    
    return result


def parse_ports(ports_str: str) -> List[int]:
    """
    Parsează specificația de porturi în listă de porturi.
    
    Suportă formate:
    - "80" → [80]
    - "80,443,8080" → [80, 443, 8080]
    - "1-1024" → [1, 2, ..., 1024]
    - "22,80,443,1000-2000" → [22, 80, 443, 1000, ..., 2000]
    """
    ports: List[int] = []
    
    for part in ports_str.split(","):
        part = part.strip()
        if not part:
            continue
        
        if "-" in part:
            # Interval de porturi
            try:
                start, end = part.split("-", 1)
                start_port, end_port = int(start), int(end)
                
                if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
                    raise ValueError(f"Port invalid în intervalul: {part}")
                if start_port > end_port:
                    raise ValueError(f"Interval invalid: {part}")
                
                ports.extend(range(start_port, end_port + 1))
            except ValueError as e:
                print(f"[!] Eroare parsare interval: {e}")
                sys.exit(1)
        else:
            # Port individual
            try:
                port = int(part)
                if not (1 <= port <= 65535):
                    raise ValueError(f"Port în afara domeniului: {port}")
                ports.append(port)
            except ValueError as e:
                print(f"[!] Eroare parsare port: {e}")
                sys.exit(1)
    
    return sorted(set(ports))  # Eliminăm duplicate și sortăm


def parse_targets(target_str: str) -> List[str]:
    """
    Parsează specificația de ținte în listă de adrese IP.
    
    Suportă:
    - "192.168.1.1" → single host
    - "192.168.1.1-10" → range simplu (ultimul octet)
    - "192.168.1.0/24" → CIDR notation
    """
    targets: List[str] = []
    
    if "/" in target_str:
        # CIDR notation
        try:
            network = ipaddress.ip_network(target_str, strict=False)
            targets = [str(ip) for ip in network.hosts()]
        except ValueError as e:
            print(f"[!] CIDR invalid: {e}")
            sys.exit(1)
    
    elif "-" in target_str and target_str.count(".") == 3:
        # Range simplu (e.g., 192.168.1.1-10)
        try:
            base, range_part = target_str.rsplit(".", 1)
            if "-" in range_part:
                start, end = range_part.split("-")
                for i in range(int(start), int(end) + 1):
                    targets.append(f"{base}.{i}")
            else:
                targets.append(target_str)
        except ValueError:
            targets.append(target_str)
    else:
        targets.append(target_str)
    
    return targets


def scan_host(
    target: str,
    ports: List[int],
    timeout: float = 0.5,
    max_workers: int = 100,
    grab_banner: bool = True,
    verbose: bool = True
) -> HostScanResult:
    """
    Scanează toate porturile specificate pe un host.
    
    Utilizează ThreadPoolExecutor pentru paralelism eficient.
    """
    start_time = time.perf_counter()
    scan_timestamp = datetime.now().isoformat()
    
    open_ports: List[ScanResult] = []
    closed_count = 0
    filtered_count = 0
    
    if verbose:
        print(f"\n{Colors.BOLD}[*] Scanare {target} - {len(ports)} porturi{Colors.RESET}")
        print(f"    Timeout: {timeout}s | Workers: {max_workers}")
    
    # Scanăm porturile în paralel
    with ThreadPoolExecutor(max_workers=min(max_workers, len(ports))) as executor:
        futures = {
            executor.submit(tcp_connect_scan, target, port, timeout, grab_banner): port
            for port in ports
        }
        
        for future in as_completed(futures):
            result = future.result()
            
            if result.state == "open":
                open_ports.append(result)
                if verbose:
                    banner_info = f" | {result.banner[:50]}" if result.banner else ""
                    print(f"    {Colors.GREEN}[OPEN]{Colors.RESET} {result.port:5d}/tcp"
                          f"  {result.service or 'unknown':15s}{banner_info}")
            
            elif result.state == "closed":
                closed_count += 1
            
            elif result.state == "filtered":
                filtered_count += 1
    
    duration = time.perf_counter() - start_time
    
    # Sortăm porturile deschise
    open_ports.sort(key=lambda x: x.port)
    
    if verbose:
        print(f"\n{Colors.BOLD}[+] Rezultate pentru {target}:{Colors.RESET}")
        print(f"    Open: {Colors.GREEN}{len(open_ports)}{Colors.RESET} | "
              f"Closed: {closed_count} | Filtered: {filtered_count}")
        print(f"    Durată: {duration:.2f}s")
    
    return HostScanResult(
        target=target,
        scan_time=scan_timestamp,
        total_ports=len(ports),
        open_ports=open_ports,
        closed_ports=closed_count,
        filtered_ports=filtered_count,
        duration_seconds=round(duration, 2)
    )


def discover_hosts(
    targets: List[str],
    timeout: float = 0.5,
    max_workers: int = 50
) -> List[str]:
    """
    Descoperă hosturile active prin verificarea porturilor comune.
    """
    DISCOVERY_PORTS = [22, 80, 443, 445, 3389, 8080]
    alive_hosts: List[str] = []
    
    print(f"\n{Colors.BOLD}[*] Descoperire hosturi în rețea...{Colors.RESET}")
    print(f"    Ținte: {len(targets)} | Porturi test: {DISCOVERY_PORTS}")
    
    def check_host(host: str) -> Optional[str]:
        for port in DISCOVERY_PORTS:
            result = tcp_connect_scan(host, port, timeout, grab_banner=False)
            if result.state == "open":
                return host
        return None
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_host, host): host for host in targets}
        
        for future in as_completed(futures):
            host = future.result()
            if host:
                alive_hosts.append(host)
                print(f"    {Colors.GREEN}[ALIVE]{Colors.RESET} {host}")
    
    print(f"\n{Colors.BOLD}[+] Hosturi active: {len(alive_hosts)}/{len(targets)}{Colors.RESET}")
    return alive_hosts


# ==============================================================================
# EXPORT ȘI RAPORTARE
# ==============================================================================

def export_json(results: List[HostScanResult], output_path: str) -> None:
    """Exportă rezultatele în format JSON."""
    data = {
        "scan_report": {
            "generated_at": datetime.now().isoformat(),
            "tool": "S13 Port Scanner",
            "hosts": []
        }
    }
    
    for result in results:
        host_data = {
            "target": result.target,
            "scan_time": result.scan_time,
            "statistics": {
                "total_scanned": result.total_ports,
                "open": len(result.open_ports),
                "closed": result.closed_ports,
                "filtered": result.filtered_ports
            },
            "open_ports": [
                {
                    "port": p.port,
                    "service": p.service,
                    "banner": p.banner,
                    "response_ms": p.response_time_ms
                }
                for p in result.open_ports
            ],
            "duration_seconds": result.duration_seconds
        }
        data["scan_report"]["hosts"].append(host_data)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{Colors.GREEN}[✓] Rezultate exportate: {output_path}{Colors.RESET}")


# ==============================================================================
# MAIN
# ==============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scanner TCP pentru laborator S13",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  %(prog)s --target 10.0.13.11 --ports 1-1024
  %(prog)s --target 10.0.13.1-15 --mode discovery
  %(prog)s --target 10.0.13.11 --ports 22,80,443 --json-out scan.json
        """
    )
    
    parser.add_argument("--target", required=True,
                        help="Țintă: IP, range (192.168.1.1-10), sau CIDR (/24)")
    parser.add_argument("--ports", default="1-1024",
                        help="Porturi: 80, 1-1024, sau 22,80,443")
    parser.add_argument("--mode", choices=["scan", "discovery"], default="scan",
                        help="Mod: scan (porturi) sau discovery (hosturi active)")
    parser.add_argument("--timeout", type=float, default=0.5,
                        help="Timeout conexiune în secunde (default: 0.5)")
    parser.add_argument("--workers", type=int, default=100,
                        help="Număr threaduri paralele (default: 100)")
    parser.add_argument("--no-banner", action="store_true",
                        help="Nu încerca să citească banner-ul serviciului")
    parser.add_argument("--json-out", metavar="FILE",
                        help="Export rezultate în fișier JSON")
    parser.add_argument("--quiet", action="store_true",
                        help="Output minimal")
    
    args = parser.parse_args()
    
    # Banner
    if not args.quiet:
        print(f"\n{Colors.CYAN}{'='*60}")
        print("  S13 - Scanner TCP pentru laborator")
        print("  ATENȚIE: Doar pentru mediu controlat!")
        print(f"{'='*60}{Colors.RESET}")
    
    # Parsăm țintele
    targets = parse_targets(args.target)
    
    if args.mode == "discovery":
        # Mod descoperire hosturi
        alive_hosts = discover_hosts(targets, args.timeout, args.workers)
        
        if args.json_out:
            with open(args.json_out, "w") as f:
                json.dump({"alive_hosts": alive_hosts}, f, indent=2)
    
    else:
        # Mod scanare porturi
        ports = parse_ports(args.ports)
        results: List[HostScanResult] = []
        
        for target in targets:
            result = scan_host(
                target=target,
                ports=ports,
                timeout=args.timeout,
                max_workers=args.workers,
                grab_banner=not args.no_banner,
                verbose=not args.quiet
            )
            results.append(result)
        
        # Export JSON dacă cerut
        if args.json_out:
            export_json(results, args.json_out)
    
    print()


if __name__ == "__main__":
    main()
