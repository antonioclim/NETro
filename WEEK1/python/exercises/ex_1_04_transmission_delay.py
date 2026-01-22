#!/usr/bin/env python3
"""
Exercițiul 1.04: Calculator delay transmisie
============================================
Rețele de Calculatoare - Săptămâna 1
ASE București

Obiective:
- Înțelegerea componentelor întârzierii în rețele
- Calculul timpului de transmisie pentru diferite scenarii
- Compararea performanței diferitelor tipuri de legături

Nivel: Mediu
Timp estimat: 20 minute

Formule fundamentale:
- Delay transmisie = Dimensiune_pachet / Bandwidth
- Delay propagare = Distanță / Viteză_propagare
- Delay total ≈ D_transmisie + D_propagare + D_procesare + D_coadă
"""

from dataclasses import dataclass
from enum import Enum
import sys


class MediaType(Enum):
    """Tipuri de medii de transmisie cu viteze de propagare."""
    COPPER = 2.0e8      # ~200,000 km/s în cablu de cupru
    FIBER = 2.0e8       # ~200,000 km/s în fibră optică
    WIRELESS = 3.0e8    # ~300,000 km/s (viteza luminii în aer)


class LinkSpeed(Enum):
    """Viteze comune de legături de rețea."""
    ETHERNET_10 = 10e6          # 10 Mbps - Ethernet clasic
    FAST_ETHERNET = 100e6       # 100 Mbps - Fast Ethernet
    GIGABIT = 1e9               # 1 Gbps - Gigabit Ethernet
    TEN_GIGABIT = 10e9          # 10 Gbps
    WIFI_N = 150e6              # ~150 Mbps - WiFi 802.11n
    WIFI_AC = 867e6             # ~867 Mbps - WiFi 802.11ac
    WIFI_6 = 1.2e9              # ~1.2 Gbps - WiFi 6
    DSL = 24e6                  # ~24 Mbps - ADSL2+
    FIBER_HOME = 1e9            # 1 Gbps - FTTH
    MOBILE_4G = 100e6           # ~100 Mbps - LTE
    MOBILE_5G = 1e9             # ~1 Gbps - 5G


@dataclass
class TransmissionResult:
    """Rezultatul calculului de transmisie."""
    packet_size_bytes: int
    link_speed_bps: float
    distance_km: float
    
    transmission_delay_ms: float
    propagation_delay_ms: float
    total_delay_ms: float
    
    throughput_theoretical_mbps: float
    
    def __str__(self) -> str:
        return f"""
╔══════════════════════════════════════════════════════════╗
║           REZULTAT CALCUL TRANSMISIE                     ║
╠══════════════════════════════════════════════════════════╣
║ Parametri intrare:                                       ║
║   • Dimensiune pachet:  {self.packet_size_bytes:>10,} bytes                ║
║   • Viteză legătură:    {self.link_speed_bps/1e6:>10.1f} Mbps                 ║
║   • Distanță:           {self.distance_km:>10.1f} km                   ║
╠══════════════════════════════════════════════════════════╣
║ Rezultate:                                               ║
║   • Delay transmisie:   {self.transmission_delay_ms:>10.4f} ms                 ║
║   • Delay propagare:    {self.propagation_delay_ms:>10.4f} ms                 ║
║   • Delay TOTAL:        {self.total_delay_ms:>10.4f} ms                 ║
║   • Throughput teoretic:{self.throughput_theoretical_mbps:>10.2f} Mbps                 ║
╚══════════════════════════════════════════════════════════╝
"""


def calculate_transmission_delay(
    packet_size_bytes: int,
    link_speed_bps: float
) -> float:
    """
    Calculează delay-ul de transmisie (serialization delay).
    
    Formula: D_trans = L / R
    Unde:
        L = dimensiunea pachetului în biți
        R = rata de transmisie în biți/secundă
    
    Args:
        packet_size_bytes: Dimensiunea pachetului în bytes
        link_speed_bps: Viteza legăturii în biți/secundă
    
    Returns:
        Delay de transmisie în milisecunde
    """
    packet_size_bits = packet_size_bytes * 8
    delay_seconds = packet_size_bits / link_speed_bps
    return delay_seconds * 1000  # convertim în ms


