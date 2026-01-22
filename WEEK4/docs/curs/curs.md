# Curs 4: Nivelul Fizic și Nivelul Legătură de Date

## Obiective

Săptămâna asta studiem bazele comunicării în rețele: cum biții devin semnale și cum semnalele devin cadre structurate. O să vedem de ce nivelul fizic nu poate comunica direct cu software-ul și cum nivelul legătura de date rezolvă problema.

## La ce ajută în practică

Ca programatori, nu interacționăm direct cu nivelurile 1 și 2. Totuși, înțelegerea lor ne ajută să diagnosticăm probleme de rețea, să optimizăm performanța și să proiectăm protocoale bune. Când un pachet "dispare", când latența crește inexplicabil, sau când trebuie să alegem între Ethernet și WiFi pentru o aplicație critică – aici contează ce știm despre aceste nivele.

---

## Nivelul Fizic (Layer 1)

### Rol și responsabilități

Nivelul fizic transformă **biți** în **semnale** transmisibile pe un mediu fizic. Și invers. E singurul nivel care operează cu fenomene analogice: curenți electrici, unde luminoase, unde radio.

**Ce definește:**
- Tipul semnalului (electric, optic, electromagnetic)
- Rata de transfer (bps, Mbps, Gbps)
- Sincronizarea între emițător și receptor
- Caracteristicile fizice ale conectorilor
- Specificațiile cablurilor și mediilor de transmisie
- Distanțele maxime de transmisie
- Toleranțele la erori (BER - Bit Error Rate)

### Medii de transmisie

#### Medii ghidate (cu suport fizic)

| Mediu | Caracteristici | Unde se folosește |
|-------|----------------|-------------------|
| **Cablu coaxial** | Ecranare bună, depășit | Televiziune cablu, rețele vechi |
| **Cablu torsadat (UTP/STP)** | Ieftin, flexibil, susceptibil la interferențe | Ethernet (Cat5e, Cat6, Cat6a) |
| **Fibră optică single-mode** | Distanțe mari (km), bandă largă | WAN, backbone |
| **Fibră optică multi-mode** | Distanțe medii (m-km), mai ieftină | LAN, centre de date |

#### Medii neghidate (fără fir)

- **WiFi (2.4 GHz, 5 GHz, 6 GHz)**: LAN wireless
- **Celular (LTE, 5G)**: WAN mobil
- **Bluetooth**: PAN (Personal Area Network)
- **Infraroșu**: Comunicare punct-la-punct

### Proprietăți ale mediului

Orice mediu de transmisie suferă de:

- **Atenuare**: semnalul slăbește cu distanța
- **Zgomot**: interferențe externe sau interne
- **Diafonie**: interferență între fire adiacente (cablu)
- **Reflexii**: dezadaptare de impedanță
- **Dispersie**: în fibră, diferite lungimi de undă merg cu viteze diferite

### Codare pe linie (Line Coding)

Problema: transmiterea unei secvențe lungi de 0-uri sau 1-uri identice face sincronizarea dificilă.

**NRZ (Non-Return to Zero)**
- 1 = nivel înalt constant
- 0 = nivel jos constant
- Problemă: fără tranziții, receptorul pierde sincronizarea

**NRZI (Non-Return to Zero Inverted)**
- 1 = tranziție
- 0 = fără tranziție
- Mai bine: garantează tranziții pentru secvențe de 1-uri

**Manchester**
- Tranziție în mijlocul fiecărui bit
- 1 = tranziție low→high, 0 = tranziție high→low
- Avantaj: sincronizare garantată
- Dezavantaj: necesită dublul lățimii de bandă

### Modulație (pentru transmisie wireless)

Modulația variază o undă purtătoare pentru a codifica informația:

- **ASK (Amplitude Shift Keying)**: variază amplitudinea
- **FSK (Frequency Shift Keying)**: variază frecvența
- **PSK (Phase Shift Keying)**: variază faza
- **QAM (Quadrature Amplitude Modulation)**: variază și amplitudinea și faza (WiFi modern)

