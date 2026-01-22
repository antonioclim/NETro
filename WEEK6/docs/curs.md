# Curs 6 – Nivelul Rețea: Protocoale Suport
## NAT/PAT · ARP · DHCP/BOOTP · NDP (IPv6) · ICMP

**Disciplina:** Rețele de calculatoare  
**Săptămâna:** 6 | **Durata:** 100 minute (2 ore academice)  
**Program:** Informatică Economică, ASE-CSIE  
**Anul universitar:** 2025-2026

---

## Ce vom învăța

La finalul acestui curs, studentul va putea:

1. **Identifica** rolul NAT în conservarea adreselor IPv4 și compromisurile pe care le introduce
2. **Distinge** între NAT static, NAT dinamic și PAT (NAT overload) – scop, mecanism, cazuri de utilizare
3. **Explica** procesul ARP și Proxy ARP (IPv4), respectiv echivalentul IPv6 prin NDP
4. **Descrie** pașii DHCP (DORA) și rolul DHCP Relay în rețele segmentate
5. **Înțelege** rolul ICMP în diagnostic și control (ping, traceroute, mesaje de eroare)
6. **Evalua** impactul NAT asupra principiului end-to-end în comunicațiile de rețea

---

## De ce contează

Aceste mecanisme sunt **fundamentale** pentru funcționarea practică a rețelelor moderne:

- **NAT/PAT** – permite miliardelor de dispozitive să acceseze Internetul cu un număr limitat de adrese IPv4 publice
- **ARP/NDP** – fără rezoluția adreselor, cadrele Ethernet nu ar putea ajunge la destinație
- **DHCP** – automatizează configurarea rețelei, esențială în medii enterprise și domestice
- **ICMP** – instrument indispensabil pentru diagnosticare și troubleshooting

Ca viitori programatori și arhitecți de sisteme, veți întâlni aceste tehnologii în:
- Configurarea infrastructurii cloud (AWS VPC, Azure VNet)
- Debugging conexiuni de rețea în aplicații distribuite
- Implementarea serviciilor containerizate cu Docker/Kubernetes
- Securizarea perimetrului de rețea

---

## Prerechizite

Din săptămânile anterioare, trebuie să stăpâniți:

| Concept | Relevanță pentru S6 |
|---------|---------------------|
| Modelul TCP/IP și OSI | Înțelegerea nivelului 3 (rețea) vs. nivelul 2 (legătură de date) |
| Adresare IPv4/IPv6 | Subnetting, VLSM, clase de adrese private (RFC 1918) |
| Structura pachetelor IP | Header-ul IP, câmpuri relevante (TTL, Protocol, adrese) |
| Socket programming | Client-server TCP/UDP pentru demo-uri practice |

**Recapitulare ultra-scurtă:**
- **IPv4**: 32 biți, ~4.3 miliarde adrese, spațiu epuizat
- **RFC 1918**: Adrese private (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) – nu sunt rutabile global
- **MAC address**: Identificator de 48 biți la nivel legătură de date (Ethernet)

---

## 1. Contextul: Criza spațiului IPv4

### 1.1 Problema fundamentală

- **IPv4**: 2³² ≈ 4.3 miliarde adrese totale
- **Realitatea**: >5 miliarde dispozitive conectate, zeci de miliarde cu IoT
- **Discrepanță**: Cererea depășește cu mult oferta

### 1.2 Soluții adoptate în timp

| An | Soluție | Descriere |
|----|---------|-----------|
| 1993 | CIDR | Classless Inter-Domain Routing – subrețele flexibile |
| 1994 | NAT | RFC 1631 – traducerea adreselor private → publice |
| 1996 | RFC 1918 | Spații de adrese private reutilizabile |
| 1998 | IPv6 | 2¹²⁸ adrese – soluția pe termen lung |

### 1.3 Adrese private (RFC 1918)

| Bloc | Prefix CIDR | Interval | Nr. adrese aprox. |
|------|-------------|----------|-------------------|
| Clasa A | 10.0.0.0/8 | 10.0.0.0 – 10.255.255.255 | ~16.7 milioane |
| Clasa B | 172.16.0.0/12 | 172.16.0.0 – 172.31.255.255 | ~1 milion |
| Clasa C | 192.168.0.0/16 | 192.168.0.0 – 192.168.255.255 | ~65.000 |

