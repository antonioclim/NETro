# Scenario S14 — Sarcini de Laborator (Recapitulare)

**Săptămâna 14 — Recapitulare Integrată & Evaluarea Proiectului**  
Rețele de Calculatoare — CSIE/ASE

---

## Obiective

- Consolidarea conceptelor din semestru într-un scenariu integrat
- Verificarea reproducibilității unui sistem distribuit
- Pregătirea pentru prezentarea proiectului de echipă

---

## Sarcini

### S1: Setup și Verificare Mediu (10 min)

```bash
# Pornește din directorul kit-ului
cd starterkit_saptamana_14

# Verifică dependențele
make verify

# Rulează demo-ul automat
make run-demo

# Verifică artefactele
ls -la artifacts/
cat artifacts/validation.txt
```

**Întrebări de control:**
1. Ce artefacte produce demo-ul?
2. Ce conține fișierul `validation.txt`?
3. Ce conversații TCP apar în `demo.pcap`?

---

### S2: Analiză Trafic (15 min)

Utilizează tshark pentru analiza capturii:

```bash
# Conversații IP
tshark -r artifacts/demo.pcap -q -z conv,ip

# Cereri HTTP
tshark -r artifacts/demo.pcap -Y "http.request" \
  -T fields -e ip.src -e ip.dst -e http.request.uri

# Handshake-uri TCP (SYN)
tshark -r artifacts/demo.pcap \
  -Y "tcp.flags.syn==1 && tcp.flags.ack==0" \
  -T fields -e frame.number -e ip.src -e ip.dst -e tcp.dstport

# Conexiuni pe port 8080
tshark -r artifacts/demo.pcap -Y "tcp.port==8080" | head -20
```

**Sarcină:** Identifică și documentează:
- Numărul de conexiuni TCP distincte
- Distribuția cererilor HTTP între backends
- Latența medie a răspunsurilor

---

### S3: Diagnosticare Erori (15 min)

Simulează și diagnostichează erori:

```bash
# Pornește topologia interactiv
make run-lab

# În CLI Mininet:
mininet> app1 ip link set app1-eth0 down  # Deconectează app1
mininet> cli curl -v http://10.0.14.10:8080/
mininet> app1 ip link set app1-eth0 up    # Reconectează
```

**Întrebări:**
1. Ce se întâmplă când un backend devine indisponibil?
2. Cum detectează load balancer-ul starea backend-urilor?
3. Cum ai implementa health checking automat?

---

### S4: Modificări și Teste (20 min)

#### S4a: Modificare topologie

Editează `mininet/topologies/topo_14_recap.py`:
- Adaugă un al treilea backend (`app3` cu IP 10.0.14.4)
- Modifică delay-ul pe link-uri la 5ms
- Rulează din nou demo-ul și compară latențele

#### S4b: Modificare load balancer

Editează `python/apps/lb_proxy.py`:
- Schimbă algoritmul de la round-robin la random
- Adaugă logging pentru fiecare cerere distribuită
- Testează cu 50 de cereri și verifică distribuția

---

### S5: Harness de Verificare (10 min)

Utilizează harness-ul pentru verificare automată:

```bash
# Din directorul kit-ului
python3 python/exercises/ex_14_02.py \
  --config project_config.json \
  --out artifacts/harness_report.json

# Verifică rezultatele
cat artifacts/harness_report.json | python3 -m json.tool
```

**Sarcină:** Modifică `project_config.json` pentru a adăuga:
- Check de latență (verifică că RTT < 100ms)
- Check pentru endpoint `/health` pe load balancer
- Check pentru disponibilitatea serverului TCP echo

---

### S6: Pregătire Prezentare Proiect (10 min)

**Checklist pentru proiect:**

- [ ] README.md clar cu: instalare, pornire, testare, curățare
- [ ] Demo plan: pași + comenzi + output așteptat
- [ ] Captură pcap (1-2 fișiere) cu interpretare
- [ ] Report.json din harness
- [ ] Răspunsuri pregătite pentru întrebări de apărare

**Întrebări frecvente la apărare:**
1. Cum funcționează TCP handshake în sistemul vostru?
2. Ce se întâmplă când un component eșuează?
3. Cum ați testat reproducibilitatea?
4. Ce limitări are implementarea voastră?
5. Ce ați face diferit dacă ați reîncepe?

---

## Livrabile

După completarea sarcinilor, studenții ar trebui să aibă:

1. **Artefacte generate:** `artifacts/demo.pcap`, `demo.log`, `validation.txt`
2. **Raport harness:** `artifacts/harness_report.json`
3. **Note personale:** Răspunsuri la întrebările de control
4. **Modificări (opțional):** Cod modificat + diferențe observate

---

## Resurse Utile

- RFC 793 (TCP): https://datatracker.ietf.org/doc/html/rfc793
- RFC 2616 (HTTP/1.1): https://datatracker.ietf.org/doc/html/rfc2616
- Mininet Walkthrough: http://mininet.org/walkthrough/
- Tshark Manual: https://www.wireshark.org/docs/man-pages/tshark.html
