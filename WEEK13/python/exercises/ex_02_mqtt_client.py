#!/usr/bin/env python3
"""
================================================================================
Exercițiul 2: Client MQTT (Publisher/Subscriber)
================================================================================
S13 - IoT și Securitate în Rețele de Calculatoare

OBIECTIVE PEDAGOGICE:
1. Înțelegerea modelului publish-subscribe
2. Implementarea comunicării MQTT plaintext și TLS
3. Configurarea autentificării și QoS
4. Analiza diferențelor de securitate între moduri

CONCEPTE CHEIE:
- Topic: canal de comunicare (ex: home/kitchen/temperature)
- Publisher: trimite mesaje pe un topic
- Subscriber: primește mesaje de pe topic-uri
- QoS: Quality of Service (0 = fire-and-forget, 1 = at least once, 2 = exactly once)
- TLS: Transport Layer Security (criptare end-to-end)

UTILIZARE:
    # Controller (subscriber) - plaintext
    python3 ex_02_mqtt_client.py --role controller --host 10.0.0.100 --port 1883 \\
        --topic home/kitchen/telemetry

    # Sensor (publisher) - plaintext
    python3 ex_02_mqtt_client.py --role sensor --host 10.0.0.100 --port 1883 \\
        --topic home/kitchen/telemetry --payload '{"temp":22.5}' --count 5

    # Cu TLS și autentificare
    python3 ex_02_mqtt_client.py --role sensor --host 10.0.0.100 --port 8883 \\
        --tls on --cafile configs/certs/ca.crt \\
        --username sensor1 --password sensor1pass \\
        --topic home/kitchen/telemetry
================================================================================
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime
from typing import Optional

# ==============================================================================
# VERIFICARE DEPENDENȚE
# ==============================================================================

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("[FATAL] Biblioteca paho-mqtt nu este instalată!")
    print("        Rulează: pip install paho-mqtt")
    sys.exit(1)

# ==============================================================================
# CONSTANTE ȘI CONFIGURĂRI
# ==============================================================================

class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


# Coduri de returnare MQTT
MQTT_RC_CODES = {
    0: "Connection successful",
    1: "Connection refused - incorrect protocol version",
    2: "Connection refused - invalid client identifier",
    3: "Connection refused - server unavailable",
    4: "Connection refused - bad username or password",
    5: "Connection refused - not authorised"
}


# ==============================================================================
# FUNCȚII AUXILIARE
# ==============================================================================

def generate_sensor_data() -> dict:
    """
    Generează date simulate de senzor IoT.
    
    Simulează un senzor de mediu cu:
    - Temperatură (°C)
    - Umiditate (%)
    - Presiune (hPa)
    - Luminozitate (lux)
    """
    return {
        "device_id": f"sensor_{os.getpid()}",
        "timestamp": datetime.now().isoformat(),
        "readings": {
            "temperature_c": round(20 + random.gauss(0, 2), 2),
            "humidity_pct": round(50 + random.gauss(0, 10), 1),
            "pressure_hpa": round(1013 + random.gauss(0, 5), 1),
            "light_lux": round(max(0, 500 + random.gauss(0, 100)), 0)
        },
        "status": "ok"
    }


def format_message(topic: str, payload: str, qos: int) -> str:
    """Formatează mesajul pentru afișare."""
    try:
        obj = json.loads(payload)
        formatted = json.dumps(obj, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        formatted = payload
    return formatted


# ==============================================================================
# CLIENT MQTT
# ==============================================================================

class MQTTClient:
    """
    Client MQTT cu suport pentru plaintext și TLS.
    
    Această clasă încapsulează funcționalitatea paho-mqtt și oferă
    o interfață simplificată pentru scenariile de laborator.
    """
    
    def __init__(
        self,
        role: str,  # "sensor" sau "controller"
        host: str,
        port: int,
        topic: str,
        qos: int = 0,
        tls: bool = False,
        cafile: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: Optional[str] = None
    ):
        self.role = role
        self.host = host
        self.port = port
        self.topic = topic
        self.qos = qos
        self.tls = tls
        self.connected = False
        self.message_count = 0
        
        # Generăm un client ID unic dacă nu e furnizat
        self.client_id = client_id or f"{role}_{os.getpid()}"
        
        # ========================================
        # SECȚIUNEA STUDENT - Creare client MQTT
        # ========================================
        # Creăm clientul paho-mqtt
        self.client = mqtt.Client(
            client_id=self.client_id,
            clean_session=True,
            protocol=mqtt.MQTTv311
        )
        
        # Configurăm autentificarea dacă e necesară
        if username:
            self.client.username_pw_set(username, password)
        
        # Configurăm TLS dacă e activat
        if tls:
            if not cafile:
                raise ValueError("TLS activat dar cafile nu e specificat!")
            self.client.tls_set(ca_certs=cafile)
            self.client.tls_insecure_set(False)
        
        # Înregistrăm callback-urile
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback apelat la conectare."""
        if rc == 0:
            self.connected = True
            print(f"{Colors.GREEN}[✓] Conectat la broker{Colors.RESET}")
            print(f"    Host: {self.host}:{self.port}")
            print(f"    TLS: {'DA' if self.tls else 'NU'}")
            print(f"    Client ID: {self.client_id}")
            
            # Dacă suntem controller (subscriber), ne abonăm
            if self.role == "controller":
                self.client.subscribe(self.topic, qos=self.qos)
                print(f"    {Colors.BLUE}Abonat la: {self.topic} (QoS={self.qos}){Colors.RESET}")
        else:
            print(f"{Colors.RED}[✗] Conexiune eșuată: {MQTT_RC_CODES.get(rc, f'Unknown error ({rc})')}{Colors.RESET}")
    
    def _on_message(self, client, userdata, msg):
        """Callback apelat la primirea unui mesaj."""
        self.message_count += 1
        
        try:
            payload = msg.payload.decode("utf-8", errors="replace")
        except Exception:
            payload = str(msg.payload)
        
        print(f"\n{Colors.CYAN}[MSG #{self.message_count}]{Colors.RESET}")
        print(f"  Topic: {msg.topic}")
        print(f"  QoS: {msg.qos}")
        print(f"  Payload: {format_message(msg.topic, payload, msg.qos)}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback apelat la deconectare."""
        self.connected = False
        if rc == 0:
            print(f"{Colors.YELLOW}[i] Deconectat de la broker{Colors.RESET}")
        else:
            print(f"{Colors.RED}[!] Conexiune pierdută (rc={rc}){Colors.RESET}")
    
    def _on_publish(self, client, userdata, mid):
        """Callback apelat la publicarea cu succes a unui mesaj."""
        pass  # Log minimal pentru a nu polua output-ul
    
    def connect(self, timeout: float = 10.0) -> bool:
        """Conectează la broker."""
        print(f"\n{Colors.BOLD}[*] Conectare la broker MQTT...{Colors.RESET}")
        
        try:
            self.client.connect(self.host, self.port, keepalive=60)
            self.client.loop_start()
            
            # Așteptăm conexiunea
            start = time.time()
            while not self.connected and (time.time() - start) < timeout:
                time.sleep(0.1)
            
            return self.connected
        
        except Exception as e:
            print(f"{Colors.RED}[✗] Eroare conectare: {e}{Colors.RESET}")
            return False
    
    def disconnect(self):
        """Deconectează de la broker."""
        self.client.loop_stop()
        self.client.disconnect()
    
    def publish(self, payload: str, retain: bool = False) -> bool:
        """
        Publică un mesaj pe topic.
        
        Args:
            payload: Conținutul mesajului (string, de obicei JSON)
            retain: Dacă mesajul să fie reținut pentru subscriberi noi
        
        Returns:
            True dacă publicarea a reușit
        """
        if not self.connected:
            print(f"{Colors.RED}[!] Nu sunt conectat la broker{Colors.RESET}")
            return False
        
        # ========================================
        # SECȚIUNEA STUDENT - Publicare mesaj
        # ========================================
        info = self.client.publish(
            topic=self.topic,
            payload=payload,
            qos=self.qos,
            retain=retain
        )
        
        # Așteptăm confirmarea pentru QoS > 0
        if self.qos > 0:
            info.wait_for_publish(timeout=5.0)
        
        return info.is_published() if self.qos > 0 else True
    
    def run_publisher(self, count: int = 1, interval: float = 1.0, custom_payload: Optional[str] = None):
        """
        Rulează în modul publisher (sensor).
        
        Publică mesaje periodice cu date simulate sau payload custom.
        """
        print(f"\n{Colors.BOLD}[*] Mod Publisher - {count} mesaje{Colors.RESET}")
        print(f"    Topic: {self.topic}")
        print(f"    Interval: {interval}s")
        print(f"    QoS: {self.qos}")
        print()
        
        for i in range(count):
            # Generăm payload-ul
            if custom_payload:
                try:
                    data = json.loads(custom_payload)
                except json.JSONDecodeError:
                    data = {"raw": custom_payload}
            else:
                data = generate_sensor_data()
            
            # Adăugăm metadate
            data["sequence"] = i + 1
            data["total"] = count
            
            payload = json.dumps(data, ensure_ascii=False)
            
            # Publicăm
            if self.publish(payload):
                print(f"{Colors.GREEN}[PUB #{i+1}]{Colors.RESET} {self.topic}")
                print(f"  {payload[:100]}{'...' if len(payload) > 100 else ''}")
            else:
                print(f"{Colors.RED}[!] Publicare eșuată pentru mesaj #{i+1}{Colors.RESET}")
            
            # Pauză între mesaje
            if i < count - 1:
                time.sleep(interval)
        
        print(f"\n{Colors.GREEN}[✓] Publicare completă ({count} mesaje){Colors.RESET}")
    
    def run_subscriber(self):
        """
        Rulează în modul subscriber (controller).
        
        Ascultă mesaje până la Ctrl+C.
        """
        print(f"\n{Colors.BOLD}[*] Mod Subscriber - așteaptă mesaje...{Colors.RESET}")
        print(f"    Topic: {self.topic}")
        print(f"    QoS: {self.qos}")
        print(f"    (Ctrl+C pentru oprire)")
        print()
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}[i] Oprire la cererea utilizatorului{Colors.RESET}")
            print(f"    Mesaje primite: {self.message_count}")


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Client MQTT pentru laborator S13",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  # Subscriber (controller)
  %(prog)s --role controller --host 10.0.0.100 --port 1883 --topic home/temp

  # Publisher (sensor)  
  %(prog)s --role sensor --host 10.0.0.100 --port 1883 --topic home/temp --count 5

  # Cu TLS
  %(prog)s --role sensor --host 10.0.0.100 --port 8883 --tls on \\
      --cafile configs/certs/ca.crt --username sensor1 --password pass123
        """
    )
    
    # Argumente obligatorii
    parser.add_argument("--role", required=True, choices=["sensor", "controller"],
                        help="Rol: sensor (publisher) sau controller (subscriber)")
    parser.add_argument("--host", required=True,
                        help="Adresa broker MQTT")
    parser.add_argument("--topic", required=True,
                        help="Topic MQTT (ex: home/kitchen/telemetry)")
    
    # Argumente opționale
    parser.add_argument("--port", type=int, default=1883,
                        help="Port broker (default: 1883, TLS: 8883)")
    parser.add_argument("--qos", type=int, choices=[0, 1, 2], default=0,
                        help="Quality of Service (default: 0)")
    
    # TLS și autentificare
    parser.add_argument("--tls", choices=["on", "off"], default="off",
                        help="Activare TLS (default: off)")
    parser.add_argument("--cafile",
                        help="Certificat CA pentru TLS")
    parser.add_argument("--username",
                        help="Username pentru autentificare")
    parser.add_argument("--password",
                        help="Parolă pentru autentificare")
    
    # Opțiuni publisher
    parser.add_argument("--count", type=int, default=1,
                        help="Număr mesaje de publicat (default: 1)")
    parser.add_argument("--interval", type=float, default=1.0,
                        help="Interval între mesaje în secunde (default: 1.0)")
    parser.add_argument("--payload",
                        help="Payload custom (JSON string)")
    
    # Alte opțiuni
    parser.add_argument("--client-id",
                        help="Client ID custom")
    
    args = parser.parse_args()
    
    # Banner
    print(f"\n{Colors.CYAN}{'='*60}")
    print("  S13 - Client MQTT pentru laborator IoT")
    print(f"{'='*60}{Colors.RESET}")
    
    # Creăm clientul
    client = MQTTClient(
        role=args.role,
        host=args.host,
        port=args.port,
        topic=args.topic,
        qos=args.qos,
        tls=(args.tls == "on"),
        cafile=args.cafile,
        username=args.username,
        password=args.password,
        client_id=args.client_id
    )
    
    # Conectăm
    if not client.connect():
        print(f"\n{Colors.RED}[✗] Nu s-a putut conecta la broker{Colors.RESET}")
        sys.exit(1)
    
    try:
        if args.role == "sensor":
            client.run_publisher(
                count=args.count,
                interval=args.interval,
                custom_payload=args.payload
            )
        else:
            client.run_subscriber()
    
    finally:
        client.disconnect()
    
    print()


if __name__ == "__main__":
    main()
