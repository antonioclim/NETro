# Rubrici de Evaluare – Săptămâna 2

**Modele Arhitecturale OSI/TCP-IP & Programare Socket**

---

## Evaluare formativă (în timpul seminarului)

### Criteriu 1: Înțelegerea modelelor arhitecturale

| Nivel | Descriere | Punctaj |
|-------|-----------|---------|
| **Excelent** | Explică toate cele 7 straturi OSI și 4 straturi TCP/IP, cu exemple de protocoale și PDU pentru fiecare | 10 |
| **Bine** | Cunoaște straturile principale, face echivalențe corecte OSI↔TCP/IP | 8 |
| **Satisfăcător** | Poate enumera straturile, cunoaște câteva protocoale | 6 |
| **Insuficient** | Confuzie între straturi, nu face legătura cu protocoale | 4 |

### Criteriu 2: Programare socket TCP

| Nivel | Descriere | Punctaj |
|-------|-----------|---------|
| **Excelent** | Server concurent funcțional, gestionează corect excepții, logging complet | 10 |
| **Bine** | Server funcțional, tratează conexiuni multiple, răspuns corect | 8 |
| **Satisfăcător** | Server simplu funcțional, un client la un moment dat | 6 |
| **Insuficient** | Cod incomplet sau nu compilează | 4 |

### Criteriu 3: Programare socket UDP

| Nivel | Descriere | Punctaj |
|-------|-----------|---------|
| **Excelent** | Server cu protocol aplicație complet, gestionare timeout, statistici | 10 |
| **Bine** | Server funcțional cu protocol de bază (ping/upper) | 8 |
| **Satisfăcător** | Server echo simplu funcțional | 6 |
| **Insuficient** | Cod incomplet sau erori | 4 |

### Criteriu 4: Analiză trafic

| Nivel | Descriere | Punctaj |
|-------|-----------|---------|
| **Excelent** | Identifică corect handshake TCP, corelează cu codul, explică diferențele TCP/UDP | 10 |
| **Bine** | Identifică handshake și payload, înțelege overhead | 8 |
| **Satisfăcător** | Poate rula captură și vizualiza cu tshark | 6 |
| **Insuficient** | Nu poate genera sau interpreta capturi | 4 |

### Criteriu 5: Exerciții de înțelegere (nou)

| Nivel | Descriere | Punctaj |
|-------|-----------|---------|
| **Excelent** | Parsons problem corect, trace exercise complet, bug identificat și explicat | 10 |
| **Bine** | 2 din 3 exerciții corecte, explicații adecvate | 8 |
| **Satisfăcător** | 1 exercițiu corect, încercare la celelalte | 6 |
| **Insuficient** | Nu a încercat sau răspunsuri incorecte | 4 |

---

## Grilă sintetică pentru seminar

| Activitate | Punctaj maxim | Observații |
|------------|---------------|------------|
| Prezență și participare | 1 punct | Include răspuns la MCQ |
| Exerciții TCP completate | 2 puncte | Template funcțional |
| Exerciții UDP completate | 2 puncte | Protocol implementat |
| Analiză captură | 2 puncte | Identificare handshake |
| Exerciții de înțelegere | 2 puncte | Parsons, trace, debugging |
| Extensie opțională | 1 punct bonus | Topologie router |
| **TOTAL** | **10 puncte** | |

---

## Contribuția la proiectul de echipă

### Artefact livrabil săptămâna 2

**Modul de comunicare TCP/UDP pentru aplicația de echipă**

| Criteriu | Cerință | Pondere |
|----------|---------|---------|
| **Funcționalitate** | Server acceptă conexiuni multiple concurent | 40% |
| **Protocol** | Protocol aplicație definit (format mesaje, comenzi) | 25% |
| **Documentare** | README cu instrucțiuni de rulare | 20% |
| **Cod curat** | Structură, comentarii, naming | 15% |

### Integrare cu proiectul

