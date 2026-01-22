# Starterkit Săptămâna 14 — Recapitulare Integrată & Evaluarea Proiectului

**Disciplină:** Rețele de calculatoare / Networking  
**Semestru:** An 3, Sem. 2 — Informatică Economică (CSIE/ASE)  
**Versiune:** 2025-12-31  
**Licență cod:** MIT | **Autori materiale didactice:** Hypotheticalandrei & Revolvix

---

## Quickstart (sub 2 minute)

```bash
# 0) În VM Linux (Ubuntu/Debian CLI), din rădăcina kit-ului:
cd starterkit_saptamana_14

# 1) Instalează dependențele (Mininet, OVS, tshark, utilitare)
sudo bash scripts/setup.sh

# 2) Verifică că mediul este OK
bash tests/smoke_test.sh

# 3) Rulează demo-ul automat complet
make run-demo

# 4) Verifică artefactele generate
ls -la artifacts/

# 5) Analizează pcap-ul offline
tshark -r artifacts/demo.pcap -q -z conv,tcp

# 6) Curățare completă
make clean
```

---

## Ce demonstrează acest kit

1. **Topologie Mininet compactă:**  
   `client ↔ switch1 ↔ switch2 ↔ [app1, app2]` + `switch1 ↔ lb`

2. **Pattern Load Balancer / Reverse Proxy:**  
   Clientul trimite cereri HTTP către `lb:8080` (10.0.14.1:8080); proxy-ul le distribuie round-robin către backends (`app1:8080`, `app2:8080` = 10.0.14.100:8080, 10.0.14.101:8080).

3. **Trafic diversificat:**  
   - ICMP (ping) pentru conectivitate de bază  
   - TCP echo (server/client simplu)  
   - HTTP (cereri multiple, observarea distribuției)

4. **Captură și analiză:**  
   - `tcpdump` pe interfața lb → pcap  
   - `tshark` post-procesare: conversații IP/TCP, cereri HTTP, handshakes

5. **Artefacte verificabile:**  
   - `artifacts/demo.pcap` (captură Mininet)
   - `artifacts/demo.log` (log consolidat)
   - `artifacts/validation.txt` (checklist verificare)
   - `artifacts/tshark_summary.txt`  
   - `artifacts/report.json` (sinteză)  
   - Loguri individuale per componentă

---

## Cerințe minime

| Componentă | Minim | Recomandat |
|------------|-------|------------|
| OS | Ubuntu 20.04+ / Debian 11+ | Ubuntu 22.04 Server (CLI) |
| Python | 3.8+ | 3.10+ |
| RAM | 2 GB | 4 GB |
| vCPU | 1 | 2 |
| Disk | 10 GB | 15 GB |
| Acces | sudo | root |

**Pachete necesare** (instalate automat de `setup.sh`):  
`mininet`, `openvswitch-switch`, `tcpdump`, `tshark`, `iproute2`, `netcat-openbsd`, `curl`, `apache2-utils`

---

## Structura kit-ului

```
starterkit_saptamana_14/
├── README.md                    # acest fișier
├── Makefile                     # automatizare (setup, run-demo, run-lab, etc.)
├── requirements.txt             # dependențe Python
├── project_config.json          # configurare pentru harness verificare
│
├── scripts/
│   ├── setup.sh                 # instalare pachete + configurare
│   ├── run_all.sh               # demo automat complet
│   ├── cleanup.sh               # oprire procese + curățare Mininet
│   ├── capture.sh               # pornire captură tcpdump standalone
│   └── verify.sh                # verificare mediu și dependențe
│
├── python/
│   ├── apps/
│   │   ├── backend_server.py    # server HTTP simplu (backend)
│   │   ├── lb_proxy.py          # load balancer / reverse proxy
│   │   ├── http_client.py       # client HTTP cu logging
│   │   ├── tcp_echo_server.py   # server TCP echo
│   │   ├── tcp_echo_client.py   # client TCP echo
│   │   └── run_demo.py          # orchestrator demo automat
│   ├── utils/
│   │   ├── net_utils.py         # utilitare de rețea
│   │   └── __init__.py
│   └── exercises/
│       ├── ex_14_01.py          # drill-uri recapitulare (quiz)
│       ├── ex_14_02.py          # harness verificare proiect
│       ├── ex_14_03.py          # exerciții avansate (challenge)
│       └── ex_14_04_tracing.py  # exerciții tracing (fără execuție)
│
├── mininet/
│   ├── topologies/
│   │   └── topo_14_recap.py     # topologie: cli, lb, app1, app2
│   └── scenarios/
│       └── scenario_14_tasks.md # sarcini de laborator
│
├── docker/
│   ├── README.md                # ghid Docker (opțional)
│   ├── Dockerfile               # imagine minimală
│   └── docker-compose.yml       # orchestrare
│
├── pcap/
│   └── sample_http.pcap         # exemplu pcap pentru analiză offline
│
├── docs/
│   ├── curs.md                  # material curs (Markdown)
│   ├── seminar.md               # material seminar (Markdown)
│   ├── lab.md                   # ghid laborator (Markdown)
│   ├── checklist.md             # checklist cadru didactic
│   └── rubrici.md               # criterii evaluare
│
├── slides/
│   ├── curs_slides_outline.txt  # schiță slide-uri curs
│   └── seminar_slides_outline.txt # schiță slide-uri seminar
│
├── tests/
│   ├── smoke_test.sh            # verificări rapide de mediu
│   └── expected_outputs.md      # output-uri de referință
│
├── configs/
│   └── sysctl.conf              # tunări kernel (opțional)
│
└── assets/
    ├── style.css                # stil comun HTML-uri
    └── logo.svg                 # logo minimal
```

