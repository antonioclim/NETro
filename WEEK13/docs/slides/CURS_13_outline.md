# CURS 13 — IoT și Securitate în Rețele de Calculatoare

## Schița prezentării pentru curs (2 ore)

---

## SLIDE 1: Pagină de titlu

**Titlu**: IoT și Securitate în Rețele de Calculatoare  
**Curs 13 — Rețele de Calculatoare**  
**An universitar 2025-2026, Semestrul 2**  
**Academia de Studii Economice din București**  
**Facultatea de Cibernetică, Statistică și Informatică Economică**

---

## SLIDE 2: Agenda cursului

1. Introducere în Internet of Things (IoT) — 20 min
2. Protocoale de comunicare IoT — 25 min
3. Amenințări și vectori de atac — 25 min
4. Măsuri defensive și best practices — 20 min
5. Studii de caz și demonstrații — 15 min
6. Recapitulare și pregătire examen — 15 min

---

## SLIDE 3: Obiective de învățare

La finalul acestui curs, studenții vor fi capabili să:

- **Identifice** componentele arhitecturale ale sistemelor IoT
- **Explice** funcționarea protocoalelor MQTT, CoAP și HTTP în context IoT
- **Clasifice** amenințările de securitate specifice dispozitivelor IoT
- **Evalueze** vulnerabilitățile comune în infrastructuri de rețea
- **Propună** măsuri de protecție adecvate pentru scenarii reale
- **Analizeze** traficul de rețea pentru identificarea anomaliilor

---

## SLIDE 4: Ce este IoT?

### Definiție
**Internet of Things** = Rețea de dispozitive fizice echipate cu senzori, software și conectivitate care le permit să colecteze și să schimbe date.

### Statistici (2025)
- ~15 miliarde dispozitive IoT conectate global
- Creștere anuală de ~25%
- 70% din dispozitive au vulnerabilități critice de securitate

### Domenii de aplicare
- Smart Home / Smart Building
- Industrial IoT (IIoT)
- Healthcare / Wearables
- Smart Cities / Transport
- Agriculture de precizie

---

## SLIDE 5: Arhitectura IoT pe straturi

```
┌─────────────────────────────────────────────┐
│           STRATUL APLICAȚIE                 │
│  Dashboard-uri, Analiză, Automatizări       │
├─────────────────────────────────────────────┤
│           STRATUL PLATFORMĂ/CLOUD           │
│  Procesare date, Storage, API-uri           │
├─────────────────────────────────────────────┤
│           STRATUL COMUNICARE                │
│  MQTT, CoAP, HTTP, WebSocket, LoRaWAN       │
├─────────────────────────────────────────────┤
│           STRATUL GATEWAY                   │
│  Agregare, Protocol translation, Edge       │
├─────────────────────────────────────────────┤
│           STRATUL DISPOZITIVE               │
│  Senzori, Actuatori, Microcontrollere       │
└─────────────────────────────────────────────┘
```

---

## SLIDE 6: Protocolul MQTT

### Message Queuing Telemetry Transport

**Caracteristici**:
- Protocol publish/subscribe
- Foarte ușor (overhead minimal)
- Optimizat pentru conexiuni nesigure
- Porturi: 1883 (plaintext), 8883 (TLS)

**Concepte cheie**:
- **Broker**: Intermediar central
- **Topic**: Canal de comunicare (`home/kitchen/temperature`)
- **Publisher**: Trimite mesaje
- **Subscriber**: Primește mesaje
- **QoS**: 0 (fire-and-forget), 1 (at least once), 2 (exactly once)

---

## SLIDE 7: Diagrama MQTT

```
     Publisher                              Subscriber
    (Sensor)                               (Controller)
        │                                       │
        │ CONNECT                               │ CONNECT
        ├─────────────────►┌──────┐◄────────────┤
        │                  │      │             │
        │ PUBLISH          │Broker│  SUBSCRIBE  │
        │ topic: home/temp │      │  topic: #   │
        ├─────────────────►│      │◄────────────┤
        │                  │      │             │
        │                  │      │  PUBLISH    │
        │                  │      ├────────────►│
        │                  └──────┘             │
```

---

## SLIDE 8: QoS în MQTT

| QoS | Nume | Descriere | Utilizare |
|-----|------|-----------|-----------|
| 0 | At most once | Fire-and-forget, fără confirmare | Telemetrie frecventă, non-critică |
| 1 | At least once | Cu ACK, posibile duplicate | Alerte, statusuri importante |
| 2 | Exactly once | 4-way handshake, fără duplicate | Tranzacții, comenzi critice |

