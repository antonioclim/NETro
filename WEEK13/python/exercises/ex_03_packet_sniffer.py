#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exercițiul 03 - Packet Sniffer și Analizor de Trafic
====================================================

Săptămâna 13 - IoT și Securitate în Rețele de Calculatoare
Academia de Studii Economice - CSIE

Scopul exercițiului:
    Implementarea unui sniffer de pachete pentru interceptarea și analiza
    traficului de rețea în timp real, cu focus pe protocoalele relevante
    pentru IoT (MQTT, HTTP, FTP, DNS).

Competențe dezvoltate:
    - Înțelegerea structurii pachetelor TCP/IP la nivel de octeți
    - Utilizarea bibliotecii Scapy pentru analiză de trafic
    - Identificarea patterns de comunicare în rețea
    - Detectarea potențialelor amenințări de securitate

Dependențe:
    pip install scapy --break-system-packages

ATENȚIE:
    Acest instrument este destinat EXCLUSIV pentru medii de testare controlate!
    Interceptarea traficului de rețea fără autorizare este ILEGALĂ.

Autor: Colectiv Didactic ASE-CSIE
Data: 2025
"""

import argparse
import json
import sys
import signal
import os
from datetime import datetime
from collections import defaultdict
from typing import Optional, Dict, List, Any, Callable

# ============================================================================
# VERIFICARE DEPENDENȚE
# ============================================================================

try:
    from scapy.all import (
        sniff, IP, TCP, UDP, ICMP, DNS, DNSQR, DNSRR,
        Raw, Ether, ARP, conf, get_if_list, hexdump
    )
    SCAPY_DISPONIBIL = True
except ImportError:
    SCAPY_DISPONIBIL = False
    print("[!] AVERTISMENT: Scapy nu este instalat.")
    print("    Instalare: pip install scapy --break-system-packages")
    print("    Sau folosiți modul simplu cu socket raw.")

# ============================================================================
# CONSTANTE ȘI CONFIGURAȚII
# ============================================================================

# Porturi cunoscute pentru analiză
PORTURI_CUNOSCUTE = {
    20: ("FTP-DATA", "Transfer date FTP"),
    21: ("FTP", "Control FTP"),
    22: ("SSH", "Secure Shell"),
    23: ("TELNET", "Telnet (nesigur!)"),
    25: ("SMTP", "Email outgoing"),
    53: ("DNS", "Domain Name System"),
    80: ("HTTP", "Web trafic necriptat"),
    110: ("POP3", "Email retrieval"),
    143: ("IMAP", "Email access"),
    443: ("HTTPS", "Web trafic criptat"),
    445: ("SMB", "Windows file sharing"),
    1883: ("MQTT", "IoT messaging (plain)"),
    8883: ("MQTT-TLS", "IoT messaging (criptat)"),
    3306: ("MySQL", "Bază de date"),
    5432: ("PostgreSQL", "Bază de date"),
    6379: ("Redis", "Cache/NoSQL"),
    27017: ("MongoDB", "NoSQL database"),
}

# Coduri de culoare ANSI
class Culori:
    """Coduri ANSI pentru output colorat în terminal."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    
    @classmethod
    def disable(cls):
        """Dezactivează culorile pentru pipe/fișier."""
        cls.RESET = cls.BOLD = cls.RED = cls.GREEN = ""
        cls.YELLOW = cls.BLUE = cls.MAGENTA = cls.CYAN = cls.WHITE = ""

# Dezactivare culori dacă output nu e terminal
if not sys.stdout.isatty():
    Culori.disable()

# ============================================================================
# CLASA PRINCIPALĂ - PACKET SNIFFER
# ============================================================================

