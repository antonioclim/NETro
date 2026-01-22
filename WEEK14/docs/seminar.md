# Seminar 14 — Evaluarea Proiectului în Echipă

**Disciplină:** Rețele de calculatoare / Networking  
**Săptămâna:** 14 (finală)  
**Durată:** 120 minute

---

## Obiectiv

Seminarul 14 este dedicat **prezentării și evaluării proiectelor de echipă**. Conform fișei disciplinei, prezentarea proiectului este **condiție de acces la examen**.

### Ce demonstrezi

1. Proiectul **funcționează** (rulare reproductibilă din mediu curat)
2. Înțelegi **arhitectura** și poți justifica deciziile tehnice
3. Poți **diagnostica** probleme folosind instrumentele învățate
4. Produci **evidențe verificabile** (loguri, capturi, rapoarte)

---

## Structura prezentării (7-10 minute/echipă)

### 1. Introducere (1 min)
- Ce face proiectul? (o propoziție)
- Ce protocoale/tehnologii folosește?

### 2. Demo live (3-4 min)
- Pornire din mediu curat (setup, run)
- Demonstrare funcționalitate principală
- Arată o captură pcap relevantă

### 3. Arhitectură (2 min)
- Diagramă simplă (componente, fluxuri)
- Justificare alegeri tehnice

### 4. Q&A (2-3 min)
- Întrebări de apărare (vezi mai jos)

---

## Întrebări tipice de apărare

### Nivel 1: Cunoaștere
- Pe ce port ascultă serverul?
- Ce protocol de transport folosiți?
- Ce înseamnă codul HTTP 502?

### Nivel 2: Înțelegere
- Explică fluxul unei cereri de la client la server
- Ce se întâmplă când `accept()` returnează?
- De ce ai ales TCP și nu UDP?

### Nivel 3: Aplicare
- Modifică timeout-ul și arată efectul
- Adaugă un nou endpoint și testează-l
- Schimbă IP-ul și arată ce se strică

### Nivel 4: Analiză
- De ce crezi că `recv()` se blochează?
- Compară latența cu și fără proxy
- Ce indică retransmisiile din pcap?

### Nivel 5: Evaluare
- Este serviciul tău vulnerabil la DoS?
- Cum ai îmbunătăți scalabilitatea?
- Ce ai face diferit în producție?

---

## Întrebări Peer Instruction (pentru seminar interactiv)

Aceste întrebări pot fi folosite cu metodologia Peer Instruction:
1. Studenții votează individual (1 min)
2. Discuție în perechi (3 min)
3. Revot și explicație (2 min)

### PI-1: Connection Refused vs Timeout

**Scenariu:** Clientul încearcă `curl http://10.0.0.5:8080/` și primește eroare după 3 secunde.

Ce s-a întâmplat cel mai probabil?

A) Serverul ascultă pe port dar a refuzat cererea HTTP  
B) Portul 8080 nu ascultă pe 10.0.0.5 (primim RST imediat)  
C) Un firewall a blocat pachetul SYN (timeout fără răspuns)  
D) DNS-ul nu a putut rezolva adresa IP  

<details>
<summary>Răspuns și analiză</summary>

**Corect: C** — Timeout de 3 secunde indică SYN trimis dar fără răspuns (DROP în firewall).

**Distractori:**
- **A** — Greșit: Serverul care refuză cererea HTTP tot răspunde (cod 4xx/5xx), nu timeout
- **B** — Greșit: RST vine imediat (<100ms), nu după 3 secunde
- **D** — Greșit: Am specificat IP direct, nu hostname

**Misconceptie vizată:** Confuzia între Connection Refused (RST rapid) și Timeout (no response).
</details>

### PI-2: TCP Handshake

**Scenariu:** În pcap vezi: `SYN → SYN-ACK → ACK → PSH,ACK (GET) → RST`

Ce s-a întâmplat?

A) Handshake-ul a eșuat, conexiunea nu s-a stabilit  
B) Conexiunea s-a stabilit, dar serverul a închis-o brusc după GET  
C) Clientul a anulat cererea înainte să primească răspuns  
D) Firewall-ul a injectat RST pentru a bloca traficul  

<details>
<summary>Răspuns și analiză</summary>

**Corect: B** — Handshake complet (SYN/SYN-ACK/ACK), apoi RST de la server după primirea GET.

**Distractori:**
- **A** — Greșit: SYN-ACK + ACK = handshake complet
- **C** — Greșit: Clientul a trimis GET, deci nu a anulat înainte
- **D** — Posibil dar mai puțin probabil decât B; firewall RST ar veni mai devreme

**Misconceptie vizată:** Nu se recunoaște că handshake-ul în 3 pași s-a finalizat.
</details>

### PI-3: ss -lntp output

**Scenariu:** Rulezi `ss -lntp` și vezi:
```
LISTEN  0  128  0.0.0.0:80  0.0.0.0:*  users:(("nginx",pid=1234,fd=6))
```

Poți accesa serverul de pe alt host cu `curl http://192.168.1.100:80/`?

