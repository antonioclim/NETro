# Curs 2: Modele Arhitecturale pentru Rețele de Calculatoare

**Disciplina:** Rețele de Calculatoare  
**Durată:** 2 ore (100 minute)  
**Forma:** Prelegere interactivă cu diagrame și dialog  
**Materiale:** Slide-uri PPT/reveal.js, diagrame PNG, dashboard HTML

---

## Scopul săptămânii

### Ce vom învăța
Vom studia cele două modele principale de arhitectură a rețelelor de calculatoare: **modelul OSI** (teoretic, 7 straturi) și **modelul TCP/IP** (practic, 4 straturi). Vom analiza rolul fiecărui strat, procesul de încapsulare a datelor și vom stabili legătura cu programarea de rețea.

### De ce contează
Orice profesionist IT are nevoie să înțeleagă modelele arhitecturale deoarece oferă vocabularul comun pentru comunicarea despre probleme de rețea, structura conceptuală pentru diagnosticare și debugging, și baza pentru înțelegerea protocoalelor și a implementării lor.

Un informatician economist trebuie să distingă rapid între o problemă de aplicație (stratul 7, de exemplu un server HTTP care returnează erori 500) și o problemă de conectivitate (stratul 3, de exemplu pachete pierdute sau timeout la ping).

---

## Prerechizite

### Din săptămâna anterioară (Curs 1)
- **Protocol**: set de reguli pentru comunicare între entități
- **Stivă de protocoale**: ierarhie de protocoale cooperante
- **Încapsulare**: adăugarea de antete la transmitere
- **Adresare**: identificarea unică a dispozitivelor în rețea

### Recapitulare ultra-scurtă
Un protocol definește formatul mesajelor și regulile de schimb. Protocoalele se organizează ierarhic într-o stivă, fiecare nivel oferind servicii celui superior. La transmitere, datele sunt încapsulate progresiv cu antete specifice fiecărui nivel.

---

## Partea I: Fundamentele Modelării (25 minute)

### De ce avem nevoie de modele arhitecturale?

Rețelele de calculatoare sunt sisteme complexe, implicând hardware divers (routere, switch-uri, cabluri, antene), software variat (drivere, sisteme de operare, aplicații) și protocoale multiple care trebuie să coopereze.

**Separarea pe straturi** rezolvă această complexitate prin:
1. **Reducerea complexității** – fiecare strat gestionează un set limitat de responsabilități
2. **Interoperabilitatea** – echipamente de la producători diferiți pot comunica respectând specificațiile stratului
3. **Dezvoltarea independentă** – un strat poate evolua fără a afecta celelalte
4. **Testarea sistematică** – problemele pot fi izolate la un anumit nivel

**Analogie arhitecturală**: La fel cum o clădire are fundație, structură, instalații și finisaje care se construiesc independent dar funcționează împreună, o rețea are straturi distincte cu interfețe bine definite.

### Conceptul de strat (layer)

Un strat îndeplinește un rol specific în procesul de comunicare:
- **Oferă servicii** stratului imediat superior
- **Utilizează servicii** de la stratul imediat inferior
- **Comunică prin interfețe** standardizate cu straturile adiacente
- **Implementează protocoale** specifice rolului său

Comunicarea între straturi se face exclusiv prin interfețe definite; un strat nu „sare" peste altul.

**💭 Întrebare de reflecție:**
> Ce s-ar întâmpla dacă un strat ar putea „sări" peste altul și ar accesa direct servicii de la un strat non-adiacent? Gândește-te 30 de secunde la ce probleme ar apărea.

### Noțiuni-cheie

| Termen | Definiție | Exemplu |
|--------|-----------|---------|
| **PDU** | Protocol Data Unit – unitatea de date la un anumit strat | Segment TCP, Pachet IP, Cadru Ethernet |
| **SDU** | Service Data Unit – date primite de la stratul superior | Payload-ul TCP este SDU pentru IP |
| **SAP** | Service Access Point – punct de acces între straturi | Port TCP |
| **Încapsulare** | Adăugarea antetului propriu la SDU | IP Header + TCP Segment |

---

## Partea II: Modelul OSI (35 minute)

### Introducere

**OSI** = Open Systems Interconnection, dezvoltat de ISO (International Organization for Standardization) în anii 1980 ca răspuns la proliferarea sistemelor proprietare incompatibile.

**Caracteristici**:
- Model teoretic de referință
- 7 straturi distincte
- Scop: descriere completă și standardizată a comunicării
- Independență față de implementare hardware/software

### Cele 7 Straturi OSI

#### Stratul 1 – Fizic (Physical)

