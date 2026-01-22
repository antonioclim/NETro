# Cursul 5: Nivelul Rețea — Adresare IPv4/IPv6, Subnetting, VLSM

## 1. Obiective și la ce folosește

### După curs vei ști să:
- Deosebești și clasifici adrese IP (v4, v6, publice, private, speciale)
- Explici cum funcționează adresarea la nivel 3 și de ce diferă de MAC
- Calculezi toți parametrii CIDR pentru orice adresă dată
- Împarți rețele cu FLSM și VLSM, alegând tehnica potrivită
- Citești header-ele IP și înțelegi ce face fiecare câmp
- Proiectezi scheme de adresare pentru scenarii reale de firmă

### La ce folosește în practică

Fără să înțelegi adresarea IP, orice configurare de rețea devine ghicit. E ca să conduci fără să știi regulile de circulație — poate merge o vreme, dar când apare o problemă, nu ai idee de unde să începi.

Un programator care stăpânește CIDR și subnetting poate:
- Configura corect aplicații client-server fără să ghicească adrese
- Diagnostica probleme de conectivitate în 5 minute, nu în 5 ore
- Proiecta infrastructuri cloud scalabile (VPC, Kubernetes)
- Automatiza provizionarea rețelei cu Terraform sau Ansible

---

## 2. Ce trebuie să știi deja

### Din cursurile anterioare
- **Curs 1-2**: Modelele OSI și TCP/IP, principiul încapsulării
- **Curs 3**: Programare socket (client-server)
- **Curs 4**: Nivelul fizic și legătură de date, adrese MAC

### Recapitulare rapidă

| Nivel | Unitate | Identificator | Rol |
|-------|---------|---------------|-----|
| Legătură date (L2) | Cadru | MAC address | Comunicare locală (switch) |
| Rețea (L3) | Pachet | IP address | Comunicare globală (router) |

> **Întrebare de control:** Ce se întâmplă dacă un host trimite un pachet către o adresă IP din altă subrețea, dar nu are configurat un gateway? Gândește-te 30 de secunde înainte să citești mai departe.

---

## 3. Conținut teoretic

### 3.1 Rolul nivelului rețea

Nivelul rețea asigură **adresarea logică** și **rutarea** pachetelor între rețele diferite. Spre deosebire de adresele MAC (fixate în hardware), adresele IP sunt **ierarhice** și **configurabile**, permițând agregarea rutelor.

#### Analogie: Adresa IP ca adresa poștală

Gândește-te la adresa IP ca la adresa unei case:
- **Partea de rețea** = orașul și strada (192.168.1)
- **Partea de host** = numărul casei (.10)
- **Masca de rețea** = cât de mare e "cartierul" care share-uiește aceeași rută
- **Broadcast** = megafonul care anunță tot cartierul simultan

Când trimiți un pachet, routerul se uită la "oraș" (partea de rețea) ca să știe încotro să-l trimită. Dacă adresa MAC e "numărul de serie al telefonului", adresa IP e "numărul de telefon" — poate fi schimbat, portat, și permite rutare ierarhică.

### 3.2 Adresarea IPv4

#### Structura adresei
- 32 biți (4 octeți), reprezentare dotted-decimal: `192.168.1.10`
- Fiecare octet: 0–255 (2⁸ valori)
- Notație binară completă: `11000000.10101000.00000001.00001010`

#### Clase istorice (învechite, dar le vei întâlni)

Sistemul claselor e un concept din anii '80. Clasa A avea /8, clasa B avea /16, clasa C avea /24. Astăzi folosim **CIDR** care permite orice lungime de prefix — mult mai flexibil.

| Clasă | Prim octet | Netmask implicită | Utilizare |
|-------|------------|-------------------|-----------|
| A | 1–126 | /8 (255.0.0.0) | Rețele foarte mari |
| B | 128–191 | /16 (255.255.0.0) | Rețele medii |
| C | 192–223 | /24 (255.255.255.0) | Rețele mici |

#### Adrese speciale

