#!/usr/bin/env python3
"""
Exercițiul 1.01: Măsurarea latenței cu ping
===========================================
Rețele de Calculatoare - Săptămâna 1
ASE București

Obiective:
- Înțelegerea conceptului de Round-Trip Time (RTT)
- Utilizarea subprocess pentru executarea comenzilor sistem
- Parsarea și analiza output-ului ping

Nivel: Începător
Timp estimat: 15 minute
"""

# =============================================================================
# SETUP_ENVIRONMENT
# =============================================================================
import subprocess
import re
import statistics
import sys
from typing import NamedTuple


# =============================================================================
# DEFINE_DATA_STRUCTURES
# =============================================================================
class PingResult(NamedTuple):
    """Rezultatul unei sesiuni ping."""
    host: str
    packets_sent: int
    packets_received: int
    packet_loss_percent: float
    rtt_min_ms: float
    rtt_avg_ms: float
    rtt_max_ms: float
    rtt_mdev_ms: float


# =============================================================================
# CORE_FUNCTIONS
# =============================================================================
def ping_host(host: str, count: int = 4, timeout: int = 5) -> PingResult | None:
    """
    Execută ping către un host și returnează statisticile.
    
    Args:
        host: Adresa IP sau hostname de testat
        count: Numărul de pachete de trimis
        timeout: Timeout per pachet în secunde
    
    Returns:
        PingResult cu statisticile sau None dacă ping eșuează
    
    Exemplu:
        >>> result = ping_host("127.0.0.1", count=4)
        >>> print(f"RTT mediu: {result.rtt_avg_ms:.2f} ms")
    """
    # -------------------------------------------------------------------------
    # EXECUTE_COMMAND
    # -------------------------------------------------------------------------
    try:
        # Rulăm ping cu parametri specifici Linux
        cmd = ["ping", "-c", str(count), "-W", str(timeout), host]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=count * timeout + 5
        )
        
        output = result.stdout
        
        # ---------------------------------------------------------------------
        # PARSE_STATISTICS
        # ---------------------------------------------------------------------
        # Exemplu: "4 packets transmitted, 4 received, 0% packet loss"
        stats_pattern = r"(\d+) packets transmitted, (\d+) received.*?(\d+(?:\.\d+)?)% packet loss"
        stats_match = re.search(stats_pattern, output)
        
        if not stats_match:
            return None
        
        packets_sent = int(stats_match.group(1))
        packets_received = int(stats_match.group(2))
        packet_loss = float(stats_match.group(3))
        
        # ---------------------------------------------------------------------
        # PARSE_RTT
        # ---------------------------------------------------------------------
        # Exemplu: "rtt min/avg/max/mdev = 0.023/0.027/0.031/0.003 ms"
        rtt_pattern = r"rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)"
        rtt_match = re.search(rtt_pattern, output)
        
        if rtt_match:
            rtt_min = float(rtt_match.group(1))
            rtt_avg = float(rtt_match.group(2))
            rtt_max = float(rtt_match.group(3))
            rtt_mdev = float(rtt_match.group(4))
        else:
            # Dacă nu primim răspuns, setăm RTT la 0
            rtt_min = rtt_avg = rtt_max = rtt_mdev = 0.0
        
        # ---------------------------------------------------------------------
        # BUILD_RESULT
        # ---------------------------------------------------------------------
        return PingResult(
            host=host,
            packets_sent=packets_sent,
            packets_received=packets_received,
            packet_loss_percent=packet_loss,
            rtt_min_ms=rtt_min,
            rtt_avg_ms=rtt_avg,
            rtt_max_ms=rtt_max,
            rtt_mdev_ms=rtt_mdev
        )
    
    # -------------------------------------------------------------------------
    # HANDLE_ERRORS
    # -------------------------------------------------------------------------
    except subprocess.TimeoutExpired:
        print(f"[EROARE] Timeout la ping către {host}")
        return None
    except Exception as e:
        print(f"[EROARE] {e}")
        return None


