# Expected Outputs - Săptămâna 2: Socket Programming

## Artefacte Generate

După rularea `scripts/run_all.sh`, următoarele fișiere trebuie să existe în `artifacts/`:

### 1. demo.log

**Locație:** `artifacts/demo.log`  
**Tip:** Text log  
**Conținut minim:** 20+ linii

**Structură așteptată:**
```
[2025-XX-XX HH:MM:SS][INFO] ════════════════════════════════════
[2025-XX-XX HH:MM:SS][INFO]  WEEK 2 - Demo Automat: Socket Programming
[2025-XX-XX HH:MM:SS][INFO] ════════════════════════════════════
[2025-XX-XX HH:MM:SS][INFO] Artefacte vor fi salvate în: .../artifacts
[2025-XX-XX HH:MM:SS][INFO] Network plan: 10.0.2.0/24 | Ports: TCP=9090, UDP=9091
[2025-XX-XX HH:MM:SS][INFO] ─── Verificări pre-execuție ───
[2025-XX-XX HH:MM:SS][ OK ] Python3: Python 3.x.x
[2025-XX-XX HH:MM:SS][ OK ] Exercițiu TCP: ...
[2025-XX-XX HH:MM:SS][ OK ] Exercițiu UDP: ...
[2025-XX-XX HH:MM:SS][INFO] ─── Demo TCP (Server Concurent) ───
[2025-XX-XX HH:MM:SS][INFO] Pornire server TCP pe 0.0.0.0:9090
[2025-XX-XX HH:MM:SS][ OK ] Server TCP activ (PID: XXXX)
[2025-XX-XX HH:MM:SS][INFO] Trimitere mesaje de test (3 clienți secvențiali)
...
[2025-XX-XX HH:MM:SS][INFO] ─── Demo UDP (Protocol Aplicație Custom) ───
...
[2025-XX-XX HH:MM:SS][ OK ] Validare completă
```

**Indicatori succes:**
- Prezența `[ OK ]` pentru fiecare verificare
- Absența `[ERR ]` în log
- Minim 3 mesaje TCP trimise și primite

---

### 2. demo.pcap

**Locație:** `artifacts/demo.pcap`  
**Tip:** PCAP (Packet Capture)  
**Cerințe:** Necesar tcpdump pentru generare

**Conținut așteptat (vizualizare cu tshark):**
```bash
tshark -r artifacts/demo.pcap -Y "tcp" | head
```

Output exemplu:
```
  1   0.000000    127.0.0.1 → 127.0.0.1    TCP 74 58000 → 9090 [SYN]
  2   0.000050    127.0.0.1 → 127.0.0.1    TCP 74 9090 → 58000 [SYN, ACK]
  3   0.000080    127.0.0.1 → 127.0.0.1    TCP 66 58000 → 9090 [ACK]
  4   0.000120    127.0.0.1 → 127.0.0.1    TCP 82 58000 → 9090 [PSH, ACK]
  5   0.000150    127.0.0.1 → 127.0.0.1    TCP 66 9090 → 58000 [ACK]
```

**Ce să verifici:**
- Handshake TCP complet (SYN → SYN/ACK → ACK)
- Pachete de date cu flag [PSH, ACK]
- Secvență de închidere (FIN)
- Porturi: 9090 (TCP), 9091 (UDP)

**Analiză rapidă:**
```bash
# Numără pachete per protocol
tshark -r artifacts/demo.pcap -Y "tcp" | wc -l
tshark -r artifacts/demo.pcap -Y "udp" | wc -l

# Verifică handshake
tshark -r artifacts/demo.pcap -Y "tcp.flags.syn==1"
```

---

### 3. validation.txt

**Locație:** `artifacts/validation.txt`  
**Tip:** Text raport  
**Conținut:** Sumar validare artefacte

**Structură așteptată:**
```
═══════════════════════════════════════════════════════════════
 WEEK 2 - Socket Programming: Validare Demo
 Generat: 2025-XX-XX HH:MM:SS
═══════════════════════════════════════════════════════════════

─── Verificare fișiere artefacte ───
[OK] demo.log prezent (XX linii)
[OK] demo.pcap prezent (XXXX bytes)

─── Verificare execuție demo ───
[OK] Server TCP: X răspunsuri OK
[OK] Server UDP: răspunsuri protocol validate

─── Analiză trafic (dacă tshark disponibil) ───
[INFO] Pachete TCP: XX
[INFO] Pachete UDP: XX
[OK] Handshake TCP detectat (X SYN flags)

═══════════════════════════════════════════════════════════════
 REZULTAT: VALIDARE REUȘITĂ
═══════════════════════════════════════════════════════════════
```

**Indicatori succes:**
- `REZULTAT: VALIDARE REUȘITĂ`
- Toate verificările cu `[OK]`
- Zero `[FAIL]`

---

## Fișiere Log Secundare

### logs/tcp_demo.log

Conține output-ul serverului și clienților TCP:
```
[HH:MM:SS.mmm][SERVER] TCP pe 0.0.0.0:9090 | mod=threaded
[HH:MM:SS.mmm][SERVER] Așteptare conexiuni...
[HH:MM:SS.mmm][MAIN] Conexiune nouă: 127.0.0.1:XXXXX
[HH:MM:SS.mmm][Worker-XXXXX] RX   16B de la 127.0.0.1:XXXXX: b'WEEK2_TEST_MSG_1'
[HH:MM:SS.mmm][Worker-XXXXX] TX   20B către 127.0.0.1:XXXXX: b'OK: WEEK2_TEST_MSG_1'
```

### logs/udp_demo.log

Conține output-ul serverului UDP:
```
[HH:MM:SS.mmm][SERVER] UDP pe 0.0.0.0:9091
[HH:MM:SS.mmm][SERVER] #1 RX 4B 127.0.0.1:XXXXX: b'ping'
[HH:MM:SS.mmm][SERVER] #1 TX 4B: b'PONG'
```

---

## Verificare Manuală Rapidă

```bash
# 1. Verifică toate artefactele există
ls -la artifacts/

# 2. Verifică log-ul principal
head -20 artifacts/demo.log

# 3. Verifică validarea
cat artifacts/validation.txt

# 4. Analizează captura (necesită tshark)
tshark -r artifacts/demo.pcap -c 10

# 5. Rulează smoke test
./tests/smoke_test.sh
```

---

## Troubleshooting

| Simptom | Cauză probabilă | Soluție |
|---------|-----------------|---------|
| `demo.pcap` gol | tcpdump indisponibil/fără privilegii | Rulează ca root sau instalează tcpdump |
| `[FAIL]` în validation.txt | Server nu a pornit | Verifică porturi libere: `ss -tuln` |
| Handshake incomplet | Timeout prea scurt | Mărește așteptarea în run_all.sh |
| Zero răspunsuri UDP | Firewall blochează UDP | Verifică `iptables -L` |

---

## Note

- **Porturi standard WEEK 2:** TCP=9090, UDP=9091
- **Network plan:** 10.0.2.0/24 (pentru Mininet)
- **Timeouts:** 5 secunde pentru conexiuni
