#!/usr/bin/env python3
"""
Utilitare de rețea pentru Săptămâna 5 – Nivelul Rețea: Adresare IP
=================================================================
Funcții reutilizabile pentru calcule CIDR, VLSM, IPv6 și validări.

Autor: Material didactic ASE-CSIE
Versiune: 2.0 (Decembrie 2025)
"""

from __future__ import annotations

import ipaddress
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union


@dataclass
class IPv4NetworkInfo:
    """Informații complete despre o rețea/interfață IPv4."""
    address: ipaddress.IPv4Address
    network: ipaddress.IPv4Network
    netmask: ipaddress.IPv4Address
    wildcard: ipaddress.IPv4Address
    broadcast: ipaddress.IPv4Address
    total_addresses: int
    usable_hosts: int
    first_host: Optional[ipaddress.IPv4Address]
    last_host: Optional[ipaddress.IPv4Address]
    is_private: bool
    address_type: str  # 'network', 'broadcast', 'host'


@dataclass
class VLSMAllocation:
    """Rezultatul unei alocări VLSM."""
    required_hosts: int
    allocated_prefix: int
    network: ipaddress.IPv4Network
    gateway: ipaddress.IPv4Address
    broadcast: ipaddress.IPv4Address
    usable_hosts: int
    efficiency: float  # procent utilizare


@dataclass
class IPv6Info:
    """Informații despre o adresă IPv6."""
    full_form: str
    compressed: str
    exploded: str
    network: Optional[ipaddress.IPv6Network]
    address_type: str
    scope: str


def analyze_ipv4_interface(cidr: str) -> IPv4NetworkInfo:
    """
    Analizează complet o adresă IPv4 cu prefix CIDR.
    
    Args:
        cidr: Adresă în format 'x.x.x.x/n' (ex: '192.168.10.14/26')
    
    Returns:
        IPv4NetworkInfo cu toate detaliile rețelei
    
    Raises:
        ValueError: pentru adrese invalide
    """
    interface = ipaddress.IPv4Interface(cidr)
    network = interface.network
    address = interface.ip
    
    # Calculăm wildcard mask (inversul măștii)
    netmask_int = int(network.netmask)
    wildcard_int = netmask_int ^ 0xFFFFFFFF
    wildcard = ipaddress.IPv4Address(wildcard_int)
    
    # Determinăm tipul adresei
    if address == network.network_address:
        addr_type = "network"
    elif address == network.broadcast_address:
        addr_type = "broadcast"
    else:
        addr_type = "host"
    
    # Calculăm hosturi utilizabile
    total = network.num_addresses
    if network.prefixlen == 32:
        usable = 1
        first_host = last_host = address
    elif network.prefixlen == 31:
        # RFC 3021: point-to-point links
        usable = 2
        first_host = network.network_address
        last_host = network.broadcast_address
    else:
        usable = total - 2
        first_host = network.network_address + 1
        last_host = network.broadcast_address - 1
    
    return IPv4NetworkInfo(
        address=address,
        network=network,
        netmask=network.netmask,
        wildcard=wildcard,
        broadcast=network.broadcast_address,
        total_addresses=total,
        usable_hosts=usable,
        first_host=first_host if usable > 0 else None,
        last_host=last_host if usable > 0 else None,
        is_private=network.is_private,
        address_type=addr_type
    )


def ipv4_host_range(network: ipaddress.IPv4Network) -> Tuple[Optional[ipaddress.IPv4Address], 
                                                              Optional[ipaddress.IPv4Address], 
                                                              int]:
    """
    Returnează (first_host, last_host, usable_count) pentru o rețea IPv4.
    """
    total = network.num_addresses
    if network.prefixlen == 32:
        return network.network_address, network.network_address, 1
    elif network.prefixlen == 31:
        return network.network_address, network.broadcast_address, 2
    elif total <= 2:
        return None, None, 0
    else:
        return network.network_address + 1, network.broadcast_address - 1, total - 2