---

## Nivelul Legătură de Date (Layer 2)

### Limitările nivelului fizic

Nivelul fizic are limite structurale:
1. Nu poate comunica direct cu software-ul
2. Nu suportă adresare
3. Gestionează doar un flux de biți
4. Nu oferă detectare sau corecție de erori

### Rol și structură

Nivelul 2 construiește **cadre (frames)** din fluxul de biți și oferă:
- **Adresare locală** (adrese MAC)
- **Delimitarea mesajelor** (framing)
- **Detectarea erorilor** (CRC/FCS)
- **Controlul accesului la mediu** (când poate transmite fiecare stație)

Se împarte în două subniveluri:
- **LLC (Logical Link Control)** – IEEE 802.2: interfață cu nivelurile superioare
- **MAC (Media Access Control)**: interfață cu hardware-ul

### Structura unui cadru (Frame)

Un cadru tipic arată așa:

```
+----------+---------+----------+------+------------+---------+
| Preambul | Dest MAC| Src MAC  | Type | Payload    | FCS/CRC |
+----------+---------+----------+------+------------+---------+
  sync       6 bytes   6 bytes   2B    46-1500 B     4 bytes
```

**Analogie: Cadrul ca plic poștal standardizat**

Gândește-te la un cadru Ethernet ca la un plic cu format strict:

| Parte cadru | Echivalent plic | Ce face |
|-------------|-----------------|---------|
| **Preambul** | Banda de deschidere | Marchează "aici începe plicul", sincronizare |
| **Dest MAC** | Adresa destinatarului (dreapta-sus) | Cine primește |
| **Src MAC** | Adresa expeditorului (stânga-sus) | Cine trimite |
| **Type** | Mențiunea "Fragil" / "Documente" | Ce tip de conținut |
| **Payload** | Scrisoarea din interior | Datele propriu-zise |
| **FCS/CRC** | Sigiliul de pe plic | Verificare dacă plicul a fost deschis/deteriorat |

Structura fixă permite hardware-ului (switch-uri, plăci de rețea) să proceseze cadre rapid – știe exact unde să caute fiecare informație, fără să "deschidă plicul".

### Detectarea erorilor cu CRC

**CRC (Cyclic Redundancy Check)** sau **FCS (Frame Check Sequence)** detectează dacă datele au fost corupte în tranzit.

**Analogie: CRC ca suma de control pe un bon fiscal**

Primești un bon de la supermarket:
- Pâine 5 lei, Lapte 8 lei, Ouă 12 lei
- La final: **TOTAL: 25 lei**

Poți verifica rapid: 5 + 8 + 12 = 25 ✓

Dacă totalul ar fi 27, știi că **ceva e greșit** – fie un articol, fie totalul. Dar **nu știi exact ce**.

CRC funcționează similar:
1. **Emițătorul** calculează o "amprentă matematică" a datelor și o atașează
2. **Receptorul** recalculează amprenta pe datele primite
3. Dacă diferă → date corupte în tranzit

**Ce poate și ce NU poate CRC:**
- ✅ **Detectează** erori de transmisie (biți inversați, date lipsă)
- ❌ **NU corectează** erori (doar le semnalează)
- ❌ **NU oferă securitate** (e ușor de falsificat intenționat)

**În practică (Python):**
```python
import zlib

# Calculează CRC32 (32 biți = 4 bytes)
data = b"Hello, World!"
crc = zlib.crc32(data) & 0xFFFFFFFF  # Mască pentru unsigned
print(f"CRC32: {crc:08x}")  # ex: 1c291ca3
```

### Vizualizare: Cum funcționează verificarea CRC