**Caracteristici:**
- Nu sunt rutabile pe Internet public
- Pot fi refolosite în orice organizație
- **Necesită traducere (NAT)** pentru acces extern

---

## 2. NAT – Network Address Translation

### 2.0 Analogie: NAT ca recepționer de hotel

Înainte de detaliile tehnice, o analogie care ajută la înțelegere:

**Imaginează-ți un hotel** (rețeaua privată) cu un **singur număr de telefon public** (IP-ul NAT):

```
┌─────────────────────────────────────────────────────────────┐
│                        HOTEL INTERNET                        │
│                                                              │
│  Camera 101  ──┐                                             │
│  Camera 102  ──┼───► RECEPȚIE ◄────► Număr public: 0721-NAT │
│  Camera 103  ──┘      (NAT)              ↕                   │
│                         │          Lumea exterioară          │
│                    Registru:                                 │
│                    "Apel 42 → Camera 101"                    │
│                    "Apel 43 → Camera 102"                    │
└─────────────────────────────────────────────────────────────┘
```

**Ce se păstrează:**
- Oaspeții (hosturi interne) pot suna în exterior liber
- Recepționerul (NAT) ține evidența: "apelul 42 este pentru camera 101"
- Când vine răspunsul, îl redirecționează către camera corectă

**Ce se pierde (principiul end-to-end):**
- Lumea exterioară nu poate suna direct la o cameră
- Trebuie să sune la recepție și să ceară "camera 101" (port forwarding)
- Unele servicii (ex: video call direct) necesită configurare specială

Această analogie ilustrează de ce NAT "funcționează dar încalcă" designul original al Internetului.

### 2.1 Principiul de bază

În mod normal, un router **forwardează** pachete fără a modifica adresele IP sursă/destinație. NAT **încalcă** acest principiu: modifică adresele pentru a permite comunicarea între rețele private și Internet.

```
┌─────────────────┐       ┌────────────────┐       ┌─────────────────┐
│  Rețea privată  │       │   Router NAT   │       │    Internet     │
│  192.168.1.0/24 │ ───── │  (gateway)     │ ───── │  Adrese publice │
│  h1: .10        │       │                │       │                 │
│  h2: .20        │       └────────────────┘       └─────────────────┘
└─────────────────┘              │
                           Traducere:
                     192.168.1.10 → 203.0.113.5
```

### 2.2 Tabela NAT (concept)

Router-ul NAT menține o **tabelă de corespondențe** între adrese interne și externe:

| IP Intern | Port Intern | IP Extern | Port Extern | Protocol |
|-----------|-------------|-----------|-------------|----------|
| 192.168.1.10 | 54321 | 203.0.113.5 | 40001 | TCP |
| 192.168.1.20 | 54322 | 203.0.113.5 | 40002 | TCP |

### 2.3 Tipuri de NAT

#### a) NAT Static (1:1)
- **Mapare permanentă** între o adresă privată și una publică
- **Cazuri de utilizare**: Servere interne accesibile din exterior
- **Exemplu**: 192.168.1.100 ↔ 203.0.113.10 (fix)
- *În analogia hotelului: o cameră VIP cu linie directă*

#### b) NAT Dinamic (Pool)
- **Alocare temporară** din pool de adrese publice
- **Cazuri de utilizare**: Organizații cu mai multe IP-uri publice
- **Limitare**: Conexiuni limitate de mărimea pool-ului
- *În analogia hotelului: mai multe linii telefonice disponibile*

#### c) PAT / NAPT / NAT Overload
- **Cea mai răspândită formă** – folosită în rețele casnice și IMM-uri
- **Principiu**: Multiple adrese private → o singură adresă publică
- **Diferențiere**: Prin **porturi** (de aceea Port Address Translation)
- *În analogia hotelului: o singură linie, dar cu extensii interne diferite*

