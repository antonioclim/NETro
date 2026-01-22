#!/usr/bin/env python3
"""
Exercițiul 5.01 – Analiză CIDR și Subnetting FLSM
=================================================
CLI pentru calculul parametrilor de rețea și împărțirea în subrețele egale.

Utilizare:
    python ex_5_01_cidr_flsm.py analyze 192.168.10.14/26 [--verbose] [--json]
    python ex_5_01_cidr_flsm.py flsm 192.168.100.0/24 4
    python ex_5_01_cidr_flsm.py binary 192.168.10.14

Autor: Material didactic ASE-CSIE
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════════════════
# SETUP_ENVIRONMENT
# ═══════════════════════════════════════════════════════════════════════════════
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
    analyze_ipv4_interface,
    flsm_split,
    ipv4_host_range,
    ip_to_binary,
    ip_to_dotted_binary,
    prefix_to_netmask,
    netmask_to_prefix,
)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER_UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════
class Colors:
    """Coduri de culoare ANSI pentru output în terminal."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def colorize(text: str, color: str) -> str:
    """Aplică culoare dacă stdout e terminal."""
    if sys.stdout.isatty():
        return f"{color}{text}{Colors.END}"
    return text


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND_ANALYZE
# ═══════════════════════════════════════════════════════════════════════════════
def cmd_analyze(target: str, verbose: bool = False, as_json: bool = False) -> int:
    """Analizează o adresă IPv4 cu prefix CIDR."""
    
    # --- VALIDATE_INPUT ---
    try:
        info = analyze_ipv4_interface(target)
    except ValueError as e:
        print(colorize(f"Eroare: {e}", Colors.RED), file=sys.stderr)
        return 1
    
    # --- BUILD_RESULT_STRUCTURE ---
    payload = {
        "input": target,
        "address": str(info.address),
        "address_type": info.address_type,
        "network": str(info.network.network_address),
        "prefix": info.network.prefixlen,
        "netmask": str(info.netmask),
        "wildcard": str(info.wildcard),
        "broadcast": str(info.broadcast),
        "total_addresses": info.total_addresses,
        "usable_hosts": info.usable_hosts,
        "first_host": str(info.first_host) if info.first_host else None,
        "last_host": str(info.last_host) if info.last_host else None,
        "is_private": info.is_private,
    }
    
    # --- OUTPUT_JSON ---
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0
    
    # --- FORMAT_HUMAN_OUTPUT ---
    print()
    print(colorize("═" * 50, Colors.BLUE))
    print(colorize("  Analiză CIDR IPv4", Colors.BOLD))
    print(colorize("═" * 50, Colors.BLUE))
    print()
    
    print(f"  {colorize('Input:', Colors.CYAN):30} {target}")
    print(f"  {colorize('Adresă IP:', Colors.CYAN):30} {info.address}")
    print(f"  {colorize('Tip adresă:', Colors.CYAN):30} {colorize(info.address_type.upper(), Colors.YELLOW)}")
    print()
    
    print(f"  {colorize('Adresă de rețea:', Colors.CYAN):30} {info.network.network_address}/{info.network.prefixlen}")
    print(f"  {colorize('Mască de rețea:', Colors.CYAN):30} {info.netmask}")
    print(f"  {colorize('Wildcard mask:', Colors.CYAN):30} {info.wildcard}")
    print(f"  {colorize('Adresă broadcast:', Colors.CYAN):30} {info.broadcast}")
    print()
    
    print(f"  {colorize('Total adrese:', Colors.CYAN):30} {info.total_addresses}")
    print(f"  {colorize('Hosturi utilizabile:', Colors.CYAN):30} {colorize(str(info.usable_hosts), Colors.GREEN)}")
    print(f"  {colorize('Primul host:', Colors.CYAN):30} {info.first_host or 'N/A'}")
    print(f"  {colorize('Ultimul host:', Colors.CYAN):30} {info.last_host or 'N/A'}")
    print()
    
    print(f"  {colorize('Adresă privată:', Colors.CYAN):30} {'Da' if info.is_private else 'Nu'}")
    
    # --- VERBOSE_BINARY_OUTPUT ---
    if verbose:
        print()
        print(colorize("─" * 50, Colors.BLUE))
        print(colorize("  Reprezentare binară", Colors.BOLD))
        print(colorize("─" * 50, Colors.BLUE))
        print()
        
        addr_bin = ip_to_dotted_binary(str(info.address))
        mask_bin = ip_to_dotted_binary(str(info.netmask))
        net_bin = ip_to_dotted_binary(str(info.network.network_address))
        bcast_bin = ip_to_dotted_binary(str(info.broadcast))
        
        prefix = info.network.prefixlen
        
        print(f"  {colorize('IP (binar):', Colors.CYAN):30}")
        print(f"    {colorize(addr_bin[:prefix], Colors.GREEN)}{addr_bin[prefix:]}")
        print(f"    {'─' * prefix}{'^' * (35 - prefix)} partea de host")
        print()
        
        print(f"  {colorize('Mască (binar):', Colors.CYAN):30}")
        print(f"    {mask_bin}")
        print()
        
        print(f"  {colorize('Rețea (binar):', Colors.CYAN):30}")
        print(f"    {net_bin}")
        print()
        
        print(f"  {colorize('Broadcast (binar):', Colors.CYAN):30}")
        print(f"    {bcast_bin}")
        print()
        
        # --- EXPLAIN_CALCULATION ---
        print(colorize("─" * 50, Colors.BLUE))
        print(colorize("  Explicație calcul", Colors.BOLD))
        print(colorize("─" * 50, Colors.BLUE))
        print()
        
        host_bits = 32 - prefix
        print(f"  • Prefix /{prefix} = {prefix} biți pentru rețea, {host_bits} biți pentru host")
        print(f"  • Total adrese = 2^{host_bits} = {2**host_bits}")
        print(f"  • Hosturi utilizabile = 2^{host_bits} - 2 = {2**host_bits - 2}")
        print(f"  • Adresa de rețea: toți biții host = 0")
        print(f"  • Adresa broadcast: toți biții host = 1")
    
    print()
    return 0


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND_FLSM
# ═══════════════════════════════════════════════════════════════════════════════
def cmd_flsm(base: str, n_subnets: int, as_json: bool = False) -> int:
    """Împarte o rețea în N subrețele egale."""
    
    # --- VALIDATE_AND_SPLIT ---
    try:
        subnets = flsm_split(base, n_subnets)
    except ValueError as e:
        print(colorize(f"Eroare: {e}", Colors.RED), file=sys.stderr)
        return 1
    
    # --- OUTPUT_JSON ---
    if as_json:
        result = []
        for subnet in subnets:
            first, last, usable = ipv4_host_range(subnet)
            result.append({
                "network": str(subnet.network_address),
                "prefix": subnet.prefixlen,
                "cidr": str(subnet),
                "broadcast": str(subnet.broadcast_address),
                "usable_hosts": usable,
                "first_host": str(first) if first else None,
                "last_host": str(last) if last else None,
            })
        print(json.dumps({"base": base, "num_subnets": n_subnets, "subnets": result}, indent=2))
        return 0
    
    # --- CALCULATE_PARAMETERS ---
    import ipaddress
    base_net = ipaddress.ip_network(base, strict=True)
    bits_added = n_subnets.bit_length() - 1
    new_prefix = base_net.prefixlen + bits_added
    
    # --- FORMAT_HUMAN_OUTPUT ---
    print()
    print(colorize("═" * 60, Colors.BLUE))
    print(colorize("  Subnetting FLSM (Fixed Length Subnet Mask)", Colors.BOLD))
    print(colorize("═" * 60, Colors.BLUE))
    print()
    
    print(f"  {colorize('Rețea de bază:', Colors.CYAN):30} {base}")
    print(f"  {colorize('Număr subrețele:', Colors.CYAN):30} {n_subnets}")
    print(f"  {colorize('Biți împrumutați:', Colors.CYAN):30} {bits_added}")
    print(f"  {colorize('Prefix nou:', Colors.CYAN):30} /{new_prefix}")
    print(f"  {colorize('Increment:', Colors.CYAN):30} {2**(32-new_prefix)} adrese")
    print()
    
    # --- LIST_SUBNETS ---
    print(colorize("─" * 60, Colors.BLUE))
    print(f"  {'Nr.':>4}  {'Subrețea':<20} {'Broadcast':<18} {'Hosturi':<10} {'Interval'}")
    print(colorize("─" * 60, Colors.BLUE))
    
    for i, subnet in enumerate(subnets, 1):
        first, last, usable = ipv4_host_range(subnet)
        interval = f"{first}..{last}" if first and last else "N/A"
        print(f"  {i:>4}. {str(subnet):<20} {str(subnet.broadcast_address):<18} {usable:<10} {interval}")
    
    print(colorize("─" * 60, Colors.BLUE))
    print()
    
    # --- SUMMARY ---
    total_usable = sum(ipv4_host_range(s)[2] for s in subnets)
    print(f"  {colorize('Total hosturi utilizabile:', Colors.GREEN)} {total_usable}")
    print()
    
    return 0


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND_BINARY
# ═══════════════════════════════════════════════════════════════════════════════
def cmd_binary(ip: str) -> int:
    """Afișează reprezentarea binară a unei adrese IP."""
    
    # --- VALIDATE_INPUT ---
    try:
        import ipaddress
        addr = ipaddress.IPv4Address(ip)
    except ValueError as e:
        print(colorize(f"Eroare: {e}", Colors.RED), file=sys.stderr)
        return 1
    
    # --- CONVERT_TO_BINARY ---
    binary = ip_to_binary(ip)
    dotted = ip_to_dotted_binary(ip)
    
    # --- FORMAT_OUTPUT ---
    print()
    print(colorize("═" * 50, Colors.BLUE))
    print(colorize("  Conversie IP → Binar", Colors.BOLD))
    print(colorize("═" * 50, Colors.BLUE))
    print()
    
    print(f"  {colorize('IP zecimal:', Colors.CYAN):25} {ip}")
    print(f"  {colorize('Binar complet:', Colors.CYAN):25} {binary}")
    print(f"  {colorize('Binar cu punct:', Colors.CYAN):25} {dotted}")
    print()
    
    # --- SHOW_OCTETS ---
    octets = ip.split('.')
    print(colorize("  Conversie pe octeți:", Colors.CYAN))
    for i, octet in enumerate(octets):
        oct_bin = bin(int(octet))[2:].zfill(8)
        print(f"    Octet {i+1}: {octet:>3} → {oct_bin}")
    print()
    
    return 0


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND_QUIZ
# ═══════════════════════════════════════════════════════════════════════════════
def cmd_quiz() -> int:
    """Generează o întrebare quiz rapidă."""
    import random
    
    # --- GENERATE_RANDOM_ADDRESS ---
    octets = [random.randint(1, 254) for _ in range(4)]
    prefix = random.choice([24, 25, 26, 27, 28, 29, 30])
    
    ip = '.'.join(map(str, octets))
    cidr = f"{ip}/{prefix}"
    
    # --- DISPLAY_QUESTION ---
    print()
    print(colorize("═" * 50, Colors.YELLOW))
    print(colorize("  Quiz rapid: Analiză CIDR", Colors.BOLD))
    print(colorize("═" * 50, Colors.YELLOW))
    print()
    print(f"  Adresă: {colorize(cidr, Colors.GREEN)}")
    print()
    print("  Calculează:")
    print("  1. Adresa de rețea")
    print("  2. Adresa de broadcast")
    print("  3. Numărul de hosturi utilizabile")
    print("  4. Primul și ultimul host utilizabil")
    print()
    
    # --- WAIT_AND_REVEAL ---
    input(colorize("  Apasă Enter pentru a vedea răspunsul...", Colors.CYAN))
    
    return cmd_analyze(cidr, verbose=False, as_json=False)


