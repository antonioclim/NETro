# Controlul Coerenței - Săptămâna 4

> **Disciplină:** Rețele de Calculatoare  
> **Săptămâna:** 4  
> **Temă:** Protocoale Text și Binare Custom peste TCP și UDP

---

## Hartă de Aliniere

### Temă Fișă Disciplină → Secțiuni Curs → Secțiuni Seminar → Artefacte Kit

| Temă Fișă Disciplină | Secțiuni Curs | Secțiuni Seminar | Artefacte Starterkit |
|---------------------|---------------|------------------|---------------------|
| **S4: Programare pe sockets: implementarea de protocoale text și binare custom peste TCP și UDP** | 3.1 Motivația protocoalelor custom | 4.1 Pregătire mediu | `/README.md`, `/scripts/setup.sh` |
| | 3.2 Protocoale TEXT | 4.2 Implementare Protocol TEXT | `/python/apps/text_proto_*.py` |
| | 3.2.1 Problema Framing-ului | 4.2.1 recv_until() | `/python/utils/io_utils.py` |
| | 3.3 Protocoale BINARE | 4.3 Implementare Protocol BINAR | `/python/apps/binary_proto_*.py` |
| | 3.3.1 Serializare struct | 4.3.2 Pack/Unpack | `/python/utils/proto_common.py` |
| | 3.3.2 CRC32 Validare | 4.3.3 CRC32 | `zlib.crc32()` în cod |
| | 3.4 Protocol UDP sensor | 5.3 Mininet UDP demo | `/python/apps/udp_sensor_*.py` |
| | | | `/mininet/scenario_udp_demo.py` |
| **Analiza traficului (din S1)** | Referință în 3.2, 3.3 | 5.2 Captură și analiză | `/docs/tcpdump_cheatsheet.md` |
| | | | `/docs/tshark_cheatsheet.md` |
| **Testare în simulator (din S6)** | 3.5 Testare Mininet | 5.3 Experiment Mininet | `/mininet/scenario_*.py` |
| | | | `/docs/mininet_cheatsheet.md` |

### Mapare Obiective de Învățare → Artefacte

| Obiectiv | Nivel Taxonomic | Artefact Principal |
|----------|----------------|-------------------|
| Specificare protocol text | Înțelegere | `curs.md` §3.2, `theory.html` slides 6-11 |
| Specificare protocol binar | Înțelegere | `curs.md` §3.3, `theory.html` slides 12-18 |
| Implementare recv_until/recv_exact | Aplicare | `io_utils.py`, exerciții, templates |
| Serializare cu struct | Aplicare | `proto_common.py`, `seminar.html` tab cod |
| Validare CRC32 | Aplicare | Toate protocoalele, `lab.html` step 3 |
| Analiză trafic custom | Analiză | Cheatsheets, `lab.html` step 4, `seminar.html` |
| Evaluare TEXT vs BINAR | Evaluare | Exercițiu 2, `theory.html` slide 24 |
| Proiectare protocol hibrid | Creație | Exercițiu Challenge, proiect echipă |

---

## Log de Decizii

### Modificări și motivații

1. **Structură protocol BINAR unificată (14 bytes header)**
   - *Decizie:* Header fix cu MAGIC, VERSION, TYPE, PAYLOAD_LEN, SEQUENCE, CRC32
   - *Motivație:* Oferă extensibilitate (versioning), debugging facil (magic), corelație mesaje (sequence), integritate (CRC)
   - *Sursa:* Consolidare din arhivele S4v2 și S4v3

2. **Framing TEXT cu „<LEN> <PAYLOAD>\n"**
   - *Decizie:* Lungime prefixată + newline terminator
   - *Motivație:* Self-describing, testabil cu netcat, permite payload cu spații
   - *Alternativă respinsă:* Doar newline (payload nu poate conține \n)