def prefix_for_hosts(hosts_needed: int) -> int:
    """
    Calculează prefixul minim necesar pentru un număr de hosturi.
    
    Args:
        hosts_needed: numărul de hosturi necesare
    
    Returns:
        Lungimea prefixului (ex: 26 pentru max 62 hosturi)
    """
    if hosts_needed <= 0:
        raise ValueError("Numărul de hosturi trebuie să fie pozitiv")
    
    # Adăugăm 2 pentru adresa de rețea și broadcast
    total_needed = hosts_needed + 2
    
    # Găsim puterea lui 2 >= total_needed
    host_bits = math.ceil(math.log2(total_needed))
    
    # Asigurăm minim 2 biți host (pentru /30)
    host_bits = max(host_bits, 2)
    
    prefix = 32 - host_bits
    
    if prefix < 0:
        raise ValueError(f"Nu există prefix suficient pentru {hosts_needed} hosturi")
    
    return prefix


def flsm_split(base_network: str, num_subnets: int) -> List[ipaddress.IPv4Network]:
    """
    Împarte o rețea în N subrețele egale (FLSM).
    
    Args:
        base_network: rețea de bază în format CIDR strict (ex: '192.168.100.0/24')
        num_subnets: numărul de subrețele (trebuie să fie putere a lui 2)
    
    Returns:
        Lista subrețelelor rezultate
    
    Raises:
        ValueError: dacă num_subnets nu e putere a lui 2 sau prefixul rezultat e invalid
    """
    net = ipaddress.ip_network(base_network, strict=True)
    
    if not isinstance(net, ipaddress.IPv4Network):
        raise ValueError("FLSM implementat doar pentru IPv4")
    
    if num_subnets <= 0 or (num_subnets & (num_subnets - 1)) != 0:
        raise ValueError("Numărul de subrețele trebuie să fie putere a lui 2 (2, 4, 8, 16...)")
    
    bits_needed = num_subnets.bit_length() - 1
    new_prefix = net.prefixlen + bits_needed
    
    if new_prefix > 30:
        raise ValueError(f"Prefix rezultat /{new_prefix} nu lasă hosturi utilizabile")
    
    return list(net.subnets(prefixlen_diff=bits_needed))


