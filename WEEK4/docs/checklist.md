# Checklist Săptămâna 4 – Protocoale Text și Binare Custom

> **Disciplină:** Rețele de Calculatoare  
> **Săptămâna:** 4  
> **Temă:** Implementarea de protocoale text și binare custom peste TCP și UDP

---

## ✅ Înainte de activitate (cu 24-48h înainte)

### Pregătire infrastructură

- [ ] Verificare VM/container funcțională cu Python 3.8+
- [ ] Testare `python3 --version` și `pip3 --version`
- [ ] Instalare pachete: `pip3 install --break-system-packages pyshark`
- [ ] Verificare acces sudo pentru tshark/tcpdump
- [ ] Testare Wireshark GUI (dacă se folosește)
- [ ] Verificare porturi libere: 5400, 5401, 5402
  ```bash
  netstat -tlnp | grep -E '5400|5401|5402'
  ```

### Pregătire materiale

- [ ] Starterkit S4 descărcat și dezarhivat
- [ ] Executare `make setup` fără erori
- [ ] Testare `make verify` - toate verificările trec
- [ ] Rulare smoke test: `./tests/smoke_test.sh`
- [ ] Slide-uri încărcate și testate pe proiector
- [ ] theory.html, seminar.html, lab.html testate în browser

### Pregătire demonstrații

- [ ] Terminal cu font mare (14pt+) pentru vizibilitate
- [ ] Testare demo protocol TEXT:
  ```bash
  make run-text-server &
  sleep 1
  make run-text-client
  ```
- [ ] Testare demo protocol BINAR:
  ```bash
  make run-binary-server &
  sleep 1
  make run-binary-client
  ```
- [ ] Testare demo UDP sensor:
  ```bash
  make run-udp-server &
  sleep 1
  make run-udp-client
  ```
- [ ] Pregătire captură tshark live:
  ```bash
  sudo tshark -i lo -f "tcp port 5400 or tcp port 5401 or udp port 5402"
  ```

### Verificare cunoștințe anterioare

- [ ] Recapitulare S3 (sockets TCP/UDP de bază)
- [ ] Verificare că studenții au acces la materialele S1-S3
- [ ] Pregătire întrebări de sondaj pentru recapitulare

---

## ✅ În timpul activității

### Curs (50 min)

| Timp | Activitate | Verificare |
|------|------------|------------|
| 0-5 | Recapitulare TCP/UDP, sondaj cunoștințe | [ ] Studenții răspund |
| 5-15 | Motivație protocoale custom, taxonomie | [ ] Întrebări clarificare |
| 15-25 | Protocol TEXT: format, framing, implementare | [ ] Demo live funcțional |
| 25-40 | Protocol BINAR: header, struct, CRC32 | [ ] Demo live funcțional |
| 40-48 | Protocol UDP sensor: specificație, cazuri IoT | [ ] Explicații clare |
| 48-50 | Rezumat, întrebări | [ ] Q&A |

### Seminar (50 min)

| Timp | Activitate | Verificare |
|------|------------|------------|
| 0-5 | Prezentare obiective, setup verificare | [ ] Toți au starterkit |
| 5-15 | Implementare TEXT client (ghidat) | [ ] Cod rulează |
| 15-30 | Implementare BINAR client (ghidat) | [ ] Cod rulează |
| 30-40 | Analiza trafic cu tshark | [ ] Captură vizibilă |
| 40-48 | Exerciții individuale | [ ] Progres monitorizat |
| 48-50 | Recapitulare, indicații proiect | [ ] Notițe distribuite |

### Puncte de control

- [ ] **Minutul 15:** Studenții înțeleg diferența TEXT vs BINAR?
- [ ] **Minutul 25:** recv_exact() și recv_until() clare?
- [ ] **Minutul 35:** CRC32 și validare înțelese?
- [ ] **Minutul 45:** UDP datagram vs TCP stream clar?

### Gestionare probleme frecvente

| Problemă | Soluție rapidă |
|----------|---------------|
| Port already in use | `sudo fuser -k 5400/tcp` |
| Permission denied tshark | `sudo chmod +s /usr/bin/dumpcap` |
| Python module not found | `pip3 install <module> --break-system-packages` |
| Conexiune refuzată | Verifică dacă serverul rulează: `ps aux \| grep python` |
| recv() blochează | Verifică dacă clientul trimite `\n` la final |

---

## ✅ După activitate

### Imediat (în 30 min)

- [ ] Oprire procese reziduale:
  ```bash
  make clean
  pkill -f "python.*proto"
  ```
- [ ] Salvare capturi relevante în `/pcap/`
- [ ] Notare întrebări nerezolvate pentru follow-up
- [ ] Colectare feedback rapid (3 întrebări scurte)

### În 24-48h

- [ ] Actualizare FAQ dacă au apărut întrebări noi
- [ ] Publicare materiale suplimentare (dacă solicitate)
- [ ] Verificare exerciții trimise (dacă aplică)
- [ ] Actualizare rubrici evaluare pe baza dificultăților observate

### Pentru îmbunătățiri viitoare

- [ ] Ce a mers bine?
  - _______________________________________________
- [ ] Ce ar fi putut merge mai bine?
  - _______________________________________________
- [ ] Ce exemple/demo-uri suplimentare ar ajuta?
  - _______________________________________________
- [ ] Timing adecvat? Da / Prea rapid / Prea lent
- [ ] Nivel dificultate: Prea ușor / Adecvat / Prea greu

---

## 📋 Verificare finală materiale

### Fișiere critice (trebuie să existe)

```
starterkit_s4/
├── [ ] README.md (actualizat cu S4)
├── [ ] Makefile (ținte funcționale)
├── python/
│   ├── apps/
│   │   ├── [ ] text_proto_server.py
│   │   ├── [ ] text_proto_client.py
│   │   ├── [ ] binary_proto_server.py
│   │   ├── [ ] binary_proto_client.py
│   │   ├── [ ] udp_sensor_server.py
│   │   └── [ ] udp_sensor_client.py
│   ├── exercises/
│   │   ├── [ ] ex_4_01_tcp_proto.py
│   │   └── [ ] ex_4_02_udp_sensor.py
│   └── solutions/
│       └── [ ] solutions.py
├── html/
│   ├── [ ] theory.html (min 25 slides)
│   ├── [ ] seminar.html (min 8 taburi)
│   └── [ ] lab.html (pași completi)
├── docs/
│   ├── [ ] curs.md
│   ├── [ ] seminar.md
│   └── [ ] lab.md
└── tests/
    └── [ ] smoke_test.sh (exit 0)
```

### Teste rapide pre-seminar

```bash
# Test 1: Server TEXT pornește
timeout 5 python3 python/apps/text_proto_server.py &
sleep 2 && echo "5 test1" | nc localhost 5400
pkill -f text_proto_server

# Test 2: Server BINAR pornește  
timeout 5 python3 python/apps/binary_proto_server.py &
sleep 2 && python3 python/apps/binary_proto_client.py
pkill -f binary_proto_server

# Test 3: Captura funcționează
sudo timeout 3 tshark -i lo -c 1 -q && echo "tshark OK"
```

---

## 📞 Contact și suport

- **Probleme tehnice urgente:** [email instructor]
- **Repository materiale:** [link intern]
- **Canal comunicare:** [Discord/Teams/etc]

---

*Versiune checklist: S4 v1.0 | Ultima actualizare: 2025*

<!-- Revolvix&Hypotheticalandrei -->
