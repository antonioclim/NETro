# Rubrici de Evaluare – Săptămâna 3

**Disciplină:** Rețele de Calculatoare  
**Temă:** Programare pe socket-uri: broadcast/multicast UDP, TCP tunnel  

---

## 1. Evaluare activitate săptămânală

### 1.1 Criteriu: Funcționalitate demonstrată (40%)

| Punctaj | Descriere |
|---------|-----------|
| 40% | Toate experimentele funcționează corect: broadcast, multicast, TCP tunnel |
| 30% | Două din trei experimente funcționează complet |
| 20% | Un experiment funcționează, celelalte parțial |
| 10% | Încercări vizibile, dar erori majore |
| 0% | Nimic funcțional |

**Verificare:**
```bash
make demo-broadcast  # Receivers primesc mesajele
make demo-multicast  # Doar subscribers primesc
make demo-tunnel     # curl returnează răspuns HTTP
```

### 1.2 Criteriu: Înțelegere conceptuală (30%)

| Punctaj | Descriere |
|---------|-----------|
| 30% | Explică corect diferențele broadcast/multicast, rolul SO_BROADCAST, IP_ADD_MEMBERSHIP, arhitectura tunnel |
| 22% | Înțelege 3 din 4 concepte cheie |
| 15% | Înțelege 2 din 4 concepte |
| 8% | Înțelege superficial, confuzii frecvente |
| 0% | Nu demonstrează înțelegere |

**Întrebări de verificare:**
1. De ce broadcast nu traversează routere?
2. Ce face struct `mreq` în multicast receiver?
3. De ce tunnel-ul are nevoie de două thread-uri?
4. Ce se întâmplă dacă omiți SO_REUSEADDR?

### 1.3 Criteriu: Capturare și analiză trafic (15%)

| Punctaj | Descriere |
|---------|-----------|
| 15% | Fișiere .pcap corecte, interpretare corectă a pachetelor |
| 10% | Fișiere .pcap generate, interpretare parțială |
| 5% | Comenzi de captură cunoscute, fără interpretare |
| 0% | Nu a generat capturi |

**Verificare:**
- `pcap/broadcast_capture.pcap` conține pachete UDP broadcast
- `pcap/multicast_capture.pcap` conține IGMP Join + pachete multicast

### 1.4 Criteriu: Exerciții completate (15%)

| Punctaj | Descriere |
|---------|-----------|
| 15% | 2+ exerciții template completate și funcționale |
| 10% | 1 exercițiu complet funcțional |
| 5% | Încercări vizibile, cod incomplet |
| 0% | Niciun exercițiu încercat |

**Exerciții evaluate:**
- `template_broadcast_discovery.py`
- `template_multicast_chat.py`
- `template_tunnel_logging.py`
- `template_rate_limiter.py`

---

## 2. Grading Scale

| Total | Calificativ | Descriere |
|-------|-------------|-----------|
| 90-100% | Excelent | Toate criteriile îndeplinite la nivel superior |
| 75-89% | Bine | Funcționalitate completă, înțelegere solidă |
| 60-74% | Satisfăcător | Majoritatea funcțională, lacune în înțelegere |
| 45-59% | Acceptabil | Funcționalitate parțială, necesită îmbunătățiri |
| < 45% | Insuficient | Nu îndeplinește cerințele minime |

---

## 3. Contribuția la proiectul de echipă

### 3.1 Livrabil săptămâna 3

**Cerință:** Echipa trebuie să integreze un mecanism de comunicare multi-nod în proiectul de rețea.

**Opțiuni acceptate:**
1. **Service Discovery** – componenta de descoperire folosind broadcast
2. **Notificări multicast** – sistem de publish-subscribe pentru evenimente
3. **Proxy/Tunnel** – gateway pentru servicii backend

### 3.2 Criterii de evaluare livrabil echipă

| Criteriu | Pondere | Descriere |
|----------|---------|-----------|
| **Funcționalitate** | 40% | Mecanismul funcționează conform specificațiilor |
| **Integrare** | 25% | Se integrează coerent cu componenetele din S1-S2 |
| **Documentație** | 20% | README actualizat, comentarii în cod |
| **Testabilitate** | 15% | Script de test/demo pentru componenta nouă |

### 3.3 Exemple de implementări acceptate

**Exemplu 1: Service Discovery cu Broadcast**
```
Componenta: discovery.py
Funcționalitate: 
- La pornire, serviciul trimite broadcast ANNOUNCE
- Alte servicii răspund cu endpoint-ul lor
- Se construiește o hartă a serviciilor disponibile
Integrare: Se folosește pentru a găsi serverul de configurare din S2
```

**Exemplu 2: Event Notifier cu Multicast**
```
Componenta: notifier.py
Funcționalitate:
- Serverul trimite notificări pe grupul 224.0.0.100
- Clienții se abonează și primesc evenimente
- Evenimente: USER_LOGIN, CONFIG_CHANGED, ALERT
Integrare: Completează sistemul de logging din S2
```

**Exemplu 3: API Gateway cu TCP Tunnel**
```
Componenta: gateway.py
Funcționalitate:
- Acceptă conexiuni pe port 8000
- Routează către backend servers pe baza path-ului
- Implementează basic load balancing
Integrare: Punct unic de acces pentru serviciile S1+S2
```

### 3.4 Deadline și format

| Element | Cerință |
|---------|---------|
| **Deadline** | Sfârșitul săptămânii 3 |
| **Format** | Push în repository-ul echipei |
| **Structură** | `/week3/` folder cu README, cod, test script |
| **Demo** | Video scurt (max 2 min) sau sesiune live |

---

## 4. Feedback formativ

### Ce să urmărești în săptămânile următoare

Pe baza performanței din săptămâna 3, studenții ar trebui să:

**Dacă au excelat:**
- Să exploreze challenge-ul Load Balancer
- Să implementeze extensii creative în proiectul de echipă
- Să ajute colegii care au dificultăți

**Dacă au avut dificultăți:**
- Să revadă conceptele de socket API (curs.md secțiunea 3)
- Să practice exemplele pas cu pas (lab.html)
- Să ceară clarificări la următorul seminar

### Legătura cu săptămânile viitoare

| Săptămâna | Concepte care se construiesc pe S3 |
|-----------|-----------------------------------|
| S4 | Protocoale text și binare custom peste TCP/UDP |
| S7 | Interceptare pachete, filtre, scanare porturi |
| S8 | Server HTTP (folosește TCP skills) |
| S11 | Load balancing, reverse proxy (TCP tunnel avansat) |

---

## 5. Auto-evaluare student

Studenții pot folosi acest checklist pentru auto-evaluare:

### Funcționalitate
- [ ] Pot rula `make demo-broadcast` și receivers primesc mesajele
- [ ] Pot rula `make demo-multicast` și doar subscribers primesc
- [ ] Pot rula `make demo-tunnel` și primesc răspuns HTTP

### Înțelegere
- [ ] Pot explica de ce broadcast necesită SO_BROADCAST
- [ ] Înțeleg structura mreq pentru multicast join
- [ ] Pot desena arhitectura TCP tunnel pe hârtie

### Capturare
- [ ] Pot genera capturi cu tcpdump/tshark
- [ ] Pot identifica IGMP Join în captură
- [ ] Pot filtra traficul după port în Wireshark

### Aplicare
- [ ] Am completat cel puțin un exercițiu template
- [ ] Am contribuit la livrabilul echipei
- [ ] Pot modifica exemplele pentru alt port/grup

---

*Rubrici pentru uzul evaluării – Rețele de Calculatoare, ASE-CSIE*  
*Revolvix&Hypotheticalandrei*
