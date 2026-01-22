# Exerciții — Săptămâna 7

Exercițiile sunt ordonate de la bază la provocare. Păstrează un jurnal cu comenzile rulate, rezultatele și concluziile tale.

---

## Lucru în perechi

Exercițiile 2, 3 și secțiunea de înțelegere sunt proiectate pentru **pair programming**.

**Roluri:**
- **Driver:** scrie comenzile, controlează tastatura
- **Navigator:** citește cerința, verifică output-ul, propune următorul pas

**Reguli:**
- Schimbați rolurile la fiecare 10-15 minute
- Navigatorul NU atinge tastatura
- Driverul NU citește cerința singur — ascultă de navigator
- Când nu sunteți de acord, experimentați ambele variante

**Timing recomandat:**
- Exercițiul 1: 15 min (individual e OK)
- Exercițiul 2: 25 min (2-3 schimburi de rol)
- Exercițiul 3: 35 min (3-4 schimburi de rol)
- Exerciții de înțelegere: 20 min (discuție în perechi)

---

## Exercițiul 1 (bază): captură și filtre tshark

**Timp:** 15 min | **Nivel:** Începător

1) Rulează demo-ul automat:

```bash
./scripts/run_all.sh
```

2) Verifică ce fișiere au fost generate:

```bash
ls -lh artifacts/
```

3) Folosește `tshark` pentru a răspunde la următoarele. Notează comenzile și răspunsurile.

**Întrebări:**
- Care sunt IP-urile sursă și destinație din captură?
- Câte pachete au flag-ul SYN setat?
- Există trafic UDP către portul 9091?
- Ce protocoale apar în captură? (hint: `-z io,phs`)

Comenzi utile:

```bash
tshark -r artifacts/demo.pcap -Y 'tcp.flags.syn==1'
tshark -r artifacts/demo.pcap -Y 'udp.dstport==9091'
tshark -r artifacts/demo.pcap -z io,phs -q
```

---

## Exercițiul 2 (mediu): aplică profile și validează

**Timp:** 25 min | **Nivel:** Intermediar | **Mod:** Perechi recomandat

Pentru fiecare profil de mai jos, urmează pașii și notează observațiile.

### Pas 1: Baseline

```bash
sudo python3 python/apps/firewallctl.py --profile baseline
./scripts/run_all.sh
```

Notează:
- Ce scrie în `artifacts/validation.txt`?
- Câte pachete TCP vezi cu `tshark -r artifacts/demo.pcap -Y 'tcp'`?

### Pas 2: Block TCP 9090

```bash
sudo python3 python/apps/firewallctl.py --profile block_tcp_9090
./scripts/run_all.sh
```

Notează:
- Ce s-a schimbat în validation.txt?
- Vezi RST în pcap? (`tshark -r artifacts/demo.pcap -Y 'tcp.flags.reset==1'`)
- Traficul UDP e afectat?

### Pas 3: Block UDP 9091

```bash
sudo python3 python/apps/firewallctl.py --profile baseline
sudo python3 python/apps/firewallctl.py --profile block_udp_9091
./scripts/run_all.sh
```

Notează:
- Cum se manifestă blocarea UDP vs blocarea TCP?
- Ce diferențe vezi în comportamentul clientului?

---

## Exercițiul 3 (provocare): profil personalizat

**Timp:** 35 min | **Nivel:** Avansat | **Mod:** Perechi recomandat

### Cerință

Creează un profil nou în `configs/firewall_profiles.json` care:
- permite ICMP (ping să funcționeze)
- permite TCP către portul 9090 doar din h1 (10.0.7.11) către h2 (10.0.7.200)
- blochează orice alt trafic FORWARD

### Pași

1) Deschide `configs/firewall_profiles.json` și studiază structura profilelor existente.

2) Adaugă un profil nou. Exemplu de structură:

```json
"custom_restrictive": {
  "description": "Permite doar ICMP și TCP 9090 h1->h2",
  "forward_policy": "DROP",
  "rules": [
    {
      "chain": "FORWARD",
      "proto": "icmp",
      "action": "ACCEPT"
    }
  ]
}
```

