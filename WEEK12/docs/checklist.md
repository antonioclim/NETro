# Checklist Cadru Didactic – Săptămâna 12

## Protocoale Email (SMTP, POP3, IMAP) & RPC (JSON-RPC, XML-RPC, gRPC)

---

## ☐ ÎNAINTE DE CURS/SEMINAR

### Pregătire Tehnică (30 min înainte)
- [ ] Verifică funcționarea VM-ului / containerelor Docker
- [ ] Rulează `make verify` în directorul starterkit pentru validare mediu
- [ ] Testează serverul SMTP educațional: `python3 src/email/smtp_server.py`
- [ ] Testează serverele RPC: `python3 src/rpc/jsonrpc/jsonrpc_server.py`
- [ ] Verifică Wireshark/tshark instalat și permisiuni pentru captură
- [ ] Pregătește terminale multiple (min. 3) pentru demonstrații simultane

### Pregătire Pedagogică
- [ ] Recapitulează conținutul din S11 (DNS, SSH, FTP) – legătură cu SMTP
- [ ] Revizuiește RFC-urile cheie: RFC 5321 (SMTP), RFC 1939 (POP3), RFC 3501 (IMAP)
- [ ] Notează 2-3 exemple concrete din industrie (ex: Gmail, Outlook, SendGrid)
- [ ] Pregătește întrebări de angajament pentru studenți
- [ ] Verifică rubricile de evaluare și criteriile pentru proiect

### Materiale
- [ ] Starterkit funcțional pe mașina de demonstrație
- [ ] Prezentări HTML accesibile: theory.html, seminar.html, lab.html
- [ ] Documentul Word cu notițe instructor disponibil
- [ ] Exemple de capturi PCAP pre-generate în /pcap (backup)

---

## ☐ ÎN TIMPUL CURSULUI (2h)

### Introducere (10 min)
- [ ] Contextualizare: "De ce protocoale email în era mesageriei instant?"
- [ ] Conectare cu săptămânile anterioare (TCP/S8, HTTP/S10, DNS/S11)
- [ ] Prezentare obiective: ce vor ști și ce vor putea face la final

### Conținut Principal – Email (50 min)
- [ ] Arhitectura email: MUA → MTA → MDA → MUA (diagramă)
- [ ] **Punct cheie**: Diferența Envelope vs Headers (sursa spoofing-ului)
- [ ] SMTP în detaliu: comenzi, coduri răspuns, sesiune completă
- [ ] ⚠️ **Capcană comună**: studenții confundă MAIL FROM cu Header From:
- [ ] Demo live: sesiune telnet către serverul SMTP educațional
- [ ] POP3 vs IMAP: tabel comparativ, când folosești fiecare
- [ ] Securitate email: SPF, DKIM, DMARC – explică în termeni simpli

### Verificare Înțelegere Email (10 min)
- [ ] Întrebare: "Ce se întâmplă dacă MAIL FROM diferă de From: header?"
- [ ] Mini-quiz: identifică comanda SMTP pentru fiecare acțiune
- [ ] Întrebare: "De ce POP3 nu e potrivit pentru acces multi-device?"

### Pauză (10 min)

### Conținut Principal – RPC (30 min)
- [ ] Conceptul RPC: apelezi funcție locală, execuția e remotă
- [ ] JSON-RPC 2.0: structură cerere/răspuns, coduri eroare standard
- [ ] XML-RPC: format verbose, când e încă relevant (legacy)
- [ ] gRPC/Protobuf: avantaje performanță, streaming, microservicii
- [ ] Tabel comparativ: overhead, performanță, cazuri de utilizare

### Verificare Înțelegere RPC (10 min)
- [ ] Întrebare: "Care e diferența dintre call și notification în JSON-RPC?"
- [ ] Întrebare: "De ce gRPC e mai rapid decât JSON-RPC?"

### Încheiere Curs (10 min)
- [ ] Recapitulare puncte cheie (max 5)
- [ ] Preview seminar: "Veți implementa și testa practic"
- [ ] Temă pentru acasă: citire RFC 5321 secțiunile 3-4

---

## ☐ ÎN TIMPUL SEMINARULUI (2h)

### Setup Inițial (15 min)
- [ ] Verifică toți studenții au acces la starterkit
- [ ] Rulare `make setup` pe mașinile studenților
- [ ] Rezolvă probleme de mediu (permisiuni, porturi ocupate)

