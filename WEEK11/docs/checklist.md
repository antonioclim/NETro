# Checklist Instructor – Săptămâna 11

## Înainte de Laborator (1-2 zile înainte)

### Pregătire Tehnică

- [ ] Verifică că `starterkit.zip` este disponibil pe platforma de curs
- [ ] Testează toate demo-urile pe mașina de prezentare
- [ ] Verifică că imaginile Docker sunt descărcate:
  ```bash
  docker pull nginx:alpine
  docker pull python:3.11-alpine
  ```
- [ ] Verifică accesul la `ftp.gnu.org` pentru demo FTP
- [ ] Pregătește VM-ul demo cu Mininet funcțional
- [ ] Asigură-te că porturile 80, 8080-8083 sunt libere

### Pregătire Materiale

- [ ] Deschide `docs/curs.md` pentru teorie
- [ ] Deschide `docs/seminar.md` pentru seminar
- [ ] **NOU**: Pregătește `docs/peer_instruction.md` — selectează 2-3 întrebări pentru sesiune
- [ ] **NOU**: Printează `docs/exercises_noncode.md` pentru exercițiile trace/Parsons
- [ ] Pregătește terminalul cu font mare pentru demo
- [ ] Încarcă slide-urile de backup (PDF) în caz de probleme tehnice

### Comunicare

- [ ] Anunță studenții să descarce starterkit-ul înainte de laborator
- [ ] Aminteşte cerințele de sistem (Docker, Python 3.10+)
- [ ] Publică link către documentația laboratorului

---

## În Timpul Laboratorului

### Introducere (5-10 minute)

- [ ] Prezintă obiectivele săptămânii
- [ ] Recapitulare rapidă: TCP/UDP, HTTP, servere web
- [ ] Explică legătura cu proiectul de echipă

### Peer Instruction #1: FTP Modes (8 minute)

- [ ] Afișează PI-1 din `docs/peer_instruction.md`
- [ ] Primul vot (1 min) — notează distribuția
- [ ] Discuție în perechi (3 min)
- [ ] Al doilea vot (30 sec)
- [ ] Explicație cu focus pe NAT și misconceptii (2-3 min)

### Demo Live (20-30 minute)

- [ ] Demonstrează `make setup` și `make verify`
- [ ] Arată pornirea backend-urilor + LB Python
- [ ] **PREDICȚIE**: Înainte de round robin, cere predicții (ce ordine?)
- [ ] Demonstrează Round Robin (vizual în terminal)
- [ ] **PREDICȚIE**: Pentru IP hash, cere predicția (care backend?)
- [ ] Arată IP Hash și sticky sessions
- [ ] Demonstrează failover (oprește un backend)
- [ ] Arată stack-ul Docker Nginx
- [ ] Compară vizual LB Python vs Nginx

### Peer Instruction #2: LB Algorithms (8 minute)

- [ ] Afișează PI-4 din `docs/peer_instruction.md`
- [ ] Proces standard: vot → discuție → revot → explicație

### Lucru Individual/Echipă (60-90 minute)

- [ ] Monitorizează progresul studenților
- [ ] Oferă asistență pentru probleme de configurare
- [ ] Verifică că toți au trecut de Pașii 0-4
- [ ] Încurajează experimentarea cu parametri diferiți
- [ ] **NOU**: Distribuie exercițiul T1 (DNS Trace) pentru lucru individual

### Întrebări de Control

Pune aceste întrebări în timpul laboratorului:

1. "De ce modul pasiv FTP este preferat în practică?"
2. "Ce se întâmplă dacă toate backend-urile cad?"
3. "Când ai folosi least_conn în loc de round_robin?"
4. "Cum detectează load balancer-ul că un backend a căzut?"
5. "Ce rol are TTL-ul în DNS?"

### Debugging Comun

**Problema: "Port already in use"**
```bash
sudo lsof -i :8080
sudo kill <PID>
```

**Problema: "Docker permission denied"**
```bash
sudo usermod -aG docker $USER
# Sau: sudo su - $USER
```

**Problema: "Mininet not found"**
```bash
sudo apt install mininet openvswitch-switch
sudo mn -c  # Curăță procese vechi
```

---

## Recapitulare (10-15 minute)

### Puncte Cheie de Acoperit

- [ ] Diferența round_robin vs least_conn vs ip_hash
- [ ] Failover pasiv: max_fails, fail_timeout
- [ ] Avantajele modului pasiv FTP
- [ ] Structura pachetelor DNS (header + question)
- [ ] Canalele SSH și port forwarding

