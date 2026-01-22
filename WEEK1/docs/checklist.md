# Checklist Cadru Didactic - Săptămâna 1

## Înainte de activitate

### Cu o săptămână înainte
- [ ] Verificare disponibilitate laborator
- [ ] Testare VM/imagine laborator pe calculatoarele din sală
- [ ] Actualizare starterkit dacă e cazul
- [ ] Pregătire slide-uri curs cu exemple actualizate
- [ ] Verificare funcționare proiector/ecran

### Cu o zi înainte
- [ ] Verificare acces Internet în laborator
- [ ] Testare comenzi pe configurația exactă din sală
- [ ] Pregătire fișiere demo (capturi exemplu)
- [ ] Verificare că porturile 9999, 8888, 5000 nu sunt blocate

### Înainte de intrarea în sală
- [ ] Descărcare starterkit pe stick USB (backup)
- [ ] Verificare prezență marker whiteboard funcțional
- [ ] Pregătire foaie cu structura timing-ului

---

## În timpul activității

### La începutul cursului/seminarului (5 min)
- [ ] Verificare prezență studenți
- [ ] Anunțare obiective și structură
- [ ] Verificare că toți au acces la materiale

### Pe parcursul activității
- [ ] Pauză la jumătate (~50 min) pentru curs
- [ ] Monitorizare progres studenți la exerciții
- [ ] Notare întrebări frecvente pentru FAQ
- [ ] Verificare că nimeni nu a rămas blocat

### La final (10 min)
- [ ] Recapitulare puncte cheie
- [ ] Anunțare teme/pregătire pentru săptămâna viitoare
- [ ] Colectare feedback informal

---

## După activitate

### Imediat după
- [ ] Salvare capturi demonstrative pentru referință
- [ ] Notare probleme tehnice întâlnite
- [ ] Actualizare FAQ dacă e cazul

### Până la următoarea săptămână
- [ ] Verificare livrabile studenți (dacă există)
- [ ] Pregătire materiale săptămâna 2
- [ ] Actualizare documentație cu îmbunătățiri

---

## Timing sugerat

### Curs (100 min)
| Interval | Activitate | Durată |
|----------|------------|--------|
| 0:00-0:05 | Introducere, obiective | 5 min |
| 0:05-0:35 | Partea I: Concepte de bază | 30 min |
| 0:35-0:55 | Partea II: Parametri transmisie | 20 min |
| 0:55-1:05 | **Pauză** | 10 min |
| 1:05-1:25 | Partea III: Dispozitive | 20 min |
| 1:25-1:45 | Partea IV: Modele OSI/TCP-IP | 20 min |
| 1:45-1:55 | Recapitulare, întrebări | 10 min |

### Seminar (100 min)
| Interval | Activitate | Durată |
|----------|------------|--------|
| 0:00-0:10 | Setup, verificare mediu | 10 min |
| 0:10-0:35 | Demo: ip, ping, ss | 25 min |
| 0:35-1:00 | Demo: netcat TCP/UDP | 25 min |
| 1:00-1:30 | Demo: tshark, captură | 30 min |
| 1:30-1:50 | Exerciții individuale | 20 min |
| 1:50-2:00 | Recapitulare, întrebări | 10 min |

---

## Întrebări de control

### Pentru verificare înțelegere în timpul cursului
1. "Care este diferența dintre bandwidth și throughput?"
2. "De ce un hub este considerat Layer 1 și un switch Layer 2?"
3. "Ce se întâmplă dacă un router primește un pachet cu TTL=1?"

### Pentru verificare în timpul seminarului
1. "De ce vedem 3 pachete înainte de datele efective în TCP?"
2. "Ce flag-uri TCP vedem într-un handshake?"
3. "Cum verificăm dacă un port este deja ocupat?"

---

## Probleme frecvente și soluții

### "Nu merge Mininet"
→ Nu e critic pentru S1, se poate sări. Folosiți doar netcat pe loopback.

### "tshark cere sudo"
→ Adăugați utilizatorul la grupul wireshark sau folosiți sudo.

### "Portul 9999 e ocupat"
→ Schimbați portul sau opriți procesul cu `kill`.

### "Studenții au Windows fără WSL"
→ Folosiți containerul Docker sau sugerați instalare WSL.

---

## Note pentru îmbunătățire

_(Completați după fiecare sesiune)_

**Data:**
**Probleme întâlnite:**
**Sugestii pentru viitor:**

---

*Revolvix&Hypotheticalandrei • Rețele de Calculatoare • ASE București*
