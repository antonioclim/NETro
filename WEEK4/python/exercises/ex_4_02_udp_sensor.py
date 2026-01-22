#!/usr/bin/env python3
"""
Exercițiul 4.02: Agregator Date Senzori UDP
============================================

Obiectiv: Implementați un server UDP care colectează și agregă date de la senzori.

Specificații:
- Server UDP care primește datagrame de la senzori
- Agregare: medie, min, max, număr citiri per senzor
- Raport periodic (la fiecare N citiri)
- Export statistici în format JSON

Format datagramă senzor (23 bytes - din lab):
  [0]      version: uint8 = 1
  [1:5]    sensor_id: uint32 BE
  [5:9]    temperature: float32 BE
  [9:19]   location: 10 chars (padding spații)
  [19:23]  crc32: uint32 BE

TODO-uri de implementat:
1. parse_sensor_datagram() - parsează datagrama binară
2. validate_crc() - verifică CRC32
3. update_statistics() - actualizează statisticile per senzor
4. generate_report() - generează raport JSON
5. run_aggregator() - bucla principală server

Autor: Revolvix&Hypotheticalandrei
Săptămâna 4 - Exercițiu practic UDP
"""

import socket
import struct
import zlib
import json
import time
import threading
from typing import Dict, Tuple, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

# Constante protocol
DATAGRAM_SIZE = 23
DATAGRAM_VERSION = 1
DEFAULT_PORT = 5556
REPORT_INTERVAL = 5  # secunde


@dataclass
class SensorStats:
    """
    Statistici pentru un senzor.
    """
    sensor_id: int
    location: str
    count: int = 0
    total: float = 0.0
    min_temp: float = float('inf')
    max_temp: float = float('-inf')
    last_reading: float = 0.0
    last_timestamp: str = ""
    
    @property
    def average(self) -> float:
        """Calculează media temperaturilor."""
        return self.total / self.count if self.count > 0 else 0.0
    
    def to_dict(self) -> dict:
        """Convertește la dicționar pentru JSON."""
        return {
            'sensor_id': self.sensor_id,
            'location': self.location,
            'readings_count': self.count,
            'average_temp': round(self.average, 2),
            'min_temp': round(self.min_temp, 2) if self.min_temp != float('inf') else None,
            'max_temp': round(self.max_temp, 2) if self.max_temp != float('-inf') else None,
            'last_reading': round(self.last_reading, 2),
            'last_timestamp': self.last_timestamp
        }


def calculate_crc32(data: bytes) -> int:
    """
    Calculează CRC32 pentru date.
    
    Args:
        data: Bytes pentru care se calculează CRC
    
    Returns:
        int: Valoarea CRC32 (unsigned 32-bit)
    """
    return zlib.crc32(data) & 0xFFFFFFFF


def parse_sensor_datagram(datagram: bytes) -> Optional[Tuple[int, float, str]]:
    """
    Parsează o datagramă primită de la un senzor.
    
    Structura datagramă (23 bytes):
        [0]      version: uint8
        [1:5]    sensor_id: uint32 BE
        [5:9]    temperature: float32 BE
        [9:19]   location: 10 bytes string
        [19:23]  crc32: uint32 BE
    
    Args:
        datagram: Bytes primite de la senzor
    
    Returns:
        Optional[Tuple]: (sensor_id, temperature, location) sau None dacă invalid
    
    TODO: Implementați această funcție
    Hints:
    - Verificați lungimea datagramei (DATAGRAM_SIZE = 23)
    - Folosiți struct.unpack() cu format '>BIf10sI' pentru big-endian
    - Verificați versiunea (trebuie să fie DATAGRAM_VERSION = 1)
    - Extrageți location și faceți strip() pentru a elimina spațiile de padding
    - Validați CRC32 folosind calculate_crc32() pe primii 19 bytes
    """
    # TODO: Implementare
    # 
    # Pasul 1: Verificați lungimea
    # if len(datagram) != DATAGRAM_SIZE:
    #     print(f"[!] Datagramă invalidă: lungime {len(datagram)}, așteptat {DATAGRAM_SIZE}")
    #     return None
    # 
    # Pasul 2: Unpacking
    # try:
    #     version, sensor_id, temperature, location_bytes, received_crc = struct.unpack(
    #         '>BIf10sI', datagram
    #     )
    # except struct.error as e:
    #     print(f"[!] Eroare unpacking: {e}")
    #     return None
    # 
    # Pasul 3: Verificare versiune
    # if version != DATAGRAM_VERSION:
    #     print(f"[!] Versiune invalidă: {version}, așteptat {DATAGRAM_VERSION}")
    #     return None
    # 
    # Pasul 4: Validare CRC32
    # payload_for_crc = datagram[:19]  # Tot mai puțin CRC-ul
    # calculated_crc = calculate_crc32(payload_for_crc)
    # if calculated_crc != received_crc:
    #     print(f"[!] CRC invalid: primit {received_crc:08X}, calculat {calculated_crc:08X}")
    #     return None
    # 
    # Pasul 5: Decodare location
    # location = location_bytes.decode('utf-8', errors='replace').strip()
    # 
    # return (sensor_id, temperature, location)
    
    pass  # Înlocuiți cu implementarea


