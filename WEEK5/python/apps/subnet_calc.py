#!/usr/bin/env python3
"""
Subnet Calculator — Calculator interactiv pentru subrețele
===========================================================
Instrument vizual pentru analiza și planificarea subrețelelor IPv4.

Utilizare:
    python subnet_calc.py                     # Mod interactiv
    python subnet_calc.py 192.168.1.0/24      # Analiză directă
    python subnet_calc.py --visual 10.0.0.0/8 # Cu reprezentare vizuală

Autor: Material didactic ASE-CSIE
"""

from __future__ import annotations

import argparse
import ipaddress
import sys
from typing import Optional

# Culori ANSI
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @classmethod
    def disable(cls):
        """Dezactivează culorile pentru output non-terminal."""
        for attr in dir(cls):
            if not attr.startswith('_') and attr.isupper():
                setattr(cls, attr, '')


def analyze_network(cidr: str, visual: bool = False) -> dict:
    """
    Analizează o rețea în notație CIDR și returnează toți parametrii.
    """
    try:
        interface = ipaddress.ip_interface(cidr)
        network = interface.network
    except ValueError as e:
        raise ValueError(f"Adresă invalidă: {cidr}") from e
    
    # Calculăm parametrii
    netmask = network.netmask
    wildcard = network.hostmask
    network_addr = network.network_address
    broadcast = network.broadcast_address
    prefix = network.prefixlen
    
    # Număr de gazde
    num_addresses = network.num_addresses
    num_hosts = max(0, num_addresses - 2)  # Excludem rețea și broadcast
    
    # Prima și ultima gazdă
    hosts = list(network.hosts())
    first_host = hosts[0] if hosts else None
    last_host = hosts[-1] if hosts else None
    
    # Clasa tradițională (pentru referință istorică)
    first_octet = int(str(network_addr).split('.')[0])
    if first_octet < 128:
        ip_class = 'A'
    elif first_octet < 192:
        ip_class = 'B'
    elif first_octet < 224:
        ip_class = 'C'
    elif first_octet < 240:
        ip_class = 'D (Multicast)'
    else:
        ip_class = 'E (Rezervată)'
    
    # Tip adresă
    if network.is_private:
        addr_type = 'Privată (RFC 1918)'
    elif network.is_loopback:
        addr_type = 'Loopback'
    elif network.is_link_local:
        addr_type = 'Link-Local'
    elif network.is_multicast:
        addr_type = 'Multicast'
    elif network.is_reserved:
        addr_type = 'Rezervată'
    else:
        addr_type = 'Publică (Rutabilă)'
    
    result = {
        'input': cidr,
        'ip': str(interface.ip),
        'network': str(network_addr),
        'netmask': str(netmask),
        'wildcard': str(wildcard),
        'broadcast': str(broadcast),
        'prefix': prefix,
        'first_host': str(first_host) if first_host else 'N/A',
        'last_host': str(last_host) if last_host else 'N/A',
        'num_addresses': num_addresses,
        'num_hosts': num_hosts,
        'ip_class': ip_class,
        'addr_type': addr_type,
    }
    
    # Reprezentare binară (opțional)
    if visual:
        result['binary'] = {
            'ip': ip_to_binary(str(interface.ip)),
            'netmask': ip_to_binary(str(netmask)),
            'network': ip_to_binary(str(network_addr)),
            'broadcast': ip_to_binary(str(broadcast)),
        }
    
    return result


def ip_to_binary(ip: str) -> str:
    """Convertește IP în reprezentare binară cu puncte."""
    octets = ip.split('.')
    return '.'.join(format(int(o), '08b') for o in octets)


def print_analysis(result: dict, visual: bool = False):
    """Afișează rezultatul analizei în format frumos."""
    c = Colors
    
    print()
    print(f"{c.BOLD}{c.CYAN}╔══════════════════════════════════════════════════════════════════╗{c.END}")
    print(f"{c.BOLD}{c.CYAN}║{c.END}           {c.BOLD}SUBNET CALCULATOR — Rezultate Analiză{c.END}               {c.BOLD}{c.CYAN}║{c.END}")
    print(f"{c.BOLD}{c.CYAN}╠══════════════════════════════════════════════════════════════════╣{c.END}")
    
    fields = [
        ('Input', result['input']),
        ('Adresă IP', result['ip']),
        ('Prefix', f"/{result['prefix']}"),
        ('Mască rețea', result['netmask']),
        ('Wildcard', result['wildcard']),
        ('Adresă rețea', result['network']),
        ('Broadcast', result['broadcast']),
        ('Prima gazdă', result['first_host']),
        ('Ultima gazdă', result['last_host']),
        ('Adrese totale', f"{result['num_addresses']:,}"),
        ('Gazde utilizabile', f"{result['num_hosts']:,}"),
        ('Clasă IP', result['ip_class']),
        ('Tip adresă', result['addr_type']),
    ]
    
    for label, value in fields:
        print(f"{c.BOLD}{c.CYAN}║{c.END}  {c.YELLOW}{label:18}{c.END} {c.GREEN}{value}{c.END}")
    
    print(f"{c.BOLD}{c.CYAN}╚══════════════════════════════════════════════════════════════════╝{c.END}")
    
    # Reprezentare binară
    if visual and 'binary' in result:
        print()
        print(f"{c.BOLD}Reprezentare binară:{c.END}")
        print(f"  IP:        {result['binary']['ip']}")
        print(f"  Mască:     {result['binary']['netmask']}")
        print(f"  Rețea:     {result['binary']['network']}")
        print(f"  Broadcast: {result['binary']['broadcast']}")
        
        # Vizualizare grafică a biților
        prefix = result['prefix']
        print()
        print(f"{c.BOLD}Structura biților (prefix /{prefix}):{c.END}")
        print(f"  {'█' * prefix}{'░' * (32 - prefix)}")
        print(f"  {c.GREEN}← Rețea ({prefix} biți){c.END}  {c.YELLOW}Host ({32 - prefix} biți) →{c.END}")
    
    print()