Hint: pentru a specifica sursă/destinație, s-ar putea să trebuiască să extinzi `firewallctl.py` sau să adaugi regulile manual cu `iptables`.

3) Aplică profilul și demonstrează cu:
   - comenzi de test (ping, nc, client TCP/UDP)
   - filtre tshark
   - capturi de ecran sau log

4) Documentează:
   - ce trafic e permis și de ce
   - ce trafic e blocat și cum ai verificat
   - ce ai văzut în pcap pentru fiecare caz

### Livrabil

- Fișierul JSON actualizat (sau diff-ul)
- Log cu comenzile rulate și output
- Explicație în 10-15 rânduri

---

## Exerciții de înțelegere (fără a scrie cod de la zero)

Aceste exerciții verifică înțelegerea conceptelor. Rezolvă-le pe hârtie sau discută cu un coleg înainte de a verifica soluțiile.

---

### Ex. A: Parsons Problem — Construiește regula iptables

Ai fragmentele de mai jos, amestecate. Pune-le în ordinea corectă pentru a crea o regulă care:

**Blochează (REJECT) traficul TCP pe portul 22, pe chain-ul FORWARD**

Fragmente:
```
--dport 22
iptables
-j REJECT
-A FORWARD
-p tcp
```

Scrie regula completă pe o singură linie.

<details>
<summary>Verifică soluția</summary>

```bash
iptables -A FORWARD -p tcp --dport 22 -j REJECT
```

**Ordinea logică:** 
1. `iptables` — comanda
2. `-A FORWARD` — adaugă la chain-ul FORWARD
3. `-p tcp` — protocol
4. `--dport 22` — port destinație (necesită `-p tcp` sau `-p udp` înainte)
5. `-j REJECT` — acțiunea

**Greșeală frecventă:** `--dport` înainte de `-p tcp` nu funcționează.
</details>

---

### Ex. B: Trace Exercise — Urmărește secvența

Ai captura simplificată de mai jos. Analizează și răspunde la întrebări FĂRĂ să rulezi comenzi.

```
Nr   Timp    Sursă         Dest          Proto  Info
1    0.000   10.0.7.11     10.0.7.200    TCP    SYN
2    0.001   10.0.7.200    10.0.7.11     TCP    SYN-ACK
3    0.001   10.0.7.11     10.0.7.200    TCP    ACK
4    0.002   10.0.7.11     10.0.7.200    TCP    PSH-ACK  Len=6
5    0.003   10.0.7.200    10.0.7.11     TCP    PSH-ACK  Len=6
6    0.004   10.0.7.11     10.0.7.200    TCP    FIN-ACK
7    0.005   10.0.7.200    10.0.7.11     TCP    FIN-ACK
```

**Întrebări:**

1. Care host e clientul și care e serverul? Cum ai dedus?

2. Ce pachete formează three-way handshake-ul?

3. Pachetele 4 și 5 au `Len=6`. Ce crezi că conțin? (hint: "hello\n" are 6 bytes)

4. Dacă între pachetul 3 și 4 ar fi apărut un RST de la 10.0.7.1 (firewall-ul), ce s-ar fi întâmplat?

5. Dacă serverul nu ar fi răspuns deloc la SYN (pachetul 2 lipsește), ce ai vedea în schimb?

<details>
<summary>Verifică răspunsurile</summary>

1. **Client:** 10.0.7.11 (inițiază conexiunea cu SYN). **Server:** 10.0.7.200 (răspunde cu SYN-ACK). Regula: cine trimite primul SYN e clientul.

2. Pachetele 1, 2, 3: SYN → SYN-ACK → ACK

3. Probabil mesajul "hello\n" trimis de client (pachet 4) și răspunsul echo de la server (pachet 5).

4. Conexiunea s-ar fi terminat brusc. Clientul ar fi primit RST și ar fi închis socket-ul cu eroare (Connection reset by peer).

5. Ai vedea SYN-uri repetate de la client (retransmisii la 1s, 2s, 4s...) apoi timeout după ~30-60 secunde. Niciun SYN-ACK.
</details>

---

### Ex. C: Debugging Exercise — Găsește problemele

