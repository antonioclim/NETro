#!/usr/bin/env python3
"""
Exercițiul 5.02 – VLSM și Utilitare IPv6
========================================
CLI pentru alocare VLSM și operațiuni pe adrese IPv6.

Utilizare:
    python ex_5_02_vlsm_ipv6.py vlsm 172.16.0.0/24 60 20 10 2
    python ex_5_02_vlsm_ipv6.py ipv6 2001:0db8:0000:0000:0000:0000:0000:0001
    python ex_5_02_vlsm_ipv6.py ipv6-expand 2001:db8::1
    python ex_5_02_vlsm_ipv6.py ipv6-subnets 2001:db8:10::/48 64 5

Autor: Material didactic ASE-CSIE
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

# Import utilitar local
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python.utils.net_utils import (
    vlsm_allocate,
    ipv6_compress,
    ipv6_expand,
    ipv6_info,
    ipv6_subnets_from_prefix,
    prefix_for_hosts,
)


# Coduri de culoare ANSI
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def colorize(text: str, color: str) -> str:
    """Aplică culoare dacă stdout e terminal."""
    if sys.stdout.isatty():
        return f"{color}{text}{Colors.END}"
    return text


def cmd_vlsm(base: str, requirements: List[int], as_json: bool = False) -> int:
    """Alocă subrețele cu VLSM."""
    try:
        allocations = vlsm_allocate(base, requirements)
    except ValueError as e:
        print(colorize(f"Eroare: {e}", Colors.RED), file=sys.stderr)
        return 1
    
    if as_json:
        result = []
        for alloc in allocations:
            result.append({
                "required_hosts": alloc.required_hosts,
                "prefix": alloc.allocated_prefix,
                "network": str(alloc.network),
                "gateway": str(alloc.gateway),
                "broadcast": str(alloc.broadcast),
                "usable_hosts": alloc.usable_hosts,
                "efficiency_percent": round(alloc.efficiency, 2),
            })
        output = {
            "base_network": base,
            "requirements": requirements,
            "allocations": result,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 0
    
    # Output formatat
    import ipaddress
    base_net = ipaddress.ip_network(base, strict=True)
    
    print()
    print(colorize("═" * 70, Colors.BLUE))
    print(colorize("  Alocare VLSM (Variable Length Subnet Mask)", Colors.BOLD))
    print(colorize("═" * 70, Colors.BLUE))
    print()
    
    print(f"  {colorize('Rețea disponibilă:', Colors.CYAN):30} {base}")
    print(f"  {colorize('Total adrese:', Colors.CYAN):30} {base_net.num_addresses}")
    print(f"  {colorize('Cerințe hosturi:', Colors.CYAN):30} {', '.join(map(str, requirements))}")
    print()
    
    # Explicație algoritmului
    print(colorize("─" * 70, Colors.BLUE))
    print(colorize("  Algoritmul VLSM:", Colors.BOLD))
    print(colorize("─" * 70, Colors.BLUE))
    print("  1. Sortăm cerințele descrescător")
    print("  2. Pentru fiecare cerință, calculăm prefixul minim necesar")
    print("  3. Aliniem adresa de start la granița blocului")
    print("  4. Alocăm și avansăm cursorul")
    print()
    
    # Tabel alocare
    print(colorize("─" * 70, Colors.BLUE))
    print(f"  {'#':>3}  {'Necesar':>8}  {'Prefix':>7}  {'Subrețea':<20} {'Gateway':<16} {'Eficiență'}")
    print(colorize("─" * 70, Colors.BLUE))
    
    total_required = 0
    total_allocated = 0
    
    for i, alloc in enumerate(allocations, 1):
        efficiency_color = Colors.GREEN if alloc.efficiency > 75 else Colors.YELLOW if alloc.efficiency > 50 else Colors.RED
        eff_str = colorize(f"{alloc.efficiency:5.1f}%", efficiency_color)
        
        print(f"  {i:>3}  {alloc.required_hosts:>8}  /{alloc.allocated_prefix:<6}  "
              f"{str(alloc.network):<20} {str(alloc.gateway):<16} {eff_str}")
        
        total_required += alloc.required_hosts
        total_allocated += alloc.usable_hosts
    
    print(colorize("─" * 70, Colors.BLUE))
    
    # Rezumat eficiență
    print()
    total_used = sum(alloc.network.num_addresses for alloc in allocations)
    remaining = base_net.num_addresses - total_used
    overall_efficiency = (total_required / total_allocated * 100) if total_allocated > 0 else 0
    
    print(f"  {colorize('Rezumat:', Colors.BOLD)}")
    print(f"    Total hosturi necesare:   {total_required}")
    print(f"    Total hosturi alocate:    {total_allocated}")
    print(f"    Eficiență globală:        {colorize(f'{overall_efficiency:.1f}%', Colors.GREEN)}")
    print(f"    Adrese rămase libere:     {remaining}")
    
    if remaining > 0:
        import ipaddress
        # Găsim ultima adresă alocată
        last_alloc = max(allocations, key=lambda a: int(a.network.broadcast_address))
        next_addr = int(last_alloc.network.broadcast_address) + 1
        if next_addr <= int(base_net.broadcast_address):
            print(f"    Prima adresă liberă:      {ipaddress.IPv4Address(next_addr)}")
    
    print()
    return 0


def cmd_ipv6_compress(address: str) -> int:
    """Comprimă o adresă IPv6."""
    try:
        info = ipv6_info(address)
    except ValueError as e:
        print(colorize(f"Eroare: {e}", Colors.RED), file=sys.stderr)
        return 1
    
    print()
    print(colorize("═" * 60, Colors.BLUE))
    print(colorize("  Analiză Adresă IPv6", Colors.BOLD))
    print(colorize("═" * 60, Colors.BLUE))
    print()
    
    print(f"  {colorize('Input:', Colors.CYAN):30} {address}")
    print(f"  {colorize('Forma completă:', Colors.CYAN):30} {info.full_form}")
    print(f"  {colorize('Forma comprimată:', Colors.CYAN):30} {colorize(info.compressed, Colors.GREEN)}")
    print()
    
    print(f"  {colorize('Tip adresă:', Colors.CYAN):30} {info.address_type}")
    print(f"  {colorize('Scope:', Colors.CYAN):30} {info.scope}")
    
    if info.network:
        print(f"  {colorize('Rețea:', Colors.CYAN):30} {info.network}")
    
    print()
    
    # Explicație comprimare
    print(colorize("─" * 60, Colors.BLUE))
    print(colorize("  Reguli de comprimare IPv6:", Colors.BOLD))
    print(colorize("─" * 60, Colors.BLUE))
    print("  1. Eliminăm zerourile din stânga fiecărui grup")
    print("  2. Folosim :: pentru cea mai lungă secvență de zerouri")
    print("  3. :: poate fi folosit o singură dată")
    print()
    
    return 0


def cmd_ipv6_expand(address: str) -> int:
    """Expandează o adresă IPv6."""
    try:
        expanded = ipv6_expand(address)
    except ValueError as e:
        print(colorize(f"Eroare: {e}", Colors.RED), file=sys.stderr)
        return 1
    
    print()
    print(colorize("═" * 60, Colors.BLUE))
    print(colorize("  Expandare Adresă IPv6", Colors.BOLD))
    print(colorize("═" * 60, Colors.BLUE))
    print()
    
    print(f"  {colorize('Input (comprimat):', Colors.CYAN):30} {address}")
    print(f"  {colorize('Output (expandat):', Colors.CYAN):30} {colorize(expanded, Colors.GREEN)}")
    print()
    
    # Descompunem în grupuri
    groups = expanded.split(':')
    print(colorize("  Grupuri hexazecimale:", Colors.CYAN))
    for i, group in enumerate(groups):
        decimal_val = int(group, 16)
        print(f"    Grup {i+1}: {group} = {decimal_val} (zecimal)")
    print()
    
    return 0


def cmd_ipv6_subnets(base: str, target_prefix: int, count: int) -> int:
    """Generează subrețele IPv6."""
    try:
        subnets = ipv6_subnets_from_prefix(base, target_prefix, count)
    except ValueError as e:
        print(colorize(f"Eroare: {e}", Colors.RED), file=sys.stderr)
        return 1
    
    import ipaddress
    base_net = ipaddress.ip_network(base, strict=True)
    total_possible = 2 ** (target_prefix - base_net.prefixlen)
    
    print()
    print(colorize("═" * 70, Colors.BLUE))
    print(colorize("  Subnetting IPv6", Colors.BOLD))
    print(colorize("═" * 70, Colors.BLUE))
    print()
    
    print(f"  {colorize('Prefix de bază:', Colors.CYAN):30} {base}")
    print(f"  {colorize('Prefix țintă:', Colors.CYAN):30} /{target_prefix}")
    print(f"  {colorize('Subrețele solicitate:', Colors.CYAN):30} {count}")
    print(f"  {colorize('Total subrețele posibile:', Colors.CYAN):30} {total_possible:,}")
    print()
    
    print(colorize("─" * 70, Colors.BLUE))
    print(f"  {'#':>3}  {'Prefix subrețea':<45} {'Gateway sugerat'}")
    print(colorize("─" * 70, Colors.BLUE))
    
    for i, subnet in enumerate(subnets, 1):
        # Gateway = prima adresă (::1)
        gateway = subnet.network_address + 1
        print(f"  {i:>3}  {str(subnet):<45} {gateway}")
    
    print(colorize("─" * 70, Colors.BLUE))
    print()
    
    # Note despre IPv6 subnetting
    if target_prefix == 64:
        print(colorize("  Notă:", Colors.YELLOW))
        print("  • /64 este lungimea standard pentru LAN-uri (SLAAC)")
        print("  • Interface ID ocupă ultimii 64 de biți")
        print("  • Fiecare subrețea /64 poate avea 2^64 adrese")
    
    print()
    return 0


def cmd_ipv6_types() -> int:
    """Afișează tipurile de adrese IPv6."""
    print()
    print(colorize("═" * 65, Colors.BLUE))
    print(colorize("  Tipuri de Adrese IPv6", Colors.BOLD))
    print(colorize("═" * 65, Colors.BLUE))
    print()
    
    types = [
        ("::", "Adresă nulă (unspecified)", "Folosită când nu avem adresă"),
        ("::1", "Loopback", "Echivalent 127.0.0.1"),
        ("fe80::/10", "Link-local", "Comunicare locală, auto-configurată"),
        ("fc00::/7", "Unique local", "Echivalent RFC 1918 (adrese private)"),
        ("2000::/3", "Global unicast", "Adrese rutabile pe Internet"),
        ("ff00::/8", "Multicast", "Comunicare către grupuri"),
    ]
    
    print(f"  {'Prefix':<15} {'Tip':<20} {'Descriere'}")
    print(colorize("─" * 65, Colors.BLUE))
    
    for prefix, typ, desc in types:
        print(f"  {colorize(prefix, Colors.GREEN):<24} {typ:<20} {desc}")
    
    print()
    print(colorize("  Exemple practice:", Colors.YELLOW))
    print("  • fe80::1             Link-local pe interfață")
    print("  • 2001:db8::1         Global unicast (documentație)")
    print("  • ff02::1             All-nodes multicast")
    print("  • ff02::2             All-routers multicast")
    print()
    
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construiește parser-ul de argumente."""
    parser = argparse.ArgumentParser(
        description="Exercițiul 5.02 – VLSM și Utilitare IPv6",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  %(prog)s vlsm 172.16.0.0/24 60 20 10 2       Alocare VLSM
  %(prog)s vlsm 10.0.0.0/22 200 100 50 2 2    Pentru organizație mare
  
  %(prog)s ipv6 2001:0db8:0000:0000:0000:0000:0000:0001   Comprimare IPv6
  %(prog)s ipv6-expand 2001:db8::1                        Expandare IPv6
  %(prog)s ipv6-subnets 2001:db8:10::/48 64 10            Generare subrețele
  %(prog)s ipv6-types                                      Referință tipuri
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Subcomanda vlsm
    p_vlsm = subparsers.add_parser(
        "vlsm",
        help="Alocă subrețele cu VLSM pentru o listă de cerințe"
    )
    p_vlsm.add_argument(
        "base",
        help="Rețea disponibilă în format CIDR (ex: 172.16.0.0/24)"
    )
    p_vlsm.add_argument(
        "requirements",
        type=int,
        nargs="+",
        help="Lista cerințelor de hosturi (ex: 60 20 10 2)"
    )
    p_vlsm.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output în format JSON"
    )
    
    # Subcomanda ipv6 (comprimare)
    p_ipv6 = subparsers.add_parser(
        "ipv6",
        help="Analizează și comprimă o adresă IPv6"
    )
    p_ipv6.add_argument(
        "address",
        help="Adresă IPv6 în orice format"
    )
    
    # Subcomanda ipv6-expand
    p_expand = subparsers.add_parser(
        "ipv6-expand",
        help="Expandează o adresă IPv6 la forma completă"
    )
    p_expand.add_argument(
        "address",
        help="Adresă IPv6 comprimată (ex: 2001:db8::1)"
    )
    
    # Subcomanda ipv6-subnets
    p_subnets = subparsers.add_parser(
        "ipv6-subnets",
        help="Generează subrețele IPv6 din un prefix"
    )
    p_subnets.add_argument(
        "base",
        help="Prefix de bază (ex: 2001:db8:10::/48)"
    )
    p_subnets.add_argument(
        "target_prefix",
        type=int,
        help="Lungimea prefixului țintă (ex: 64)"
    )
    p_subnets.add_argument(
        "count",
        type=int,
        help="Numărul de subrețele de generat"
    )
    
    # Subcomanda ipv6-types
    subparsers.add_parser(
        "ipv6-types",
        help="Afișează tipurile de adrese IPv6"
    )
    
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Funcția principală."""
    parser = build_parser()
    args = parser.parse_args(argv)
    
    if args.command == "vlsm":
        return cmd_vlsm(args.base, args.requirements, args.json)
    elif args.command == "ipv6":
        return cmd_ipv6_compress(args.address)
    elif args.command == "ipv6-expand":
        return cmd_ipv6_expand(args.address)
    elif args.command == "ipv6-subnets":
        return cmd_ipv6_subnets(args.base, args.target_prefix, args.count)
    elif args.command == "ipv6-types":
        return cmd_ipv6_types()
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