def compare_latencies(hosts: list[str], count: int = 10) -> None:
    """
    Compară latența către mai multe host-uri.
    
    Args:
        hosts: Lista de host-uri de testat
        count: Numărul de pachete per host
    """
    # -------------------------------------------------------------------------
    # DISPLAY_HEADER
    # -------------------------------------------------------------------------
    print(f"\n{'='*60}")
    print(f"{'Comparație latență':^60}")
    print(f"{'='*60}\n")
    
    # -------------------------------------------------------------------------
    # COLLECT_RESULTS
    # -------------------------------------------------------------------------
    results = []
    
    for host in hosts:
        print(f"[INFO] Se testează {host}...", end=" ", flush=True)
        result = ping_host(host, count=count)
        
        if result and result.packets_received > 0:
            print(f"✓ RTT={result.rtt_avg_ms:.2f}ms")
            results.append(result)
        else:
            print("✗ inaccesibil")
    
    if not results:
        print("\n[AVERTISMENT] Niciun host accesibil!")
        return
    
    # -------------------------------------------------------------------------
    # DISPLAY_RESULTS
    # -------------------------------------------------------------------------
    print(f"\n{'-'*60}")
    print(f"{'Host':<25} {'RTT avg':<12} {'Loss':<10} {'Jitter':<12}")
    print(f"{'-'*60}")
    
    for r in sorted(results, key=lambda x: x.rtt_avg_ms):
        jitter = r.rtt_mdev_ms
        loss_str = f"{r.packet_loss_percent:.1f}%"
        print(f"{r.host:<25} {r.rtt_avg_ms:>8.2f} ms  {loss_str:<10} {jitter:>8.3f} ms")
    
    print(f"{'-'*60}")
    
    # -------------------------------------------------------------------------
    # DISPLAY_SUMMARY
    # -------------------------------------------------------------------------
    avg_rtts = [r.rtt_avg_ms for r in results]
    print(f"\nStatistici agregate:")
    print(f"  - RTT minim:  {min(avg_rtts):.2f} ms ({results[0].host})")
    print(f"  - RTT maxim:  {max(avg_rtts):.2f} ms")
    print(f"  - RTT mediu:  {statistics.mean(avg_rtts):.2f} ms")


# =============================================================================
# EXERCIȚII - Completați funcțiile de mai jos
# =============================================================================

def exercitiu_1_ping_loopback() -> None:
    """
    Exercițiu 1: Ping către loopback
    
    Sarcină: Executați ping către 127.0.0.1 și afișați rezultatul.
    
    Ce învățăm: RTT-ul pe loopback este foarte mic (<1ms) deoarece
    pachetele nu părăsesc mașina.
    
    🎯 PREDICȚIE: Ce RTT estimezi pentru loopback? _____ ms
    """
    print("\n[Ex 1] Ping loopback (127.0.0.1)")
    print("-" * 40)
    
    # TODO: Completați - apelați ping_host pentru 127.0.0.1
    # result = ping_host(...)
    # if result:
    #     print(f"RTT: {result.rtt_avg_ms:.3f} ms")
    
    # Soluție:
    result = ping_host("127.0.0.1", count=4)
    if result:
        print(f"Pachete: {result.packets_sent} trimise, {result.packets_received} primite")
        print(f"Packet loss: {result.packet_loss_percent}%")
        print(f"RTT min/avg/max/mdev: {result.rtt_min_ms:.3f}/{result.rtt_avg_ms:.3f}/"
              f"{result.rtt_max_ms:.3f}/{result.rtt_mdev_ms:.3f} ms")


