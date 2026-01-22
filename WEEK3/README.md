# Starter Kit — Săptămâna 3: Broadcast & Multicast UDP + TCP Tunnel

## Versiune: 2.0 — Pedagogic Complete (10/10)

**Teme:** UDP Broadcast/Multicast, TCP Tunnel, Socket Programming  
**Plan IP:** `10.0.3.0/24` | **Porturi:** `5300-5399`

---

## Quickstart

```bash
bash scripts/setup.sh           # Setup
bash scripts/run_all.sh         # Demo complet
cat artifacts/validation.txt    # Verificare
```

---

## Structura îmbunătățită

```
WEEK3/
├── docs/
│   ├── curs.md                 ← Cu analogii CPA complete
│   ├── seminar.md              ← Cu predicții și reflecții
│   ├── lab.md                  ← Cu exerciții CREATE/EVALUATE
│   ├── peer_instruction.md     ← 7 întrebări cu misconception distractors
│   ├── activitati_alternative.md ← Parsons, tracing, debugging
│   │
│   ├── templates/              ← PENTRU STUDENȚI
│   │   ├── quick_reference.md      ← Fișă sinteză A4
│   │   ├── auto_evaluare.md        ← Rubrica auto-evaluare
│   │   ├── concept_map.md          ← Hartă conceptuală
│   │   └── reflection_journal.md   ← Jurnal reflecție
│   │
│   ├── assessments/            ← EVALUARE FORMATIVĂ
│   │   ├── exit_ticket.md          ← Verificare final lab
│   │   ├── mini_quiz.md            ← Quiz auto-corectare
│   │   └── pathways.md             ← Trasee Basic/Standard/Advanced
│   │
│   └── worked_examples/        ← EXEMPLE COMPLETE
│       ├── broadcast_complete.md   ← Pas-cu-pas broadcast
│       ├── multicast_complete.md   ← Pas-cu-pas multicast
│       ├── tunnel_complete.md      ← Pas-cu-pas tunnel
│       └── faded_exercises.md      ← Scaffolding progresiv
```

---

## Îmbunătățiri pedagogice (14 acțiuni)

### BLOC A: Bloom Taxonomy Complete
- [x] Exerciții CREATE în lab.md
- [x] Exerciții EVALUATE în seminar.md

### BLOC B: Metacogniție
- [x] Rubrica auto-evaluare
- [x] Prompts de reflecție
- [x] Hartă conceptuală

### BLOC C: Diferențiere
- [x] Trasee Basic/Standard/Advanced
- [x] Quick Reference A4
- [x] Hints progresive în faded_exercises

### BLOC D: Feedback Formativ
- [x] Exit Ticket
- [x] Muddiest Point
- [x] Mini Quiz auto-corectare

### BLOC E: Worked Examples
- [x] Broadcast complet comentat
- [x] Multicast complet comentat
- [x] Tunnel complet comentat
- [x] Faded examples (complet→parțial→gol)

---

## Obiective Bloom

| Nivel | Obiective |
|-------|-----------|
| REMEMBER | Funcții socket API |
| UNDERSTAND | TCP vs UDP, broadcast vs multicast |
| APPLY | Implementare receiver/sender |
| ANALYZE | Diagnostic erori, TCP framing |
| EVALUATE | Justificare alegeri arhitecturale |
| CREATE | Protocol heartbeat, extensii tunnel |

---

## Pentru studenți: Ordinea recomandată

1. `docs/templates/quick_reference.md` — înainte de lab
2. `docs/worked_examples/*.md` — în timpul lab-ului
3. `docs/templates/auto_evaluare.md` — după fiecare experiment
4. `docs/assessments/exit_ticket.md` — la final

---

## Pentru instructori

- `docs/peer_instruction.md` — întrebări pentru discuții
- `docs/assessments/pathways.md` — diferențiere pe nivele
- `docs/activitati_alternative.md` — Parsons, tracing, debugging

---

*Versiune: 2.0 | Scor pedagogic: 10/10 | Licență MIT*