Modulul de comunicare dezvoltat în această săptămână va fi folosit în:
- Săptămâna 8: Server HTTP (extindere la protocol text complex)
- Săptămâna 9: Transfer fișiere (FTP custom)
- Săptămâna 11: Load balancing și reverse proxy

---

## Evaluare sumativă (examen)

### Întrebări teoretice tip grilă — Cu distractori pe misconceptii

**1. Care strat OSI este responsabil de adresarea MAC?**

- a) Fizic *(Misconceptie: confuzie cu hardware-ul fizic)*
- b) **Legătură de date** ✓
- c) Rețea *(Misconceptie: confuzie cu adresarea IP)*
- d) Transport *(Misconceptie: confuzie cu porturile)*

*De ce e greșit a): Stratul Fizic se ocupă de biți și semnale, nu de adrese.*
*De ce e greșit c): Stratul Rețea se ocupă de adrese IP, nu MAC.*

---

**2. Ce PDU folosește stratul Transport pentru protocolul TCP?**

- a) Pachet *(Misconceptie: confuzie cu stratul Rețea/IP)*
- b) Cadru *(Misconceptie: confuzie cu stratul Legătură de Date)*
- c) **Segment** ✓
- d) Datagramă *(Parțial corect — dar e pentru UDP, nu TCP)*

*De ce e greșit a): Pachetul e PDU-ul stratului Rețea (IP).*
*De ce e greșit d): Datagramă e termenul pentru UDP, nu TCP.*

---

**3. Câte straturi are modelul TCP/IP?**

- a) 7 *(Misconceptie: confuzie cu OSI)*
- b) 5 *(Misconceptie: varianta hibridă uneori prezentată în cărți)*
- c) **4** ✓
- d) 3 *(Misconceptie: simplificare excesivă)*

*De ce e greșit a): 7 straturi are OSI, nu TCP/IP.*

---

**4. Care este secvența corectă a handshake-ului TCP?**

- a) ACK → SYN → SYN-ACK *(Misconceptie: inversare ordine)*
- b) **SYN → SYN-ACK → ACK** ✓
- c) SYN → ACK → SYN-ACK *(Misconceptie: confuzie cu ordinea)*
- d) SYN → SYN → ACK *(Misconceptie: crede că ambele părți trimit SYN separat)*

*De ce e greșit d): Serverul trimite SYN-ACK combinat, nu SYN separat.*

---

**5. Ce protocol oferă transfer neorientat pe conexiune?**

- a) TCP *(Misconceptie: confuzie între cele două protocoale de transport)*
- b) **UDP** ✓
- c) IP *(Parțial corect — IP e connectionless, dar nu e la stratul Transport)*
- d) ICMP *(Misconceptie: ICMP e pentru diagnosticare, nu transfer de date)*

*De ce e greșit a): TCP e orientat pe conexiune (connection-oriented).*
*De ce e greșit c): IP e la stratul Rețea, nu Transport.*

---

**6. Un ping reușit între două mașini garantează că:**

- a) Serverul web funcționează corect *(Misconceptie: confuzie L3 cu L7)*
- b) Portul 80 e deschis *(Misconceptie: ping nu verifică porturi)*
- c) **Există conectivitate IP între cele două mașini** ✓
- d) Conexiunea TCP va reuși sigur *(Misconceptie: ping folosește ICMP, nu TCP)*

*De ce e greșit a): Ping verifică L3 (IP/ICMP), nu L7 (HTTP).*
*De ce e greșit d): Firewall-ul poate bloca TCP dar permite ICMP.*

---

**7. De ce UDP e preferat pentru streaming video în timp real?**

- a) UDP e mai sigur decât TCP *(Misconceptie: confuzie securitate vs fiabilitate)*
- b) UDP garantează ordinea pachetelor *(Misconceptie: exact opusul)*
- c) **Latența mică e mai importantă decât pierderea ocazională** ✓
- d) UDP are header mai mare, deci poate trimite mai multe date *(Misconceptie: inversare — UDP are header mai mic)*