def update_statistics(stats: Dict[int, SensorStats], 
                     sensor_id: int, 
                     temperature: float, 
                     location: str) -> None:
    """
    Actualizează statisticile pentru un senzor.
    
    Args:
        stats: Dicționar cu statistici per sensor_id
        sensor_id: ID-ul senzorului
        temperature: Temperatura citită
        location: Locația senzorului
    
    TODO: Implementați această funcție
    Hints:
    - Dacă sensor_id nu există în stats, creați o nouă intrare SensorStats
    - Actualizați: count, total, min_temp, max_temp, last_reading, last_timestamp
    - Folosiți datetime.now().isoformat() pentru timestamp
    """
    # TODO: Implementare
    # 
    # if sensor_id not in stats:
    #     stats[sensor_id] = SensorStats(sensor_id=sensor_id, location=location)
    # 
    # sensor = stats[sensor_id]
    # sensor.count += 1
    # sensor.total += temperature
    # sensor.min_temp = min(sensor.min_temp, temperature)
    # sensor.max_temp = max(sensor.max_temp, temperature)
    # sensor.last_reading = temperature
    # sensor.last_timestamp = datetime.now().isoformat()
    # sensor.location = location  # Actualizăm în caz că s-a schimbat
    
    pass  # Înlocuiți cu implementarea


def generate_report(stats: Dict[int, SensorStats]) -> dict:
    """
    Generează un raport JSON cu toate statisticile.
    
    Args:
        stats: Dicționar cu statistici per senzor
    
    Returns:
        dict: Raport structurat
    
    TODO: Implementați această funcție
    """
    # TODO: Implementare
    # 
    # total_readings = sum(s.count for s in stats.values())
    # all_temps = [s.last_reading for s in stats.values() if s.count > 0]
    # 
    # report = {
    #     'timestamp': datetime.now().isoformat(),
    #     'total_sensors': len(stats),
    #     'total_readings': total_readings,
    #     'global_average': round(sum(all_temps) / len(all_temps), 2) if all_temps else None,
    #     'sensors': [s.to_dict() for s in stats.values()]
    # }
    # 
    # return report
    
    pass  # Înlocuiți cu implementarea


def print_report(stats: Dict[int, SensorStats]) -> None:
    """
    Afișează raportul în consolă.
    """
    report = generate_report(stats)
    
    if report is None:
        print("[!] Raport nu a putut fi generat")
        return
    
    print("\n" + "="*60)
    print(f"RAPORT SENZORI - {report.get('timestamp', 'N/A')}")
    print("="*60)
    print(f"Senzori activi: {report.get('total_sensors', 0)}")
    print(f"Total citiri: {report.get('total_readings', 0)}")
    
    if report.get('global_average'):
        print(f"Medie globală: {report['global_average']}°C")
    
    print("\nDetalii per senzor:")
    print("-"*60)
    
    for sensor in report.get('sensors', []):
        print(f"  Senzor {sensor['sensor_id']} @ {sensor['location']}:")
        print(f"    Citiri: {sensor['readings_count']}")
        print(f"    Medie: {sensor['average_temp']}°C")
        print(f"    Min/Max: {sensor['min_temp']}°C / {sensor['max_temp']}°C")
        print(f"    Ultima: {sensor['last_reading']}°C @ {sensor['last_timestamp']}")
    
    print("="*60 + "\n")


def export_json(stats: Dict[int, SensorStats], filename: str = 'sensor_report.json') -> None:
    """
    Exportă raportul în fișier JSON.
    
    Args:
        stats: Statistici senzori
        filename: Numele fișierului de output
    """
    report = generate_report(stats)
    if report:
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"[*] Raport exportat în {filename}")


