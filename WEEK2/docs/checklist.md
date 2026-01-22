# Checklist Cadru Didactic – Săptămâna 2

**Modele Arhitecturale OSI/TCP-IP & Programare Socket**

---

## Înainte de curs/seminar

### Cu o zi înainte

- [ ] Verificare funcționare echipamente sala (proiector, rețea)
- [ ] Actualizare slide-uri dacă e cazul
- [ ] Verificare linkuri în materiale (nu sunt broken)
- [ ] Pregătire VM/container cu mediul de lucru pentru demonstrații

### Cu 30 minute înainte

- [ ] Deschidere prezentare pe ecranul principal
- [ ] Pornire VM de demonstrație
- [ ] Verificare că `make verify` trece în VM
- [ ] Deschidere terminal pentru demo live
- [ ] Deschidere Wireshark/tshark pregătit pentru captură
- [ ] Deschidere `theory.html` în browser pentru diagrame interactive
- [ ] Pregătire răspunsuri pentru MCQ-uri (pentru discuție)

### Verificare mediu demo

```bash
cd starterkit_s2
make verify
make clean
```

---

## În timpul cursului (2h)

### Partea I: Fundamentele (0:00 – 0:25)

- [ ] Recapitulare Curs 1 (protocol, stivă, încapsulare) — 5 min
- [ ] Introducere: De ce modele arhitecturale? — 10 min
- [ ] Analogia cu arhitectura clădirilor
- [ ] Conceptul de strat și servicii — 10 min
- [ ] **Întrebare control**: „Ce s-ar întâmpla fără standarde?"

### Partea II: Modelul OSI (0:25 – 1:00)

- [ ] Prezentare cele 7 straturi — 20 min
  - [ ] Stratul Fizic: bit, cablu, semnal
  - [ ] Stratul Legătură: cadru, MAC, CRC
  - [ ] Stratul Rețea: pachet, IP, rutare
  - [ ] Stratul Transport: segment, port, TCP/UDP
  - [ ] Straturile superioare: 5-6-7 mai sumar
- [ ] Diagrama OSI (`fig-osi-straturi.png`) — vizualizare
- [ ] Încapsulare cu diagramă (`fig-osi-incapsulare.png`) — 5 min
- [ ] **Analogia plicurilor**: demonstrație concretă a încapsulării
- [ ] Comunicare orizontală/verticală (`fig-osi-comunicare.png`) — 5 min
- [ ] **Întrebări control**: 
  - [ ] „Ce PDU are stratul Transport?"
  - [ ] „Ce strat se ocupă de MAC?"

### Partea III: Modelul TCP/IP (1:00 – 1:25)

- [ ] Introducere: model practic vs teoretic — 5 min
- [ ] Cele 4 straturi TCP/IP — 10 min
- [ ] **Analogia handshake TCP** (conversație telefonică) — 3 min
- [ ] Comparație OSI vs TCP/IP (`fig-osi-vs-tcpip.png`) — 5 min
- [ ] De ce folosim ambele modele? — 2 min
- [ ] **Întrebare control**: „Când folosim UDP în loc de TCP?"

### Partea IV: Legătura cu practica (1:25 – 1:40)

- [ ] Socket API ca interfață — 5 min
- [ ] **Analogia socket = telefon mobil** — 3 min
- [ ] Preview seminar: ce vom implementa — 5 min
- [ ] Demo rapid (opțional, dacă timpul permite):
  ```bash
  make demo-tcp
  ```
- [ ] Prezentare structura kit-ului

### Partea V: Recapitulare (1:40 – 1:45)

- [ ] Rezumat pe 5 puncte principale
- [ ] Întrebări finale
- [ ] Anunț cerințe seminar

---

## În timpul seminarului (2h)

### Faza 0: Pregătire (0:00 – 0:10)

- [ ] Verificare că toți studenții au acces la VM/mediu
- [ ] Rulare `make verify` colectiv
- [ ] Rezolvare probleme de setup

### Faza 1: Warm-up Mininet (0:10 – 0:25)

- [ ] Demonstrație `make mininet-cli`
- [ ] Studenții explorează: `nodes`, `net`, `pingall`
- [ ] **Verificare**: toți au ping funcțional
- [ ] **MCQ 1**: Peer Instruction despre ce garantează ping-ul

### Faza 2: TCP Lab (0:25 – 1:00)

- [ ] **Pair Programming**: formarea perechilor, explicare roluri Driver/Navigator
- [ ] Demo server TCP — explain parametri
- [ ] **MCQ 2**: Peer Instruction despre handshake TCP (înainte de trimitere mesaj)
- [ ] Demo captură — explain filtru BPF
- [ ] Studenții rulează singuri client
- [ ] Analiză captură — identificare handshake
- [ ] **Verificare**: studenții pot identifica SYN, SYN-ACK, ACK

