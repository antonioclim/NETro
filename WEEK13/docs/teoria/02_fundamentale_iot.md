# 2. Fundamentele IoT și Protocoale de Comunicație

## 2.1 Arhitectura Sistemelor IoT

### Modelul cu Trei Niveluri

Arhitectura de referință IoT cuprinde trei straturi funcționale interdependente:

**Stratul de Percepție (Perception Layer)** constituie interfața cu lumea fizică și include:
- Senzori pentru măsurători de mediu (temperatură, umiditate, presiune, luminozitate)
- Senzori de poziție și mișcare (accelerometre, giroscoape, GPS)
- Actuatoare pentru acțiuni fizice (relee, valve, motoare)
- Circuite de condiționare a semnalului și conversie analog-digitală

**Stratul de Rețea (Network Layer)** asigură transportul datelor și cuprinde:
- Protocoale de comunicație wireless (WiFi, Zigbee, LoRa, BLE, NB-IoT)
- Gateway-uri pentru agregarea și traducerea protocoalelor
- Infrastructură de transport (Internet, rețele private, LPWAN)
- Mecanisme de adresare și rutare

**Stratul Aplicație (Application Layer)** oferă funcționalități pentru utilizatori:
- Platforme cloud pentru stocare și procesare
- Dashboard-uri pentru vizualizare în timp real
- Motoare de analiză și machine learning
- Interfețe API pentru integrare cu sisteme terțe

```
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                             │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │  Dashboard  │  │   Analytics  │  │     API Gateway        │  │
│  │  (React)    │  │   (Python)   │  │     (REST/GraphQL)     │  │
│  └─────────────┘  └──────────────┘  └────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                      NETWORK LAYER                               │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │   Gateway   │  │  MQTT Broker │  │    Cloud Connector     │  │
│  │  (Zigbee→IP)│  │  (Mosquitto) │  │    (AWS IoT Core)      │  │
│  └─────────────┘  └──────────────┘  └────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    PERCEPTION LAYER                              │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │  Temp/Hum   │  │   Motion     │  │      Actuators         │  │
│  │  (DHT22)    │  │   (PIR)      │  │      (Relay)           │  │
│  └─────────────┘  └──────────────┘  └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Modelul cu Cinci Niveluri (Cisco IoT Reference Model)

O granularitate superioară oferă modelul cu cinci niveluri:

1. **Dispozitive Fizice** - Hardware, senzori, actuatoare
2. **Conectivitate** - Protocoale de comunicație, rețelistică
3. **Edge Computing** - Procesare locală, filtrare, agregare
4. **Acumulare Date** - Stocare, normalizare, conversie
5. **Abstractizare** - API-uri, servicii, logică de business
6. **Aplicații** - Interfețe utilizator, rapoarte, automatizări
7. **Colaborare & Procese** - Integrare cu sisteme enterprise

## 2.2 Protocoale de Comunicație IoT

### MQTT (Message Queuing Telemetry Transport)

MQTT reprezintă protocolul dominant în comunicațiile IoT datorită eficienței și simplității sale.

**Caracteristici fundamentale:**
- Model publish/subscribe cu broker intermediar
- Overhead redus (header minim 2 bytes)
- Suport pentru conexiuni instabile
- Trei niveluri de Quality of Service

**Arhitectura Publish/Subscribe:**

```
                    ┌────────────────────┐
    PUBLISH         │                    │         PUBLISH
   home/temp ──────▶│   MQTT BROKER      │◀────── sensors/motion
                    │   (Mosquitto)      │
    SUBSCRIBE       │                    │         SUBSCRIBE  
   home/# ◀─────────│                    │──────▶ sensors/+/data
                    └────────────────────┘
         │                    │                    │
    ┌────┴────┐          ┌────┴────┐          ┌────┴────┐
    │ Sensor  │          │ Sensor  │          │Dashboard│
    │  DHT22  │          │   PIR   │          │ (React) │
    └─────────┘          └─────────┘          └─────────┘