| Adresă/Interval | Scop | RFC |
|-----------------|------|-----|
| `10.0.0.0/8` | Private (clasa A) | RFC 1918 |
| `127.0.0.0/8` | Loopback | RFC 1122 |
| `169.254.0.0/16` | Link-local (APIPA) | RFC 3927 |
| `172.16.0.0/12` | Private (clasa B) | RFC 1918 |
| `192.168.0.0/16` | Private (clasa C) | RFC 1918 |
| `224.0.0.0/4` | Multicast | RFC 5771 |
| `255.255.255.255` | Broadcast limitat | RFC 919 |

### 3.3 CIDR — conceptele cheie

#### Notația CIDR
Format: `<adresă IP>/<prefix length>`  
Exemplu: `192.168.10.0/24`

#### Terminologie
- **Network address** (adresa rețelei): prima adresă din bloc, biții de host = 0
- **Broadcast address**: ultima adresă din bloc, biții de host = 1
- **Hosts valizi**: toate adresele între network și broadcast (exclusiv)
- **Prefix length** (`/n`): primii n biți sunt partea de rețea
- **Subnet mask**: netmask-ul corespunzător (/24 → 255.255.255.0)

#### Formule esențiale

```
Număr total de adrese în bloc = 2^(32 - prefix)
Număr de hosturi valizi       = 2^(32 - prefix) - 2
Network address               = IP AND subnet_mask
Broadcast address             = IP OR NOT(subnet_mask)
First valid host              = network_address + 1
Last valid host               = broadcast_address - 1
```

#### Exemplu detaliat

> **🎯 Predicție:** Pentru adresa 192.168.10.50/26, estimează câți hosturi valizi are rețeaua. Notează răspunsul, apoi verifică mai jos.

```
Adresă IP: 192.168.10.50/26

1. Prefix = 26 → 32 - 26 = 6 biți pentru hosturi
2. Total adrese = 2^6 = 64
3. Hosturi valizi = 64 - 2 = 62

4. Subnet mask în binar:
   11111111.11111111.11111111.11000000 = 255.255.255.192

5. Network address:
   192.168.10.50 = 11000000.10101000.00001010.00110010
   AND mask      = 11000000.10101000.00001010.00000000
   Rezultat      = 192.168.10.0

6. Broadcast address:
   192.168.10.0 OR 00111111 = 192.168.10.63

7. Interval valid: 192.168.10.1 — 192.168.10.62
```

Ai ghicit corect? Dacă ai zis 64, ai căzut în capcana clasică — ai uitat să scazi adresa de rețea și broadcast.

### 3.4 Subnetting cu FLSM

#### Analogie: Pizza tăiată în felii egale

Imaginează-ți că ai o pizza (rețeaua /24) și trebuie să o împarți pentru 4 persoane:
- **FLSM** = tai în 4 felii egale, indiferent cât mănâncă fiecare
- E simplu, dar dacă unul mănâncă puțin, risipești

**FLSM** (Fixed-Length Subnet Mask) împarte o rețea în subrețele egale.

#### Algoritm
1. Determină câte subrețele sunt necesare (N)
2. Calculează biții suplimentari: `⌈log₂(N)⌉`
3. Noul prefix = prefix_vechi + biți_suplimentari
4. Dimensiunea fiecărei subrețele = 2^(32 - prefix_nou)

#### Exemplu

> **🎯 Predicție:** Dacă împarți 10.0.0.0/8 în 16 subrețele egale, ce prefix va avea fiecare?

```
Rețea: 10.0.0.0/8
Nevoi: 16 subrețele egale

log₂(16) = 4 biți suplimentari
Nou prefix = 8 + 4 = /12

Subrețele rezultate:
  10.0.0.0/12   (10.0.0.1 — 10.15.255.254)
  10.16.0.0/12  (10.16.0.1 — 10.31.255.254)
  10.32.0.0/12  ...
  ... (16 subrețele × 1.048.574 hosturi/subrețea)
```

### 3.5 Subnetting cu VLSM

#### Analogie: Pizza tăiată pe porții

**VLSM** e ca atunci când tai pizza în felii de mărimi diferite, adaptate apetitului fiecăruia. Cine mănâncă mult primește felie mare, cine mănâncă puțin primește felie mică. Nu arunci nimic.