```
TRIMITERE:
┌──────────────────────────────────────────┐
│ Date originale: "Hello"                  │
│ Calcul: CRC32("Hello") = 0x3610A686      │
│                                          │
│ Pachet trimis:                           │
│ ┌─────────┬────────────┐                 │
│ │ "Hello" │ 0x3610A686 │ ──────────────► │
│ └─────────┴────────────┘                 │
│   date       CRC atașat                  │
└──────────────────────────────────────────┘

RECEPȚIE (OK):
┌──────────────────────────────────────────┐
│ Primit: "Hello" + 0x3610A686             │
│ Recalcul: CRC32("Hello") = 0x3610A686    │
│ Comparație: 0x3610A686 == 0x3610A686 ✓   │
│ → Date VALIDE                            │
└──────────────────────────────────────────┘

RECEPȚIE (CORUPT):
┌──────────────────────────────────────────┐
│ Primit: "Hallo" + 0x3610A686  (e→a)      │
│ Recalcul: CRC32("Hallo") = 0x4F4E2192    │
│ Comparație: 0x4F4E2192 != 0x3610A686 ✗   │
│ → Date CORUPTE - aruncă/retransmite      │
└──────────────────────────────────────────┘
```

Din experiența cu studenții din anii trecuți: greșeala cea mai frecventă e să calculezi CRC-ul pe date diferite la sender și receiver. Verifică de două ori că folosești exact aceiași bytes – inclusiv ordinea și padding-ul.

### Ethernet (IEEE 802.3)

Cel mai răspândit standard la nivel 2 pentru rețele cablate.

**Variante comune:**
- 10BASE-T: 10 Mbps
- 100BASE-TX: 100 Mbps (Fast Ethernet)
- 1000BASE-T: 1 Gbps (Gigabit Ethernet)
- 10GBASE-T: 10 Gbps

**Adrese MAC (48 biți = 6 octeți)**
- Format: `XX:XX:XX:YY:YY:YY`
- Primii 3 octeți (OUI): identifică fabricantul
- Ultimii 3 octeți: identifică interfața
- Broadcast: `FF:FF:FF:FF:FF:FF`

### CSMA/CD (Ethernet pe mediu partajat)

**Carrier Sense Multiple Access with Collision Detection**

1. Ascultă mediul
2. Dacă e liber, transmite
3. Dacă detectezi coliziune, oprește și trimite JAM signal
4. Așteaptă timp aleatoriu (binary exponential backoff)
5. Repetă

**Notă:** În rețelele moderne cu switch-uri full-duplex, coliziunile nu mai apar.

### WiFi (IEEE 802.11)

**Benzi de frecvență:**
- 2.4 GHz: acoperire mare, interferențe multe, 3 canale ne-suprapuse
- 5 GHz: viteză mare, acoperire mai mică, mai multe canale
- 6 GHz (WiFi 6E): foarte rapid, acoperire limitată

**CSMA/CA (Collision Avoidance)**

În wireless, nu poți detecta coliziuni în timp ce transmiți. Soluția:
1. Ascultă mediul
2. Dacă e liber, așteaptă un timp aleatoriu
3. Transmite
4. Așteaptă ACK de la receptor
5. Dacă nu primești ACK, retransmite

### Switch-uri și CAM Learning

Un switch învață unde se află fiecare MAC:
1. Primește cadru pe port X
2. Citește MAC sursă
3. Asociază: MAC sursă → Port X în tabela CAM
4. Caută MAC destinație în tabelă
5. Dacă găsește: trimite doar pe portul respectiv
6. Dacă nu: flooding (trimite pe toate porturile, mai puțin sursa)

**CAM Aging:** intrările expiră după un timp (implicit ~300 secunde)

### VLAN (Virtual LAN)

Problema: într-o rețea mare, broadcast-urile ajung la toate dispozitivele.

Soluția: **VLAN** segmentează logic rețeaua:
- Fiecare VLAN = domeniu de broadcast separat
- Dispozitivele din VLAN-uri diferite nu comunică direct
- Trebuie router pentru comunicare inter-VLAN

**802.1Q Tagging:** adaugă 4 octeți în header pentru VLAN ID (trunk ports)

---