def vlsm_allocate(base_network: str, host_requirements: List[int]) -> List[VLSMAllocation]:
    """
    Alocă subrețele cu VLSM pentru o listă de cerințe de hosturi.
    
    Args:
        base_network: rețea disponibilă în format CIDR (ex: '10.0.0.0/24')
        host_requirements: lista cerințelor (ex: [60, 30, 10, 2])
    
    Returns:
        Lista alocărilor VLSM în ordine descrescătoare a cerințelor
    
    Raises:
        ValueError: dacă spațiul de adrese e insuficient
    """
    net = ipaddress.ip_network(base_network, strict=True)
    
    if not isinstance(net, ipaddress.IPv4Network):
        raise ValueError("VLSM implementat doar pentru IPv4")
    
    # Sortăm cerințele descrescător
    sorted_reqs = sorted(enumerate(host_requirements), key=lambda x: -x[1])
    
    allocations: List[VLSMAllocation] = []
    current_addr = int(net.network_address)
    end_addr = int(net.broadcast_address)
    
    for orig_idx, hosts in sorted_reqs:
        prefix = prefix_for_hosts(hosts)
        block_size = 2 ** (32 - prefix)
        
        # Aliniem la granița blocului
        if current_addr % block_size != 0:
            current_addr = ((current_addr // block_size) + 1) * block_size
        
        if current_addr + block_size - 1 > end_addr:
            raise ValueError(
                f"Spațiu insuficient pentru {hosts} hosturi. "
                f"Adresa curentă: {ipaddress.IPv4Address(current_addr)}, "
                f"Necesar: /{prefix} ({block_size} adrese)"
            )
        
        subnet = ipaddress.IPv4Network(f"{ipaddress.IPv4Address(current_addr)}/{prefix}")
        first_host, last_host, usable = ipv4_host_range(subnet)
        
        efficiency = (hosts / usable * 100) if usable > 0 else 0
        
        allocations.append(VLSMAllocation(
            required_hosts=hosts,
            allocated_prefix=prefix,
            network=subnet,
            gateway=first_host if first_host else subnet.network_address,
            broadcast=subnet.broadcast_address,
            usable_hosts=usable,
            efficiency=efficiency
        ))
        
        current_addr += block_size
    
    # Reordonăm conform indexului original
    result = [None] * len(host_requirements)
    for i, (orig_idx, _) in enumerate(sorted_reqs):
        result[orig_idx] = allocations[i]
    
    return result


def ipv6_compress(address: str) -> str:
    """
    Comprimă o adresă IPv6 la forma minimală.
    
    Args:
        address: adresă IPv6 în orice format valid
    
    Returns:
        Forma comprimată (ex: '2001:db8::1')
    """
    addr = ipaddress.IPv6Address(address)
    return str(addr)


def ipv6_expand(address: str) -> str:
    """
    Expandează o adresă IPv6 la forma completă.
    
    Args:
        address: adresă IPv6 în orice format
    
    Returns:
        Forma completă cu toate zerourile (ex: '2001:0db8:0000:...')
    """
    addr = ipaddress.IPv6Address(address)
    return addr.exploded


def ipv6_info(address_or_network: str) -> IPv6Info:
    """
    Analizează o adresă sau rețea IPv6.
    
    Args:
        address_or_network: adresă sau prefix IPv6
    
    Returns:
        IPv6Info cu detalii complete
    """
    # Încercăm mai întâi ca rețea
    network = None
    try:
        if '/' in address_or_network:
            iface = ipaddress.IPv6Interface(address_or_network)
            addr = iface.ip
            network = iface.network
        else:
            addr = ipaddress.IPv6Address(address_or_network)
    except ValueError as e:
        raise ValueError(f"Adresă IPv6 invalidă: {address_or_network}") from e
    
    # Determinăm tipul și scope-ul
    if addr.is_loopback:
        addr_type = "loopback"
        scope = "node-local"
    elif addr.is_link_local:
        addr_type = "link-local"
        scope = "link-local"
    elif addr.is_site_local:
        addr_type = "site-local (deprecated)"
        scope = "site-local"
    elif addr.is_multicast:
        addr_type = "multicast"
        # Scope din al doilea nibble
        scope_nibble = (int(addr) >> 112) & 0xF
        scope_map = {
            1: "interface-local",
            2: "link-local", 
            5: "site-local",
            8: "organization-local",
            14: "global"
        }
        scope = scope_map.get(scope_nibble, f"scope-{scope_nibble}")
    elif addr.is_private:
        # Unique Local Address (fc00::/7)
        addr_type = "unique-local"
        scope = "global (private)"
    elif addr.is_global:
        addr_type = "global-unicast"
        scope = "global"
    else:
        addr_type = "other"
        scope = "unknown"
    
    return IPv6Info(
        full_form=addr.exploded,
        compressed=str(addr),
        exploded=addr.exploded,
        network=network,
        address_type=addr_type,
        scope=scope
    )


def ipv6_subnets_from_prefix(base_prefix: str, target_prefix: int, count: int) -> List[ipaddress.IPv6Network]:
    """
    Generează subrețele IPv6 din un prefix de bază.
    
    Args:
        base_prefix: prefix de bază (ex: '2001:db8:10::/48')
        target_prefix: lungimea prefixului țintă (ex: 64)
        count: numărul de subrețele de generat
    
    Returns:
        Lista primelor N subrețele cu prefixul specificat
    """
    net = ipaddress.IPv6Network(base_prefix, strict=True)
    
    if target_prefix <= net.prefixlen:
        raise ValueError(f"Target prefix /{target_prefix} trebuie să fie mai lung decât /{net.prefixlen}")
    
    if target_prefix > 128:
        raise ValueError("Prefix maxim IPv6 este /128")
    
    all_subnets = net.subnets(new_prefix=target_prefix)
    result = []
    
    for i, subnet in enumerate(all_subnets):
        if i >= count:
            break
        result.append(subnet)
    
    return result


def validate_ip_in_network(ip: str, network: str) -> bool:
    """
    Verifică dacă o adresă IP aparține unei rețele.
    
    Args:
        ip: adresa IP de verificat
        network: rețeaua în format CIDR
    
    Returns:
        True dacă adresa aparține rețelei
    """
    try:
        addr = ipaddress.ip_address(ip)
        net = ipaddress.ip_network(network, strict=False)
        return addr in net
    except ValueError:
        return False


def is_valid_host_address(cidr: str) -> Tuple[bool, str]:
    """
    Verifică dacă o adresă CIDR poate fi folosită ca adresă de host.
    
    Args:
        cidr: adresă în format 'x.x.x.x/n'
    
    Returns:
        Tuple (este_valid, motiv)
    """
    try:
        info = analyze_ipv4_interface(cidr)
        
        if info.address_type == "network":
            return False, f"Adresa {info.address} este adresa de rețea pentru {info.network}"
        elif info.address_type == "broadcast":
            return False, f"Adresa {info.address} este adresa de broadcast pentru {info.network}"
        else:
            return True, f"Adresă de host validă în rețeaua {info.network}"
    
    except ValueError as e:
        return False, str(e)


def summarize_networks(networks: List[str]) -> List[ipaddress.IPv4Network]:
    """
    Sumarizează o listă de rețele IPv4 (supernetting/aggregation).
    
    Args:
        networks: lista rețelelor în format CIDR
    
    Returns:
        Lista rețelelor sumarizate
    """
    nets = [ipaddress.ip_network(n, strict=False) for n in networks]
    return list(ipaddress.collapse_addresses(nets))


# Funcții de conversie și formatare
def netmask_to_prefix(netmask: str) -> int:
    """Convertește o mască de rețea în lungime prefix."""
    mask = ipaddress.IPv4Address(netmask)
    binary = bin(int(mask))[2:].zfill(32)
    return binary.count('1')


def prefix_to_netmask(prefix: int) -> str:
    """Convertește o lungime prefix în mască de rețea."""
    if not 0 <= prefix <= 32:
        raise ValueError("Prefix trebuie să fie între 0 și 32")
    bits = '1' * prefix + '0' * (32 - prefix)
    octets = [int(bits[i:i+8], 2) for i in range(0, 32, 8)]
    return '.'.join(map(str, octets))


def ip_to_binary(ip: str) -> str:
    """Convertește o adresă IP în reprezentare binară."""
    addr = ipaddress.IPv4Address(ip)
    return bin(int(addr))[2:].zfill(32)


def ip_to_dotted_binary(ip: str) -> str:
    """Convertește IP în binar cu punct între octeți."""
    binary = ip_to_binary(ip)
    return '.'.join([binary[i:i+8] for i in range(0, 32, 8)])


if __name__ == "__main__":
    # Demonstrație rapidă
    print("=== Demonstrație Utilitare Rețea ===\n")
    
    # Test analyze
    info = analyze_ipv4_interface("192.168.10.14/26")
    print(f"Analiză 192.168.10.14/26:")
    print(f"  Rețea: {info.network}")
    print(f"  Mască: {info.netmask}")
    print(f"  Broadcast: {info.broadcast}")
    print(f"  Hosturi utilizabile: {info.usable_hosts}")
    print(f"  Interval: {info.first_host} - {info.last_host}")
    print()
    
    # Test VLSM
    print("VLSM pentru 172.16.0.0/24 cu cerințe [60, 20, 10, 2]:")
    allocs = vlsm_allocate("172.16.0.0/24", [60, 20, 10, 2])
    for i, a in enumerate(allocs, 1):
        print(f"  {i}. {a.network} (necesar: {a.required_hosts}, util: {a.usable_hosts}, ef: {a.efficiency:.1f}%)")
    print()
    
    # Test IPv6
    print("IPv6 2001:0db8:0000:0000:0000:0000:0000:0001:")
    v6 = ipv6_info("2001:0db8:0000:0000:0000:0000:0000:0001")
    print(f"  Comprimat: {v6.compressed}")
    print(f"  Tip: {v6.address_type}")
    print(f"  Scope: {v6.scope}")