def interactive_mode():
    """Mod interactiv cu meniu."""
    c = Colors
    
    print()
    print(f"{c.BOLD}{c.CYAN}═══════════════════════════════════════════════════════════════════{c.END}")
    print(f"{c.BOLD}        SUBNET CALCULATOR — Mod Interactiv{c.END}")
    print(f"{c.BOLD}{c.CYAN}═══════════════════════════════════════════════════════════════════{c.END}")
    print()
    print("Comenzi disponibile:")
    print("  • Introduceți o adresă CIDR (ex: 192.168.1.100/24)")
    print("  • 'prefix N' — Informații despre prefixul /N")
    print("  • 'hosts N' — Ce prefix pentru N gazde")
    print("  • 'help' — Afișare ajutor")
    print("  • 'quit' sau 'exit' — Ieșire")
    print()
    
    while True:
        try:
            user_input = input(f"{c.BOLD}subnet>{c.END} ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nLa revedere!")
            break
        
        if not user_input:
            continue
        
        cmd = user_input.lower()
        
        if cmd in ('quit', 'exit', 'q'):
            print("La revedere!")
            break
        
        elif cmd == 'help':
            print("\nExemple:")
            print("  192.168.1.0/24    — Analiză rețea")
            print("  10.0.0.1/8        — Analiză cu IP specific")
            print("  prefix 24         — Info despre /24")
            print("  hosts 500         — Prefix pentru 500 gazde")
            print()
        
        elif cmd.startswith('prefix '):
            try:
                n = int(cmd.split()[1])
                if 0 <= n <= 32:
                    hosts = max(0, 2 ** (32 - n) - 2)
                    print(f"\n  Prefix /{n}:")
                    print(f"    Mască: {ipaddress.IPv4Address(2**32 - 2**(32-n))}")
                    print(f"    Adrese totale: {2 ** (32 - n):,}")
                    print(f"    Gazde utilizabile: {hosts:,}")
                    print()
                else:
                    print("  Prefix invalid (0-32)")
            except (ValueError, IndexError):
                print("  Utilizare: prefix N (ex: prefix 24)")
        
        elif cmd.startswith('hosts '):
            try:
                n = int(cmd.split()[1])
                if n < 1:
                    print("  Numărul de gazde trebuie să fie >= 1")
                else:
                    # Găsim cel mai mic prefix
                    for prefix in range(32, 0, -1):
                        available = 2 ** (32 - prefix) - 2
                        if available >= n:
                            print(f"\n  Pentru {n} gazde:")
                            print(f"    Prefix recomandat: /{prefix}")
                            print(f"    Gazde disponibile: {available:,}")
                            print(f"    Eficiență: {n / available * 100:.1f}%")
                            break
                    else:
                        print("  Prea multe gazde (max ~4 miliarde)")
                    print()
            except (ValueError, IndexError):
                print("  Utilizare: hosts N (ex: hosts 500)")
        
        else:
            # Presupunem că e o adresă CIDR
            try:
                result = analyze_network(user_input, visual=True)
                print_analysis(result, visual=True)
            except ValueError as e:
                print(f"  {c.RED}Eroare: {e}{c.END}")
                print("  Tip: Introduceți în format CIDR (ex: 192.168.1.0/24)")


def main():
    """Funcția principală."""
    parser = argparse.ArgumentParser(
        description="Subnet Calculator — Calculator interactiv pentru subrețele IPv4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  %(prog)s                          # Mod interactiv
  %(prog)s 192.168.1.0/24           # Analiză directă
  %(prog)s 10.0.0.0/8 --visual      # Cu reprezentare binară
  %(prog)s 172.16.50.12/21 --json   # Output JSON
"""
    )
    
    parser.add_argument(
        'cidr',
        nargs='?',
        help="Adresa în format CIDR (ex: 192.168.1.0/24)"
    )
    
    parser.add_argument(
        '--visual', '-v',
        action='store_true',
        help="Afișare reprezentare binară și vizualizare"
    )
    
    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help="Output în format JSON"
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help="Dezactivare culori"
    )
    
    args = parser.parse_args()
    
    # Dezactivăm culorile dacă nu e terminal sau dacă e cerut explicit
    if args.no_color or not sys.stdout.isatty():
        Colors.disable()
    
    if args.cidr:
        # Mod direct
        try:
            result = analyze_network(args.cidr, visual=args.visual)
            
            if args.json:
                import json
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print_analysis(result, visual=args.visual)
                
        except ValueError as e:
            print(f"Eroare: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Mod interactiv
        interactive_mode()


if __name__ == "__main__":
    main()