# ═══════════════════════════════════════════════════════════════════════════════
# ARGUMENT_PARSER
# ═══════════════════════════════════════════════════════════════════════════════
def build_parser() -> argparse.ArgumentParser:
    """Construiește parser-ul de argumente."""
    parser = argparse.ArgumentParser(
        description="Exercițiul 5.01 – Analiză CIDR și Subnetting FLSM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  %(prog)s analyze 192.168.10.14/26           Analizează adresa
  %(prog)s analyze 192.168.10.14/26 --verbose Cu explicații detaliate
  %(prog)s analyze 192.168.10.14/26 --json    Output JSON
  %(prog)s flsm 192.168.100.0/24 4            Împarte în 4 subrețele
  %(prog)s flsm 10.0.0.0/24 8                 Împarte în 8 subrețele
  %(prog)s binary 192.168.1.1                 Conversie binar
  %(prog)s quiz                               Quiz rapid aleator
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Subcomanda analyze
    p_analyze = subparsers.add_parser(
        "analyze",
        help="Analizează o adresă IPv4 cu prefix CIDR"
    )
    p_analyze.add_argument(
        "target",
        help="Adresă IPv4 cu prefix (ex: 192.168.10.14/26)"
    )
    p_analyze.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Afișează explicații detaliate și reprezentare binară"
    )
    p_analyze.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output în format JSON"
    )
    
    # Subcomanda flsm
    p_flsm = subparsers.add_parser(
        "flsm",
        help="Împarte o rețea în N subrețele egale (FLSM)"
    )
    p_flsm.add_argument(
        "base",
        help="Rețea de bază în format CIDR (ex: 192.168.100.0/24)"
    )
    p_flsm.add_argument(
        "n",
        type=int,
        help="Număr de subrețele (putere a lui 2)"
    )
    p_flsm.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output în format JSON"
    )
    
    # Subcomanda binary
    p_binary = subparsers.add_parser(
        "binary",
        help="Afișează reprezentarea binară a unei adrese IP"
    )
    p_binary.add_argument(
        "ip",
        help="Adresă IPv4 (ex: 192.168.1.1)"
    )
    
    # Subcomanda quiz
    subparsers.add_parser(
        "quiz",
        help="Generează o întrebare quiz rapidă"
    )
    
    return parser


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN_ENTRY_POINT
# ═══════════════════════════════════════════════════════════════════════════════
def main(argv: Optional[List[str]] = None) -> int:
    """Funcția principală."""
    parser = build_parser()
    args = parser.parse_args(argv)
    
    if args.command == "analyze":
        return cmd_analyze(args.target, args.verbose, args.json)
    elif args.command == "flsm":
        return cmd_flsm(args.base, args.n, args.json)
    elif args.command == "binary":
        return cmd_binary(args.ip)
    elif args.command == "quiz":
        return cmd_quiz()
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