| Aspect | Descriere |
|--------|-----------|
| **Rol** | Transmiterea biților pe mediul fizic |
| **PDU** | Bit |
| **Funcții** | Modulare semnal, sincronizare bit, control rată transmisie |
| **Implementare** | Hardware (NIC, cablu, transceiver) |
| **Exemple** | Ethernet Cat5/6, Fibră optică, WiFi radio |

**Întrebare de reflecție**: Ce diferență există între reprezentarea unui bit „1" pe cablu de cupru (semnal electric) și pe fibră optică (impuls luminos)?

#### Stratul 2 – Legătură de Date (Data Link)

| Aspect | Descriere |
|--------|-----------|
| **Rol** | Transfer de cadre între noduri direct conectate |
| **PDU** | Cadru (Frame) |
| **Funcții** | Adresare fizică (MAC), detectare erori (CRC), delimitare cadre |
| **Substraturi** | MAC (Media Access Control), LLC (Logical Link Control) |
| **Exemple** | Ethernet (IEEE 802.3), WiFi (IEEE 802.11) |

Adresa MAC este identificatorul unic de 48 biți „ars" în hardware, format din OUI (primii 24 biți, identifică producătorul) și identificator de dispozitiv.

#### Stratul 3 – Rețea (Network)

| Aspect | Descriere |
|--------|-----------|
| **Rol** | Livrarea pachetelor între rețele diferite |
| **PDU** | Pachet (Packet) |
| **Funcții** | Adresare logică (ierarhică), rutare, fragmentare/reasamblare |
| **Protocol principal** | IP (Internet Protocol) |
| **Dispozitive** | Router |

**Conceptul-cheie**: Diferența dintre adresă fizică (MAC – unică global, plată) și adresă logică (IP – ierarhică, configurabilă). MAC identifică interfața hardware, IP identifică poziția în topologia logică.

#### Stratul 4 – Transport

| Aspect | Descriere |
|--------|-----------|
| **Rol** | Comunicare proces-la-proces (end-to-end) |
| **PDU** | Segment (TCP) / Datagramă (UDP) |
| **Funcții** | Multiplexare prin porturi, control flux/erori, reordonare |
| **Protocoale** | TCP (orientat conexiune), UDP (fără conexiune) |

**Analogie**: Dacă adresa IP este adresa blocului, portul este numărul apartamentului.

**💭 Întrebare de reflecție:**
> Dacă TCP oferă fiabilitate și UDP nu, de ce nu folosim TCP pentru absolut tot? Pare că ar fi mereu alegerea mai bună, nu? Gândește-te ce am pierde.

*Din experiența mea de predare, asta e momentul "aha" pentru mulți studenți — când realizează că fiabilitatea vine cu un cost (latență, overhead) și că uneori preferăm să pierdem un pachet decât să așteptăm retransmisia lui.*

#### Stratul 5 – Sesiune

| Aspect | Descriere |
|--------|-----------|
| **Rol** | Gestionarea dialogului între aplicații |
| **Funcții** | Inițiere/menținere/terminare sesiune, control dialog |
| **Observație** | Adesea implementat implicit în aplicațiile moderne |

#### Stratul 6 – Prezentare

| Aspect | Descriere |
|--------|-----------|
| **Rol** | Reprezentarea și transformarea datelor |
| **Funcții** | Codificare/decodificare, conversii format, compresie, criptare |
| **Exemple** | TLS/SSL, UTF-8, JSON, XML, ASN.1 |

#### Stratul 7 – Aplicație

| Aspect | Descriere |
|--------|-----------|
| **Rol** | Interfața cu utilizatorul sau aplicația |
| **Funcții** | Servicii specifice aplicațiilor (web, email, fișiere) |
| **Protocoale** | HTTP, FTP, SMTP, DNS, SSH |

**Distincție importantă**: „Aplicație" (browser Chrome) vs. „protocol de aplicație" (HTTP).

### Comunicarea în modelul OSI

**Comunicare verticală**: între straturi din același sistem, prin interfețe SAP.

**Comunicare orizontală (virtuală)**: între straturi omoloage de pe sisteme diferite. Fiecare strat „crede" că discută direct cu corespondentul său, deși în realitate datele traversează toată stiva.

### Procesul de încapsulare

**Analogie concretă — Plicuri în plicuri:**
Imaginează-ți că trimiți o scrisoare unui coleg dintr-un alt departament, situat în altă clădire:
1. Scrii mesajul pe hârtie (date aplicație)
2. Pui hârtia într-un plic interior cu numele colegului și biroul (antet Transport — port)
3. Pui plicul interior într-un plic mai mare cu adresa clădirii (antet Rețea — IP)
4. Pui totul într-un plic de curierat cu adresa fizică exactă (antet Legătură — MAC)
5. Curierul ia plicul și-l transportă fizic (biți pe fir)