**Trade-off**: QoS mai mare = overhead mai mare, latență crescută

---

## SLIDE 9: Vectori de atac IoT

### Suprafața de atac extinsă

1. **Dispozitiv**
   - Firmware vulnerabil
   - Credențiale hardcodate
   - Interfețe de debug expuse

2. **Comunicare**
   - Lipsa criptării
   - Interceptare trafic (MITM)
   - Replay attacks

3. **Cloud/Backend**
   - API-uri nesecurizate
   - Injection attacks
   - Autentificare slabă

4. **Rețea**
   - Segmentare inadecvată
   - Servicii expuse nenecesar
   - Lipsa monitorizării

---

## SLIDE 10: OWASP IoT Top 10 (2024)

1. **Weak, Guessable, or Hardcoded Passwords**
2. **Insecure Network Services**
3. **Insecure Ecosystem Interfaces**
4. **Lack of Secure Update Mechanism**
5. **Use of Insecure or Outdated Components**
6. **Insufficient Privacy Protection**
7. **Insecure Data Transfer and Storage**
8. **Lack of Device Management**
9. **Insecure Default Settings**
10. **Lack of Physical Hardening**

---

## SLIDE 11: Studiu de caz — Mirai Botnet (2016)

### Context
- Malware care a infectat dispozitive IoT (camere IP, routere)
- A scanat internet pentru dispozitive cu credențiale default
- A format un botnet de ~600.000 dispozitive

### Atac
- DDoS de 1.2 Tbps contra Dyn DNS
- Au căzut: Twitter, Netflix, Spotify, Reddit, GitHub

### Lecții învățate
- **Schimbați** parolele default
- **Dezactivați** Telnet/SSH dacă nu e necesar
- **Segmentați** rețeaua IoT
- **Monitorizați** traficul outbound

---

## SLIDE 12: Procesul de Penetration Testing

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  1. RECON   │──►│ 2. SCANNING │──►│ 3. ENUMERA- │
│             │   │             │   │    TION     │
│ Informații  │   │ Porturi     │   │ Servicii    │
│ publice     │   │ deschise    │   │ Versiuni    │
└─────────────┘   └─────────────┘   └─────────────┘
                                           │
                                           ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ 6. REPORT   │◄──│ 5. POST-    │◄──│ 4. EXPLOIT- │
│             │   │ EXPLOITA-   │   │    ATION    │
│ Documentare │   │ TION        │   │ Vulnerabi-  │
│ Remediere   │   │ Pivot       │   │ lități      │
└─────────────┘   └─────────────┘   └─────────────┘
```

---

## SLIDE 13: Scanarea porturilor

### De ce scanăm?
- Identificăm serviciile expuse
- Detectăm configurări greșite
- Evaluăm suprafața de atac

### Stări ale porturilor
- **OPEN**: Serviciu activ, acceptă conexiuni
- **CLOSED**: Port accesibil, dar niciun serviciu
- **FILTERED**: Firewall blochează probe

### Tehnici de scanare
- **TCP Connect**: Full 3-way handshake
- **SYN Scan**: Half-open (stealth)
- **UDP Scan**: Servicii UDP (DNS, DHCP)
- **Version Detection**: Fingerprinting servicii

---

## SLIDE 14: Vulnerabilitatea vsftpd 2.3.4

### CVE-2011-2523 — Smiley Backdoor

**Ce s-a întâmplat**:
- Atacator a compromis serverul de distribuție vsftpd
- A injectat cod în sursa oficială
- Backdoor-ul verifica username pentru `:)`
- Dacă găsit, deschidea shell pe portul 6200

**Lecții**:
- Verificați integritatea software-ului (checksums)
- Monitorizați porturile neașteptate
- Actualizați software-ul prompt

---

## SLIDE 15: Măsuri defensive — Principii

### Defense in Depth
Straturi multiple de protecție:
```
┌─────────────────────────────────────┐
│         Politici și Proceduri       │
├─────────────────────────────────────┤
│           Firewall Perimetru        │
├─────────────────────────────────────┤
│         Segmentare Rețea            │
├─────────────────────────────────────┤
│         Criptare Transport          │
├─────────────────────────────────────┤
│         Autentificare/Autorizare    │
├─────────────────────────────────────┤
│         Hardening Dispozitive       │
└─────────────────────────────────────┘
```

---

## SLIDE 16: Criptarea traficului IoT

### TLS pentru MQTT

**Fără TLS (port 1883)**:
- Trafic în clar
- Credențiale vizibile
- Mesaje interceptabile

**Cu TLS (port 8883)**:
- Criptare end-to-end
- Autentificare server (certificat)
- Integritate mesaje (HMAC)

### Configurare recomandată:
- TLS 1.3 sau 1.2 (minimum)
- Certificate semnate de CA intern
- Mutual TLS pentru dispozitive critice

---

## SLIDE 17: Autentificare și Autorizare

### Autentificare
- **Ce știi**: Username/parolă
- **Ce ai**: Token, certificat
- **Ce ești**: Biometric (rar în IoT)

### Autorizare (ACL)
```
# Exemplu Mosquitto ACL
user sensor1
topic write home/+/telemetry

