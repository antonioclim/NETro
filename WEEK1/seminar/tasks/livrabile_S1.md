# 📋 Livrabile Săptămâna 1

## Prezentare Generală

Această săptămână contribui cu primul artefact la proiectul semestrial. Livrabilele demonstrează că ai înțeles fundamentele rețelelor și poți folosi instrumentele de bază pentru diagnostic și analiză.

## Deadline

**Înainte de Săptămâna 2** - Încărcare în sistemul de management al cursului.

## Structura Livrabilelor

### 1. Raport Analiză Rețea Personală

**Fișier:** `S1_[NumeStudent]_Raport.pdf` sau `.docx`

**Conținut obligatoriu:**

#### Secțiunea A: Topologia Rețelei (15%)
- Schiță/diagramă a rețelei tale (poate fi desenată manual și scanată)
- Identificare dispozitive: router, switch, access point, PC-uri
- Adrese IP pentru fiecare dispozitiv cunoscut
- Tip conexiune (Ethernet, WiFi)

#### Secțiunea B: Configurație Locală (20%)
- Output complet `ip addr show` cu interpretare
- Output complet `ip route show` cu interpretare
- Identificare:
  - Interfața principală (nume și tip)
  - Adresa IPv4 și masca de rețea
  - Gateway implicit
  - Server DNS (din /etc/resolv.conf)

#### Secțiunea C: Test Conectivitate (25%)
- Rezultate ping către 5 destinații:
  1. 127.0.0.1 (loopback)
  2. Gateway-ul tău
  3. 8.8.8.8 (Google DNS)
  4. 1.1.1.1 (Cloudflare DNS)
  5. Un site la alegere (ex: www.ase.ro)
  
- Pentru fiecare destinație, documentează:
  - Comanda executată
  - RTT min/avg/max
  - Packet loss
  - TTL observat

- Tabel comparativ:
  | Destinație | Min (ms) | Avg (ms) | Max (ms) | Loss | TTL |
  |------------|----------|----------|----------|------|-----|
  | ...        | ...      | ...      | ...      | ...  | ... |

#### Secțiunea D: Captură Trafic (25%)
- Descriere metodologie (ce ai capturat, de ce)
- Statistici captură:
  - Număr total pachete
  - Protocoale identificate
  - Durata capturii
- Screenshot sau output tshark relevant
- Identificare TCP handshake (dacă există)

#### Secțiunea E: Concluzii (15%)
- 3 observații interesante despre rețeaua ta
- Ce ai învățat din acest exercițiu
- O întrebare pe care o ai despre rețele

### 2. Fișier Captură PCAP

**Fișier:** `S1_[NumeStudent]_capture.pcap`

**Cerințe:**
- Minim 50 pachete
- Cel puțin 2 protocoale diferite (ex: TCP + ICMP, sau TCP + UDP)
- Capturat pe propria mașină (nu descărcat de pe Internet)
- Să nu conțină informații sensibile (parole, date personale)

**Cum generezi:**
```bash
# Exemplu: captură 2 minute de trafic general
tshark -i eth0 -a duration:120 -w capture.pcap

# Sau: captură trafic web
tshark -i eth0 -f "port 80 or port 443" -c 100 -w capture.pcap
```

### 3. Script Diagnostic (Opțional - Bonus)

**Fișier:** `S1_[NumeStudent]_diagnostic.sh`

Script bash care automatizează verificările din secțiunea B și C:

```bash
#!/bin/bash
# Exemplu structură minimă

echo "=== Diagnostic Rețea ==="
echo "Data: $(date)"
echo ""

echo "--- Interfețe ---"
ip addr show

echo "--- Rutare ---"
ip route show

echo "--- Test Conectivitate ---"
for target in 127.0.0.1 8.8.8.8 google.com; do
    echo "Ping $target:"
    ping -c 4 $target
done
```

## Criterii de Evaluare

| Criteriu | Punctaj | Descriere |
|----------|---------|-----------|
| Completitudine | 2.0p | Toate secțiunile prezente și populate |
| Corectitudine tehnică | 1.5p | Comenzi corecte, interpretări valide |
| Claritate prezentare | 1.0p | Format profesional, organizare logică |
| Captură validă | 0.5p | PCAP funcțional, minim 50 pachete |
| **Total** | **5.0p** | Contribuie la nota proiectului |

**Bonus:**
- Script funcțional și documentat: +0.5p
- Analiză aprofundată (ex: identificare probleme, sugestii): +0.5p

## Cum Încarci

1. Arhivează toate fișierele într-un singur ZIP:
   ```bash
   zip S1_NumeStudent.zip S1_NumeStudent_Raport.pdf S1_NumeStudent_capture.pcap
   ```

2. Încarcă în platforma cursului în secțiunea "Săptămâna 1 - Livrabile"

3. Verifică că fișierele s-au încărcat corect

## Greșeli Frecvente de Evitat

❌ **Nu face:**
- Nu copia output-uri de pe Internet
- Nu trimite capturi descărcate
- Nu uita să anonimizezi date sensibile
- Nu trimite fișiere corupte

✅ **Verifică înainte de trimitere:**
- PCAP se deschide cu tshark: `tshark -r capture.pcap | head`
- Raportul conține output-uri proprii (IP-uri reale ale rețelei tale)
- Toate secțiunile sunt complete

## Întrebări Frecvente

**Q: Nu am acces la Linux, ce fac?**
A: Folosește WSL2 pe Windows sau Docker. Starterkit-ul include instrucțiuni.

**Q: tshark cere sudo, e ok?**
A: Ideal adaugă user-ul la grupul wireshark. Dacă nu poți, folosește sudo, dar menționează în raport.

**Q: Pot folosi Wireshark grafic în loc de tshark?**
A: Da, pentru captură și analiză personală. Dar include și comenzi tshark în raport.

**Q: Câte pagini trebuie să aibă raportul?**
A: Nu există limită. Calitate > cantitate. Tipic: 3-5 pagini.

**Q: Pot colabora cu colegii?**
A: Poți discuta concepte, dar fiecare trimite propria rețea și propria captură.

## Resurse Ajutătoare

- `make help` - Vezi toate comenzile disponibile
- `./scripts/verify.sh` - Verifică mediul
- `docs/seminar.md` - Ghid pas cu pas
- `seminar/scenarios/` - Scenarii detaliate

## Contact

Pentru întrebări tehnice:
- Forum cursului
- Email instructor (vezi syllabus)

---

*Spor la lucru!*

*Revolvix&Hypotheticalandrei*
