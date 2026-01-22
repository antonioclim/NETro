# Checklist Cadru Didactic – Săptămâna 3

**Disciplină:** Rețele de Calculatoare  
**Temă:** Introducere în programarea de rețea / Socket programming  

---

## ✅ ÎNAINTE de curs/seminar/laborator

### Cu 1-2 zile înainte

- [ ] Verificare VM-uri funcționale (testare pe o mașină reprezentativă)
- [ ] Rulare `make verify` pe VM de test
- [ ] Verificare că toate exemplele Python rulează fără erori
- [ ] Testare demo-uri automate: `make demo-broadcast`, `make demo-multicast`, `make demo-tunnel`
- [ ] Verificare că fișierele HTML (theory.html, seminar.html, lab.html) se încarcă corect
- [ ] Pregătire slide-uri/notițe adiționale dacă e cazul
- [ ] Verificare disponibilitate internet în sală (pentru documentație)

### Cu 30 min înainte

- [ ] Pornire calculator/proiector
- [ ] Deschidere fișiere HTML în browser
- [ ] Verificare că terminalul e vizibil și font-ul suficient de mare
- [ ] Pregătire ferestre pentru demo live (Mininet CLI, terminal captură)
- [ ] Verificare microfon/audio (dacă e cazul)

---

## ✅ ÎN TIMPUL sesiunii

### Curs (2 ore)

| Timp | Activitate | Material | Note |
|------|------------|----------|------|
| 0:00-0:10 | Recapitulare săptămâna anterioară | Întrebări orale | 2-3 întrebări rapide |
| 0:10-0:30 | Socket API fundamentals | theory.html slides 1-8 | Accent pe model mental |
| 0:30-0:50 | TCP: caracteristici, framing, concurență | theory.html slides 9-14 | Exemplu cod echo server |
| 0:50-1:00 | **Pauză** | - | - |
| 1:00-1:20 | UDP: datagrame, broadcast | theory.html slides 15-18 | Demo tcpdump broadcast |
| 1:20-1:35 | UDP multicast | theory.html slides 18-20 | Observare IGMP cu tshark |
| 1:35-1:50 | TCP tunnel, RAW sockets | theory.html slides 21-24 | Menționare Scapy |
| 1:50-2:00 | Recapitulare, întrebări | theory.html slide 25 | Quiz interactiv |

### Seminar (2 ore)

| Timp | Activitate | Material | Verificare |
|------|------------|----------|------------|
| 0:00-0:15 | Setup mediu | seminar.html tab "Concept" | `make verify` |
| 0:15-0:35 | Experiment broadcast | seminar.html tab "Demo Live" | Mesaje pe h2, h3 |
| 0:35-0:55 | Experiment multicast | seminar.html tab "Demo Live" | IGMP Join vizibil |
| 0:55-1:05 | **Pauză** | - | - |
| 1:05-1:25 | TCP tunnel | seminar.html tab "Cod Ghidat" | HTTP prin tunnel |
| 1:25-1:45 | Capturare trafic | seminar.html tab "Wireshark" | Fișiere .pcap |
| 1:45-2:00 | Exerciții, întrebări | seminar.html tab "Exerciții" | 1 template completat |

### Laborator (2 ore)

| Timp | Activitate | Material | Checkpoint |
|------|------------|----------|------------|
| 0:00-0:15 | Verificare mediu + topologie | lab.html Pas 0-1 | pingall 0% loss |
| 0:15-0:35 | Broadcast experiment | lab.html Pas 2 | Receivers primesc |
| 0:35-0:55 | Multicast experiment | lab.html Pas 3 | Doar subscribers |
| 0:55-1:05 | **Pauză** | - | - |
| 1:05-1:25 | TCP tunnel experiment | lab.html Pas 4 | curl funcționează |
| 1:25-1:40 | Capturare + exerciții | lab.html Pas 5-6 | .pcap generate |
| 1:40-2:00 | Validare + cleanup | lab.html Pas 7 | `make test` passed |

---

## ✅ Întrebări de control (în timpul sesiunii)

### Nivel 1 - Cunoaștere

1. Ce protocol de transport folosește broadcast: TCP sau UDP?
2. Care este adresa broadcast pentru subrețeaua 10.0.0.0/24?
3. Ce face funcția `bind()` pe un socket?

### Nivel 2 - Înțelegere

4. De ce TCP nu suportă broadcast?
5. Care este diferența între `send()` și `sendall()`?
6. De ce avem nevoie de SO_REUSEADDR în server?

### Nivel 3 - Aplicare

7. Cum modifici codul pentru a folosi alt port?
8. Ce comanda tcpdump folosești pentru a vedea doar pachetele multicast?
9. Cum testezi că tunelul funcționează corect?

### Nivel 4 - Analiză

10. De ce un receiver multicast care nu face JOIN nu primește mesaje?
11. Ce se întâmplă dacă unul din thread-urile tunnel-ului se blochează?
12. Ce observi în captura pcap când un host face IGMP Join?

---

## ✅ Capcane comune / Greșeli studenți

| Greșeală | Simptom | Intervenție |
|----------|---------|-------------|
| Uitare SO_BROADCAST | Permission denied | Arată linia exactă de cod |
| Port diferit sender/receiver | Receivers nu primesc | Verificare parametri |
| Uitare IP_ADD_MEMBERSHIP | Multicast nu funcționează | Explicare struct mreq |
| Mininet necurățat | RTNETLINK errors | `sudo mn -c` |
| Firewall activ | Conexiuni eșuate | `sudo iptables -F` |
| Python 2 vs Python 3 | Syntax errors | Verificare `python3 --version` |

---

## ✅ DUPĂ sesiune

### Imediat după

- [ ] Răspuns la întrebări rămase (email/forum)
- [ ] Notare studenți care au avut dificultăți (pentru follow-up)
- [ ] Colectare feedback informal

### În 1-2 zile

- [ ] Publicare materiale pe platformă (dacă nu erau deja)
- [ ] Actualizare FAQ dacă au apărut întrebări noi
- [ ] Notițe pentru îmbunătățiri viitoare

### Pentru proiectul de echipă

- [ ] Verificare că echipele înțeleg componenta săptămânii 3
- [ ] Clarificări despre integrarea cu săptămânile anterioare
- [ ] Deadline reminder pentru livrabilul incremental

---

## ✅ Resurse de backup

### Dacă Mininet nu funcționează

```bash
# Alternativă cu Docker
make docker-build
make docker-run

# Sau netcat simplu între terminale locale
# Terminal 1: nc -lu 5007
# Terminal 2: echo "test" | nc -u -b 255.255.255.255 5007
```

### Dacă nu există conexiune internet

- Toate materialele sunt offline-capable (HTML standalone)
- Documentația RFC este menționată, nu necesară în timp real
- Exemplele Python nu au dependențe externe (doar `scapy` pentru ex08)

### Dacă timpul e insuficient

**Prioritizare (dacă trebuie să tai):**
1. ✅ Broadcast (OBLIGATORIU)
2. ✅ Multicast (IMPORTANT)
3. ⚠️ TCP Tunnel (poate fi homework)
4. ⚠️ Capturare detaliată (poate fi homework)

---

*Checklist pentru uzul cadrelor didactice – Rețele de Calculatoare, ASE-CSIE*  
*Revolvix&Hypotheticalandrei*
