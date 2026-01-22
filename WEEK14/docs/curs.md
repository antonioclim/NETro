# Curs 14 — Recapitulare Integrată

**Disciplină:** Rețele de calculatoare / Networking  
**Săptămâna:** 14 (finală)  
**Durată:** 90 minute

---

## Ce vom învăța

Săptămâna 14 consolidează toate conceptele din semestru într-un model mental coerent. Nu memorăm liste de protocoale, ci exersăm un **proces de diagnostic reproductibil**: de la simptom la cauză probabilă, cu dovezi verificabile (capturi, loguri, măsurători).

### Obiective operaționale

La finalul cursului, studentul poate:

1. **Reconstitui traseul complet** al unui mesaj: aplicație → socket → TCP/UDP → IP → Ethernet/ARP (și invers)
2. **Aplica un checklist de diagnostic** în ordine logică: conectivitate L3 → porturi → captură → aplicație
3. **Interpreta o captură pcap** și corela simptomul cu cauza (timeout vs RST, retransmisii, coduri HTTP)
4. **Justifica decizii tehnice** într-o prezentare de proiect

---

## De ce contează (pentru programatori)

Defectele de rețea se manifestă ca bug-uri de aplicație: timeouts inexplicabile, erori intermitente, performanță instabilă. Un programator care înțelege stratul de sub API-ul de socket poate:

- **Reduce timpul de debugging** de la ore la minute
- **Comunica eficient** cu echipele de DevOps/Infra folosind termeni preciși
- **Construi servicii mai solide** (timeout-uri corecte, retry cu backoff, health checks)

### Exemple concrete

| Simptom în aplicație | Cauza reală | Cum se vede |
|---------------------|-------------|-------------|
| `Connection timeout` | Firewall blochează SYN | pcap: SYN fără SYN-ACK |
| `Connection refused` | Portul nu ascultă | ss: nu e în LISTEN |
| `504 Gateway Timeout` | Backend lent/down | LB log + pcap către backend |
| Latență variabilă | Retransmisii TCP | pcap: pachete duplicate |

---

## Recapitulare: Harta conceptelor

### 1. Straturi și încapsulare

```
Aplicație  → [Date]
Transport  → [Header TCP/UDP | Date] = Segment/Datagramă
Network    → [Header IP | Segment]   = Pachet
Link       → [Header Eth | Pachet]   = Frame
```

**Întrebare de control:** Ce overhead introduce fiecare strat? (Ethernet: 14B, IP: 20B+, TCP: 20B+)

### 2. Adresare pe nivele

| Nivel | Adresă | Scop | Rezoluție |
|-------|--------|------|-----------|
| Link (2) | MAC (48 biți) | Identificare în LAN | ARP |
| Network (3) | IP (32/128 biți) | Identificare globală | DNS, routing |
| Transport (4) | Port (16 biți) | Identificare proces | Aplicație |

**Întrebare de control:** De ce ai nevoie de ARP înainte de a trimite un ping?

**Analogie practică — Socket ca telefon:**
- **IP** = numărul de telefon al clădirii
- **Port** = extensia internă (care birou răspunde)
- **Socket** = aparatul telefonic conectat — combină IP + Port + Protocol
- Când suni (connect), centralista (OS) te pune în legătură cu extensia cerută

### 3. TCP vs UDP

| Caracteristică | TCP | UDP |
|----------------|-----|-----|
| Conexiune | Da (3-way handshake) | Nu |
| Fiabilitate | Garantată (retransmisii) | Best-effort |
| Ordonare | Garantată | Nu |
| Flow control | Da (fereastră) | Nu |
| Overhead | Mai mare | Mai mic |
| Folosire | HTTP, SSH, FTP | DNS, VoIP, gaming |

**Întrebare de control:** Ce înseamnă un RST într-o captură TCP?

### 4. Rutare

- **Tabela de rutare:** lista de reguli (destinație, mască, next-hop, interfață)
- **Longest Prefix Match:** se alege ruta cea mai specifică
- **Default gateway:** ruta 0.0.0.0/0 când nu există potrivire mai bună

```bash
ip route
# Exemplu output:
# default via 192.168.1.1 dev eth0
# 10.0.0.0/24 dev mininet-h1 scope link
```

