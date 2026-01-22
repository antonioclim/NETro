# Întrebări Peer Instruction — Săptămâna 13
## IoT și Securitate în Rețele de Calculatoare

---

## Instrucțiuni pentru Instructor

**Protocol pentru fiecare întrebare:**
1. Afișează întrebarea pe ecran (1 min citire)
2. **Vot individual** — studenții ridică mâna sau folosesc poll digital (1 min)
3. Notează distribuția răspunsurilor
4. **Discuție în perechi** — 2-3 minute, studenții își explică reciproc alegerea
5. **Revot** (30 sec)
6. **Debrief** — explicația corectă + de ce sunt greșite celelalte (2 min)

**Timp total per întrebare:** ~7 minute

**Plasare în seminar:**
- PI-1: După explicația QoS (Faza 3)
- PI-2: După explicația port states (Faza 2)
- PI-3: La începutul Fazei 4 (captură)
- PI-4: În introducere sau recapitulare
- PI-5: După discuția despre măsuri defensive

---

## 🗳️ PI-1: QoS pentru Alerte Critice

### Scenariu
Un senzor de fum dintr-o clădire de birouri trimite alerte prin MQTT.
Conexiunea WiFi poate fi instabilă din cauza interferențelor.

### Întrebare
Ce nivel QoS ar trebui configurat pentru alertele de fum?

| | Răspuns |
|---|---------|
| **A** | QoS 0 — pentru latență minimă și viteză |
| **B** | QoS 1 — garantează livrarea, acceptă duplicate |
| **C** | QoS 2 — pentru a evita duplicatele |
| **D** | Nu contează, broker-ul optimizează automat |

---

### ✅ Răspuns corect: **B**

### 📋 Note Instructor

**Target accuratețe primul vot:** ~55%

**Analiza distractorilor:**

| Opțiune | Misconceptie vizată | Contraargument |
|---------|---------------------|----------------|
| **A** | "Viteza e mai importantă pentru alerte" | O alertă pierdută e mai gravă decât 50ms întârziere. Siguranța > viteză. |
| **C** | "Duplicatele sunt problematice" | Pentru alerte, duplicatele sunt OK — le tratezi la aplicație (idempotent handler). QoS 2 adaugă overhead inutil. |
| **D** | "Protocolul se descurcă singur" | QoS e negociat între client și broker. Clientul trebuie să specifice. |

**Întrebare follow-up:** "Ce QoS ați folosi pentru telemetria de temperatură la fiecare 5 secunde?" (Răspuns: QoS 0 — pierderea unei citiri nu e critică)

---

## 🗳️ PI-2: Interpretare Port State

### Scenariu
```bash
$ python3 port_scanner.py --target 192.168.1.100 --port 22
Port 22: FILTERED
```

### Întrebare
Ce indică rezultatul **"FILTERED"**?

| | Răspuns |
|---|---------|
| **A** | SSH nu e instalat pe server |
| **B** | Firewall-ul blochează și nu răspunde (DROP) |
| **C** | Serverul a trimis pachet RST |
| **D** | Portul e deschis dar serviciul nu răspunde |

---

### ✅ Răspuns corect: **B**

### 📋 Note Instructor

**Target accuratețe primul vot:** ~45% (întrebare mai dificilă)

**Analiza distractorilor:**

| Opțiune | Misconceptie vizată | Contraargument |
|---------|---------------------|----------------|
| **A** | Confuzie FILTERED vs CLOSED | Dacă SSH nu e instalat dar firewall-ul permite, primești RST → CLOSED, nu FILTERED |
| **C** | Nu înțelege diferența RST vs DROP | RST = CLOSED (refuz explicit). FILTERED = niciun răspuns (DROP silențios) |
| **D** | Confuzie timeout aplicație vs rețea | Timeout la scan = firewall DROP, nu serviciu lent |

**Vizualizare pe tablă:**
```
OPEN:     SYN ──────► SYN-ACK ◄────── (serviciu răspunde)
CLOSED:   SYN ──────► RST ◄────────── (port refuzat)
FILTERED: SYN ──────► ... ◄────────── (nimic, firewall DROP)
```

---

## 🗳️ PI-3: Securitatea MQTT fără TLS

### Scenariu
Un sistem IoT industrial folosește MQTT pe **portul 1883** (plaintext, fără TLS).
Un atacator este conectat în aceeași rețea WiFi.

### Întrebare
Ce poate face atacatorul?

| | Răspuns |
|---|---------|
| **A** | Doar să asculte mesajele (pasiv) |
| **B** | Să asculte și să trimită mesaje false |
| **C** | Să asculte, injecteze, și modifice mesaje în tranzit |
| **D** | Nimic, MQTT are protecție built-in |

---

### ✅ Răspuns corect: **C**

### 📋 Note Instructor

**Target accuratețe primul vot:** ~60%

**Analiza distractorilor:**