class PacketSniffer:
    """
    Sniffer de pachete cu suport pentru multiple protocoale.
    
    Arhitectura:
        - Capturare: Scapy sniff() cu BPF filter
        - Procesare: Callback chain pentru fiecare pachet
        - Statistici: Agregare în timp real
        - Export: JSON pentru analiză ulterioară
    
    Attributes:
        interface: Interfața de rețea pentru captură
        packet_count: Număr maxim de pachete de capturat (0=infinit)
        bpf_filter: Berkeley Packet Filter pentru pre-filtrare
        verbose: Nivel de detaliere output
    """
    
    def __init__(
        self,
        interface: str = "any",
        packet_count: int = 0,
        bpf_filter: str = "",
        verbose: int = 1,
        output_file: Optional[str] = None
    ):
        """
        Inițializează sniffer-ul.
        
        Args:
            interface: Interfața de captură ("any", "eth0", "docker0", etc.)
            packet_count: Număr pachete de capturat (0 = infinit)
            bpf_filter: Filtru BPF (ex: "tcp port 1883")
            verbose: 0=silent, 1=normal, 2=detaliat, 3=debug
            output_file: Fișier JSON pentru export statistici
        """
        self.interface = interface
        self.packet_count = packet_count
        self.bpf_filter = bpf_filter
        self.verbose = verbose
        self.output_file = output_file
        
        # Statistici agregate
        self.statistici: Dict[str, Any] = {
            "start_time": None,
            "end_time": None,
            "total_pachete": 0,
            "total_bytes": 0,
            "protocoale": defaultdict(int),
            "ip_sursa": defaultdict(int),
            "ip_dest": defaultdict(int),
            "porturi_sursa": defaultdict(int),
            "porturi_dest": defaultdict(int),
            "dns_queries": [],
            "http_requests": [],
            "mqtt_mesaje": [],
            "alerte_securitate": [],
            "conexiuni": defaultdict(lambda: {"pachete": 0, "bytes": 0}),
        }
        
        # Flag pentru oprire gracioasă
        self._running = False
        self._pachete_capturate: List[Dict] = []
        
        # Configurare handler pentru SIGINT
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, sig, frame):
        """Handler pentru Ctrl+C - oprire gracioasă."""
        print(f"\n{Culori.YELLOW}[*] Se oprește captura...{Culori.RESET}")
        self._running = False
    
    # ========================================================================
    # PARSARE PACHETE
    # ========================================================================
    
    def _parseaza_pachet(self, pachet) -> Optional[Dict]:
        """
        Parsează un pachet și extrage informații relevante.
        
        Strategie de parsare:
            1. Layer 2 (Ethernet/ARP)
            2. Layer 3 (IP)
            3. Layer 4 (TCP/UDP/ICMP)
            4. Layer 7 (HTTP/MQTT/DNS/FTP)
        
        Args:
            pachet: Pachet Scapy raw
            
        Returns:
            Dict cu informații parsate sau None dacă nu e relevant
        """
        info = {
            "timestamp": datetime.now().isoformat(),
            "lungime": len(pachet),
            "layers": [],
            "sursa": {},
            "destinatie": {},
            "protocol": "UNKNOWN",
            "detalii": {},
        }
        
        # -------------------------------------------------------------------
        # Layer 2 - Data Link
        # -------------------------------------------------------------------
        if pachet.haslayer(Ether):
            info["layers"].append("Ethernet")
            info["sursa"]["mac"] = pachet[Ether].src
            info["destinatie"]["mac"] = pachet[Ether].dst
        
        if pachet.haslayer(ARP):
            info["layers"].append("ARP")
            info["protocol"] = "ARP"
            info["detalii"]["arp_op"] = "request" if pachet[ARP].op == 1 else "reply"
            info["detalii"]["arp_src_ip"] = pachet[ARP].psrc
            info["detalii"]["arp_dst_ip"] = pachet[ARP].pdst
            return info
        
        # -------------------------------------------------------------------
        # Layer 3 - Network
        # -------------------------------------------------------------------
        if not pachet.haslayer(IP):
            return None  # Ignorăm pachete non-IP
        
        info["layers"].append("IP")
        info["sursa"]["ip"] = pachet[IP].src
        info["destinatie"]["ip"] = pachet[IP].dst
        info["detalii"]["ttl"] = pachet[IP].ttl
        info["detalii"]["ip_id"] = pachet[IP].id
        
        # -------------------------------------------------------------------
        # Layer 4 - Transport
        # -------------------------------------------------------------------
        if pachet.haslayer(TCP):
            info["layers"].append("TCP")
            info["protocol"] = "TCP"
            info["sursa"]["port"] = pachet[TCP].sport
            info["destinatie"]["port"] = pachet[TCP].dport
            info["detalii"]["tcp_flags"] = self._parseaza_tcp_flags(pachet[TCP].flags)
            info["detalii"]["seq"] = pachet[TCP].seq
            info["detalii"]["ack"] = pachet[TCP].ack
            info["detalii"]["window"] = pachet[TCP].window
            
            # Detectare protocol Layer 7 pe baza portului
            port_dst = pachet[TCP].dport
            port_src = pachet[TCP].sport
            
            if port_dst in PORTURI_CUNOSCUTE or port_src in PORTURI_CUNOSCUTE:
                port_info = PORTURI_CUNOSCUTE.get(port_dst) or PORTURI_CUNOSCUTE.get(port_src)
                info["detalii"]["serviciu"] = port_info[0] if port_info else "Unknown"
            
            # Parsare payload pentru protocoale text
            if pachet.haslayer(Raw):
                self._parseaza_payload_tcp(pachet, info)
        
        elif pachet.haslayer(UDP):
            info["layers"].append("UDP")
            info["protocol"] = "UDP"
            info["sursa"]["port"] = pachet[UDP].sport
            info["destinatie"]["port"] = pachet[UDP].dport
            
            # DNS
            if pachet.haslayer(DNS):
                self._parseaza_dns(pachet, info)
        
        elif pachet.haslayer(ICMP):
            info["layers"].append("ICMP")
            info["protocol"] = "ICMP"
            info["detalii"]["icmp_type"] = pachet[ICMP].type
            info["detalii"]["icmp_code"] = pachet[ICMP].code
        
        return info
    
    def _parseaza_tcp_flags(self, flags) -> str:
        """
        Convertește flags TCP în string lizibil.
        
        Flags TCP:
            S = SYN (synchronize)
            A = ACK (acknowledge)
            F = FIN (finish)
            R = RST (reset)
            P = PSH (push)
            U = URG (urgent)
        """
        flag_map = {
            'F': 'FIN',
            'S': 'SYN',
            'R': 'RST',
            'P': 'PSH',
            'A': 'ACK',
            'U': 'URG',
            'E': 'ECE',
            'C': 'CWR',
        }
        result = []
        flags_str = str(flags)
        for char, name in flag_map.items():
            if char in flags_str:
                result.append(name)
        return ",".join(result) if result else str(flags)
    
    def _parseaza_payload_tcp(self, pachet, info: Dict):
        """
        Parsează payload TCP pentru protocoale Layer 7.
        
        Protocoale detectate:
            - HTTP (GET, POST, HEAD, etc.)
            - FTP (comenzi și răspunsuri)
            - MQTT (CONNECT, PUBLISH, SUBSCRIBE)
        """
        try:
            payload = bytes(pachet[Raw].load)
            
            # Încercăm decodare UTF-8
            try:
                payload_text = payload.decode('utf-8', errors='ignore')
            except:
                payload_text = ""
            
            port_dst = pachet[TCP].dport
            port_src = pachet[TCP].sport
            
            # ---------------------------------------------------------------
            # SECȚIUNEA STUDENT - Analiza HTTP
            # Completați: Identificarea metodei HTTP și path-ului
            # Hint: HTTP începe cu "GET ", "POST ", "HEAD ", etc.
            # ---------------------------------------------------------------
            if port_dst == 80 or port_src == 80:
                info["detalii"]["serviciu"] = "HTTP"
                if payload_text.startswith(("GET ", "POST ", "HEAD ", "PUT ", "DELETE ")):
                    lines = payload_text.split('\r\n')
                    if lines:
                        info["detalii"]["http_request"] = lines[0]
                        # Extrage headers
                        headers = {}
                        for line in lines[1:]:
                            if ': ' in line:
                                key, val = line.split(': ', 1)
                                headers[key.lower()] = val
                        info["detalii"]["http_headers"] = headers
                elif payload_text.startswith("HTTP/"):
                    lines = payload_text.split('\r\n')
                    if lines:
                        info["detalii"]["http_response"] = lines[0]
            
            # ---------------------------------------------------------------
            # Analiza FTP
            # ---------------------------------------------------------------
            if port_dst == 21 or port_src == 21:
                info["detalii"]["serviciu"] = "FTP"
                # Comenzi FTP cunoscute
                ftp_comenzi = ["USER", "PASS", "LIST", "RETR", "STOR", "QUIT", "PWD", "CWD"]
                for cmd in ftp_comenzi:
                    if payload_text.upper().startswith(cmd):
                        info["detalii"]["ftp_command"] = payload_text.strip()
                        # Alertă pentru credențiale în clar
                        if cmd in ["USER", "PASS"]:
                            self._adauga_alerta(
                                "MEDIUM",
                                "FTP_CREDENTIALS_CLEARTEXT",
                                f"Credențiale FTP transmise în clar: {cmd}",
                                info
                            )
                        break
                # Răspuns FTP
                if payload_text[:3].isdigit():
                    info["detalii"]["ftp_response"] = payload_text.strip()[:100]
            
            # ---------------------------------------------------------------
            # Analiza MQTT
            # ---------------------------------------------------------------
            if port_dst == 1883 or port_src == 1883:
                info["detalii"]["serviciu"] = "MQTT"
                self._parseaza_mqtt(payload, info)
                # Alertă: MQTT fără TLS
                self._adauga_alerta(
                    "HIGH",
                    "MQTT_NO_TLS",
                    "Trafic MQTT necriptat detectat",
                    info
                )
            
        except Exception as e:
            if self.verbose >= 3:
                print(f"{Culori.RED}[!] Eroare parsare payload: {e}{Culori.RESET}")
    
    def _parseaza_mqtt(self, payload: bytes, info: Dict):
        """
        Parsează mesaje MQTT la nivel de octeți.
        
        Structura header MQTT:
            Byte 0: Control packet type (bits 7-4) + Flags (bits 3-0)
            Bytes 1-4: Remaining length (variable length encoding)
        
        Tipuri de pachete:
            1 = CONNECT
            2 = CONNACK
            3 = PUBLISH
            4 = PUBACK
            8 = SUBSCRIBE
            9 = SUBACK
            12 = PINGREQ
            13 = PINGRESP
            14 = DISCONNECT
        """
        if len(payload) < 2:
            return
        
        # Primul byte: tip pachet (4 biți superiori)
        packet_type = (payload[0] & 0xF0) >> 4
        
        mqtt_types = {
            1: "CONNECT",
            2: "CONNACK",
            3: "PUBLISH",
            4: "PUBACK",
            5: "PUBREC",
            6: "PUBREL",
            7: "PUBCOMP",
            8: "SUBSCRIBE",
            9: "SUBACK",
            10: "UNSUBSCRIBE",
            11: "UNSUBACK",
            12: "PINGREQ",
            13: "PINGRESP",
            14: "DISCONNECT",
        }
        
        mqtt_type_name = mqtt_types.get(packet_type, f"UNKNOWN({packet_type})")
        info["detalii"]["mqtt_type"] = mqtt_type_name
        
        # ---------------------------------------------------------------
        # SECȚIUNEA STUDENT - Parsare MQTT PUBLISH
        # Completați: Extrageți topic și payload din mesaj PUBLISH
        # Hint: După header, urmează lungime topic (2 bytes) + topic + payload
        # ---------------------------------------------------------------
        if packet_type == 3:  # PUBLISH
            try:
                # QoS din flags (bits 1-2)
                qos = (payload[0] & 0x06) >> 1
                info["detalii"]["mqtt_qos"] = qos
                
                # Skip remaining length (poate fi 1-4 bytes)
                pos = 1
                remaining_length = 0
                multiplier = 1
                while pos < min(len(payload), 5):
                    byte = payload[pos]
                    remaining_length += (byte & 0x7F) * multiplier
                    pos += 1
                    if (byte & 0x80) == 0:
                        break
                    multiplier *= 128
                
                # Topic length (2 bytes big-endian)
                if pos + 2 <= len(payload):
                    topic_len = (payload[pos] << 8) | payload[pos + 1]
                    pos += 2
                    
                    # Topic name
                    if pos + topic_len <= len(payload):
                        topic = payload[pos:pos + topic_len].decode('utf-8', errors='ignore')
                        info["detalii"]["mqtt_topic"] = topic
                        pos += topic_len
                        
                        # Skip packet identifier pentru QoS > 0
                        if qos > 0 and pos + 2 <= len(payload):
                            pos += 2
                        
                        # Payload
                        if pos < len(payload):
                            mqtt_payload = payload[pos:].decode('utf-8', errors='ignore')
                            info["detalii"]["mqtt_payload"] = mqtt_payload[:200]  # Limită
            except Exception as e:
                if self.verbose >= 3:
                    print(f"[!] Eroare parsare MQTT PUBLISH: {e}")
    
    def _parseaza_dns(self, pachet, info: Dict):
        """
        Parsează interogări și răspunsuri DNS.
        
        DNS poate expune:
            - Domenii accesate (privacy concern)
            - Potențiale tuneluri DNS (exfiltrare date)
            - DNS spoofing attacks
        """
        info["detalii"]["serviciu"] = "DNS"
        info["protocol"] = "DNS"
        
        dns = pachet[DNS]
        
        # Query (QR=0) sau Response (QR=1)
        is_response = dns.qr == 1
        info["detalii"]["dns_type"] = "response" if is_response else "query"
        
        # Extrage query name
        if dns.qdcount > 0 and pachet.haslayer(DNSQR):
            qname = pachet[DNSQR].qname.decode('utf-8', errors='ignore').rstrip('.')
            info["detalii"]["dns_query"] = qname
            
            # Stocare pentru statistici
            if not is_response:
                self.statistici["dns_queries"].append({
                    "timestamp": info["timestamp"],
                    "query": qname,
                    "src_ip": info["sursa"]["ip"]
                })
        
        # Răspunsuri
        if is_response and dns.ancount > 0 and pachet.haslayer(DNSRR):
            answers = []
            for i in range(dns.ancount):
                try:
                    rr = dns.an[i]
                    if hasattr(rr, 'rdata'):
                        answers.append(str(rr.rdata))
                except:
                    pass
            info["detalii"]["dns_answers"] = answers
    
    def _adauga_alerta(
        self, 
        severitate: str, 
        tip: str, 
        mesaj: str, 
        pachet_info: Dict
    ):
        """
        Adaugă o alertă de securitate.
        
        Severități:
            - LOW: Informațional
            - MEDIUM: Potențial risc
            - HIGH: Risc semnificativ
            - CRITICAL: Necesită acțiune imediată
        """
        alerta = {
            "timestamp": datetime.now().isoformat(),
            "severitate": severitate,
            "tip": tip,
            "mesaj": mesaj,
            "sursa_ip": pachet_info.get("sursa", {}).get("ip", "N/A"),
            "dest_ip": pachet_info.get("destinatie", {}).get("ip", "N/A"),
        }
        self.statistici["alerte_securitate"].append(alerta)
        
        if self.verbose >= 1:
            culoare = {
                "LOW": Culori.BLUE,
                "MEDIUM": Culori.YELLOW,
                "HIGH": Culori.RED,
                "CRITICAL": Culori.RED + Culori.BOLD,
            }.get(severitate, Culori.WHITE)
            
            print(f"{culoare}[ALERTĂ {severitate}] {tip}: {mesaj}{Culori.RESET}")
    
    # ========================================================================
    # PROCESARE PACHETE
    # ========================================================================
    
    def _proceseaza_pachet(self, pachet):
        """
        Callback pentru fiecare pachet capturat.
        
        Flow:
            1. Parsare pachet
            2. Actualizare statistici
            3. Afișare (dacă verbose)
            4. Stocare pentru export
        """
        info = self._parseaza_pachet(pachet)
        if info is None:
            return
        
        # Actualizare statistici
        self.statistici["total_pachete"] += 1
        self.statistici["total_bytes"] += info["lungime"]
        self.statistici["protocoale"][info["protocol"]] += 1
        
        if "ip" in info["sursa"]:
            self.statistici["ip_sursa"][info["sursa"]["ip"]] += 1
        if "ip" in info["destinatie"]:
            self.statistici["ip_dest"][info["destinatie"]["ip"]] += 1
        if "port" in info["sursa"]:
            self.statistici["porturi_sursa"][info["sursa"]["port"]] += 1
        if "port" in info["destinatie"]:
            self.statistici["porturi_dest"][info["destinatie"]["port"]] += 1
        
        # Tracking conexiuni (5-tuple)
        if "ip" in info["sursa"] and "port" in info["sursa"]:
            conn_key = (
                info["sursa"]["ip"],
                info["sursa"].get("port", 0),
                info["destinatie"]["ip"],
                info["destinatie"].get("port", 0),
                info["protocol"]
            )
            self.statistici["conexiuni"][conn_key]["pachete"] += 1
            self.statistici["conexiuni"][conn_key]["bytes"] += info["lungime"]
        
        # Afișare
        if self.verbose >= 1:
            self._afiseaza_pachet(info)
        
        # Stocare pentru export
        self._pachete_capturate.append(info)
    
    def _afiseaza_pachet(self, info: Dict):
        """
        Afișează informații despre pachet în format lizibil.
        """
        ts = info["timestamp"].split("T")[1][:12]  # HH:MM:SS.mmm
        
        # Culoare pe baza protocolului
        culoare = {
            "TCP": Culori.GREEN,
            "UDP": Culori.BLUE,
            "ICMP": Culori.YELLOW,
            "DNS": Culori.CYAN,
            "ARP": Culori.MAGENTA,
        }.get(info["protocol"], Culori.WHITE)
        
        # Format de bază
        src = info["sursa"].get("ip", info["sursa"].get("mac", "?"))
        dst = info["destinatie"].get("ip", info["destinatie"].get("mac", "?"))
        
        if "port" in info["sursa"]:
            src += f":{info['sursa']['port']}"
        if "port" in info["destinatie"]:
            dst += f":{info['destinatie']['port']}"
        
        output = f"{culoare}[{ts}] {info['protocol']:5} {src:22} → {dst:22}"
        
        # Adăugare detalii
        detalii = info.get("detalii", {})
        extras = []
        
        if "tcp_flags" in detalii:
            extras.append(f"Flags={detalii['tcp_flags']}")
        if "serviciu" in detalii:
            extras.append(f"[{detalii['serviciu']}]")
        if "http_request" in detalii:
            extras.append(detalii["http_request"][:50])
        if "mqtt_type" in detalii:
            extras.append(f"MQTT:{detalii['mqtt_type']}")
            if "mqtt_topic" in detalii:
                extras.append(f"Topic={detalii['mqtt_topic']}")
        if "dns_query" in detalii:
            extras.append(f"DNS:{detalii['dns_query']}")
        if "ftp_command" in detalii:
            extras.append(detalii["ftp_command"][:30])
        
        if extras:
            output += f" | {' '.join(extras)}"
        
        output += f" ({info['lungime']}B){Culori.RESET}"
        print(output)
    
    # ========================================================================
    # EXECUȚIE CAPTURĂ
    # ========================================================================
    
    def start(self):
        """
        Pornește captura de pachete.
        
        Metodă:
            - Scapy sniff() cu callback
            - Filter BPF pentru eficiență
            - Stop condition: count sau Ctrl+C
        """
        if not SCAPY_DISPONIBIL:
            print(f"{Culori.RED}[!] Scapy nu este disponibil. Instalați cu:")
            print(f"    pip install scapy --break-system-packages{Culori.RESET}")
            return False
        
        # Verificare permisiuni
        if os.geteuid() != 0:
            print(f"{Culori.YELLOW}[!] AVERTISMENT: Rulare fără root poate limita funcționalitatea")
            print(f"    Recomandare: sudo python3 {sys.argv[0]}{Culori.RESET}")
        
        # Header
        print(f"\n{Culori.CYAN}{'='*70}")
        print(f"  PACKET SNIFFER - IoT & Network Security")
        print(f"  Interfață: {self.interface}")
        if self.bpf_filter:
            print(f"  Filtru BPF: {self.bpf_filter}")
        if self.packet_count > 0:
            print(f"  Limită pachete: {self.packet_count}")
        print(f"  Apăsați Ctrl+C pentru oprire")
        print(f"{'='*70}{Culori.RESET}\n")
        
        self.statistici["start_time"] = datetime.now().isoformat()
        self._running = True
        
        try:
            # Configurare Scapy
            conf.verb = 0  # Dezactivare output Scapy
            
            # Start sniffing
            sniff(
                iface=self.interface if self.interface != "any" else None,
                filter=self.bpf_filter if self.bpf_filter else None,
                prn=self._proceseaza_pachet,
                count=self.packet_count if self.packet_count > 0 else 0,
                store=False,  # Nu stocăm în memorie Scapy
                stop_filter=lambda x: not self._running
            )
            
        except PermissionError:
            print(f"{Culori.RED}[!] Eroare permisiuni. Rulați cu sudo.{Culori.RESET}")
            return False
        except Exception as e:
            print(f"{Culori.RED}[!] Eroare captură: {e}{Culori.RESET}")
            return False
        finally:
            self.statistici["end_time"] = datetime.now().isoformat()
            self._afiseaza_statistici()
            
            if self.output_file:
                self._exporta_json()
        
        return True
    
    def _afiseaza_statistici(self):
        """
        Afișează statistici agregate la finalul capturii.
        """
        stats = self.statistici
        
        print(f"\n{Culori.CYAN}{'='*70}")
        print(f"  STATISTICI CAPTURĂ")
        print(f"{'='*70}{Culori.RESET}")
        
        # Sumar
        print(f"\n{Culori.BOLD}Sumar:{Culori.RESET}")
        print(f"  Total pachete:  {stats['total_pachete']}")
        print(f"  Total bytes:    {stats['total_bytes']:,}")
        print(f"  Durată:         {stats['start_time']} - {stats['end_time']}")
        
        # Protocoale
        if stats["protocoale"]:
            print(f"\n{Culori.BOLD}Protocoale:{Culori.RESET}")
            for proto, count in sorted(stats["protocoale"].items(), key=lambda x: -x[1]):
                pct = (count / stats["total_pachete"]) * 100 if stats["total_pachete"] > 0 else 0
                print(f"  {proto:10} {count:6} ({pct:5.1f}%)")
        
        # Top IP-uri
        if stats["ip_sursa"]:
            print(f"\n{Culori.BOLD}Top 5 IP-uri sursă:{Culori.RESET}")
            for ip, count in sorted(stats["ip_sursa"].items(), key=lambda x: -x[1])[:5]:
                print(f"  {ip:20} {count:6} pachete")
        
        # Top porturi destinație
        if stats["porturi_dest"]:
            print(f"\n{Culori.BOLD}Top 5 porturi destinație:{Culori.RESET}")
            for port, count in sorted(stats["porturi_dest"].items(), key=lambda x: -x[1])[:5]:
                port_name = PORTURI_CUNOSCUTE.get(port, ("Unknown",))[0]
                print(f"  {port:5} ({port_name:10}) {count:6} pachete")
        
        # DNS Queries
        if stats["dns_queries"]:
            print(f"\n{Culori.BOLD}DNS Queries ({len(stats['dns_queries'])}):{Culori.RESET}")
            # Unique queries
            unique = list(set(q["query"] for q in stats["dns_queries"]))[:10]
            for query in unique:
                print(f"  {query}")
        
        # Alerte securitate
        if stats["alerte_securitate"]:
            print(f"\n{Culori.RED}{Culori.BOLD}Alerte Securitate ({len(stats['alerte_securitate'])}):{Culori.RESET}")
            for alerta in stats["alerte_securitate"][-10:]:  # Ultimele 10
                print(f"  [{alerta['severitate']}] {alerta['tip']}: {alerta['mesaj']}")
        
        print(f"\n{Culori.CYAN}{'='*70}{Culori.RESET}")
    
    def _exporta_json(self):
        """
        Exportă statisticile în format JSON.
        """
        try:
            # Convertim defaultdict în dict standard
            export_data = {
                "metadata": {
                    "start_time": self.statistici["start_time"],
                    "end_time": self.statistici["end_time"],
                    "interface": self.interface,
                    "filter": self.bpf_filter,
                },
                "summary": {
                    "total_packets": self.statistici["total_pachete"],
                    "total_bytes": self.statistici["total_bytes"],
                },
                "protocols": dict(self.statistici["protocoale"]),
                "top_src_ips": dict(sorted(
                    self.statistici["ip_sursa"].items(),
                    key=lambda x: -x[1]
                )[:20]),
                "top_dst_ips": dict(sorted(
                    self.statistici["ip_dest"].items(),
                    key=lambda x: -x[1]
                )[:20]),
                "top_dst_ports": dict(sorted(
                    self.statistici["porturi_dest"].items(),
                    key=lambda x: -x[1]
                )[:20]),
                "dns_queries": self.statistici["dns_queries"][-100:],
                "security_alerts": self.statistici["alerte_securitate"],
            }
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n{Culori.GREEN}[✓] Statistici exportate în: {self.output_file}{Culori.RESET}")
            
        except Exception as e:
            print(f"{Culori.RED}[!] Eroare export JSON: {e}{Culori.RESET}")