### 5. HTTP (Layer 7)

```
Request:  GET /path HTTP/1.1\r\nHost: example.com\r\n\r\n
Response: HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html>...
```

**Coduri importante:** 200 OK, 301/302 Redirect, 404 Not Found, 500/502/503/504 Server Errors

---

## Checklist de diagnostic

Când ceva „nu merge", aplică în ordine:

```
1. Reproducere minimală
   └─ Același request, aceeași topologie, aceeași versiune?

2. Conectivitate L3
   └─ ping <ip>
   └─ ip route get <ip>
   └─ ip neigh (cache ARP)

3. Porturi și socket-uri
   └─ ss -lntp (ce ascultă?)
   └─ ss -tnp (conexiuni active)

4. Captură la limită
   └─ tcpdump -i <iface> host <ip> -w capture.pcap
   └─ tshark -r capture.pcap -Y "tcp.port==80"

5. Interpretare
   └─ Handshake complet? Retransmisii? RST? Coduri HTTP?

6. Remediere + validare
   └─ Schimbare mică → măsurare → comparare
```

---

## Demonstrații recomandate

### Demo 1: TCP Handshake vs Timeout (5 min)

```bash
# Terminal 1: server simplu
python3 -m http.server 8000

# Terminal 2: captură
sudo tcpdump -i lo port 8000 -nn

# Terminal 3: client
curl http://localhost:8000/

# Observă: SYN → SYN-ACK → ACK → GET → 200 OK → FIN
```

### Demo 2: Connection Refused vs Timeout (5 min)

```bash
# Port închis (refuzat imediat)
curl http://localhost:9999/
# → Connection refused (RST imediat)

# Port filtrat (timeout)
sudo iptables -A INPUT -p tcp --dport 8888 -j DROP
curl --connect-timeout 3 http://localhost:8888/
# → Timeout (SYN fără răspuns)
```

### Demo 3: DNS ca punct de eșec (5 min)

```bash
# Cu DNS funcțional
curl http://example.com/

# Cu DNS stricat
echo "nameserver 1.2.3.4" | sudo tee /etc/resolv.conf
curl http://example.com/
# → DNS resolution failed

# Cu IP direct (ocolește DNS)
curl http://93.184.216.34/
# → Funcționează
```

---

## Greșeli tipice

| Greșeală | Consecință | Cum o eviți |
|----------|------------|-------------|
| Confuzie IP vs Port | „Nu răspunde pe 10.0.0.2:8080" | Verifică `ss -lntp` pe host |
| Ping OK = Serviciu OK | Serviciul poate fi down | Testează cu `curl`/client |
| Ignoră retransmisiile | Nu observi congestia/pierderea | Analizează pcap detaliat |
| Firewall uitat | Trafic blocat misterios | `iptables -L -n` |
| DNS cache | Schimbări nu se propagă | `dig +short` sau `nslookup` |

---

## Ce am învățat / La ce ne ajută

Săptămâna 14 nu adaugă concepte noi, ci le **integrează** într-un proces de lucru. Valoarea practică:

1. **Debugging mai rapid:** știi unde să cauți prima dată
2. **Comunicare precisă:** folosești termeni corecți (SYN, RST, 502)
3. **Servicii mai solide:** setezi timeout-uri și retry-uri informate
4. **Pregătire pentru industrie:** interviurile tehnice testează exact aceste abilități

---

## Legătura cu proiectul de echipă

În prezentarea proiectului, demonstrezi:

- **Reproductibilitate:** pornești din mediu curat, pași clari
- **Evidențe:** captură pcap care susține o afirmație tehnică
- **Diagnostic:** poți explica un simptom (ce vedem?) și cauza (de ce?)
- **Justificare:** de ce ai ales TCP/UDP, porturi, arhitectură

---

## Bibliografie

- Kurose, J. F., & Ross, K. W. (2017). *Computer Networking: A Top-Down Approach* (7th ed.). Pearson.
- Stevens, W. R. (1994). *TCP/IP Illustrated, Volume 1*. Addison-Wesley.
- RFC 791 (IP), RFC 793 (TCP), RFC 768 (UDP)
