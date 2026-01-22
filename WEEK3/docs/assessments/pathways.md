# Trasee de învățare — WEEK3

Nu toți studenții sunt la același nivel. Alege traseul potrivit.

---

## Care ești tu?

Răspunde sincer:

**Pot scrie un socket UDP fără să mă uit în documentație?**
- "Nu" sau "Nu prea" → **BASIC**
- "Da, dar verific uneori" → **STANDARD**
- "Da, din memorie" → **ADVANCED**

**Am folosit threading în Python?**
- Nu → rămâi la traseu sau coboară un nivel pentru tunnel

---

## Traseu BASIC

Pentru cine: termeni ca "socket", "bind", "port" sunt încă noi.

### Ce faci (2.5 ore)

1. **Teorie** (30 min)
   - Citește curs.md secțiunile 1-4
   - Focus pe analogii: telefonul, megafonul, WhatsApp
   - NU sări peste ele, ajută

2. **Broadcast — doar receiver** (30 min)
   - Copiază codul din quick_reference
   - Rulează pe h2, așteptă mesaje de la instructor
   - Observă output-ul, notează IP-ul sursă

3. **Broadcast — sender** (30 min)
   - ÎNTÂI rulează FĂRĂ SO_BROADCAST
   - Notează eroarea
   - Adaugă SO_BROADCAST, rulează din nou
   - Verifică că h2 primește

4. **Multicast — doar receiver** (30 min)
   - Copiază receiver-ul din quick_reference
   - ATENȚIE la ordinea bind/JOIN
   - Rulează, verifică cu instructor

5. **Auto-evaluare** (20 min)
   - Completează templates/auto_evaluare.md
   - Doar secțiunile A și B

### NU face

- TCP Tunnel (prea complex pentru acum)
- Exerciții CREATE

### Dacă termini devreme

- Încearcă să scrii receiver broadcast din memorie
- Explică unui coleg ce face SO_BROADCAST

---

## Traseu STANDARD

Pentru cine: ai folosit socket-uri dar nu broadcast/multicast.

### Ce faci (2 ore)

1. **Recapitulare** (15 min)
   - Citește quick_reference.md
   - Testează: scrii receiver broadcast în 2 minute fără notițe?

2. **Broadcast complet** (25 min)
   - Urmează lab.md Partea 1
   - Completează predicțiile
   - Captură cu tshark

3. **Multicast complet** (30 min)
   - Urmează lab.md Partea 2
   - Testează: ce se întâmplă cu JOIN înainte de bind?
   - Experiment: receiver fără JOIN

4. **TCP Tunnel** (35 min)
   - Urmează lab.md Partea 3
   - Testează cu netcat

5. **Evaluare** (15 min)
   - Exercițiu EVALUATE E1 sau E2 din lab.md
   - Quiz rapid din assessments/mini_quiz.md

### NU face (decât dacă ai timp)

- Exerciții CREATE (C1, C2)

---

## Traseu ADVANCED

Pentru cine: poți scrie un echo server din memorie.

### Ce faci (2 ore)

1. **Verificare** (10 min)
   - Scrie din memorie: broadcast sender + multicast receiver
   - Dacă nu poți în 5 minute → coboară la STANDARD

2. **Implementare rapidă** (20 min)
   - Parcurge lab.md Părțile 1-3
   - Toate predicțiile ar trebui să le nimerești

3. **Exerciții EVALUATE** (25 min)
   - Toate cele 3 din seminar.md
   - Discută cu instructor sau coleg

4. **Exercițiu CREATE** (50 min)
   - Alege: Protocol Heartbeat SAU Tunnel cu Logging
   - Cod funcțional + document justificare
   - Vezi lab.md Partea 4

5. **Peer teaching** (15 min)
   - Ajută pe cineva de pe traseul BASIC
   - Explică-i un concept, nu-i da codul

### Stretch goals

Dacă ai terminat tot:

- Implementează reliable multicast cu ACK-uri
- Adaugă load balancing la tunnel (round-robin)
- Fă un discovery service complet

---

## Tranziții

**De la BASIC la STANDARD:**
- Ai terminat BASIC și mai ai 45+ minute
- Poți scrie receiver broadcast din memorie
- → Continuă cu Multicast complet

**De la STANDARD la ADVANCED:**
- Ai terminat STANDARD și mai ai 30+ minute
- → Alege un exercițiu CREATE

**Coborâre:**
- Te simți copleșit? E OK să cobori un nivel
- Mai bine înveți bine 70% decât superficial 100%

---

## Sumar

| | BASIC | STANDARD | ADVANCED |
|---|---|---|---|
| Timp | 2.5h | 2h | 2h |
| Broadcast | Receiver | Full | Rapid |
| Multicast | Receiver | Full | Rapid |
| Tunnel | Nu | Da | + extensii |
| CREATE | Nu | Nu | 1 obligatoriu |
| Peer teaching | Primește | Opțional | Dă |