### Experiment 1 – SMTP (30 min)
- [ ] Pornire server SMTP: `python3 src/email/smtp_server.py`
- [ ] Trimitere email cu clientul: `python3 src/email/smtp_client.py`
- [ ] Captură trafic: `make capture-smtp` (tshark în background)
- [ ] **Observație ghidată**: identificați HELO, MAIL FROM, RCPT TO, DATA
- [ ] ⚠️ **Punct de atenție**: verificați că port 1025 e liber

### Experiment 2 – JSON-RPC (25 min)
- [ ] Pornire server: `python3 src/rpc/jsonrpc/jsonrpc_server.py`
- [ ] Demo client: `python3 src/rpc/jsonrpc/jsonrpc_client.py --demo`
- [ ] Apeluri individuale: add, subtract, multiply, divide
- [ ] Batch requests: demonstrați reducerea overhead-ului
- [ ] Captură și analiză: HTTP POST cu payload JSON

### Experiment 3 – XML-RPC (20 min)
- [ ] Pornire server: `python3 src/rpc/xmlrpc/xmlrpc_server.py`
- [ ] Test cu client: `python3 src/rpc/xmlrpc/xmlrpc_client.py`
- [ ] Introspecție: system.listMethods()
- [ ] **Comparație**: observați dimensiunea payload XML vs JSON

### Benchmark Comparativ (15 min)
- [ ] Rulare: `make benchmark-rpc` sau `scripts/benchmark_rpc.sh`
- [ ] Discuție rezultate: de ce JSON-RPC e mai rapid?
- [ ] Interpretare: overhead serialization/deserialization

### Exerciții Individuale (15 min)
- [ ] Exercițiul 1: Modificați MAIL FROM și observați diferența
- [ ] Exercițiul 2: Adăugați metodă nouă la serverul RPC
- [ ] Suport pentru studenții care întâmpină dificultăți

### Încheiere Seminar (10 min)
- [ ] Colectare feedback: ce a fost clar, ce nu
- [ ] Reminder proiect: modulul de notificări sau API RPC
- [ ] Preview S13: IoT și securitate în rețele

---

## ☐ DUPĂ CURS/SEMINAR

### Imediat După (15 min)
- [ ] Salvează capturile PCAP relevante pentru referință
- [ ] Notează întrebările frecvente ale studenților
- [ ] Identifică conceptele care au necesitat explicații suplimentare

### În Următoarele 48h
- [ ] Verifică progresul la proiectele de echipă
- [ ] Răspunde la întrebări pe forum/email
- [ ] Actualizează materialele dacă au apărut ambiguități

### Pregătire Evaluare
- [ ] Verifică rubricile pentru contribuția săptămânală
- [ ] Pregătește feedback pentru echipele care au livrat
- [ ] Notează aspecte pentru evaluarea finală

---

## Puncte Critice de Atenție

### Confuzii Frecvente la Studenți
1. **Envelope vs Headers**: Mulți nu înțeleg de ce pot fi diferite
2. **POP3 șterge emailurile**: Nu întotdeauna, depinde de configurare
3. **RPC vs REST**: RPC e orientat pe acțiuni, REST pe resurse
4. **gRPC necesită HTTP/2**: Da, nu merge pe HTTP/1.1

### Probleme Tehnice Anticipate
1. Port 25 blocat de ISP → folosim 1025 în demo
2. Wireshark fără permisiuni → rulează cu sudo sau configurează grupul
3. Python 3.6+ necesar → verifică versiunea la început
4. Firewall blochează traficul → dezactivează temporar sau adaugă excepții

### Întrebări de Control Recomandate
- "Ce protocol folosește Gmail când trimiți un email către Yahoo?"
- "Cum verifică serverul destinatar că emailul nu e spoofed?"
- "De ce JSON-RPC folosește HTTP POST și nu GET?"
- "În ce situație ai folosi gRPC în loc de REST?"

---

## Resurse Rapid Access

| Resursă | Locație |
|---------|---------|
| Server SMTP | `src/email/smtp_server.py` |
| Client SMTP | `src/email/smtp_client.py` |
| Server JSON-RPC | `src/rpc/jsonrpc/jsonrpc_server.py` |
| Server XML-RPC | `src/rpc/xmlrpc/xmlrpc_server.py` |
| Benchmark | `scripts/benchmark_rpc.sh` |
| Captură | `scripts/capture.sh` |
| Prezentare teorie | `docs/presentations/theory.html` |
| Prezentare seminar | `docs/presentations/seminar.html` |
| Ghid laborator | `docs/presentations/lab.html` |

---

*Material didactic — Săptămâna 12, Rețele de Calculatoare, ASE-CSIE*