def calculate_propagation_delay(
    distance_km: float,
    media_type: MediaType = MediaType.FIBER
) -> float:
    """
    Calculează delay-ul de propagare.
    
    Formula: D_prop = d / s
    Unde:
        d = distanța în metri
        s = viteza de propagare în mediu (m/s)
    
    Args:
        distance_km: Distanța în kilometri
        media_type: Tipul mediului de transmisie
    
    Returns:
        Delay de propagare în milisecunde
    """
    distance_m = distance_km * 1000
    propagation_speed = media_type.value
    delay_seconds = distance_m / propagation_speed
    return delay_seconds * 1000  # convertim în ms


def calculate_total_transmission(
    packet_size_bytes: int,
    link_speed_bps: float,
    distance_km: float,
    media_type: MediaType = MediaType.FIBER
) -> TransmissionResult:
    """
    Calculează toate componentele de delay pentru o transmisie.
    
    Args:
        packet_size_bytes: Dimensiunea pachetului
        link_speed_bps: Viteza legăturii
        distance_km: Distanța
        media_type: Tipul mediului
    
    Returns:
        TransmissionResult cu toate metricile
    """
    trans_delay = calculate_transmission_delay(packet_size_bytes, link_speed_bps)
    prop_delay = calculate_propagation_delay(distance_km, media_type)
    total = trans_delay + prop_delay
    
    # Throughput teoretic (fără overhead)
    throughput_mbps = link_speed_bps / 1e6
    
    return TransmissionResult(
        packet_size_bytes=packet_size_bytes,
        link_speed_bps=link_speed_bps,
        distance_km=distance_km,
        transmission_delay_ms=trans_delay,
        propagation_delay_ms=prop_delay,
        total_delay_ms=total,
        throughput_theoretical_mbps=throughput_mbps
    )


def calculate_file_transfer_time(
    file_size_mb: float,
    link_speed: LinkSpeed,
    distance_km: float = 0,
    overhead_percent: float = 5.0
) -> dict:
    """
    Calculează timpul de transfer pentru un fișier.
    
    Args:
        file_size_mb: Dimensiunea fișierului în MB
        link_speed: Viteza legăturii
        distance_km: Distanța (pentru delay propagare)
        overhead_percent: Overhead protocol (headers, ACK-uri)
    
    Returns:
        Dict cu metrici de transfer
    """
    file_size_bytes = file_size_mb * 1024 * 1024
    file_size_bits = file_size_bytes * 8
    
    # Ajustăm pentru overhead
    effective_speed = link_speed.value * (1 - overhead_percent/100)
    
    # Timp de transmisie
    transfer_time_sec = file_size_bits / effective_speed
    
    # Adăugăm delay propagare (neglijabil pentru fișiere mari)
    prop_delay_sec = (distance_km * 1000) / MediaType.FIBER.value
    total_time = transfer_time_sec + prop_delay_sec
    
    # Throughput efectiv
    effective_throughput_mbps = (file_size_bits / total_time) / 1e6
    
    return {
        "file_size_mb": file_size_mb,
        "link_speed_mbps": link_speed.value / 1e6,
        "transfer_time_seconds": total_time,
        "transfer_time_formatted": format_time(total_time),
        "effective_throughput_mbps": effective_throughput_mbps,
        "overhead_percent": overhead_percent
    }


def format_time(seconds: float) -> str:
    """Formatează timpul în format uman."""
    if seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} secunde"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes} min {secs:.1f} sec"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours} ore {minutes} min"


# =============================================================================
# SCENARII DEMONSTRATIVE
# =============================================================================

def demo_transmission_delays():
    """Demonstrație: comparație delay-uri pentru diferite scenarii."""
    
    print("\n" + "="*70)
    print(" DEMONSTRAȚIE: Componente Delay în Transmisie ".center(70))
    print("="*70)
    
    scenarios = [
        # (descriere, packet_size, link_speed, distance_km)
        ("LAN local (100m, Gigabit)", 1500, LinkSpeed.GIGABIT.value, 0.1),
        ("LAN local (100m, Fast Ethernet)", 1500, LinkSpeed.FAST_ETHERNET.value, 0.1),
        ("București-Cluj (~400km, fibră)", 1500, LinkSpeed.GIGABIT.value, 400),
        ("București-New York (~8000km)", 1500, LinkSpeed.GIGABIT.value, 8000),
        ("Wireless home (10m, WiFi 6)", 1500, LinkSpeed.WIFI_6.value, 0.01),
        ("Mobile 4G (1km)", 1500, LinkSpeed.MOBILE_4G.value, 1),
    ]
    
    print(f"\n{'Scenariu':<35} {'Trans.':<12} {'Prop.':<12} {'Total':<12}")
    print("-"*70)
    
    for desc, pkt_size, speed, dist in scenarios:
        result = calculate_total_transmission(pkt_size, speed, dist)
        print(f"{desc:<35} {result.transmission_delay_ms:>8.4f} ms  "
              f"{result.propagation_delay_ms:>8.4f} ms  {result.total_delay_ms:>8.4f} ms")
    
    print("-"*70)
    print("\nObservații:")
    print("  • Pentru distanțe mici, delay-ul de transmisie domină")
    print("  • Pentru distanțe mari, delay-ul de propagare devine semnificativ")
    print("  • Viteza legăturii afectează doar delay-ul de transmisie")