**VLSM** (Variable-Length Subnet Mask) permite alocarea de blocuri de dimensiuni diferite.

#### Algoritm
1. Sortează nevoile de hosturi **descrescător** (important!)
2. Pentru fiecare nevoie:
   - Calculează prefixul minim: `/prefix = 32 - ⌈log₂(hosts + 2)⌉`
   - Alocă primul bloc disponibil cu acel prefix
   - Marchează blocul ca utilizat
3. Calculează eficiența: `hosturi_folosiți / adrese_alocate × 100%`

> **Din experiența de predare:** Cea mai frecventă greșeală pe care o văd la studenți e că uită să sorteze descrescător cerințele înainte de alocare. Rezultatul? Subrețele care se suprapun și ore de debugging. Sortează ÎNTÂI, alocă DUPĂ.

#### Exemplu practic

> **🎯 Predicție:** Pentru cerințele de mai jos și rețeaua 192.168.1.0/24, ce prefix vei aloca pentru departamentul cu 100 hosturi?

```
Rețea disponibilă: 192.168.1.0/24
Nevoi:
  - Departament A: 100 hosturi
  - Departament B: 50 hosturi
  - Departament C: 25 hosturi
  - Link P2P: 2 hosturi

Sortare: 100 > 50 > 25 > 2

Alocare VLSM:
1. Dept A (100): nevoie 128 adrese → /25 (126 hosturi)
   → 192.168.1.0/25 (0-127)

2. Dept B (50): nevoie 64 adrese → /26 (62 hosturi)
   → 192.168.1.128/26 (128-191)

3. Dept C (25): nevoie 32 adrese → /27 (30 hosturi)
   → 192.168.1.192/27 (192-223)

4. P2P (2): nevoie 4 adrese → /30 (2 hosturi)
   → 192.168.1.224/30 (224-227)

Eficiență: (100+50+25+2) / (128+64+32+4) = 177/228 = 77.6%
Spațiu rămas: 192.168.1.228 — 192.168.1.255 (liber pentru extindere)
```

Răspuns la predicție: /25. De ce nu /26? Pentru că 100 + 2 = 102, și /26 oferă doar 62 hosturi. Trebuie să mergi la prefixul mai mic (/25 = 126 hosturi).

### 3.6 Adresarea IPv6

#### Analogie: Numerele de telefon extinse

IPv4 e ca un număr de telefon fix cu 10 cifre — s-au terminat combinațiile în 2011.  
IPv6 e ca și cum am extinde numerele la 32 de cifre — nu mai avem niciodată lipsă.

Comprimarea IPv6 e ca prescurtările din SMS:
- "0000" devine "0" (elimini zerourile inutile)
- Mai multe grupuri de "0000" devin "::" (o singură dată, ca "etc.")

#### De ce IPv6?
- IPv4: ~4.3 miliarde de adrese (2³²), epuizate în 2011
- IPv6: ~340 undecilioane de adrese (2¹²⁸) — practic infinite

#### Structura
- 128 biți, reprezentare hexazecimală cu două puncte: `2001:0db8:85a3:0000:0000:8a2e:0370:7334`
- 8 grupuri × 16 biți = 128 biți

#### Reguli de comprimare
1. **Eliminare zerouri de început** în fiecare grup: `0db8` → `db8`
2. **Comprimare grupuri consecutive de zerouri** cu `::` (o singură dată): 
   `2001:0db8:0000:0000:0000:0000:0000:0001` → `2001:db8::1`

> **🎯 Predicție:** Cum se comprimă `2001:0db8:0000:0000:0000:ff00:0042:8329`? Încearcă singur înainte să verifici.

Răspuns: `2001:db8::ff00:42:8329`

#### Tipuri de adrese IPv6

| Tip | Prefix | Descriere |
|-----|--------|-----------|
| Link-local | `fe80::/10` | Comunicare locală, necesar |
| Unique local | `fc00::/7` | Echivalent RFC 1918 |
| Global unicast | `2000::/3` | Rutabile pe Internet |
| Multicast | `ff00::/8` | Grup de destinatari |
| Loopback | `::1/128` | Localhost |