# ============================================================================
# FUNCȚII HELPER - FILTRE PREDEFINITE
# ============================================================================

def get_predefined_filters() -> Dict[str, str]:
    """
    Returnează filtre BPF predefinite pentru scenarii comune.
    
    BPF (Berkeley Packet Filter) permite filtrarea eficientă
    la nivel kernel, înainte ca pachetele să ajungă în userspace.
    """
    return {
        "mqtt": "tcp port 1883 or tcp port 8883",
        "http": "tcp port 80 or tcp port 443 or tcp port 8080",
        "ftp": "tcp port 20 or tcp port 21",
        "dns": "udp port 53 or tcp port 53",
        "ssh": "tcp port 22",
        "pentest": "tcp port 21 or tcp port 22 or tcp port 80 or tcp port 443 or tcp port 1883",
        "iot": "tcp port 1883 or tcp port 8883 or tcp port 5683 or tcp port 5684",  # MQTT + CoAP
        "docker": "net 172.17.0.0/16 or net 172.18.0.0/16 or net 172.20.0.0/16",
    }


# ============================================================================
# CLI - INTERFAȚA LINIE DE COMANDĂ
# ============================================================================

def lista_interfete():
    """Listează interfețele de rețea disponibile."""
    if not SCAPY_DISPONIBIL:
        print("[!] Scapy nu este instalat")
        return
    
    print(f"\n{Culori.CYAN}Interfețe de rețea disponibile:{Culori.RESET}")
    for iface in get_if_list():
        print(f"  - {iface}")
    print()