def exercitiu_2_ping_gateway() -> None:
    """
    Exercițiu 2: Ping către gateway
    
    Sarcină: Determinați gateway-ul și măsurați RTT.
    
    Ce învățăm: RTT-ul către gateway este de obicei 1-5ms în rețele locale.
    
    🎯 PREDICȚIE: Ce RTT estimezi pentru gateway? _____ ms
    """
    print("\n[Ex 2] Ping gateway")
    print("-" * 40)
    
    # -------------------------------------------------------------------------
    # DETECT_GATEWAY
    # -------------------------------------------------------------------------
    try:
        route_output = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True, text=True
        )
        gateway_match = re.search(r"default via ([\d.]+)", route_output.stdout)
        
        if gateway_match:
            gateway = gateway_match.group(1)
            print(f"Gateway detectat: {gateway}")
            
            # -----------------------------------------------------------------
            # TEST_GATEWAY
            # -----------------------------------------------------------------
            result = ping_host(gateway, count=4)
            if result:
                print(f"RTT mediu către gateway: {result.rtt_avg_ms:.2f} ms")
            else:
                print("Gateway inaccesibil (poate blochează ICMP)")
        else:
            print("Nu s-a putut determina gateway-ul")
            
    except Exception as e:
        print(f"Eroare: {e}")


def exercitiu_3_compare_destinations() -> None:
    """
    Exercițiu 3: Comparați latența către diferite destinații
    
    Sarcină: Testați mai multe destinații și observați diferențele.
    
    Ce învățăm: Distanța geografică și numărul de hop-uri afectează RTT.
    
    🎯 PREDICȚIE: Care destinație va avea RTT-ul cel mai mic?
    """
    print("\n[Ex 3] Comparație destinații multiple")
    print("-" * 40)
    
    destinations = [
        "127.0.0.1",        # Loopback (local)
        "8.8.8.8",          # Google DNS (US)
        "1.1.1.1",          # Cloudflare DNS (anycast)
    ]
    
    compare_latencies(destinations, count=5)


# =============================================================================
# AUTO-TEST
# =============================================================================

def run_self_test() -> bool:
    """Rulează auto-testele pentru verificare."""
    print("\n" + "="*60)
    print(" AUTO-TEST ".center(60, "="))
    print("="*60 + "\n")
    
    tests_passed = 0
    tests_total = 3
    
    # -------------------------------------------------------------------------
    # TEST_LOOPBACK
    # -------------------------------------------------------------------------
    print("[TEST 1] Ping loopback...", end=" ")
    result = ping_host("127.0.0.1", count=2)
    if result and result.packets_received > 0 and result.rtt_avg_ms < 10:
        print("✓ PASS")
        tests_passed += 1
    else:
        print("✗ FAIL")
    
    # -------------------------------------------------------------------------
    # TEST_STRUCTURE
    # -------------------------------------------------------------------------
    print("[TEST 2] Structură PingResult...", end=" ")
    if result and hasattr(result, 'rtt_avg_ms') and hasattr(result, 'packet_loss_percent'):
        print("✓ PASS")
        tests_passed += 1
    else:
        print("✗ FAIL")
    
    # -------------------------------------------------------------------------
    # TEST_UNREACHABLE
    # -------------------------------------------------------------------------
    print("[TEST 3] Host inaccesibil (10.255.255.1)...", end=" ")
    result_fail = ping_host("10.255.255.1", count=1, timeout=1)
    if result_fail is None or result_fail.packets_received == 0:
        print("✓ PASS")
        tests_passed += 1
    else:
        print("✗ FAIL")
    
    # -------------------------------------------------------------------------
    # DISPLAY_SUMMARY
    # -------------------------------------------------------------------------
    print(f"\nRezultat: {tests_passed}/{tests_total} teste trecute")
    return tests_passed == tests_total


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = run_self_test()
        sys.exit(0 if success else 1)
    
    print("="*60)
    print(" Exercițiul 1.01: Măsurarea latenței cu ping ".center(60))
    print("="*60)
    
    exercitiu_1_ping_loopback()
    exercitiu_2_ping_gateway()
    exercitiu_3_compare_destinations()
    
    print("\n[INFO] Pentru auto-test, rulați: python ex_1_01_ping_latency.py --test")