```
┌──────────────────────────────────────────────────────────────┐
│              TABELA NAT (PAT/MASQUERADE)                     │
├──────────────────┬────────┬──────────────────┬───────┬───────┤
│ IP Intern        │ Port I │ IP Extern        │ Port E│ Proto │
├──────────────────┼────────┼──────────────────┼───────┼───────┤
│ 192.168.1.10     │ 54321  │ 203.0.113.5      │ 40001 │ TCP   │
│ 192.168.1.20     │ 54321  │ 203.0.113.5      │ 40002 │ TCP   │
│ 192.168.1.10     │ 12345  │ 203.0.113.5      │ 40003 │ UDP   │
└──────────────────┴────────┴──────────────────┴───────┴───────┘
```

### 2.4 Fluxul PAT – pas cu pas

**1. Pachet OUTBOUND (intern → extern):**
```
[SRC: 192.168.1.10:54321] [DST: 93.184.216.34:80]
        ↓ NAT translation
[SRC: 203.0.113.5:40001]  [DST: 93.184.216.34:80]
```

**2. Răspuns INBOUND (extern → intern):**
```
[SRC: 93.184.216.34:80]  [DST: 203.0.113.5:40001]
        ↓ Reverse lookup în tabela NAT
[SRC: 93.184.216.34:80]  [DST: 192.168.1.10:54321]
```

### 2.5 Dezavantaje NAT/PAT

| Problemă | Impact |
|----------|--------|
| Conexiuni din exterior dificile | Port forwarding necesar pentru servere interne |
| Încălcarea end-to-end | Aplicații P2P, VoIP, gaming – pot avea probleme |
| Dependență de L4 | NAT folosește porturi (L4) pentru a rezolva o problemă L3 |
| Probleme cu unele protocoale | FTP activ, SIP, IPSec (fără NAT-T) |
| Complicații VPN/tuneluri | Necesită configurare suplimentară |

---

## 3. ARP – Address Resolution Protocol

### 3.0 Analogie: ARP ca întrebarea "Cine are numărul X?"

**Imaginează-ți o sală de conferințe** unde știi numele (IP) dar nu fața (MAC):

```
Tu (Host A): "CINE ARE IP-ul 192.168.1.2?" (strigă în sală - broadcast)
             ↓
Toți aud, dar doar proprietarul răspunde
             ↓
Host B: "EU! MAC-ul meu este BB:BB:BB:BB:BB:BB" (răspunde direct - unicast)
             ↓
Tu notezi în agenda ta (ARP cache): "192.168.1.2 = BB:BB:..."
```

### 3.1 De ce există ARP?

Pentru a trimite un cadru Ethernet, avem nevoie de **adresa MAC destinație**. ARP face maparea:

**IP address → MAC address** (în rețeaua locală)

### 3.2 Cum funcționează

```
┌────────────┐  ARP Request (broadcast)  ┌────────────┐
│  Host A    │ ─────────────────────────>│  Toți din  │
│ 192.168.1.1│                           │  subnet    │
│ MAC: AA:AA │<─────────────────────────│            │
└────────────┘  ARP Reply (unicast)      └────────────┘
               "192.168.1.2 are MAC BB:BB"
```

**Pașii:**
1. **ARP Request**: Host A trimite broadcast – „Cine are IP-ul X?"
2. **ARP Reply**: Host B răspunde unicast – „Eu am IP-ul X, MAC-ul meu este Y"
3. **Cache**: Host A salvează maparea în ARP cache (temporar)

### 3.3 Proxy ARP

Când IP-ul căutat este în **altă rețea**, router-ul poate răspunde cu propriul MAC. Traficul ajunge la router, care îl forwardează.

```
Host A (192.168.1.10) vrea să contacteze 10.0.0.50
Router-ul răspunde la ARP cu MAC-ul său
Traficul ajunge la router, care îl rutează către 10.0.0.50
```

---

## 4. DHCP – Dynamic Host Configuration Protocol

### 4.0 Analogie: DHCP ca check-in la hotel