```

**Niveluri QoS (Quality of Service):**

| QoS | Denumire | Garantie | Use Case |
|-----|----------|----------|----------|
| 0 | At most once | Fire & forget, fără confirmare | Telemetrie non-critică |
| 1 | At least once | Confirmare, posibile duplicate | Comenzi, alerte |
| 2 | Exactly once | Handshake 4-way, fără pierderi/duplicate | Tranzacții financiare |

**Structura pachetului MQTT CONNECT:**

```
┌────────────────────────────────────────────────────────────────┐
│ Fixed Header (2+ bytes)                                        │
├────────────────────────────────────────────────────────────────┤
│ Byte 1: Packet Type (0x10 = CONNECT) + Flags                   │
│ Byte 2+: Remaining Length (variable encoding)                  │
├────────────────────────────────────────────────────────────────┤
│ Variable Header                                                │
├────────────────────────────────────────────────────────────────┤
│ Protocol Name: "MQTT" (UTF-8 encoded)                          │
│ Protocol Level: 4 (MQTT 3.1.1) or 5 (MQTT 5.0)                │
│ Connect Flags: CleanSession, Will, WillQoS, WillRetain, Auth   │
│ Keep Alive: interval în secunde (uint16)                       │
├────────────────────────────────────────────────────────────────┤
│ Payload                                                        │
├────────────────────────────────────────────────────────────────┤
│ Client ID (obligatoriu)                                        │
│ Will Topic (opțional)                                          │
│ Will Message (opțional)                                        │
│ Username (opțional)                                            │
│ Password (opțional)                                            │
└────────────────────────────────────────────────────────────────┘
```

**Wildcards în Topic Subscription:**

- `+` (single-level): `home/+/temperature` → match `home/living/temperature`, `home/bedroom/temperature`
- `#` (multi-level): `home/#` → match `home/living/temperature`, `home/bedroom/humidity/raw`
- `$SYS/#` - topic-uri sistem pentru monitorizarea broker-ului

### CoAP (Constrained Application Protocol)

CoAP este proiectat pentru dispozitive cu resurse extrem de limitate și rețele cu pierderi mari.

**Caracteristici:**
- Bazat pe UDP (overhead redus vs TCP)
- Model request/response similar HTTP
- Suport pentru observare (notifications)
- Mapping nativ către HTTP pentru gateway-uri

**Comparație MQTT vs CoAP:**

| Aspect | MQTT | CoAP |
|--------|------|------|
| Transport | TCP | UDP |
| Model | Pub/Sub | Request/Response |
| Header | 2 bytes minim | 4 bytes fix |
| Discovery | Nu nativ | Resource Directory |
| Observe | Reținere mesaje | Observer pattern |
| Security | TLS | DTLS |

### HTTP/HTTPS pentru IoT

Deși nu este optimizat pentru IoT, HTTP rămâne relevant pentru:
- Dispozitive cu resurse suficiente (Raspberry Pi, ESP32)
- Integrare cu servicii web existente
- RESTful API pentru configurare și management
- Webhook-uri pentru notificări

**Limitări în context IoT:**
- Overhead mare (header-e verbose)
- Conexiuni stateless (reconectare costisitoare)
- Nu există model publish/subscribe nativ
- TLS handshake costisitor energetic

### Protocoale de Nivel Fizic

**Zigbee (IEEE 802.15.4)**
- Frecvență: 2.4 GHz (global), 868 MHz (EU), 915 MHz (US)
- Rată: 250 kbps
- Rază: 10-100m
- Topologie: Mesh, Star, Tree
- Use case: Home automation, iluminat inteligent

**LoRa/LoRaWAN**
- Frecvență: 868 MHz (EU), 915 MHz (US), 433 MHz (Asia)
- Rată: 0.3-50 kbps
- Rază: 2-15 km (urban), 45+ km (rural, line of sight)
- Use case: Smart agriculture, asset tracking, utilities

**BLE (Bluetooth Low Energy)**
- Frecvență: 2.4 GHz
- Rată: 1-2 Mbps
- Rază: 10-100m
- Use case: Wearables, beacons, sănătate

**NB-IoT (Narrowband IoT)**
- Rețea celulară licențiată
- Rată: ~200 kbps
- Acoperire excelentă (inclusiv indoor, subteran)
- Use case: Utilități, smart city, asset tracking

## 2.3 Securitatea Protocoalelor IoT

### Vulnerabilități MQTT