Scriptul de mai jos ar trebui să testeze conectivitatea TCP, dar are **2 probleme**. Găsește-le fără să rulezi codul.

```python
#!/usr/bin/env python3
import socket

def test_connection(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Linia 5
    s.timeout(3)                                           # Linia 6
    try:
        s.connect((host, port))
        s.send(b"test")
        data = s.recv(1024)
        print(f"OK: {data}")
    except Exception as e:
        print(f"Eroare: {e}")
    s.close()

test_connection("10.0.7.200", 9090)
```

Identifică cele 2 probleme și scrie fix-ul pentru fiecare.

<details>
<summary>Verifică soluțiile</summary>

**Problema 1 (Linia 5):** `SOCK_DGRAM` creează socket UDP, dar portul 9090 e serverul TCP din kit.

Fix: `socket.SOCK_STREAM`

**Problema 2 (Linia 6):** Metoda corectă e `settimeout()`, nu `timeout()`.

Fix: `s.settimeout(3)`

**Bonus (nu e eroare critică):** `send()` ar trebui să fie `sendall()` pentru a garanta că toți bytes sunt trimiși. Și `s.close()` ar trebui în `finally:` pentru cleanup sigur.
</details>

---

### Ex. D: Code Reading — Explică funcția

Citește codul și răspunde la întrebări FĂRĂ să-l rulezi.

```python
def mystery(host, ports):
    results = []
    for p in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            s.connect((host, p))
            results.append((p, "open"))
        except:
            results.append((p, "closed"))
        finally:
            s.close()
    return results
```

**Întrebări:**

1. Ce face funcția `mystery`?

2. Ce returnează `mystery("10.0.7.200", [22, 80, 9090])` dacă doar portul 9090 ascultă?

3. De ce timeout-ul e doar 0.5 secunde? Ce compromis face?

4. Ce problemă are `except:` fără tip de excepție specificat?

<details>
<summary>Verifică răspunsurile</summary>

1. Scanează o listă de porturi TCP și returnează care sunt deschise ("open") sau închise ("closed").

2. `[(22, "closed"), (80, "closed"), (9090, "open")]`

3. Timeout mic = scanare rapidă. Compromis: 0.5s poate fi prea scurt pentru rețele lente sau cu latență mare. Unele porturi deschise pot părea închise dacă răspunsul întârzie.

4. `except:` prinde TOATE excepțiile, inclusiv `KeyboardInterrupt` și `SystemExit`. Mai corect: `except (socket.timeout, ConnectionRefusedError, OSError):`. În plus, nu distinge între "closed" (refused) și "filtered" (timeout).
</details>

---

### Ex. E: Completează codul lipsă

Funcția de mai jos ar trebui să facă probe UDP, dar îi lipsesc 3 linii. Completează.

```python
def udp_probe(host, port, timeout=1.0):
    """Trimite un pachet UDP și încearcă să primească răspuns."""
    s = socket.socket(socket.AF_INET, _____)  # 1. Ce tip de socket?
    s.settimeout(timeout)
    try:
        s.sendto(b"ping", _____)               # 2. Ce parametru lipsește?
        data, addr = s.recvfrom(1024)
        return "open (răspuns primit)"
    except socket.timeout:
        return _____                            # 3. Ce returnezi la timeout?
    finally:
        s.close()
```

<details>
<summary>Verifică completările</summary>

1. `socket.SOCK_DGRAM` — pentru UDP
2. `(host, port)` — tuplu adresă
3. `"open|filtered"` sau `"timeout (probabil filtrat)"` — la UDP, timeout nu înseamnă neapărat closed

**Cod complet:**
```python
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b"ping", (host, port))
return "open|filtered"
```
</details>

---

## Criterii de reușită (autoevaluare)

După ce termini exercițiile, verifică:

- [ ] Poți reproduce demo-ul complet (setup → demo → test → cleanup)
- [ ] Poți argumenta o regulă de firewall printr-o captură pcap și loguri
- [ ] Înțelegi diferența dintre DROP și REJECT și cum se manifestă
- [ ] Poți explica diferența dintre "aplicația nu merge" și "traficul este blocat"
- [ ] Ai rezolvat corect cel puțin 4 din 5 exerciții de înțelegere