def demo_file_transfers():
    """Demonstrație: timp de transfer pentru diferite fișiere și legături."""
    
    print("\n" + "="*70)
    print(" DEMONSTRAȚIE: Timp de Transfer Fișiere ".center(70))
    print("="*70)
    
    file_sizes = [1, 100, 1000, 10000]  # MB
    links = [
        LinkSpeed.FAST_ETHERNET,
        LinkSpeed.GIGABIT,
        LinkSpeed.WIFI_6,
        LinkSpeed.MOBILE_4G,
    ]
    
    # Header
    print(f"\n{'Fișier':<12}", end="")
    for link in links:
        name = link.name.replace("_", " ")[:10]
        print(f"{name:>14}", end="")
    print()
    print("-"*70)
    
    for size in file_sizes:
        print(f"{size:>6} MB    ", end="")
        for link in links:
            result = calculate_file_transfer_time(size, link)
            time_str = result["transfer_time_formatted"]
            print(f"{time_str:>14}", end="")
        print()
    
    print("-"*70)


def demo_bandwidth_delay_product():
    """Demonstrație: Bandwidth-Delay Product (BDP)."""
    
    print("\n" + "="*70)
    print(" DEMONSTRAȚIE: Bandwidth-Delay Product (BDP) ".center(70))
    print("="*70)
    
    print("""
BDP = Bandwidth × RTT

Reprezintă cantitatea de date "în zbor" la un moment dat.
Este crucial pentru dimensionarea buffer-elor TCP (window size).
""")
    
    scenarios = [
        ("LAN local", LinkSpeed.GIGABIT.value, 0.5),      # 0.5 ms RTT
        ("Legături naționale", LinkSpeed.GIGABIT.value, 20),  # 20 ms RTT
        ("Transatlantic", LinkSpeed.GIGABIT.value, 100),  # 100 ms RTT
        ("Satelit GEO", LinkSpeed.FAST_ETHERNET.value, 600),  # 600 ms RTT
    ]
    
    print(f"{'Scenariu':<25} {'Bandwidth':<15} {'RTT':<10} {'BDP':<15}")
    print("-"*70)
    
    for desc, bw, rtt_ms in scenarios:
        rtt_sec = rtt_ms / 1000
        bdp_bits = bw * rtt_sec
        bdp_bytes = bdp_bits / 8
        
        bw_str = f"{bw/1e6:.0f} Mbps"
        rtt_str = f"{rtt_ms:.0f} ms"
        
        if bdp_bytes < 1024:
            bdp_str = f"{bdp_bytes:.0f} bytes"
        elif bdp_bytes < 1024*1024:
            bdp_str = f"{bdp_bytes/1024:.1f} KB"
        else:
            bdp_str = f"{bdp_bytes/(1024*1024):.2f} MB"
        
        print(f"{desc:<25} {bw_str:<15} {rtt_str:<10} {bdp_str:<15}")
    
    print("-"*70)
    print("\nImplicații practice:")
    print("  • TCP window size trebuie să fie >= BDP pentru throughput maxim")
    print("  • Legături cu RTT mare necesită buffere mai mari")
    print("  • Satelitul GEO are probleme serioase cu TCP standard")


# =============================================================================
# INTERFAȚĂ INTERACTIVĂ
# =============================================================================