def periodic_reporter(stats: Dict[int, SensorStats], 
                     interval: int, 
                     stop_event: threading.Event):
    """
    Thread pentru raportare periodică.
    
    Args:
        stats: Dicționar cu statistici
        interval: Interval de raportare (secunde)
        stop_event: Event pentru oprire thread
    """
    while not stop_event.is_set():
        stop_event.wait(interval)
        if not stop_event.is_set() and stats:
            print_report(stats)


def run_aggregator(host: str = '0.0.0.0', 
                   port: int = DEFAULT_PORT,
                   report_interval: int = REPORT_INTERVAL) -> None:
    """
    Rulează serverul agregator UDP.
    
    Args:
        host: Adresa de ascultare
        port: Portul UDP
        report_interval: Interval pentru rapoarte automate (0 = dezactivat)
    
    TODO: Implementați această funcție
    Hints:
    - Creați socket UDP: socket.socket(AF_INET, SOCK_DGRAM)
    - Folosiți recvfrom() pentru a primi datagrame
    - Apelați parse_sensor_datagram() și update_statistics()
    - Opțional: porniți thread pentru raportare periodică
    """
    # Statistici globale
    stats: Dict[int, SensorStats] = {}
    
    # TODO: Implementare
    # 
    # # Creare socket UDP
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.bind((host, port))
    # sock.settimeout(1.0)  # Timeout pentru a putea verifica stop
    # 
    # print(f"[*] Agregator UDP pornit pe {host}:{port}")
    # print(f"[*] Raportare la fiecare {report_interval} secunde")
    # 
    # # Thread pentru raportare periodică
    # stop_event = threading.Event()
    # if report_interval > 0:
    #     reporter = threading.Thread(
    #         target=periodic_reporter,
    #         args=(stats, report_interval, stop_event),
    #         daemon=True
    #     )
    #     reporter.start()
    # 
    # try:
    #     while True:
    #         try:
    #             datagram, addr = sock.recvfrom(DATAGRAM_SIZE + 100)  # Buffer cu margine
    #             
    #             result = parse_sensor_datagram(datagram)
    #             if result:
    #                 sensor_id, temperature, location = result
    #                 update_statistics(stats, sensor_id, temperature, location)
    #                 print(f"[+] Senzor {sensor_id} @ {location}: {temperature:.1f}°C")
    #             else:
    #                 print(f"[-] Datagramă invalidă de la {addr}")
    #                 
    #         except socket.timeout:
    #             continue  # Normal, verificăm periodic pentru Ctrl+C
    #             
    # except KeyboardInterrupt:
    #     print("\n[*] Oprire...")
    #     stop_event.set()
    #     
    #     # Raport final
    #     if stats:
    #         print_report(stats)
    #         export_json(stats)
    #         
    # finally:
    #     sock.close()
    #     print("[*] Agregator oprit")
    
    pass  # Înlocuiți cu implementarea


# =============================================================================
# CLIENT DE TEST (nu trebuie modificat)
# =============================================================================

def create_test_datagram(sensor_id: int, temperature: float, location: str) -> bytes:
    """
    Creează o datagramă de test validă.
    """
    location_padded = location[:10].ljust(10)
    
    # Pack fără CRC
    payload = struct.pack(
        '>BIf10s',
        DATAGRAM_VERSION,
        sensor_id,
        temperature,
        location_padded.encode('utf-8')
    )
    
    # Calculare și adăugare CRC
    crc = calculate_crc32(payload)
    datagram = payload + struct.pack('>I', crc)
    
    return datagram


def test_client(host: str = 'localhost', port: int = DEFAULT_PORT):
    """
    Client de test care trimite datagrame simulate.
    """
    import random
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    sensors = [
        (1001, "Sala_A1"),
        (1002, "Sala_B2"),
        (2001, "Exterior"),
    ]
    
    print(f"[*] Trimitere datagrame către {host}:{port}")
    
    try:
        for _ in range(10):
            sensor_id, location = random.choice(sensors)
            temperature = random.uniform(18.0, 28.0)
            
            datagram = create_test_datagram(sensor_id, temperature, location)
            sock.sendto(datagram, (host, port))
            
            print(f"    Trimis: Senzor {sensor_id} @ {location}: {temperature:.1f}°C")
            time.sleep(0.5)
            
    finally:
        sock.close()
        print("[*] Test client terminat")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Mod test client
        host = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
        port = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_PORT
        test_client(host, port)
    else:
        # Mod server agregator
        port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
        run_aggregator(port=port)