```
Oaspete nou (client):  "Am nevoie de o cameră!" (DISCOVER - strigă în hol)
Recepția (server):     "Îți ofer camera 205, etaj 2" (OFFER)
Oaspete:               "OK, accept camera 205!" (REQUEST - confirmă)
Recepția:              "Confirmat! Checkout în 24h" (ACK - lease time)
```

### 4.1 Rolul DHCP

Configurare **automată** a parametrilor de rețea:
- Adresă IP
- Mască de rețea
- Default gateway
- Servere DNS
- Lease time (durata alocării)

### 4.2 DORA – Cei 4 pași

| Pas | Mesaj | Direcție | Descriere |
|-----|-------|----------|-----------|
| **D** | Discover | Client → Broadcast | „Există vreun server DHCP?" |
| **O** | Offer | Server → Client | „Îți ofer IP-ul X cu parametrii Y" |
| **R** | Request | Client → Broadcast | „Accept oferta de la serverul Z" |
| **A** | Acknowledge | Server → Client | „Confirmat. Lease-ul tău e de N secunde" |

### 4.3 BOOTP vs DHCP

| Caracteristică | BOOTP | DHCP |
|----------------|-------|------|
| Alocare | Statică (config pe server) | Dinamică (pool de adrese) |
| Lease | Permanent | Temporar (reînnoibil) |
| Extensibilitate | Limitată | Opțiuni multiple |
| Utilizare actuală | Legacy, PXE boot | Standard modern |

### 4.4 DHCP Relay

**Problemă**: Discover este broadcast, nu trece prin router.

**Soluție**: DHCP Relay Agent pe router convertește broadcast → unicast și îl trimite către serverul DHCP din altă rețea.

---

## 5. NDP – Neighbor Discovery Protocol (IPv6)

### 5.1 Roluri unificate în NDP

IPv6 consolidează în NDP funcții care în IPv4 erau separate:

| Funcție IPv4 | Echivalent NDP |
|--------------|----------------|
| ARP | Neighbor Solicitation / Advertisement |
| ICMP Router Discovery | Router Solicitation / Advertisement |
| DHCP (parțial) | SLAAC (Stateless Address Autoconfiguration) |

### 5.2 Neighbor Solicitation / Advertisement

Similar cu ARP, dar folosește **multicast** (nu broadcast):

```
NS: ff02::1:ffXX:XXXX (multicast solicitat-node)
NA: Răspuns unicast sau multicast
```

### 5.3 SLAAC – Autoconfigurare stateless

1. Host-ul generează adresa **link-local** (fe80::/64 + Interface ID)
2. Execută **DAD** (Duplicate Address Detection)
3. Primește **Router Advertisement** cu prefix-ul global
4. Generează adresa globală: prefix + Interface ID

---

## 6. ICMP – Internet Control Message Protocol

### 6.1 Rolul ICMP

- **Mesaje de eroare**: Destination Unreachable, Time Exceeded
- **Mesaje de informare**: Echo Request/Reply (ping)
- **Diagnostic**: traceroute (TTL exceeded)

### 6.2 Tipuri comune ICMP

| Tip | Cod | Descriere |
|-----|-----|-----------|
| 0 | 0 | Echo Reply |
| 3 | 0 | Destination Network Unreachable |
| 3 | 1 | Destination Host Unreachable |
| 8 | 0 | Echo Request |
| 11 | 0 | TTL Exceeded in Transit |

### 6.3 Ping și Traceroute

**Ping**: Echo Request (tip 8) → Echo Reply (tip 0)

**Traceroute**: Trimite pachete cu TTL crescător (1, 2, 3...), fiecare router decrementează TTL și când ajunge la 0, trimite ICMP Time Exceeded. Astfel descoperim calea.

---

## Greșeli frecvente și cum le depistezi

| Greșeală | Simptom | Diagnostic | Soluție |
|----------|---------|------------|---------|
| IP forwarding dezactivat | NAT nu funcționează | `sysctl net.ipv4.ip_forward` | `sysctl -w net.ipv4.ip_forward=1` |
| Reguli iptables lipsă | Trafic blocat | `iptables -t nat -L -n -v` | Adaugă MASQUERADE |
| ARP cache corupt | Conexiune intermitentă | `ip neigh show` | `ip neigh flush all` |
| DHCP server down | Clienți nu primesc IP | `systemctl status isc-dhcp-server` | Verifică configurația și pornește |
| MTU mismatch | Pachete mari pierdute | `ping -M do -s 1472` | Ajustează MTU |

