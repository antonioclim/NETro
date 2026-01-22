# Cheatsheet CLI - Săptămâna 13: IoT & Securitate

## Plan unitar de adrese (WEEK=13)

```
Rețea:       10.0.13.0/24
Gateway:     10.0.13.1
MQTT Broker: 10.0.13.100
DVWA:        10.0.13.11
vsftpd:      10.0.13.12
IoT Sensor:  10.0.13.30
Controller:  10.0.13.31
```

## Porturi standard

| Port | Serviciu | Descriere |
|------|----------|-----------|
| 1883 | MQTT     | Plaintext |
| 8883 | MQTT-TLS | Cu criptare |
| 8080 | HTTP     | DVWA (vulnerabil) |
| 2121 | FTP      | vsftpd vulnerabil |
| 6200 | Backdoor | CVE-2011-2523 |
| 9001 | MQTT-WS  | WebSocket |

## Comenzi rapide

### Setup și verificare
```bash
./scripts/setup.sh              # Setup complet
./scripts/setup.sh --check      # Doar verificare
./scripts/verify.sh             # Verificare rapidă
./tests/smoke_test.sh           # Test complet
```

### Demo și rulare
```bash
./scripts/run_all.sh            # Demo automat
./scripts/run_all.sh --quick    # Demo rapid (fără Docker)
make demo-offensive             # Demo ofensiv
make demo-defensive             # Demo defensiv
```

### Docker
```bash
docker-compose up -d            # Pornire containere
docker-compose logs -f          # Vizualizare loguri
docker-compose down             # Oprire containere
docker exec -it mqtt-broker sh  # Shell în container
```

### Scanare porturi
```bash
# Cu Python
python3 python/exercises/ex_01_port_scanner.py --target 10.0.13.11 --ports 1-1024
python3 python/exercises/ex_01_port_scanner.py --target 10.0.13.11 --ports 22,80,443

# Cu nmap (dacă disponibil)
nmap -sT -p 1-1000 10.0.13.11
nmap -sV 10.0.13.11             # Detectare servicii
```

### MQTT
```bash
# Publicare
mosquitto_pub -h 10.0.13.100 -t "iot/sensors/temp" -m "25.5"

# Abonare
mosquitto_sub -h 10.0.13.100 -t "iot/#" -v

# Cu Python
python3 python/exercises/ex_02_mqtt_client.py --broker 10.0.13.100 --mode pub --topic test
python3 python/exercises/ex_02_mqtt_client.py --broker 10.0.13.100 --mode sub --topic "iot/#"
```

### Captură trafic
```bash
# tcpdump
sudo tcpdump -i any -w capture.pcap port 1883

# tshark
sudo tshark -i any -f "port 1883" -w mqtt.pcap

# Cu script
./scripts/capture_traffic.sh 30  # Captură 30 secunde
```

### Vulnerabilități
```bash
# Banner grabbing
python3 python/exploits/banner_grabber.py --target 10.0.13.12 --port 2121

# vsftpd exploit (doar în lab controlat!)
python3 python/exploits/ftp_backdoor_vsftpd.py --target 10.0.13.12 --ftp-port 2121
```

### Mininet
```bash
# Pornire topologie
sudo python3 mininet/topologies/topo_base.py --cli

# În CLI mininet
mininet> pingall
mininet> h1 ping h2
mininet> xterm h1
mininet> exit
```

### Curățare
```bash
./scripts/cleanup.sh            # Curățare completă
make clean                      # Curățare fișiere temporare
sudo mn -c                      # Reset Mininet
docker-compose down -v          # Oprire + ștergere volume
```

## Structură directoare

```
artifacts/              # Output-uri demo (demo.log, demo.pcap, validation.txt)
configs/mosquitto/      # Configurări MQTT (plain, TLS, ACL)
docs/                   # Documentație și slides
mininet/topologies/     # Topologii Mininet (canonical)
python/exercises/       # Exerciții principale
python/exploits/        # Demonstrații vulnerabilități
python/utils/           # Utilitare comune
scripts/                # Automatizări (setup, run_all, cleanup)
tests/                  # Smoke tests
```

## Troubleshooting rapid

| Problemă | Soluție |
|----------|---------|
| `Permission denied` Docker | `sudo usermod -aG docker $USER && newgrp docker` |
| Port ocupat | `sudo lsof -i :<PORT>` și oprește procesul |
| Mininet stale | `sudo mn -c` |
| Module Python lipsă | `pip3 install -r requirements.txt --break-system-packages` |
| tcpdump nu funcționează | Verifică permisiuni: `sudo tcpdump -i any` |