| Opțiune | Misconceptie vizată | Contraargument |
|---------|---------------------|----------------|
| **A** | Subestimează capabilitățile atacatorului | Dacă poate asculta, poate și trimite pe același canal. WiFi e shared medium. |
| **B** | Nu consideră MITM complet | Cu ARP spoofing, atacatorul poate intercepta și modifica tot traficul între client și broker |
| **D** | **Misconceptie periculoasă!** | MQTT protocol = zero security by default. TLS e opțional și trebuie configurat explicit. |

**Demo impact:** Deschide Wireshark, capturează MQTT plaintext, arată payload în clar. Efect vizual puternic!

---

## 🗳️ PI-4: Cyber Kill Chain

### Scenariu
Un atacator a compromis un dispozitiv IoT vulnerabil din rețeaua companiei.
Administratorul observă că dispozitivul trimite trafic către un server extern necunoscut, la fiecare 30 de secunde.

### Întrebare
În ce fază a Cyber Kill Chain se află atacul?

| | Răspuns |
|---|---------|
| **A** | Reconnaissance |
| **B** | Exploitation |
| **C** | Command & Control (C2) |
| **D** | Actions on Objectives |

---

### ✅ Răspuns corect: **C**

### 📋 Note Instructor

**Target accuratețe primul vot:** ~50%

**Analiza distractorilor:**

| Opțiune | Misconceptie vizată | Contraargument |
|---------|---------------------|----------------|
| **A** | Confuzie temporală | Reconnaissance = ÎNAINTE de atac, culegere informații. Aici dispozitivul e deja compromis. |
| **B** | Nu înțelege că exploitation e momentan | Exploitation = momentul pătrunderii inițiale. Deja trecut dacă dispozitivul comunică. |
| **D** | Sare peste C2 | Actions on Objectives = obiectivul final (exfiltrare, sabotaj). Întâi trebuie canal C2 stabil. |

**Indicator cheie:** "Trafic periodic către server necunoscut" = beaconing = C2 clasic.

---

## 🗳️ PI-5: Segmentare Rețea

### Scenariu
O companie are:
- Senzori IoT (termostate, camere)
- Servere interne (ERP, baze de date)
- Stații de lucru (angajați)

Toate sunt în **aceeași rețea plată**: `192.168.1.0/24`

Un senzor IoT este compromis de malware.

### Întrebare
Ce poate accesa atacatorul din senzorul compromis?

| | Răspuns |
|---|---------|
| **A** | Doar alte dispozitive IoT similare |
| **B** | Orice dispozitiv din rețea (servere, workstations) |
| **C** | Nimic altceva, IoT-ul e izolat automat |
| **D** | Doar gateway-ul de internet |

---

### ✅ Răspuns corect: **B**

### 📋 Note Instructor

**Target accuratețe primul vot:** ~70% (mai ușor, dar foarte important)

**Analiza distractorilor:**

| Opțiune | Misconceptie vizată | Contraargument |
|---------|---------------------|----------------|
| **A** | "IoT stă în bula lui" | Fals! Fără segmentare explicită (VLAN), totul e accesibil în rețeaua plată. |
| **C** | "Izolare automată" | Nu există izolare automată. Flat network = acces la tot. |
| **D** | Confuzie gateway vs lateral | Gateway permite ieșire la internet, dar NU limitează mișcarea laterală în LAN. |

**De aceea segmentarea e critică!** Desenează pe tablă:
```
GREȘIT (flat):                    CORECT (segmentat):
┌─────────────────┐              ┌─────────────────┐
│ 192.168.1.0/24  │              │   VLAN 10       │ ◄── IoT
│  IoT + Servere  │              │   10.10.10.0/24 │
│  + Workstations │              ├─────────────────┤
│                 │              │   VLAN 20       │ ◄── Servere
│  TOTUL EXPUS!   │              │   10.10.20.0/24 │
└─────────────────┘              ├─────────────────┤
                                 │   VLAN 30       │ ◄── Users
                                 │   10.10.30.0/24 │
                                 └─────────────────┘
                                 + Firewall între VLAN-uri
```

---

## Sumar Timing

| Întrebare | Concept | Când | Durată |
|-----------|---------|------|--------|
| PI-1 | QoS MQTT | După Faza 3 (MQTT demo) | 7 min |
| PI-2 | Port states | În Faza 2 (scanare) | 7 min |
| PI-3 | Securitate MQTT | Început Faza 4 (captură) | 7 min |
| PI-4 | Kill Chain | Introducere sau recap | 7 min |
| PI-5 | Segmentare | După măsuri defensive | 7 min |

**Total:** ~35 minute (5 întrebări × 7 min)

Selectează **3 întrebări** pentru un seminar de 75 min (PI-1, PI-2, PI-3 recomandate).

---

*Material didactic — Rețele de Calculatoare*  
*ASE-CSIE | 2025-2026*