def interactive_calculator():
    """Calculator interactiv pentru delay de transmisie."""
    
    print("\n" + "="*70)
    print(" CALCULATOR INTERACTIV DELAY TRANSMISIE ".center(70))
    print("="*70)
    
    try:
        print("\nIntroduceți parametrii (sau Enter pentru valori implicite):\n")
        
        # Dimensiune pachet
        pkt_input = input("Dimensiune pachet [1500 bytes]: ").strip()
        packet_size = int(pkt_input) if pkt_input else 1500
        
        # Viteză legătură
        print("\nViteze disponibile:")
        speeds = list(LinkSpeed)
        for i, s in enumerate(speeds, 1):
            print(f"  {i}. {s.name}: {s.value/1e6:.0f} Mbps")
        
        speed_input = input(f"\nAlegeți viteza [1-{len(speeds)}, implicit 3]: ").strip()
        speed_idx = int(speed_input) - 1 if speed_input else 2
        link_speed = speeds[speed_idx].value
        
        # Distanță
        dist_input = input("\nDistanță în km [10]: ").strip()
        distance = float(dist_input) if dist_input else 10.0
        
        # Calculăm și afișăm
        result = calculate_total_transmission(packet_size, link_speed, distance)
        print(result)
        
    except (ValueError, IndexError) as e:
        print(f"\n[EROARE] Valoare invalidă: {e}")
    except KeyboardInterrupt:
        print("\n\n[INFO] Anulat.")


# =============================================================================
# AUTO-TEST
# =============================================================================

def run_self_test() -> bool:
    """Rulează auto-testele."""
    print("\n" + "="*60)
    print(" AUTO-TEST ".center(60, "="))
    print("="*60 + "\n")
    
    tests_passed = 0
    tests_total = 4
    
    # Test 1: Delay transmisie
    print("[TEST 1] Delay transmisie (1500B, 1Gbps)...", end=" ")
    delay = calculate_transmission_delay(1500, 1e9)
    expected = 0.012  # 12 microsecunde = 0.012 ms
    if abs(delay - expected) < 0.001:
        print(f"✓ PASS ({delay:.4f} ms)")
        tests_passed += 1
    else:
        print(f"✗ FAIL (așteptat {expected}, primit {delay})")
    
    # Test 2: Delay propagare
    print("[TEST 2] Delay propagare (1000km, fibră)...", end=" ")
    delay = calculate_propagation_delay(1000, MediaType.FIBER)
    expected = 5.0  # 1000km / 200000 km/s = 5 ms
    if abs(delay - expected) < 0.1:
        print(f"✓ PASS ({delay:.2f} ms)")
        tests_passed += 1
    else:
        print(f"✗ FAIL (așteptat {expected}, primit {delay})")
    
    # Test 3: Transfer fișier
    print("[TEST 3] Transfer 100MB pe Gigabit...", end=" ")
    result = calculate_file_transfer_time(100, LinkSpeed.GIGABIT, overhead_percent=0)
    # 100 MB = 800 Mbit, 1 Gbps → 0.8 secunde
    if 0.7 < result["transfer_time_seconds"] < 0.9:
        print(f"✓ PASS ({result['transfer_time_seconds']:.2f} sec)")
        tests_passed += 1
    else:
        print(f"✗ FAIL ({result['transfer_time_seconds']:.2f} sec)")
    
    # Test 4: Format timp
    print("[TEST 4] Formatare timp...", end=" ")
    t1 = format_time(0.5)
    t2 = format_time(90)
    t3 = format_time(3700)
    if "ms" in t1 and "min" in t2 and "ore" in t3:
        print("✓ PASS")
        tests_passed += 1
    else:
        print("✗ FAIL")
    
    print(f"\nRezultat: {tests_passed}/{tests_total} teste trecute")
    return tests_passed == tests_total


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            success = run_self_test()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "--interactive":
            interactive_calculator()
        elif sys.argv[1] == "--demo":
            demo_transmission_delays()
            demo_file_transfers()
            demo_bandwidth_delay_product()
        else:
            print(f"Opțiune necunoscută: {sys.argv[1]}")
    else:
        print("""
Exercițiul 1.04: Calculator Delay Transmisie
============================================

Utilizare:
    python ex_1_04_transmission_delay.py --demo         # Demonstrații
    python ex_1_04_transmission_delay.py --interactive  # Calculator interactiv
    python ex_1_04_transmission_delay.py --test         # Auto-teste

Exemple programatice:
    >>> from ex_1_04_transmission_delay import *
    >>> result = calculate_total_transmission(1500, 1e9, 100)
    >>> print(result)
""")
        # Rulăm demo implicit
        demo_transmission_delays()