La destinație, se deschid plicurile în ordine inversă până ajunge mesajul original la coleg.

*Analogia asta funcționează cel mai bine când o desenezi pe tablă pas cu pas. Am observat că studenții rețin mult mai bine dacă văd efectiv cum "crește" pachetul la transmitere și cum "se micșorează" la recepție.*

**💭 Întrebare de reflecție:**
> În analogia cu plicurile, ce s-ar întâmpla dacă curierul ar deschide plicul exterior (cel cu adresa MAC) și ar încerca să livreze direct bazându-se pe conținut? De ce NU face asta?

**La transmitere**:
1. Aplicația generează date
2. Fiecare strat adaugă propriul antet (și eventual trailer)
3. La nivel fizic, se transmit biții

**La recepție**:
1. Stratul fizic primește biții
2. Fiecare strat elimină antetul propriu și livrează payload-ul stratului superior
3. Aplicația primește datele originale

### Localizarea implementării

| Straturi | Implementare tipică |
|----------|---------------------|
| 5-7 (Sesiune, Prezentare, Aplicație) | Aplicații în user space |
| 4 (Transport) | Kernel sistem de operare |
| 2-3 (Legătură, Rețea) | Kernel + Driver |
| 1 (Fizic) | Hardware (NIC) |

---

## Partea III: Modelul TCP/IP (25 minute)

### Introducere

Modelul TCP/IP este modelul efectiv al Internetului, dezvoltat în anii 1970 pentru ARPANET, înainte de OSI. Este un model pragmatic, bazat pe protocoale reale, nu pe abstractizări teoretice.

### Cele 4 Straturi TCP/IP

#### Stratul Acces la Rețea (Network Access / Link)
- Echivalent cu: Fizic + Legătură de date (OSI)
- Nu este standardizat de TCP/IP – se bazează pe tehnologii existente
- Exemple: Ethernet, WiFi, PPP

#### Stratul Internet
- Protocol principal: IP (IPv4, IPv6)
- Caracteristici: neorientat pe conexiune, fără garanții, rutare best-effort
- Protocoale auxiliare: ICMP (diagnosticare), ARP (rezolvare adrese)

#### Stratul Transport
| Protocol | Caracteristici |
|----------|----------------|
| **TCP** | Orientat conexiune, confirmări (ACK), control flux/erori/congestie, reordonare |
| **UDP** | Fără conexiune, fără garanții, overhead minim, latență redusă |

**Când folosim UDP?** Streaming video/audio (Netflix, Zoom), gaming online, DNS queries, IoT cu constrângeri de resurse.

*Anul trecut, un student a exclamat după ce a văzut diferența în captură: "Deci de-aia lag-uiește jocul când forțez TCP!" — exact asta e intuiția corectă. UDP pierde pachete, dar jocul continuă fluid; TCP ar fi așteptat retransmisia și ai fi simțit "freeze-ul".*

#### Stratul Aplicație
- Combină funcționalitățile straturilor 5, 6, 7 din OSI
- Protocoale: HTTP/HTTPS, DNS, SMTP, FTP, SSH, TLS

### TCP Three-Way Handshake — Analogie concretă

Handshake-ul TCP funcționează ca o conversație telefonică politicoasă:

| Pas | TCP | Conversație umană |
|-----|-----|-------------------|
| 1. SYN | Client trimite SYN | „Bună, mă auzi?" |
| 2. SYN-ACK | Server răspunde SYN+ACK | „Da, te aud! Tu mă auzi?" |
| 3. ACK | Client confirmă ACK | „Da, perfect! Hai să vorbim." |

Abia după acești trei pași, conexiunea e stabilită și pot curge datele.

**De ce 3 pași și nu 2?** Fiecare parte trebuie să confirme că poate și trimite, și primi. Cu doar 2 pași, serverul nu ar ști dacă clientul i-a primit răspunsul.

### Comparație OSI vs TCP/IP

| Criteriu | OSI | TCP/IP |
|----------|-----|--------|
| **Origine** | ISO (standard) | DARPA (practic) |
| **Straturi** | 7 | 4 |
| **Abordare** | Model-first | Implementation-first |
| **Separare** | Strictă | Flexibilă |
| **Utilizare** | Referință, învățare | Internet real |

**💭 Întrebare de reflecție:**
> Dacă TCP/IP e modelul "real" și OSI e doar "teoretic", de ce ne mai chinuim să învățăm OSI? Nu ar fi mai simplu să-l ignorăm?

### De ce folosim ambele?

- **OSI pentru**: analiză, învățare, depanare conceptuală, certificări (CCNA)
- **TCP/IP pentru**: implementare reală, programare, configurare

Când un administrator spune „problema e la L3", se referă fie la IP (TCP/IP) fie la stratul Rețea (OSI) – sunt echivalente.