3. **recv_until() și recv_exact() ca funcții separate**
   - *Decizie:* Două funcții distincte în io_utils.py
   - *Motivație:* Claritate pedagogică - studenții înțeleg diferența între citire până la delimiter vs citire exactă

4. **CRC32 cu zlib (nu crc32c sau custom)**
   - *Decizie:* zlib.crc32() disponibil în standard library
   - *Motivație:* Zero dependențe externe, performanță acceptabilă, compatibilitate largă
   - *Notă:* Masca & 0xFFFFFFFF pentru rezultat unsigned

5. **Protocol UDP sensor cu format fix 23 bytes**
   - *Decizie:* Format rigid vs lungime variabilă
   - *Motivație:* Demonstrează diferența față de TCP, parsing simplu pentru dispozitive embedded

6. **Trei scenarii Mininet separate**
   - *Decizie:* scenario_arp_demo.py, scenario_tcp_demo.py, scenario_udp_demo.py
   - *Motivație:* Izolare conceptuală, rulare independentă, focus pe un protocol la un moment dat
   - *Alternativă respinsă:* Un singur script mare cu toate demo-urile

7. **Docker Compose cu 3 servicii (server, client, monitor)**
   - *Decizie:* Orchestrare multi-container vs single container
   - *Motivație:* Simulează arhitectură reală, permite captura din container separat

8. **Exerciții gradate pe 6 niveluri**
   - *Decizie:* De la înțelegere (Ex1) la creație (Challenge)
   - *Motivație:* Progresie pedagogică, diferențiere pentru studenți cu niveluri diferite

9. **HTML cu același stil vizual pentru toate cele 3 fișiere**
   - *Decizie:* Paletă comună, fonturi identice, layout consistent
   - *Motivație:* Identitate vizuală unitară, experiență coerentă pentru studenți
   - *Footer:* „Revolvix&Hypotheticalandrei" conform cerințelor

10. **Slide outlines TEXT vs PPT/PPTX**
    - *Decizie:* Format text structurat, nu PowerPoint nativ
    - *Motivație:* Portabilitate, ușor de importat în orice tool, versioning în git

11. **Cheatsheets pentru tcpdump, tshark, Mininet**
    - *Decizie:* Trei documente Markdown separate
    - *Motivație:* Quick reference independente, printabile, reutilizabile în alte săptămâni

12. **Makefile cu ținte standardizate**
    - *Decizie:* setup, run-*, capture, verify, clean, reset
    - *Motivație:* One-command experience, consistență între săptămâni

13. **Rubrici cu punctaje explicite**
    - *Decizie:* Grile detaliate pentru fiecare criteriu
    - *Motivație:* Transparență evaluare, auto-evaluare pentru studenți

14. **Două perspective în DOCX (instructor + student)**
    - *Decizie:* Note instructor în stil diferențiat (italic, fundal galben)
    - *Motivație:* Un singur document servește ambele audiențe

15. **Assets din arhiva S4v3starterkit_ideal refolosite**
    - *Decizie:* Diagrame PNG și PlantUML copiate ca atare
    - *Motivație:* Calitate existentă, consistență vizuală demonstrată

---

## Lista Presupunerilor

1. **Mediu de execuție**
   - Se presupune VM Linux (Ubuntu 22.04/24.04) cu Python 3.8+ preinstalat
   - Acces sudo pentru tshark/tcpdump
   - Porturi 5400, 5401, 5402 disponibile

2. **Cunoștințe anterioare**
   - Studenții au parcurs S1-S3 și sunt familiari cu sockets TCP/UDP de bază
   - Înțeleg conceptele client-server și threading minimal

3. **Disponibilitate instrumente**
   - Wireshark/tshark și netcat instalate în laborator
   - Opțional: Docker și docker-compose pentru varianta containerizată

4. **Proiect de echipă**
   - Există un proiect de echipă în desfășurare unde protocolul custom va fi integrat
   - Deadline-ul artefactului S4 este sincronizat cu planificarea generală