---

## Consolidare: Exerciții

### Exercițiul 1 (Înțelegere)
Explicați diferența dintre NAT static și PAT. Când ați folosi fiecare?

### Exercițiul 2 (Aplicare)
Un host cu IP 192.168.1.50 trimite un pachet HTTP către 93.184.216.34:80. Router-ul NAT are IP public 203.0.113.1. Scrieți cum arată header-ul IP înainte și după traducere.

### Exercițiul 3 (Analiză)
Analizați următoarea captură ARP și identificați problema:
```
ARP Request: Who has 192.168.1.1? Tell 192.168.1.50
ARP Request: Who has 192.168.1.1? Tell 192.168.1.50
ARP Request: Who has 192.168.1.1? Tell 192.168.1.50
(niciun reply)
```

### Exercițiul 4 (Evaluare)
Comparați avantajele și dezavantajele folosirii NAT vs. trecerea completă la IPv6. De ce NAT rămâne prevalent?

### Exercițiul 5 (Sinteză)
Proiectați schema de adresare pentru o rețea cu 3 departamente (50, 100, 200 stații), folosind un singur IP public și NAT.

### Exercițiul 6 – Challenge
Implementați în Python un script care:
- Detectează adresa MAC a gateway-ului folosind ARP
- Trimite un pachet ICMP Echo Request manual (cu Scapy)
- Interpretează răspunsul

---

## Ce am învățat

- NAT/PAT rezolvă problema epuizării IPv4, dar introduce complexitate și încalcă end-to-end
- ARP face maparea IP→MAC, esențială pentru comunicarea în LAN
- DHCP automatizează configurarea rețelei (DORA)
- NDP unifică în IPv6 funcții care în IPv4 erau separate
- ICMP oferă feedback despre starea rețelei și instrumente de diagnostic

---

## La ce ne ajută

| Context | Aplicație practică |
|---------|-------------------|
| Cloud/DevOps | Configurare VPC, NAT Gateway, Security Groups |
| Dezvoltare web | Înțelegerea conexiunilor client-server prin NAT |
| Troubleshooting | Folosirea ping, traceroute, tcpdump pentru debugging |
| Securitate | Înțelegerea limitărilor NAT ca „firewall" implicit |
| IoT | Configurare DHCP pentru dispozitive embedded |

---

## Contribuția la proiectul de echipă

**Livrabil săptămâna 6**: Implementați un modul de monitoring care:
- Detectează gateway-ul prin ARP
- Verifică conectivitatea prin ICMP
- Loghează traducerile NAT observate

Acest modul va fi integrat în aplicația de rețea dezvoltată pe parcursul semestrului.

---

## Bibliografie selectivă

| Autori | Titlu | Editor | An | DOI |
|--------|-------|--------|----|----|
| Kurose, J., Ross, K. | Computer Networking: A Top-Down Approach, 7th Ed. | Pearson | 2016 | 10.5555/3312979 |
| Rhodes, B., Goetzen, J. | Foundations of Python Network Programming | Apress | 2014 | 10.1007/978-1-4302-5855-1 |
| Srisuresh, P., Egevang, K. | Traditional IP Network Address Translator (RFC 3022) | IETF | 2001 | 10.17487/RFC3022 |
| Narten, T., et al. | Neighbor Discovery for IP version 6 (RFC 4861) | IETF | 2007 | 10.17487/RFC4861 |

### Standarde și specificații (fără DOI)

- RFC 1918 – Address Allocation for Private Internets
- RFC 5737 – IPv4 Address Blocks Reserved for Documentation
- RFC 826 – Ethernet Address Resolution Protocol (ARP)
- RFC 2131 – Dynamic Host Configuration Protocol (DHCP)

---

*Revolvix&Hypotheticalandrei*
