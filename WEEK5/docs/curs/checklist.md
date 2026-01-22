# Checklist Cadru Didactic — Săptămâna 5

## Înainte de activitate

### Cu 1-2 zile înainte

- [ ] Verifică funcționarea VM-ului/mediului de laborator
  ```bash
  make verify
  ```
- [ ] Testează toate demo-urile din curs
  ```bash
  make demo-cidr demo-flsm demo-vlsm demo-ipv6
  ```
- [ ] Pornește o dată topologiile Mininet pentru a detecta probleme
  ```bash
  make mininet-test
  ```
- [ ] Pregătește exemple personalizate (adrese IP ale facultății, companii cunoscute studenților)
- [ ] Verifică slide-urile și actualizează dacă e cazul
- [ ] Alege 2-3 întrebări Peer Instruction din `docs/peer_instruction_week5.md`
- [ ] Pregătește întrebări de control pentru curs (minim 5)

### Cu 30 minute înainte

- [ ] Pornește calculatorul și deschide terminalul
- [ ] Deschide materialele în browser
- [ ] Verifică conexiunea la Internet (pentru eventuale demo-uri live)
- [ ] Pregătește foile de prezență și eventuale chestionare

---

## În timpul activității

### Curs (2 ore)

**Prima oră — Teorie**

- [ ] 0:00–0:10 — Recapitulare săptămâna anterioară, întrebări studenți
- [ ] 0:10–0:30 — Introducere în nivelul rețea, rolul adresării IP, analogii
- [ ] 0:30–0:50 — CIDR: notație, mască, adresă rețea, broadcast
- [ ] 0:50–1:00 — Mini-demonstrație Python: `ex_5_01_cidr_flsm.py analyze`
  - **Nu uita:** Cere predicții înainte de a rula codul!

**A doua oră — Aplicații și IPv6**

- [ ] 1:00–1:15 — Întrebare Peer Instruction (PI-5.1 sau PI-5.3)
- [ ] 1:15–1:35 — FLSM vs VLSM: când și de ce (cu analogia pizza)
- [ ] 1:35–1:50 — Introducere IPv6: format, comprimare, tipuri
- [ ] 1:50–2:00 — Întrebări finale, anunț seminar

**Puncte de verificare curs:**
- [ ] Studenții știu să calculeze numărul de gazde pentru un prefix dat?
- [ ] Studenții înțeleg diferența între FLSM și VLSM?
- [ ] Studenții pot comprima/expanda o adresă IPv6?

### Seminar/Laborator (2 ore)

**Prima oră — Exerciții CIDR/VLSM**

- [ ] 0:00–0:05 — Organizare perechi pentru pair programming
- [ ] 0:05–0:10 — Verificare prezență, răspuns la întrebări din curs
- [ ] 0:10–0:40 — Părțile A+B din seminar.md (CIDR, FLSM)
  - **Atenție:** Cere predicții înainte de fiecare execuție!
- [ ] 0:40–1:00 — Partea C (VLSM) — lucru asistat

**A doua oră — Mininet și consolidare**

- [ ] 1:00–1:30 — Experimente 5–6 din lab.md (topologii Mininet)
- [ ] 1:30–1:45 — Un exercițiu din `docs/exercitii_variate_week5.md` (Parsons sau Debugging)
- [ ] 1:45–1:55 — Exerciții individuale / lucru la proiect
- [ ] 1:55–2:00 — Recapitulare, feedback, anunț pentru săptămâna următoare

**Puncte de verificare seminar:**
- [ ] Toți studenții au rulat cu succes `topo_5_base.py`?
- [ ] Ping-ul între subrețele funcționează?
- [ ] Studenții au completat minim 3 exerciții?
- [ ] Cel puțin o predicție a fost discutată în grup?

---

## După activitate

### Imediat după (în aceeași zi)

- [ ] Notează problemele tehnice întâmpinate
- [ ] Notează întrebările frecvente ale studenților
- [ ] Marchează exercițiile unde studenții au avut dificultăți
- [ ] Notează ce misconceptii au apărut la Peer Instruction
- [ ] Curăță mediul de laborator
  ```bash
  make clean
  sudo mn -c
  ```

### În termen de 3 zile

- [ ] Publică materialele pe platforma de e-learning (dacă nu sunt deja)
- [ ] Răspunde la întrebările primite pe email/forum
- [ ] Actualizează materialele pe baza feedback-ului
- [ ] Verifică progresul echipelor la proiect (artefactul săptămânii)

### Înainte de săptămâna următoare

- [ ] Revizuiește soluțiile exercițiilor challenge
- [ ] Pregătește feedback pentru rapoartele de laborator primite
- [ ] Identifică studenții care au nevoie de suport suplimentar

---

## Probleme frecvente și soluții rapide

| Problemă | Comandă de rezolvare |
|----------|---------------------|
| Mininet nu pornește | `sudo mn -c && sudo service openvswitch-switch restart` |
| Eroare permisiuni | `sudo chmod +x scripts/*.sh` |
| Python module lipsă | `pip install -r requirements.txt --break-system-packages` |
| Topologie rămâne blocată | Ctrl+C, apoi `sudo mn -c` |

> **Din experiență:** Dacă OVS refuză să pornească, verifică dacă ai suficientă memorie liberă. Mininet + OVS au nevoie de cel puțin 1GB RAM disponibil.

---

## Note pentru îmbunătățiri viitoare

*(Spațiu pentru notițe personale)*

- 
- 
- 

---

*Template checklist — actualizat pentru anul universitar 2025-2026*
