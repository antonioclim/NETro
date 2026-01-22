# Laborator 14 — Dry-Run Evaluare & Diagnostic Practic

**Disciplină:** Rețele de calculatoare / Networking  
**Săptămâna:** 14 (finală)  
**Durată:** 90-120 minute

---

## Obiectiv

Laboratorul simulează o **evaluare tehnică realistă**: rulăm demo-ul din starterkit, interpretăm artefactele, facem modificări controlate și producem un raport scurt.

---

## Plan pe timp

| Timp | Activitate | Livrabil |
|------|------------|----------|
| 0-10 min | Setup + smoke test | `smoke_test.sh` OK |
| 10-25 min | Demo automat | `artifacts/` complet |
| 25-55 min | Analiză ghidată pcap | Răspunsuri la întrebări |
| 55-75 min | Modificare + rerun | Diferențe observate |
| 75-95 min | REPORT.md | Concluzii + comenzi + output |
| 95-120 min | Debrief + checklist | Plan prezentare proiect |

---

## Lucru în perechi (Pair Programming)

Pentru exercițiile practice, lucrați în perechi cu roluri alternate:

| Rol | Responsabilitate | Durată |
|-----|------------------|--------|
| **Driver** | Scrie comenzi, editează fișiere | 15 min |
| **Navigator** | Verifică, sugerează, consultă documentația | 15 min |

**Reguli:**
- Schimbați rolurile la fiecare 15 minute
- Navigator-ul NU dictează caracter cu caracter — sugerează direcția
- Ambii sunt responsabili pentru rezultat
- Discutați înainte de a executa comenzi cu `sudo`

**De ce funcționează:** Două perechi de ochi detectează erori mai repede; explicarea gândirii clarifică înțelegerea.

---

## Pas 0: Setup mediu

```bash
# Intră în directorul kit-ului
cd starterkit_saptamana_14

# Instalează dependențele (dacă nu sunt deja)
sudo bash scripts/setup.sh

# Verifică mediul
bash tests/smoke_test.sh
```

**Output așteptat:** Toate testele trec (✓).

---

## Pas 1: Demo automat

```bash
# Rulează demo-ul complet
make run-demo

# SAU explicit
sudo bash scripts/run_all.sh
```

**Ce se întâmplă:**
1. Pornește rețeaua Mininet (4 hosturi, 2 switch-uri)
2. Pornește backend servers pe app1 și app2
3. Pornește load balancer pe lb
4. Pornește captură tcpdump
5. Generează trafic TCP echo și HTTP
6. Oprește captura și procesează cu tshark
7. Generează report.json

**Verificare:**
```bash
ls -la artifacts/
# Ar trebui să vezi:
# - capture_lb.pcap
# - tshark_summary.txt
# - http_client.log
# - report.json
# - app1.log, app2.log, lb.log
```

---

## Pas 2: Analiză pcap

### 2.1 Conversații IP
```bash
tshark -r artifacts/capture_lb.pcap -q -z conv,ip
```

**Întrebare:** Câte perechi IP distincte apar? Care sunt?

### 2.2 Conversații TCP
```bash
tshark -r artifacts/capture_lb.pcap -q -z conv,tcp
```

**Întrebare:** Câte conexiuni TCP au fost stabilite?

### 2.3 Cereri HTTP
```bash
tshark -r artifacts/capture_lb.pcap -Y "http.request" \
  -T fields -e frame.number -e ip.src -e ip.dst -e http.request.uri
```

**Întrebare:** Câte cereri HTTP apar? Către ce destinații?

### 2.4 Handshake TCP (SYN)
```bash
tshark -r artifacts/capture_lb.pcap -Y "tcp.flags.syn==1 && tcp.flags.ack==0"
```

**Întrebare:** Câte conexiuni noi (SYN) au fost inițiate?

### 2.5 Corelație cu loguri
```bash
cat artifacts/http_client.log | head -10
cat artifacts/report.json | python3 -m json.tool
```

**Întrebare:** Distribuția pe backends corespunde cu ce vezi în pcap?

---

## Pas 3: Modificări controlate

### Modificare A: Oprește un backend
```bash
# În timpul demo-ului sau într-o sesiune separată:
# 1. Găsește PID-ul backend-ului app2
ps aux | grep backend_server

# 2. Oprește-l
kill <PID>

# 3. Generează trafic și observă
curl http://10.0.0.10:8080/
# Ce status primești? Ce vezi în lb.log?
```

**Observație așteptată:** Toate cererile merg către app1; app2 e marcat unhealthy.

### Modificare B: Adaugă delay
Editează `mininet/topologies/topo_14_recap.py`:
```python
# Schimbă delay="1ms" în delay="50ms" în addLink()
```

Rerulează demo-ul și compară latențele din `http_client.log`.

### Modificare C: Timeout prea mic
Editează `python/apps/http_client.py`, setează `--timeout 0.01` și observă erorile.

---

## Pas 4: Raport (REPORT.md)

Creează un fișier `REPORT.md` cu:

```markdown
# Raport Laborator S14

## 1. Comenzi rulate
- `make run-demo`
- `tshark -r artifacts/capture_lb.pcap -q -z conv,tcp`
- ...

## 2. Rezultate principale
- Total cereri HTTP: X
- Distribuție: app1=Y, app2=Z
- Latență medie: W ms

## 3. Observații din pcap
- Am observat N handshake-uri TCP
- Cereri HTTP distribuite către: ...

## 4. Modificare testată
- Am oprit backend app2
- Efect: toate cererile au mers la app1

## 5. Concluzie
- Kit-ul demonstrează corect pattern-ul LB
- Diagnosticul cu tshark confirmă distribuția
```

---

## Pas 5: Cleanup

```bash
make clean
# SAU
sudo bash scripts/cleanup.sh
```

---

## Exerciții suplimentare (opțional)

### E1: Verificare proiect propriu
Adaptează `project_config.json` pentru proiectul tău și rulează harness-ul:
```bash
python3 python/exercises/ex_14_02.py --config my_config.json --out my_report.json
```

### E2: Quiz recapitulare
```bash
python3 python/exercises/ex_14_01.py --selftest
```

### E3: Captură manuală
```bash
# Terminal 1: pornește server
python3 python/apps/backend_server.py --id test --port 9999

# Terminal 2: captură
sudo tcpdump -i lo port 9999 -w /tmp/test.pcap

# Terminal 3: client
curl http://localhost:9999/

# Analiză
tshark -r /tmp/test.pcap
```

### E4: Tracing (fără execuție)
Exerciții de urmărire a codului — prezici ce se întâmplă fără să rulezi:
```bash
python3 python/exercises/ex_14_04_tracing.py --list
python3 python/exercises/ex_14_04_tracing.py --show 1
```

---

## Întrebări de reflecție

1. Ce dovezi minimale ai include într-un bug report de rețea?
2. Când este pcap-ul prea mult și când este indispensabil?
3. Ce ai automatiza (în CI) din acest workflow?
4. Cum ai demonstra că load balancer-ul distribuie corect?

---

## Criterii evaluare laborator

| Criteriu | Puncte |
|----------|--------|
| Setup corect + smoke test | 2 |
| Demo rulat cu succes | 2 |
| Analiză pcap corectă | 2 |
| Modificare testată | 2 |
| REPORT.md complet | 2 |
| **Total** | **10** |

---

## Resurse

- `docs/curs.md` - Teorie recapitulare
- `docs/seminar.md` - Pregătire prezentare
- `docs/checklist.md` - Checklist cadru didactic
- `tests/expected_outputs.md` - Output-uri de referință