A) Da, 0.0.0.0 înseamnă că ascultă pe toate interfețele  
B) Nu, 0.0.0.0 înseamnă că ascultă doar pe localhost  
C) Da, dar doar dacă nginx e configurat cu server_name corect  
D) Nu, portul 80 necesită HTTPS pentru acces extern  

<details>
<summary>Răspuns și analiză</summary>

**Corect: A** — `0.0.0.0:80` = bind pe toate interfețele, accesibil de oriunde (dacă nu e firewall).

**Distractori:**
- **B** — Greșit: 127.0.0.1 = localhost; 0.0.0.0 = toate interfețele
- **C** — Greșit: server_name afectează virtual hosts, nu conectivitatea de bază
- **D** — Greșit: HTTP funcționează pe port 80 fără TLS

**Misconceptie vizată:** Confuzia între 0.0.0.0 (wildcard) și 127.0.0.1 (localhost only).
</details>

---

## Rubrică de evaluare

### Criterii (total: 100 puncte → nota pe proiect)

| Criteriu | Pondere | Excelent (90-100%) | Bun (70-89%) | Suficient (50-69%) | Insuficient (<50%) |
|----------|---------|-------------------|--------------|--------------------|--------------------|
| **Complexitate** | 40% | Arhitectură multi-componentă, protocoale diverse | Arhitectură solidă, 2+ componente | Implementare de bază funcțională | Prea simplu/incomplet |
| **Funcționalitate** | 30% | Funcționează perfect, edge cases tratate | Funcționează cu mici probleme | Funcționează parțial | Nu funcționează |
| **Prezentare/Q&A** | 20% | Explicații clare, răspunsuri corecte | Majoritatea răspunsurilor corecte | Răspunsuri parțiale | Nu poate explica |
| **Documentație** | 10% | README complet, comentarii, exemple | README bun, unele comentarii | README minimal | Lipsește |

### Semne de reuștă

**Complexitate:**
- [ ] Mai multe componente (client, server, proxy/LB)
- [ ] Protocoale diverse (TCP, HTTP, eventual TLS)
- [ ] Persistență sau stare (opțional)

**Funcționalitate:**
- [ ] Pornește din mediu curat în < 5 minute
- [ ] Demonstrează flow principal
- [ ] Tratează erori (timeout, conexiune refuzată)

**Prezentare:**
- [ ] Poate explica fiecare componentă
- [ ] Răspunde la întrebări fără a citi din cod
- [ ] Arată evidențe (pcap, loguri)

**Documentație:**
- [ ] README cu pași de instalare/rulare
- [ ] Comentarii în cod pentru părțile complexe
- [ ] Exemplu de output așteptat

---

## Pregătire pentru prezentare

### Checklist înainte de seminar

- [ ] Proiectul pornește din mediu curat (VM nouă/curățată)
- [ ] README actualizat cu pași exacti
- [ ] Am testat demo-ul de cel puțin 2 ori
- [ ] Am pregătit 1-2 capturi pcap relevante
- [ ] Știu să răspund la întrebările de bază

### Ce să aduci

1. **Laptop** cu VM pregătită SAU acces la mediul de dezvoltare
2. **README** clar (printabil)
3. **Demo plan** (pași scriși)
4. **Capturi** pregătite (pentru cazul în care demo-ul eșuează)

### Troubleshooting rapid

| Problemă | Soluție rapidă |
|----------|----------------|
| VM nu pornește | Folosește capturile pregătite |
| Port ocupat | `sudo ss -lntp | grep <port>` + kill |
| Mininet murdar | `sudo mn -c` |
| OVS down | `sudo systemctl restart openvswitch-switch` |

---

## Desfășurarea seminarului

### Ordine prezentări
- Se stabilește la începutul seminarului (random sau voluntari)
- Fiecare echipă are 10-12 minute (prezentare + Q&A)

### Rolul audienței
- Ascultă activ
- Pune întrebări constructive
- Ia notițe pentru propria pregătire

### Evaluare
- Cadrul didactic notează conform rubricii
- Feedback oral imediat sau la final

---

## După seminar

### Pentru studenți
- Finalizați documentația
- Pregătiți-vă pentru examen (70% din nota finală)
- Reflectați: ce ați învățat? ce ați face diferit?

### Livrabile finale
- Codul sursă (repository sau arhivă)
- README actualizat
- Raport scurt (opțional, pentru bonus)

---

## Exemple de proiecte acceptabile

### Nivel minim
- Client-server TCP echo cu logging
- Server HTTP simplu cu 2-3 endpoint-uri

### Nivel mediu
- Load balancer cu 2 backends
- Chat multi-client cu broadcast
- DNS proxy cu cache

### Nivel avansat
- Microservicii cu service discovery
- VPN simplu (tunnel TCP)
- SDN controller cu politici custom

---

## Resurse

- Starterkit S14 (exemplu de structură)
- Documentația kit-ului (docs/)
- Întrebările de recapitulare (ex_14_01.py)