user controller
topic read home/#/telemetry
```

### Best practices:
- Credențiale unice per dispozitiv
- Rotație periodică
- Principiul privilegiului minim

---

## SLIDE 18: Segmentarea rețelei

### De ce segmentăm?
- Izolăm dispozitivele IoT de rețeaua principală
- Limităm mișcarea laterală a atacatorilor
- Aplicăm politici de firewall specifice

### Arhitectură recomandată:
```
[Internet] ─── [Firewall] ─── [Rețea Corporativă]
                   │
                   ├── [DMZ - Servere publice]
                   │
                   └── [VLAN IoT] ─── [Broker MQTT]
                                 └── [Senzori]
```

---

## SLIDE 19: Monitorizare și Logging

### Ce monitorizăm?
- **Trafic rețea**: Anomalii, volume neobișnuite
- **Loguri servicii**: Erori, tentative de acces
- **Stare dispozitive**: Uptime, resurse

### Instrumente:
- **Wireshark/tcpdump**: Captură pachete
- **ELK Stack**: Centralizare loguri
- **Prometheus/Grafana**: Metrici și alerte

### Indicatori de compromis:
- Conexiuni către IP-uri suspecte
- Trafic în afara orelor normale
- Scanări de porturi interne

---

## SLIDE 20: Recapitulare

### Puncte cheie:
1. IoT extinde dramatic suprafața de atac
2. MQTT este protocolul dominant, necesită TLS
3. Atacatorii exploatează servicii neactualizate
4. Defense in depth: straturi multiple de protecție
5. Segmentarea și monitorizarea sunt esențiale

### Pentru examen:
- Modelul OSI vs TCP/IP în context IoT
- Diferențele între QoS 0/1/2
- Tipuri de scanări și rezultatele lor
- Măsuri de hardening pentru dispozitive IoT

---

## SLIDE 21: Resurse suplimentare

### Bibliografie recomandată:
- Kurose & Ross — Computer Networking, Cap. 8 (Security)
- OWASP IoT Security Verification Standard
- NIST SP 800-183 — Networks of 'Things'

### Online:
- https://mqtt.org/
- https://owasp.org/www-project-internet-of-things/
- https://www.shodan.io/ (motorul de căutare IoT)

### Laborator:
- Starterkit S13 disponibil pe platforma cursului
- Demo-uri: `make demo-offensive` și `make demo-defensive`

---

## SLIDE 22: Întrebări?

**Contact colectiv didactic**:  
retele-calc@ie.ase.ro

**Consultații**:  
Conform programării pe platforma online.ase.ro

**Evaluare**:
- Proiect echipă: 15%
- Teste seminar: 15%
- Examen scris: 70%

---

## Note pentru prezentator

### Timing recomandat:
- Slides 1-5: 15 min (Introducere IoT)
- Slides 6-8: 15 min (MQTT detaliat)
- Slides 9-12: 25 min (Amenințări, studii de caz)
- Slides 13-14: 15 min (Pentest, vulnerabilități)
- Slides 15-19: 30 min (Măsuri defensive)
- Slides 20-22: 10 min (Recapitulare)

### Demonstrații live (opțional):
1. Captură trafic MQTT plaintext vs TLS (5 min)
2. Scanare porturi cu nmap/Python (5 min)
3. Exploatare vsftpd în container Docker (5 min)

### Întrebări de verificare:
- "Ce QoS ați folosi pentru o alertă de incendiu?"
- "De ce e important să segmentăm rețeaua IoT?"
- "Ce indică un port în stare filtered?"
