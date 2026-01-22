# Expected Outputs - Săptămâna 1

## Artefacte generate de `run_all.sh`

După rularea `bash scripts/run_all.sh`, directorul `artifacts/` trebuie să conțină:

### 1. `demo.log`
Log complet al execuției demo-ului.

**Conținut minim așteptat:**
```
# Demo Log - Săptămâna 1: Analiză trafic și instrumentare
# Generat: <timestamp ISO>
...
[INFO] Pornire server TCP echo pe port 9090...
[✓] Captură TCP: <N> pachete
...
[INFO] Trimitere datagrame UDP...
[✓] Captură UDP: <N> pachete
...
[✓] Demo finalizat! Status: SUCCESS
```

**Dimensiune tipică:** 5-20 KB

### 2. `demo.pcap`
Captură trafic combinată (TCP + UDP + HTTP).

**Verificare:**
```bash
tshark -r artifacts/demo.pcap | head -20
```

**Conținut minim așteptat:**
- ≥10 pachete totale
- Pachete TCP cu flags SYN, ACK
- Pachete UDP (dacă demo complet)

**Structură tipică:**
```
  1   0.000000    127.0.0.1 → 127.0.0.1    TCP 74 [SYN] ...
  2   0.000050    127.0.0.1 → 127.0.0.1    TCP 74 [SYN, ACK] ...
  3   0.000080    127.0.0.1 → 127.0.0.1    TCP 66 [ACK] ...
  ...
```

### 3. `validation.txt`
Rezultate validare componente.

**Format:**
```
# Validation Results - Week 1
# Timestamp: <ISO timestamp>

PASS: nc disponibil
PASS: tshark disponibil
PASS: python3 disponibil
...
PASS: TCP capture - <N> packets
PASS: UDP capture - <N> packets
...
Status: SUCCESS
```

**Criterii pass:**
- ≥5 linii `PASS:`
- 0 linii `FAIL:` (ideal)
- Ultima linie: `Status: SUCCESS` sau `Status: PARTIAL`

---

## Rezultate smoke_test.sh

După rularea `bash tests/smoke_test.sh`:

### Teste structură
| Test | Criteriu | Așteptat |
|------|----------|----------|
| Director scripts/ | Există | PASS |
| Director python/ | Există | PASS |
| Director tests/ | Există | PASS |
| Director artifacts/ | Există | PASS |
| scripts/run_all.sh | Există | PASS |
| scripts/setup.sh | Există | PASS |
| scripts/cleanup.sh | Există | PASS |

### Teste artefacte
| Test | Criteriu | Așteptat |
|------|----------|----------|
| demo.log există | Fișier prezent | PASS |
| demo.log nevid | Size > 0 | PASS |
| demo.pcap există | Fișier prezent | PASS |
| demo.pcap valid | ≥5 pachete | PASS |
| validation.txt | ≥3 PASS, 0 FAIL | PASS |

### Teste Python
| Test | Criteriu | Așteptat |
|------|----------|----------|
| Syntax Python | py_compile OK | PASS |
| Self-test TCP/UDP | Exit code 0 | PASS/WARN |

---

## Output tipic smoke_test.sh

```
╔═══════════════════════════════════════════════════════════════════╗
║              SMOKE TEST - Săptămâna 1                             ║
╚═══════════════════════════════════════════════════════════════════╝

━━━ Teste structură proiect ━━━
[PASS] Director: scripts/
[PASS] Director: python/
[PASS] Director: tests/
[PASS] Script: scripts/run_all.sh
...

━━━ Teste artefacte demo ━━━
[PASS] demo.log: fișier există
[PASS] demo.log conținut: fișier nevid (12K)
[PASS] demo.pcap: fișier există
[PASS] demo.pcap pachete: 47 pachete (min 5)
[PASS] validation.txt: 8 PASS, 0 FAIL

━━━ Teste exerciții Python ━━━
[PASS] Syntax OK: ex_1_01_ping_latency.py
[PASS] Syntax OK: ex_1_02_tcp_server_client.py
[PASS] Self-test: ex_1_02_tcp_server_client.py

═══════════════════════════════════════════════════════════════
  SUMAR SMOKE TEST - Săptămâna 1
═══════════════════════════════════════════════════════════════

  PASS: 15
  FAIL: 0
  WARN: 0
  ─────────────────
  TOTAL: 15 teste

  ✅ Toate testele critice au trecut!
```

---

## Troubleshooting

### demo.pcap gol sau cu puține pachete
**Cauze posibile:**
1. tshark nu are permisiuni pentru captură
2. Interfața loopback nu este disponibilă
3. Procesele au fost oprite prea repede

**Remediere:**
```bash
# Verifică permisiuni tshark
tshark -D

# Adaugă utilizator la grupul wireshark
sudo usermod -aG wireshark $USER
newgrp wireshark

# Sau rulează cu sudo
sudo bash scripts/run_all.sh
```

### validation.txt cu FAIL
**Cauze posibile:**
1. Instrumente lipsă (nc, tshark, curl)
2. Porturi ocupate

**Remediere:**
```bash
# Instalare instrumente
sudo bash scripts/setup.sh

# Eliberare porturi
bash scripts/cleanup.sh

# Re-rulare
bash scripts/run_all.sh
```

### Erori syntax Python
**Remediere:**
```bash
# Verifică Python versiune (necesită 3.10+)
python3 --version

# Verifică syntax individual
python3 -m py_compile python/exercises/ex_1_02_tcp_server_client.py
```

---

*Revolvix&Hypotheticalandrei | CSIE/ASE București*