*De ce e greșit b): UDP NU garantează ordinea — acesta e un avantaj al TCP.*

---

**8. Ce se întâmplă dacă uiți să apelezi `listen()` pe un socket TCP înainte de `accept()`?**

- a) Clientul se conectează normal *(Misconceptie: crede că listen() e opțional)*
- b) Socket-ul devine automat UDP *(Misconceptie: confuzie totală)*
- c) **`accept()` eșuează cu eroare** ✓
- d) Serverul primește date dar nu poate răspunde *(Misconceptie: confuzie cu send/recv)*

*De ce e greșit a): Fără listen(), socket-ul nu e marcat ca pasiv.*

---

**9. Ce reprezintă portul într-o adresă socket?**

- a) Adresa fizică a calculatorului *(Misconceptie: confuzie cu MAC)*
- b) Adresa IP a rețelei *(Misconceptie: confuzie cu IP)*
- c) **Identificatorul aplicației/procesului pe host** ✓
- d) Viteza de transfer *(Misconceptie: confuzie cu bandwidth)*

*Analogie corectă: IP = adresa clădirii, Port = numărul apartamentului.*

---

**10. În modelul OSI, încapsularea înseamnă:**

- a) Criptarea datelor pentru securitate *(Misconceptie: confuzie cu TLS/encryption)*
- b) Comprimarea datelor pentru eficiență *(Misconceptie: confuzie cu compression)*
- c) **Adăugarea antetelor specifice fiecărui strat** ✓
- d) Eliminarea informațiilor sensibile *(Misconceptie: confuzie cu redactare)*

*De ce e greșit a): Criptarea e o funcție a stratului Prezentare, nu e încapsulare.*

---

### Întrebări deschise

1. **Explicați procesul de încapsulare** pentru un mesaj HTTP de la browser la server. (5 puncte)
   - *Răspuns așteptat*: Date HTTP → Segment TCP (port 80) → Pachet IP (adrese IP) → Cadru Ethernet (adrese MAC) → Biți

2. **Comparați TCP și UDP** din perspectiva: overhead, fiabilitate, cazuri de utilizare. (5 puncte)
   - *Răspuns așteptat*: TCP are overhead mai mare (20+ bytes header, handshake, ACK-uri), oferă fiabilitate; UDP are overhead mic (8 bytes), fără garanții. TCP pentru web/email, UDP pentru streaming/gaming.

3. **Implementați în pseudocod** un server TCP care răspunde cu uppercase la mesaje. (5 puncte)
   - *Răspuns așteptat*: socket() → bind() → listen() → accept() → recv() → upper() → send() → close()

---

## Corelarea cu fișa disciplinei

### Competențe evaluate

| Competență din fișă | Cum e evaluată în S2 |
|---------------------|----------------------|
| C1: Utilizarea conceptelor de rețea | Întrebări despre straturi OSI/TCP-IP |
| C2: Programare de rețea | Implementare server/client socket |
| C3: Analiza traficului | Captură și interpretare cu tshark |
| C6: Actualizare sisteme | Integrare modul în proiect echipă |

### Obiective specifice din fișă

- *„Folosirea facilităților pentru stațiile de lucru în rețea"* → Utilizare Mininet, netcat
- *„Comunicarea, informarea și accesarea aplicațiilor online"* → Server/Client TCP/UDP

---

## Feedback și îmbunătățire

### După fiecare seminar

Întrebări pentru studenți:
1. Ce a fost cel mai util?
2. Ce a fost cel mai dificil?
3. Ce ar trebui să fie explicat mai bine?

### Indicatori de succes

- [ ] ≥80% studenți pot rula demo-all fără erori
- [ ] ≥70% studenți identifică corect handshake TCP
- [ ] ≥60% studenți completează ambele template-uri
- [ ] ≥50% studenți rezolvă corect exercițiile de înțelegere
- [ ] Timp mediu de completare: ≤100 minute

---

*Revolvix&Hypotheticalandrei*
