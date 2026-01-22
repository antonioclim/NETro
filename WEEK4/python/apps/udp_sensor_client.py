#!/usr/bin/env python3
"""
Client UDP - Simulator de senzori de temperatură.

UTILIZARE:
----------
  # Un singur pachet
  python3 udp_sensor_client.py --host localhost --port 5402 \\
      --sensor-id 1 --temp 23.5 --location "Lab1"
  
  # Simulare continuă (un pachet pe secundă)
  python3 udp_sensor_client.py --host localhost --port 5402 \\
      --sensor-id 1 --location "Lab1" --continuous --interval 1.0
  
  # Mod burst (10 pachete cât mai rapid)
  python3 udp_sensor_client.py --host localhost --port 5402 \\
      --sensor-id 1 --location "Lab1" --burst 10
  
  # Simulare pachet corupt (pentru testare detecție erori)
  python3 udp_sensor_client.py --host localhost --port 5402 \\
      --sensor-id 1 --temp 20.0 --location "Lab1" --corrupt
"""
from __future__ import annotations

import argparse
import socket
import random
import time
import sys

# Adăugăm directorul utils la path
sys.path.insert(0, str(__file__).rsplit('/', 2)[0] + '/utils')
from proto_common import pack_udp_sensor, UDP_LEN, format_sensor_reading


def send_reading(
    sock: socket.socket,
    addr: tuple[str, int],
    sensor_id: int,
    temp_c: float,
    location: str,
    corrupt: bool = False,
    verbose: bool = False
) -> None:
    """Trimite o citire de senzor."""
    # Construim pachetul
    packet = pack_udp_sensor(sensor_id, temp_c, location)
    
    # Opțional: corupem pachetul pentru testare
    if corrupt:
        packet = bytearray(packet)
        # Modificăm un byte aleatoriu
        idx = random.randint(0, len(packet) - 1)
        packet[idx] ^= 0xFF
        packet = bytes(packet)
    
    # Trimitem
    sock.sendto(packet, addr)
    
    if verbose:
        status = " (CORRUPTED)" if corrupt else ""
        reading = format_sensor_reading(sensor_id, temp_c, location)
        print(f"[UDP] > {addr[0]}:{addr[1]} {reading}{status}")


def random_temp(base: float = 22.0, variance: float = 5.0) -> float:
    """Generează o temperatură aleatorie realistă."""
    return base + random.uniform(-variance, variance)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Simulator de senzori UDP"
    )
    parser.add_argument("--host", default="localhost", help="Server hostname")
    parser.add_argument("--port", type=int, default=5402, help="Server UDP port")
    parser.add_argument("--sensor-id", type=int, default=1, help="ID senzor (default: 1)")
    parser.add_argument("--temp", type=float, help="Temperatură fixă (default: random)")
    parser.add_argument("--location", default="Lab", help="Locație (max 10 chars)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Afișează detalii")
    
    # Moduri de operare
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--continuous", action="store_true", help="Mod continuu")
    group.add_argument("--burst", type=int, metavar="N", help="Trimite N pachete rapid")
    
    parser.add_argument("--interval", type=float, default=1.0, help="Interval între pachete în mod continuu (secunde)")
    parser.add_argument("--corrupt", action="store_true", help="Corupte pachetele (pentru testare)")
    parser.add_argument("--corrupt-rate", type=float, default=0.0, help="Rata de corupere (0.0-1.0)")
    
    args = parser.parse_args()
    
    # Creare socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (args.host, args.port)
    
    try:
        if args.continuous:
            # Mod continuu
            print(f"[UDP] Continuous mode: sending every {args.interval}s to {addr[0]}:{addr[1]}")
            print(f"[UDP] Press Ctrl+C to stop")
            count = 0
            
            while True:
                temp = args.temp if args.temp is not None else random_temp()
                corrupt = args.corrupt or (random.random() < args.corrupt_rate)
                
                send_reading(sock, addr, args.sensor_id, temp, args.location, corrupt, args.verbose)
                count += 1
                
                if not args.verbose:
                    print(f"\r[UDP] Sent {count} packets", end="", flush=True)
                
                time.sleep(args.interval)
                
        elif args.burst:
            # Mod burst
            print(f"[UDP] Burst mode: sending {args.burst} packets to {addr[0]}:{addr[1]}")
            
            for i in range(args.burst):
                temp = args.temp if args.temp is not None else random_temp()
                corrupt = args.corrupt or (random.random() < args.corrupt_rate)
                
                send_reading(sock, addr, args.sensor_id, temp, args.location, corrupt, args.verbose)
            
            print(f"[UDP] Sent {args.burst} packets")
            
        else:
            # Un singur pachet
            temp = args.temp if args.temp is not None else random_temp()
            
            send_reading(sock, addr, args.sensor_id, temp, args.location, args.corrupt, True)
            print(f"[UDP] Packet sent ({UDP_LEN} bytes)")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n[UDP] Stopped")
        return 0
    except Exception as e:
        print(f"[UDP] Error: {e}")
        return 1
    finally:
        sock.close()


if __name__ == "__main__":
    raise SystemExit(main())
