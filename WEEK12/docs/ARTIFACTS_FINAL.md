# =============================================================================
# DOCUMENTE FINALE — Săptămâna 12
# Protocoale Email și RPC
# =============================================================================

## HARTA DE ALINIERE

### Temă Fișă Disciplină → Secțiuni Curs → Secțiuni Seminar → Artefacte Kit

| Temă Fișă | Curs | Seminar | Artefacte Kit |
|-----------|------|---------|---------------|
| **Curs 12: SMTP, POP3, IMAP, WebMail** | theory.html slides 1-28 | - | src/email/, docs/curs/curs.md |
| Arhitectura email (MUA/MTA/MDA) | Secțiunea 1 (slides 4-7) | - | smtp_server.py (implementare MTA simplificat) |
| SMTP protocol | Secțiunea 2 (slides 8-13) | Lab Steps 1-3 | smtp_client.py, smtp_server.py |
| POP3 protocol | Secțiunea 3 (slides 14-17) | - | smtp_server.py (mailbox listing) |
| IMAP protocol | Secțiunea 4 (slides 18-21) | - | docs/curs.md (teorie) |
| MIME și formatare | Secțiunea 5 (slides 22-24) | Exercițiu 5 | ex_01_smtp.py |
| Securitate (SPF/DKIM/DMARC) | Secțiunea 6 (slides 25-28) | - | docs/curs.md |
| **Seminar 12: RPC concepte, framework** | - | seminar.html | src/rpc/ |
| Conceptul RPC | - | Tabs 1-2 | docs/seminar.md |
| JSON-RPC 2.0 | - | Tabs 3-4, Steps 4-5 | jsonrpc_server.py, jsonrpc_client.py |
| XML-RPC | - | Tabs 5-6, Step 6 | xmlrpc_server.py, xmlrpc_client.py |
| gRPC/Protobuf | - | Tab 7 | calculator.proto (introducere) |
| Comparație protocoale | - | Tab 8, Step 7 | benchmark_rpc.sh |

---

## LOG DE DECIZII (15 Bullet-uri)

### Arhitectură și Structură

1. **Separare strictă email vs RPC** — Am păstrat directoare separate `src/email/` și `src/rpc/` pentru claritate pedagogică, permițând studenților să se concentreze pe un subiect odată.

2. **Python fără framework-uri externe pentru RPC** — Am implementat JSON-RPC și XML-RPC folosind doar `http.server` și bibliotecile standard pentru a demonstra conceptele de bază fără abstractizări.

3. **Docker opțional, nu obligatoriu** — Configurația Docker este inclusă dar toate demo-urile rulează și fără Docker, respectând cerința de setup lightweight în VirtualBox.

4. **Mininet doar pentru topologie demonstrativă** — Am inclus o topologie de bază (`topo_email_rpc_base.py`) pentru vizualizare, dar exercițiile principale nu depind de Mininet.

### Conținut Didactic

5. **Envelope vs Headers evidențiat explicit** — Aceasta este una din cele mai frecvente confuzii, așa că am dedicat slide-uri și exerciții specifice acestui concept.

6. **Securitate email (SPF/DKIM/DMARC) inclusă** — Deși nu apare explicit în fișa disciplinei, este esențială pentru înțelegerea email-ului modern și protecția împotriva spoofing-ului.

7. **Batch requests JSON-RPC demonstrat** — Feature avansat dar important pentru eficiență în aplicații reale, inclus în exerciții.

8. **gRPC doar ca introducere** — Protocolul este complex și necesită tooling suplimentar; am inclus `.proto` și explicații, dar implementarea completă este marcată ca bonus.

### Implementare Tehnică

9. **Server SMTP educațional simplificat** — Implementarea noastră acceptă orice email fără autentificare reală pentru a permite experimentarea liberă, dar documentăm clar diferențele față de serverele de producție.

10. **Logging configurabil în toate serverele** — Flag `--verbose` / `--quiet` pentru a controla nivelul de output, util atât pentru debugging cât și pentru benchmark-uri curate.

11. **Gestionare erori RPC conform specificației** — Codurile de eroare standard JSON-RPC (-32700, -32600, etc.) sunt implementate și documentate.

12. **Capturi .pcap pre-generate incluse** — Folder `pcap/` conține exemple pentru studenții care nu pot rula tshark local.

### Evaluare și Exerciții

13. **Exerciții gradate ★ la ★★★★** — Progresie clară de la simplu (metodă RPC nouă) la complex (email relay), permițând diferențiere pe nivel.

14. **Challenge email relay** — Exercițiu avansat opțional pentru studenții care doresc aprofundare în protocoale de rutare email.

15. **Rubrici detaliate pentru auto-evaluare** — Include checklist și punctaje pe criterii, permițând studenților să-și evalueze progresul înainte de predare.

---

## LISTA PRESUPUNERILOR (8 Puncte)

1. **Python 3.10+ disponibil** — Cod testat pe Python 3.10-3.12; versiuni anterioare pot avea incompatibilități minore în type hints.

2. **Porturi 1025, 8000, 8001 disponibile** — Demo-urile folosesc aceste porturi; dacă sunt ocupate, pot fi modificate via variabile de mediu.

3. **Acces la terminal/bash** — Scripturile shell presupun un mediu Unix-like (Linux, macOS, WSL pe Windows).

4. **Conexiune la internet opțională** — Demo-urile funcționează offline pe localhost; conexiunea este necesară doar pentru instalare pachete și MX lookups.

5. **tshark/Wireshark opțional** — Capturile pot fi realizate cu tcpdump ca alternativă; fișierele .pcap pre-generate sunt incluse.

6. **Docker opțional** — Toate funcționalitățile sunt disponibile și fără Docker; containerele simplifică doar deployment-ul multi-serviciu.

7. **gRPC nu este obligatoriu** — Cerința din fișă este "concepte RPC"; gRPC este inclus ca bonus avansat, JSON-RPC și XML-RPC acoperă cerințele de bază.

8. **Email-uri nu părăsesc localhost** — Serverul SMTP educațional nu face relay extern; toate email-urile rămân în mailbox local pentru siguranță.

---

*Material didactic — Săptămâna 12, Rețele de Calculatoare, ASE-CSIE*