---

## Makefile — comenzi principale

| Comandă | Descriere |
|---------|-----------|
| `make setup` | Instalează dependențele OS + Python |
| `make run-demo` | Rulează demo-ul complet (Mininet + trafic + pcap) |
| `make run-lab` | Pornește topologia interactiv (CLI Mininet) |
| `make capture` | Pornește doar captura tcpdump |
| `make verify` | Verifică mediul și dependențele |
| `make clean` | Oprește procese, curăță Mininet |
| `make reset` | Clean + șterge artefacte |

---

## Ghid rapid de laborator

### Pas 0: Setup
```bash
make setup
make verify
```

### Pas 1: Demo automat
```bash
make run-demo
```
Verifică `artifacts/` pentru pcap, loguri, raport JSON.

### Pas 2: Analiză offline
```bash
# Conversații IP
tshark -r artifacts/demo.pcap -q -z conv,ip

# Cereri HTTP
tshark -r artifacts/demo.pcap -Y "http.request" \
  -T fields -e ip.src -e ip.dst -e http.request.uri

# Handshake-uri TCP (SYN)
tshark -r artifacts/demo.pcap -Y "tcp.flags.syn==1 && tcp.flags.ack==0"
```

### Pas 3: Modificări (exerciții)
- **T1:** Oprește un backend și observă comportamentul lb (502/erori)
- **T2:** Adaugă delay pe link în topologie și măsoară latența
- **T3:** Modifică numărul de cereri HTTP și observă distribuția

### Pas 4: Raport
Completează `docs/REPORT_TEMPLATE.md` cu concluziile tale.

---

## Troubleshooting (Top 10)

| Problemă | Soluție |
|----------|---------|
| `mn: command not found` | Rulează `make setup` |
| `Permission denied` | Folosește `sudo` sau rulează ca root |
| OVS nu pornește | `sudo systemctl restart openvswitch-switch` |
| Port 8080 ocupat | `sudo ss -lntp \| grep 8080` + `kill` PID |
| pcap gol | Verifică că demo-ul a rulat complet; re-rulează |
| tshark lipsește | `sudo apt install tshark` |
| Mininet „murdar" | `sudo mn -c` + `make clean` |
| Procese rămase | `sudo pkill -f backend_server` |
| DNS nu merge | Folosește IP-uri direct în lab |
| ab lipsește | `sudo apt install apache2-utils` |

---

## Evaluarea proiectului — ce să aduci

1. **README.md** clar: cum instalezi, pornești, testezi, cureți
2. **Demo plan:** pași + comenzi + output așteptat
3. **Captură pcap** (1-2 fișiere) + interpretare scurtă (3-5 rânduri)
4. **report.json** din harness (`python/exercises/ex_14_02.py`)
5. **Răspunsuri** la 3-5 întrebări de apărare

---

## Bibliografie & standarde

- Kurose, J. F., & Ross, K. W. (2017). *Computer Networking: A Top-Down Approach* (7th ed.). Pearson.
- RFC 791 (IP), RFC 793 (TCP), RFC 768 (UDP), RFC 2616/7230 (HTTP/1.1)
- Lantz, B., et al. (2010). *A network in a laptop: Rapid prototyping for SDN*. HotNets.

---

**Notă:** Kit-ul este proiectat pentru **reproductibilitate** și audit (artefacte + comenzi explicite), nu pentru performanță maximă.