**1. Autentificare slabă sau inexistentă:**
```bash
# Conexiune anonimă (implicit permisă în multe configurări)
mosquitto_sub -h broker.example.com -t "#" -v

# Interceptare credențiale în clar
tcpdump -i eth0 port 1883 -A | grep -E "(username|password)"
```

**2. Lipsa criptării (port 1883):**
- Traficul este vizibil pentru oricine pe rețea
- Topic-uri, payload-uri și credențiale expuse
- Mitigare: utilizare TLS pe port 8883

**3. Topic Wildcards abuzate:**
```bash
# Subscriber malițios care primește TOATE mesajele
mosquitto_sub -h broker.example.com -t "#" -v
```

**4. Lipsa controlului accesului:**
- Fără ACL, orice client poate publica/subscrie oriunde
- Posibilitate de injectare comenzi false
- Exfiltrare date din topic-uri sensibile

### Securizarea MQTT

**Configurare TLS (mosquitto.conf):**
```ini
# Port securizat
listener 8883

# Certificate
cafile /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key

# Forțare TLS 1.2+
tls_version tlsv1.2

# Dezactivare anonim
allow_anonymous false

# Fișier parole (generat cu mosquitto_passwd)
password_file /etc/mosquitto/passwd

# Access Control List
acl_file /etc/mosquitto/acl
```

**Exemplu ACL (/etc/mosquitto/acl):**
```
# Utilizator admin - acces total
user admin
topic readwrite #

# Senzor - doar publicare pe topic propriu
user sensor_001
topic write sensors/001/#
topic read commands/001/#

# Dashboard - doar citire
user dashboard
topic read sensors/#
topic read status/#
```

### Vulnerabilități la Nivel Transport

**ARP Spoofing** permite interceptarea traficului local:
```
Înainte de atac:
Sensor ────────────────────▶ Gateway ────▶ Broker

După ARP Spoofing:
Sensor ────▶ Attacker ────▶ Gateway ────▶ Broker
                │
                ▼
           Interceptare
```

**DNS Spoofing** poate redirecționa dispozitivele către broker-uri malițioase.

**Replay Attacks** - Capturarea și retransmiterea mesajelor legitime:
- Mitigare: Timestamp-uri, nonce-uri, sequence numbers
- TLS previne replay la nivel transport

## 2.4 Implementare Practică

### Client MQTT în Python

```python
import paho.mqtt.client as mqtt
import ssl
import json
from datetime import datetime

class SecureMQTTClient:
    def __init__(self, broker, port=8883, username=None, password=None):
        self.client = mqtt.Client(protocol=mqtt.MQTTv311)
        self.broker = broker
        self.port = port
        
        # Configurare TLS
        self.client.tls_set(
            ca_certs="/path/to/ca.crt",
            certfile="/path/to/client.crt",  # Opțional: mutual TLS
            keyfile="/path/to/client.key",
            tls_version=ssl.PROTOCOL_TLS
        )
        
        # Autentificare
        if username and password:
            self.client.username_pw_set(username, password)
        
        # Callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
    
    def _on_connect(self, client, userdata, flags, rc):
        codes = {
            0: "Conectat cu succes",
            1: "Protocol incorect",
            2: "Client ID invalid",
            3: "Server indisponibil",
            4: "Credențiale invalide",
            5: "Neautorizat"
        }
        print(f"[CONNECT] {codes.get(rc, f'Eroare necunoscută: {rc}')}")
    
    def _on_message(self, client, userdata, msg):
        print(f"[MSG] {msg.topic}: {msg.payload.decode()}")
    
    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"[DISCONNECT] Conexiune pierdută neașteptat: {rc}")
    
    def connect(self):
        self.client.connect(self.broker, self.port, keepalive=60)
        self.client.loop_start()
    
    def publish_sensor_data(self, sensor_id, temperature, humidity):
        topic = f"sensors/{sensor_id}/data"
        payload = json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "temperature": temperature,
            "humidity": humidity
        })
        self.client.publish(topic, payload, qos=1)
    
    def subscribe(self, topic, qos=1):
        self.client.subscribe(topic, qos)
```

### Capturarea și Analiza Traficului MQTT

