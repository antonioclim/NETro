# Seminar 13 — Securitate în Rețele: Scanare și Testare

## Obiective Operaționale

1. Configurarea mediului de testare izolat
2. Implementarea unui scanner de porturi TCP
3. Identificarea serviciilor prin banner grabbing
4. Analiza traficului MQTT cu tshark
5. Demonstrarea unui exploit controlat

## Faza 1: Setup (15 min)

```bash
cd starterkit_s13
make setup
make docker-up
make verify
```

## Faza 2: Scanare Porturi (25 min)

### Cod Python — Scanner TCP

```python
import socket
from concurrent.futures import ThreadPoolExecutor

def scan_port(target, port, timeout=1.0):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target, port))
        sock.close()
        return port, "OPEN" if result == 0 else "CLOSED"
    except:
        return port, "FILTERED"
```

### Interpretare Rezultate

- **OPEN**: Serviciu activ, posibil vulnerabil
- **CLOSED**: Niciun serviciu (RST received)
- **FILTERED**: Firewall blochează (timeout)

## Faza 3: Demo MQTT (25 min)

### Publisher (Terminal 1)

```bash
mosquitto_pub -h localhost -t "iot/temp" -m '{"value": 23.5}'
```

### Subscriber (Terminal 2)

```bash
mosquitto_sub -h localhost -t "iot/#" -v
```

## Faza 4: Captură Trafic (20 min)

```bash
# Captură MQTT
sudo tshark -i any -f "port 1883" -Y mqtt

# Filtre utile
mqtt.topic contains "sensor"
mqtt.msgtype == 3  # PUBLISH only
```

## Exerciții

1. Scanați toate porturile 1-1000 pe localhost
2. Configurați QoS 1 pentru MQTT și observați diferențele
3. Capturați și analizați handshake-ul TLS pe port 8883

---
*Revolvix&Hypotheticalandrei | ASE-CSIE*