## De la teorie la practică: Protocoale custom

Când construim protocoale la nivel aplicație (vezi seminarul și laboratorul), aplicăm aceleași principii de la L2:

| Concept L2 (Ethernet) | Echivalent protocol custom | De ce contează |
|-----------------------|---------------------------|----------------|
| Header fix (MAC, Type) | Header binar cu magic, version, type | Parsing rapid și predictibil |
| FCS/CRC la final | CRC32 pentru integritate | Detectare corupție |
| Payload variabil | Date aplicație | Flexibilitate |
| Framing (delimitare cadre) | Length-prefix sau delimitatori | Separare mesaje în stream |
| Adrese MAC | ID-uri sesiune/client | Identificare participanți |

**Diferența cheie:** La L2, hardware-ul face totul automat. La nivel aplicație, **tu** scrii codul.

**Exemplu concret:**

```
Cadru Ethernet:
+--------+--------+------+-----------+-----+
|Dest MAC|Src MAC |Type  | Payload   | CRC |
| 6B     | 6B     | 2B   | variabil  | 4B  |
+--------+--------+------+-----------+-----+

Protocol custom (S4):
+-------+-----+------+-----+-----+-----------+-----+
| Magic |Ver  |Type  |Len  |Seq  | Payload   | CRC |
| 2B    | 1B  | 1B   | 2B  | 4B  | variabil  | 4B  |
+-------+-----+------+-----+-----+-----------+-----+
```

Structura e similară. Ai învățat principiile care stau la baza tuturor protocoalelor de rețea.

---

## Ce am învățat

1. **Nivelul fizic** transformă biți în semnale și definește parametrii hardware
2. **Nivelul legătura de date** structurează comunicarea prin cadre
3. **Cadrul** e ca un plic standardizat – header fix, payload variabil, CRC pentru verificare
4. **CRC** detectează erori de transmisie (ca suma de control pe bon)
5. **Ethernet** și **WiFi** sunt cele mai comune tehnologii L2
6. **Switch-urile** învață locația dispozitivelor prin CAM learning
7. **VLAN** segmentează rețeaua pentru performanță și securitate
8. **Principiile L2 se aplică** și în protocoalele custom pe care le scriem noi

## Unde se folosește în practică

- **Diagnosticare:** când ping merge dar aplicația nu, problema poate fi la L2 (MAC, ARP)
- **Design rețea:** alegerea între UTP și fibră, între WiFi și cablu
- **Securitate:** MAC filtering, VLAN isolation, port security
- **Programare:** înțelegerea MTU și fragmentării, overhead-ului headerelor

## Legătura cu rolul de programator

Când dezvolți aplicații de rețea, nu vei manipula direct cadre Ethernet. Dar o să-ți folosească să știi:
- De ce MTU-ul default e 1500 bytes
- De ce WiFi are latență mai variabilă decât Ethernet
- Cum funcționează ARP și de ce uneori "se blochează" rețeaua
- De ce switch-urile nu văd adrese IP (doar MAC)
- Cum să proiectezi headere binare eficiente (inspirat din Ethernet)

---

## Întrebări de verificare

Înainte de seminar, verifică dacă poți răspunde:

1. **Ce face nivelul fizic cu biții?** (transformare în semnale)
2. **De ce nu poate L1 să comunice direct cu software-ul?** (nu are adresare, nu structurează date)
3. **Care e rolul CRC-ului într-un cadru?** (detectare erori, NU corecție)
4. **Ce se întâmplă când un switch primește un cadru pentru o adresă MAC necunoscută?** (flooding)
5. **De ce TCP are nevoie de framing suplimentar față de Ethernet?** (Ethernet păstrează granițele cadrelor, TCP nu)

---

## Pregătire pentru săptămâna viitoare

Săptămâna 5 ne duce la **Nivelul Rețea**: adresare IP, subnetting și rutare. O să vedem diferența:
- MAC = adresare plată (flat), locală
- IP = adresare ierarhică, globală