### Exercițiu Final: Parsons Problem (5 minute)

- [ ] Distribuie P1 (SSH Port Forward) sau P2 (Nginx Config) din `docs/exercises_noncode.md`
- [ ] Rezolvare în perechi (3 min)
- [ ] Discuție soluție (2 min)

### Legătura cu Proiectul

- [ ] Explică artefactul săptămânal (docker-compose + nginx)
- [ ] Clarifică criteriile de evaluare (rubrici)
- [ ] Stabilește deadline-ul pentru predare

---

## După Laborator

### Evaluare

- [ ] Colectează artefactele de la fiecare echipă
- [ ] Verifică funcționarea `docker compose up` pentru fiecare proiect
- [ ] Aplică rubrica de evaluare
- [ ] Notează probleme comune pentru discuție la următorul curs

### Feedback

- [ ] Notează ce a funcționat bine
- [ ] Identifică puncte de îmbunătățit
- [ ] Actualizează starterkit-ul dacă e cazul
- [ ] **NOU**: Notează care întrebări PI au avut distribuție bună (40-60% corect)

### Comunicare

- [ ] Publică soluțiile / răspunsurile la exerciții
- [ ] Publică soluțiile pentru exercițiile non-cod (T1, T2, P1, P2)
- [ ] Răspunde la întrebări pe forum/email
- [ ] Anunță tema pentru săptămâna următoare (S12: SMTP, POP3, IMAP)

---

## Timing Sugerat (cu elemente pedagogice noi)

| Segment | Activitate | Durată | Cumulat |
|---------|------------|--------|---------|
| 0:00 | Introducere + setup | 10 min | 0:10 |
| 0:10 | **PI-1: FTP modes** | 8 min | 0:18 |
| 0:18 | Demo backends + LB Python (cu predicții) | 20 min | 0:38 |
| 0:38 | **PI-4: LB Algorithms** | 8 min | 0:46 |
| 0:46 | Demo Nginx Docker | 15 min | 1:01 |
| 1:01 | **Exercițiu T1: DNS Trace** (individual) | 12 min | 1:13 |
| 1:13 | Pauză | 10 min | 1:23 |
| 1:23 | Lucru individual (DNS, FTP) | 30 min | 1:53 |
| 1:53 | Demo Mininet (opțional) | 15 min | 2:08 |
| 2:08 | **Parsons P1 sau P2** (perechi) | 7 min | 2:15 |
| 2:15 | Recapitulare + Proiect | 15 min | 2:30 |

**Timp total**: ~2.5 ore

---

## Materiale Suplimentare pentru Instructor

### Peer Instruction
Fișier: `docs/peer_instruction.md`
- 5 întrebări MCQ formatate complet
- Fiecare cu distractori bazați pe misconceptii
- Timp per întrebare: 8-10 minute
- Selectează 2-3 pentru o sesiune de laborator

### Exerciții Non-Cod
Fișier: `docs/exercises_noncode.md`
- **T1**: DNS packet trace (intermediar, 15 min)
- **T2**: TCP/FTP handshake trace (începător, 10 min)
- **P1**: SSH port forwarding Parsons (intermediar, 8 min)
- **P2**: Nginx upstream Parsons (începător, 5 min)
- **P3**: DNS query construction Parsons (avansat, 10 min)
- **D1-D3**: Debugging exercises (5-10 min fiecare)

### Predicții în Lab
Fișier: `docs/lab.md` conține acum prompturi de predicție:
- Înainte de test round robin
- Înainte de test IP hash
- Înainte de test failover
- Înainte de test DNS
- Înainte de test FTP activ/pasiv

### Analogii CPA (din curs.md)
- **FTP**: Telefon (control) + Fax (date)
- **DNS**: Serviciul de Informații Telefonice
- **SSH**: Tunel securizat prin munte

---

## Resurse Rapide

### Comenzi Frecvente

```bash
# Verificare mediu
make verify

# Pornire demo complet
make demo-all

# Curățare
make clean

# Ajutor
make help
```

### Linkuri Utile

- Documentație Nginx: https://nginx.org/en/docs/
- Docker Compose: https://docs.docker.com/compose/
- Mininet Walkthrough: http://mininet.org/walkthrough/
- RFC 1035 (DNS): https://datatracker.ietf.org/doc/html/rfc1035

---

*Checklist pentru Săptămâna 11 – Rețele de Calculatoare*  
*Revolvix&Hypotheticalandrei*