#### Subnetting IPv6
Standard: prefix `/48` pentru organizații → `/64` pentru subrețele  
Exemplu: `2001:db8:abcd::/48` → 65.536 subrețele `/64` posibile

### 3.7 Header-ele IPv4 și IPv6

#### Câmpuri IPv4 (20-60 bytes)

| Câmp | Biți | Scop |
|------|------|------|
| Version | 4 | Versiunea protocolului (4) |
| IHL | 4 | Lungime header (×4 bytes) |
| ToS/DSCP | 8 | Calitatea serviciului |
| Total Length | 16 | Lungime pachet (header + payload) |
| TTL | 8 | Hop-uri rămase |
| Protocol | 8 | Protocol nivel superior (6=TCP, 17=UDP) |
| Source IP | 32 | Adresa sursă |
| Destination IP | 32 | Adresa destinație |

#### Analogie TTL: Biletul de metro

TTL (Time To Live) e ca un bilet de metro cu limită de stații. La fiecare router (stație), se ștampilează — adică scade cu 1. Când ajunge la 0, pachetul e „dat jos" și aruncat. Asta previne pachetele să circule la infinit în rețea dacă există o buclă de rutare.

#### Simplificări IPv6
- Header fix de 40 bytes (vs. variabil în IPv4)
- Fără checksum (delegat nivelurilor superioare)
- Fără fragmentare la routere (doar la sursă)
- Extension headers pentru funcționalități opționale

---

## 4. Mini-demonstrații

### Demo 1: Calculul CIDR în Python

> **🎯 Predicție:** Ce va afișa codul de mai jos pentru numărul de hosturi? Calculează mental, apoi verifică.

```python
from ipaddress import ip_interface

iface = ip_interface("192.168.10.50/26")
print(f"Network: {iface.network.network_address}")
print(f"Broadcast: {iface.network.broadcast_address}")
print(f"Netmask: {iface.netmask}")
print(f"Hosturi: {iface.network.num_addresses - 2}")
```

### Demo 2: Vizualizare pachete cu tshark

> **🎯 Predicție:** Ce adrese IP crezi că vor apărea în captură dacă rulezi asta pe laptop-ul tău conectat la WiFi?

```bash
# Captură 10 pachete, afișare IP src/dst
sudo tshark -c 10 -f "ip" -T fields -e ip.src -e ip.dst
```

### Demo 3: Verificare configurație IP

```bash
# Linux
ip addr show
ip route show

# Windows
ipconfig /all
route print
```

---

## 5. Întrebări de verificare

1. Care este diferența între adresa de rețea și adresa de broadcast?
2. De ce /31 și /32 sunt cazuri speciale? Când se folosesc?
3. Câte adrese valide de host conține o rețea /22? (Calculează!)
4. Ce avantaje oferă VLSM față de FLSM? Când ai alege FLSM?
5. De ce IPv6 nu are checksum în header?
6. Comprimă: `2001:0db8:0000:0000:0000:ff00:0042:8329`

---

## 6. Unde te ajută în carieră

| Competență | Unde o folosești |
|------------|------------------|
| CIDR/Subnetting | Configurare VPC (AWS, GCP, Azure), Kubernetes networking |
| VLSM | Design infrastructură eficientă, documentație tehnică |
| IPv6 | Aplicații moderne, IoT, compatibilitate viitoare |
| Header parsing | Debugging rețea, dezvoltare protocoale, securitate |

---

## 7. Bibliografie

| Autor | Titlu | Editură | An |
|-------|-------|---------|-----|
| Kurose, Ross | Computer Networking: A Top-Down Approach (8th ed.) | Pearson | 2021 |
| Tanenbaum, Wetherall | Computer Networks (5th ed.) | Pearson | 2011 |
| Doyle, Carroll | Routing TCP/IP, Volume I (2nd ed.) | Cisco Press | 2005 |

### Standarde și specificații
- RFC 791: Internet Protocol (IPv4)
- RFC 1918: Address Allocation for Private Internets
- RFC 4291: IP Version 6 Addressing Architecture
- RFC 4632: Classless Inter-domain Routing (CIDR)

---

*Material didactic pentru cursul „Rețele de calculatoare", ASE-CSIE, 2025*