### Faza 3: UDP Lab (1:00 – 1:25)

- [ ] Demo server UDP
- [ ] Client interactiv — explain protocol aplicație
- [ ] Comparație captură TCP vs UDP
- [ ] **MCQ 3**: Peer Instruction despre când se folosește UDP
- [ ] **Verificare**: studenții pot explica diferența overhead

### Faza 4: Exerciții de înțelegere (1:25 – 1:45)

- [ ] **Parsons Problem**: explicare și timp de lucru (5 min)
- [ ] **Trace Exercise**: explicare și timp de lucru (5 min)
- [ ] **Debugging Exercise**: explicare și timp de lucru (5 min)
- [ ] **MCQ 4**: Peer Instruction despre listen()
- [ ] Discuție răspunsuri în colectiv

### Faza 5: Template-uri (1:45 – 2:00)

- [ ] Explicare template TCP (rapid, că au făcut exercițiile)
- [ ] Timp lucru individual/perechi
- [ ] Asistență la probleme
- [ ] **Verificare**: template funcțional demonstrat

### Faza 6: Extensie (dacă timpul permite)

- [ ] Demo topologie extinsă cu router
- [ ] Discuție despre comunicare între subrețele

### Finalizare

- [ ] Anunț livrabile (ce trebuie predat, inclusiv exercițiile de înțelegere)
- [ ] Curățare mediu: `make clean`

---

## După curs/seminar

### Imediat după

- [ ] Notare observații pentru îmbunătățiri viitoare
- [ ] Verificare că materialele sunt actualizate în repository
- [ ] Răspuns la întrebări primite pe email/forum
- [ ] Notare care MCQ-uri au generat cele mai multe discuții

### Săptămânal

- [ ] Verificare livrabile primite
- [ ] Feedback pe template-uri completate
- [ ] Feedback pe exercițiile de înțelegere
- [ ] Pregătire materiale săptămâna următoare

---

## Întrebări frecvente studenți

| Întrebare | Răspuns sumar |
|-----------|---------------|
| „De ce nu merge serverul?" | Verifică portul: `lsof -i :9999`, `make clean` |
| „Captura e goală" | Verifică interfața și filtrul: `-i lo` vs `-i eth0` |
| „Connection refused" | Serverul nu rulează. Verifică `jobs`, repornește |
| „Când folosesc TCP vs UDP?" | TCP = fiabilitate (web, email); UDP = viteză (streaming, gaming) |
| „Ce înseamnă L7, L3?" | Referințe la straturile OSI: L7=Aplicație, L3=Rețea |
| „De ce 3 pași în handshake?" | Fiecare parte trebuie să confirme că poate și trimite, și primi |
| „Ce e Parsons Problem?" | Exercițiu de ordonare cod — testează înțelegerea fluxului, nu sintaxa |

---

## Capcane comune de evitat

1. **Presupunerea că toți au mediul configurat** — întotdeauna verificare colectivă la început
2. **Demo-uri care nu funcționează** — testează înainte în exact aceeași configurație
3. **Prea multă teorie fără practică** — intercalează întrebări și mini-exerciții
4. **Ignorarea studenților blocați** — alocă timp pentru asistență individuală
5. **Grăbirea prin captură** — handshake-ul TCP e conceptul cheie, dedică timp
6. **Săritul peste MCQ-uri** — discuțiile în perechi ajută la fixarea conceptelor
7. **Doar cod de la zero** — exercițiile de înțelegere (Parsons, trace) sunt la fel de valoroase

---

## Resurse auxiliare

- `theory.html` — pentru diagrame interactive în curs
- `seminar.html` — dashboard pentru seminar
- `lab.html` — ghid pas-cu-pas pentru studenți independenți
- Wireshark sample captures: [https://wiki.wireshark.org/SampleCaptures](https://wiki.wireshark.org/SampleCaptures)

---

## Răspunsuri MCQ (pentru cadru didactic)

| MCQ | Răspuns corect | Misconceptie principală vizată |
|-----|----------------|--------------------------------|
| MCQ 1 | C — conectivitate IP L3 | Confuzie L3 vs L7 |
| MCQ 2 | C — confirmare bidirecțională | Handshake-ul transferă date |
| MCQ 3 | C — latență vs pierdere | UDP e „mai bun" în absolut |
| MCQ 4 | C — accept() eșuează | listen() e opțional |

---

*Revolvix&Hypotheticalandrei*