5. **Resurse hardware**
   - VM cu minim 2GB RAM pentru rulare Mininet și capturi simultane
   - Spațiu disk suficient pentru pcap-uri (recomandat 500MB liberi)

6. **Browser modern**
   - Fișierele HTML sunt testate pe Chrome/Firefox recent
   - JavaScript enabled pentru funcționalități interactive

7. **Fișa disciplinei**
   - Tema S4 „Programare pe sockets: implementarea de protocoale text și binare custom peste TCP și UDP" rămâne neschimbată
   - 2h curs + 2h seminar per săptămână

8. **Limba**
   - Toate materialele sunt în română academică
   - Comentariile din cod sunt în engleză (convenție standard programare)

---

## Structura Finală Starterkit

```
starterkit_s4/
├── README.md                          # Start rapid, cerințe, troubleshooting
├── Makefile                           # Ținte: setup, run-*, capture, verify, clean
├── Curs4_Seminar4_Laborator4.docx     # Document complet cu două perspective
│
├── html/
│   ├── theory.html                    # 27 slides teorie navigabilă
│   ├── seminar.html                   # 8 taburi interactive
│   └── lab.html                       # Pași experimentali step-by-step
│
├── python/
│   ├── apps/                          # Implementări complete
│   │   ├── text_proto_server.py
│   │   ├── text_proto_client.py
│   │   ├── binary_proto_server.py
│   │   ├── binary_proto_client.py
│   │   ├── udp_sensor_server.py
│   │   └── udp_sensor_client.py
│   ├── exercises/                     # Exerciții cu TODO
│   │   ├── ex_4_01_tcp_proto.py
│   │   └── ex_4_02_udp_sensor.py
│   ├── solutions/                     # Soluții complete
│   │   └── solutions.py
│   ├── templates/                     # Scheleturi pentru lucru independent
│   │   ├── text_server_template.py
│   │   ├── binary_server_template.py
│   │   └── udp_client_template.py
│   └── utils/                         # Module comune
│       ├── io_utils.py                # recv_exact, recv_until
│       └── proto_common.py            # CRC32, struct helpers
│
├── mininet/
│   ├── scenario_arp_demo.py           # Demo ARP/CAM learning
│   ├── scenario_tcp_demo.py           # Demo TEXT + BINAR
│   └── scenario_udp_demo.py           # Demo UDP sensors + loss
│
├── docker/
│   ├── Dockerfile                     # Image Python + networking tools
│   └── docker-compose.yml             # Orchestrare server/client/monitor
│
├── docs/
│   ├── curs/curs.md                   # Markdown sursă teorie
│   ├── seminar/seminar.md             # Markdown sursă seminar
│   ├── lab/lab.md                     # Markdown sursă laborator
│   ├── checklist.md                   # Înainte/în timpul/după pentru instructor
│   ├── rubrici.md                     # Criterii evaluare săptămânală
│   ├── tcpdump_cheatsheet.md          # Quick reference tcpdump
│   ├── tshark_cheatsheet.md           # Quick reference tshark
│   └── mininet_cheatsheet.md          # Quick reference Mininet
│
├── slides/
│   ├── curs_slides_outline.txt        # Outline pentru prezentare curs
│   └── seminar_slides_outline.txt     # Outline pentru prezentare seminar
│
├── scripts/
│   ├── setup.sh                       # Instalare dependențe
│   ├── run_all.sh                     # Pornire toate serviciile
│   └── generate_docx.js               # Generator document Word
│
├── tests/
│   └── smoke_test.sh                  # Verificare mediu funcțional
│
├── assets/
│   ├── images/                        # Diagrame PNG
│   └── puml/                          # Surse PlantUML
│
└── pcap/                              # Director pentru capturi
```

---

*Document generat: 2025 | Revolvix&Hypotheticalandrei*