```python
from scapy.all import *

def mqtt_sniffer(interface="eth0"):
    """
    Capturează și analizează trafic MQTT.
    ATENȚIE: Necesită privilegii root!
    """
    
    def parse_mqtt(packet):
        if packet.haslayer(TCP) and packet.haslayer(Raw):
            raw = packet[Raw].load
            
            # Primul byte conține tipul pachetului (biții 7-4)
            packet_type = (raw[0] & 0xF0) >> 4
            
            types = {
                1: "CONNECT", 2: "CONNACK", 3: "PUBLISH",
                4: "PUBACK", 5: "PUBREC", 6: "PUBREL",
                7: "PUBCOMP", 8: "SUBSCRIBE", 9: "SUBACK",
                10: "UNSUBSCRIBE", 11: "UNSUBACK",
                12: "PINGREQ", 13: "PINGRESP", 14: "DISCONNECT"
            }
            
            print(f"[MQTT] {types.get(packet_type, 'UNKNOWN')}")
            
            # Pentru PUBLISH, extrage topic
            if packet_type == 3:
                # Lungime topic (bytes 2-3)
                topic_len = (raw[2] << 8) + raw[3]
                topic = raw[4:4+topic_len].decode('utf-8', errors='ignore')
                print(f"  Topic: {topic}")
    
    sniff(iface=interface, filter="port 1883", prn=parse_mqtt)
```

## 2.5 Mininet pentru Simulare IoT

Mininet permite crearea de topologii de rețea virtuale pentru testare și educație.

### Topologie IoT de Bază

```python
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, Host
from mininet.link import TCLink
from mininet.cli import CLI

def create_iot_topology():
    net = Mininet(switch=OVSKernelSwitch, link=TCLink)
    
    # Noduri
    sensor1 = net.addHost('sensor1', ip='10.0.0.11/24')
    sensor2 = net.addHost('sensor2', ip='10.0.0.12/24')
    broker = net.addHost('broker', ip='10.0.0.100/24')
    controller = net.addHost('controller', ip='10.0.0.20/24')
    
    # Switch
    switch = net.addSwitch('s1')
    
    # Legături cu caracteristici realiste
    net.addLink(sensor1, switch, bw=100, delay='2ms')
    net.addLink(sensor2, switch, bw=100, delay='2ms')
    net.addLink(broker, switch, bw=1000, delay='1ms')
    net.addLink(controller, switch, bw=1000, delay='1ms')
    
    net.start()
    
    # Pornire broker MQTT pe nodul broker
    broker.cmd('mosquitto -d')
    
    return net
```

### Scenarii de Atac în Mininet

**Interceptarea traficului (Man-in-the-Middle):**
```python
# Pe nodul atacator
attacker.cmd('tcpdump -i attacker-eth0 -w /tmp/capture.pcap &')

# Analiza ulterioară
attacker.cmd('tcpdump -r /tmp/capture.pcap -A | grep -E "(PUBLISH|username)"')
```

**Injectarea de mesaje false:**
```python
# Atacator publică date false pretinzând a fi sensor legitim
attacker.cmd('mosquitto_pub -h 10.0.0.100 -t "sensors/001/data" '
             '-m \'{"temperature": 999, "alert": true}\'')
```

## Rezumat

Arhitectura IoT se bazează pe trei straturi fundamentale (percepție, rețea, aplicație) cu MQTT ca protocol dominant pentru comunicații. Securitatea implică criptare TLS, autentificare solidă și liste de control al accesului. Mininet oferă un mediu ideal pentru simularea și testarea scenariilor de atac și apărare.

## Întrebări de Verificare

1. Care sunt cele trei niveluri QoS în MQTT și când se utilizează fiecare?
2. Explicați diferența dintre wildcard-urile `+` și `#` în subscripțiile MQTT.
3. De ce CoAP folosește UDP în loc de TCP?
4. Care sunt principalele vulnerabilități ale unei configurări MQTT implicite?
5. Cum protejează TLS împotriva atacurilor de interceptare?

## Referințe

- MQTT Version 3.1.1 - OASIS Standard (2014)
- MQTT Version 5.0 - OASIS Standard (2019)
- RFC 7252 - Constrained Application Protocol (CoAP)
- Mosquitto Documentation - https://mosquitto.org/documentation/