*Personal, când debughez o problemă de rețea, tot timpul mă gândesc în termeni OSI: "E L3 sau L7?" — chiar dacă implementarea e TCP/IP. OSI îți dă vocabularul, TCP/IP îți dă tool-urile.*

---

## Partea IV: Legătura cu Practica (15 minute)

### Programarea de rețea și straturile

Ca programator, interacționezi cu stiva de protocoale prin **Socket API**:
- **Aplicațiile** folosesc socket-uri și porturi (L7/L4)
- **Sistemul de operare** implementează TCP/UDP și IP (L4/L3)
- **Hardware-ul** gestionează accesul la rețea (L2/L1)

### Socket API – Preview

Un **socket** este un punct de acces la stiva de protocoale, o abstracție oferită de SO pentru comunicare de rețea.

**Analogie concretă — Telefonul mobil:**
- **Socket** = telefonul tău mobil (dispozitivul prin care comunici)
- **Adresa IP** = numărul tău de telefon (te identifică în rețea)
- **Portul** = extensia internă sau linia specifică (identifică aplicația/serviciul)
- **bind()** = îți activezi cartela SIM pe un număr
- **listen()** = ții telefonul deschis, aștepți să sune
- **connect()** = formezi un număr și aștepți să răspundă
- **accept()** = ridici receptorul când sună
- **send()/recv()** = vorbești și asculți

**💭 Întrebare de reflecție:**
> În analogia cu telefonul, ce crezi că face `listen()` diferit de `bind()`? Ambele par să "pregătească" telefonul pentru comunicare, dar fac lucruri diferite. La ce te-ai gândi?

**Tipuri principale**:
- `SOCK_STREAM` → TCP (flux de bytes, orientat conexiune) — ca un apel telefonic
- `SOCK_DGRAM` → UDP (datagrame, fără conexiune) — ca un SMS

La seminar vom implementa servere și clienți folosind socket-uri Python.

### Pregătire pentru seminar

La seminar vom:
1. Porni o topologie Mininet (emulare rețea)
2. Implementa un server TCP concurent
3. Captura trafic cu tshark
4. Identifica handshake-ul TCP în captură
5. Compara overhead-ul TCP vs UDP

---

## Recapitulare – Ce am învățat

1. **Rolul modelelor arhitecturale**: reducerea complexității, interoperabilitate, dezvoltare independentă
2. **Modelul OSI**: 7 straturi teoretice, de la Fizic (L1) la Aplicație (L7)
3. **Modelul TCP/IP**: 4 straturi practice, modelul real al Internetului
4. **Diferențe și echivalențe**: OSI pentru analiză, TCP/IP pentru implementare
5. **Încapsulare**: antete adăugate la transmitere, eliminate la recepție
6. **Socket API**: interfața programatorului cu stiva de protocoale

### La ce ne ajută

- **Troubleshooting**: identificarea nivelului la care apare o problemă
- **Securitate**: înțelegerea unde operează diverse mecanisme de protecție
- **Programare**: utilizarea corectă a socket-urilor și protocoalelor
- **Comunicare profesională**: vocabular comun cu alți specialiști

### Unde se așază în formarea unui programator

Modelele arhitecturale sunt baza pe care se construiesc toate cunoștințele ulterioare despre rețele. Fără înțelegerea straturilor și a încapsulării, protocoalele specifice (HTTP, DNS, TLS) rămân „cutii negre".

---

## Întrebări de verificare

1. Care strat OSI este responsabil de adresarea MAC?
2. Ce PDU are stratul Transport pentru TCP? Dar pentru UDP?
3. Câte straturi are modelul TCP/IP și care sunt?
4. Numiți 3 protocoale de la stratul Aplicație.
5. Care este diferența fundamentală între TCP și UDP?
6. De ce avem nevoie de două tipuri de adrese (MAC și IP)?

---

## Bibliografie selectivă

| Autor(i) | Titlu | Detalii | DOI |
|----------|-------|---------|-----|
| Kurose, Ross | Computer Networking: A Top-Down Approach | 7th Ed., Cap. 1-2 | 10.5555/2821234 |
| Tanenbaum, Wetherall | Computer Networks | 5th Ed., Cap. 1 | 10.5555/1972504 |
| Stevens, Fenner, Rudoff | Unix Network Programming | Vol. 1, Cap. 1-2 | 10.5555/510873 |

### Standarde și specificații

- ISO/IEC 7498-1: Information technology — Open Systems Interconnection — Basic Reference Model
- RFC 1122: Requirements for Internet Hosts — Communication Layers
- RFC 793: Transmission Control Protocol
- RFC 768: User Datagram Protocol

---

*Revolvix&Hypotheticalandrei*
