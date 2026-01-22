# ✅ Checklist Student — Pregătire Laborator Rețele

## Înainte de Primul Laborator

- [ ] VirtualBox instalat (versiunea 7.x)
- [ ] ISO Ubuntu Server 24.04 LTS descărcat
- [ ] VM creat conform ghidului de instalare
- [ ] Script verificare rulat fără erori

## Verificare Rapidă Mediu

```bash
# Rulează în VM:
~/networking/scripts/verify_installation.sh
```

**Toate verificările trebuie să fie ✓ (verde)**

## Dacă Ai Probleme

1. Verifică secțiunea Troubleshooting din ghid
2. Postează pe forum cu:
   - Output-ul exact al erorii
   - Ce comandă ai rulat
   - Ce ai încercat deja
3. Vino la consultații cu laptopul

---

## Checklist per Săptămână

### WEEK 1: Introducere
- [ ] `ping`, `traceroute`, `netcat` funcționează
- [ ] `tshark` capturează trafic
- [ ] Înțeleg TCP vs UDP

### WEEK 2-3: Socket Programming
- [ ] Python3 cu `socket` disponibil
- [ ] Mininet: `sudo mn --test pingall` OK
- [ ] Pot crea server TCP simplu

### WEEK 4: Nivel Legătură Date
- [ ] Înțeleg frame-uri Ethernet
- [ ] Captură și analiză cu tshark

### WEEK 5-6: Nivel Rețea
- [ ] `nmap`, `hping3` instalate
- [ ] `iptables` disponibil
- [ ] Înțeleg subnetting IP

### WEEK 7: Firewall
- [ ] Pot crea reguli iptables
- [ ] Înțeleg DROP vs REJECT

### WEEK 8-9: Nivel Transport
- [ ] Înțeleg TCP handshake
- [ ] Analiză sesiuni în Wireshark

### WEEK 10: HTTP
- [ ] `curl` instalat
- [ ] Pot face cereri HTTP

### WEEK 11: Load Balancing
- [ ] Docker Compose funcțional
- [ ] Nginx ca reverse proxy

### WEEK 12: Email
- [ ] Înțeleg SMTP
- [ ] Pot trimite email cu netcat

### WEEK 13: IoT/MQTT
- [ ] Înțeleg publish/subscribe
- [ ] Mosquitto (opțional)

### WEEK 14: Proiect Final
- [ ] Proiect funcțional
- [ ] Documentație completă
- [ ] Prezentare pregătită

---

## Comenzi Verificare Rapidă

```bash
# Verificare completă
~/networking/scripts/verify_installation.sh

# Docker
docker run hello-world

# Mininet
sudo mn --test pingall

# Python networking
python3 -c "import socket; print('OK')"

# TShark
tshark --version
```

---

## Resurse

| Resursă | Locație |
|---------|---------|
| Ghid instalare (RO) | `PREREQ/GHID_INSTALARE_UBUNTU_NETWORKING.md` |
| Ghid instalare (EN) | `PREREQ/UBUNTU_NETWORKING_INSTALLATION_GUIDE.md` |
| Diagrame (RO) | `PlantUML/RO/` |
| Diagrame (EN) | `PlantUML/EN/` |
| Proiecte | `PROJ/` |

---

**Succes la laborator!** 🎓
