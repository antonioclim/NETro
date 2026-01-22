# Curs 13 — IoT și Securitate în Rețele de Calculatoare

## Obiective de Învățare

La finalul acestui curs, studenții vor fi capabili să:
- Identifice componentele arhitecturale ale sistemelor IoT
- Explice funcționarea protocoalelor MQTT și CoAP
- Clasifice amenințările de securitate specifice IoT
- Evalueze vulnerabilitățile comune în infrastructuri de rețea
- Propună măsuri de protecție adecvate

## 1. Introducere în IoT

### Ce este Internet of Things?

Internet of Things (IoT) reprezintă rețeaua de dispozitive fizice echipate cu senzori, software și conectivitate care le permite să colecteze și să schimbe date.

**Statistici relevante (2025):**
- ~15 miliarde dispozitive IoT conectate global
- Creștere anuală de ~25%
- 70% din dispozitive au vulnerabilități critice

### Arhitectura pe 5 Straturi

1. **Stratul Dispozitive** — Senzori, actuatoare, microcontrollere
2. **Stratul Gateway** — Agregare, traducere protocoale, edge computing
3. **Stratul Comunicare** — MQTT, CoAP, HTTP, WebSocket
4. **Stratul Platformă** — Cloud, procesare, stocare
5. **Stratul Aplicație** — Dashboard-uri, analize, automatizări

## 2. Protocolul MQTT

### Caracteristici Fundamentale

Message Queuing Telemetry Transport (MQTT) este protocolul dominant în IoT:
- Model **publish/subscribe** cu broker intermediar
- Overhead redus (header minim 2 bytes)
- Suport pentru conexiuni instabile
- Porturi: 1883 (plaintext), 8883 (TLS)

### Quality of Service (QoS)

| QoS | Denumire | Garantie | Use Case |
|-----|----------|----------|----------|
| 0 | At most once | Fire & forget | Telemetrie non-critică |
| 1 | At least once | Cu confirmare, posibile duplicate | Comenzi, alerte |
| 2 | Exactly once | Handshake 4-way | Tranzacții financiare |

### Structura Topicurilor

Topicurile MQTT au structură ierarhică: `home/kitchen/temperature`

Wildcards:
- `+` — Un singur nivel: `home/+/temperature`
- `#` — Toate sub-nivelurile: `home/#`

## 3. Amenințări și Vulnerabilități

### OWASP IoT Top 10

1. Weak/Default Passwords
2. Insecure Network Services
3. Insecure Ecosystem Interfaces
4. Lack of Secure Update
5. Use of Insecure Components
6. Insufficient Privacy Protection
7. Insecure Data Transfer/Storage
8. Lack of Device Management
9. Insecure Default Settings
10. Lack of Physical Hardening

### Cyber Kill Chain

Modelul Lockheed Martin descrie fazele unui atac:
1. **Reconnaissance** — Scanare, OSINT
2. **Weaponization** — Creare payload
3. **Delivery** — Livrare (email, web, USB)
4. **Exploitation** — Exploatare vulnerabilitate
5. **Installation** — Persistență
6. **C2** — Command & Control
7. **Actions** — Exfiltrare, sabotaj

## 4. Măsuri Defensive

### Defense in Depth

Straturi multiple de protecție:
- Perimetru (firewall, DMZ)
- Rețea (segmentare, IDS/IPS)
- Host (hardening, AV)
- Aplicație (WAF, input validation)
- Date (criptare, backup)

### Principii de Securitate

- **Least Privilege** — Permisiuni minime necesare
- **Zero Trust** — Never trust, always verify
- **Fail Secure** — Eșec în stare sigură

### Implementare TLS pentru MQTT

```bash
# Generare certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ca.key -out ca.crt -subj "/CN=IoT-CA"

# Configurare broker
listener 8883
cafile /path/to/ca.crt
certfile /path/to/server.crt
keyfile /path/to/server.key
```

## 5. Studiu de Caz: Mirai Botnet

### Context

În 2016, botnetul Mirai a infectat ~600.000 dispozitive IoT, lansând atacuri DDoS de peste 1 Tbps.

### Vector de atac

- Scanare porturi Telnet (23) și SSH (22)
- Încercare credențiale default (62 de combinații)
- Infectare și propagare

### Lecții învățate

1. Schimbarea credențialelor default este critică
2. Segmentarea rețelei limitează propagarea
3. Monitorizarea traficului anormal permite detecție

## Bibliografie

- Kurose & Ross (2016). Computer Networking: A Top-Down Approach
- OWASP IoT Top 10 (2024)
- MQTT v5.0 Specification (OASIS)
- NIST SP 800-183: Networks of 'Things'

---
*Revolvix&Hypotheticalandrei | ASE-CSIE | 2025-2026*