def main():
    """
    Punct de intrare principal.
    
    Exemple utilizare:
        # Captură pe toate interfețele
        sudo python3 ex_03_packet_sniffer.py
        
        # Doar MQTT
        sudo python3 ex_03_packet_sniffer.py --filter mqtt
        
        # Interfață specifică, 100 pachete
        sudo python3 ex_03_packet_sniffer.py -i eth0 -c 100
        
        # Export JSON
        sudo python3 ex_03_packet_sniffer.py --output captura.json
        
        # Filtru BPF custom
        sudo python3 ex_03_packet_sniffer.py --bpf "tcp port 1883 and host 10.0.13.110"
    """
    parser = argparse.ArgumentParser(
        description="Packet Sniffer pentru IoT și Securitate în Rețele",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  %(prog)s                           # Captură pe toate interfețele
  %(prog)s -i docker0 --filter mqtt  # MQTT pe docker0
  %(prog)s -c 50 --output cap.json   # 50 pachete, export JSON
  %(prog)s --bpf "tcp port 80"       # Filtru BPF custom
  %(prog)s --list-interfaces         # Listează interfețe disponibile
  %(prog)s --list-filters            # Listează filtre predefinite
        """
    )
    
    parser.add_argument(
        '-i', '--interface',
        default='any',
        help='Interfața de captură (default: any)'
    )
    
    parser.add_argument(
        '-c', '--count',
        type=int,
        default=0,
        help='Număr maxim de pachete (default: infinit)'
    )
    
    parser.add_argument(
        '--bpf',
        default='',
        help='Filtru BPF custom (ex: "tcp port 1883")'
    )
    
    parser.add_argument(
        '--filter',
        choices=list(get_predefined_filters().keys()),
        help='Filtru predefinit: mqtt, http, ftp, dns, pentest, iot'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Fișier JSON pentru export statistici'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=1,
        help='Nivel verbozitate (-v, -vv, -vvv)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Mod silențios (doar statistici la final)'
    )
    
    parser.add_argument(
        '--list-interfaces',
        action='store_true',
        help='Listează interfețele de rețea disponibile'
    )
    
    parser.add_argument(
        '--list-filters',
        action='store_true',
        help='Listează filtrele predefinite'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Dezactivează output colorat'
    )
    
    args = parser.parse_args()
    
    # Dezactivare culori
    if args.no_color:
        Culori.disable()
    
    # Listare interfețe
    if args.list_interfaces:
        lista_interfete()
        return
    
    # Listare filtre
    if args.list_filters:
        print(f"\n{Culori.CYAN}Filtre BPF predefinite:{Culori.RESET}")
        for name, bpf in get_predefined_filters().items():
            print(f"  {Culori.GREEN}{name:10}{Culori.RESET} → {bpf}")
        print()
        return
    
    # Determinare filtru BPF
    bpf_filter = args.bpf
    if args.filter:
        bpf_filter = get_predefined_filters()[args.filter]
    
    # Verbose level
    verbose = 0 if args.quiet else args.verbose
    
    # Creare și pornire sniffer
    sniffer = PacketSniffer(
        interface=args.interface,
        packet_count=args.count,
        bpf_filter=bpf_filter,
        verbose=verbose,
        output_file=args.output
    )
    
    # Disclaimer
    print(f"""
{Culori.YELLOW}{'='*70}
  DISCLAIMER: Acest instrument este destinat EXCLUSIV pentru
  medii de testare controlate (laboratoare, containere Docker).
  
  Interceptarea traficului de rețea fără autorizare este ILEGALĂ!
{'='*70}{Culori.RESET}
    """)
    
    sniffer.start()


if __name__ == "__main__":
    main()
