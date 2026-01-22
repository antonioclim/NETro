# Docker Setup pentru Rețele de Calculatoare - Săptămâna 14

## Prezentare generală

Acest folder conține configurația Docker pentru rularea demonstrațiilor și exercițiilor.

**IMPORTANT**: Docker este o **ALTERNATIVĂ** la Mininet, nu un înlocuitor complet. Folosește:
- **Mininet** pentru: simulare layer 2/3, switch-uri, rutare, topologii complexe
- **Docker** pentru: testare rapidă aplicații, development, demo-uri simple

## Când să folosești Docker vs Mininet

| Criteriu | Docker | Mininet |
|----------|--------|---------|
| Instalare | Simplă, cross-platform | Doar Linux |
| Startup | ~10 secunde | ~5 secunde |
| Layer 2 (MAC, ARP) | Limitat | Complet |
| Rutare custom | Limitată | Completă |
| Captură pachete | Da (tcpdump) | Da (tcpdump, Wireshark) |
| Performanță | Overhead container | Performanță nativă |
| Reproducibilitate | Excelentă | Bună |

## Cerințe

- Docker Engine 20.10+
- Docker Compose 2.0+
- ~2GB spațiu disk
- ~1GB RAM

## Structura

```
docker/
├── Dockerfile          # Imagine de bază pentru toate serviciile
├── docker-compose.yml  # Orchestrare multi-container
└── README.md           # Acest fișier
```

## Utilizare rapidă

### 1. Build imagine

```bash
cd docker/
docker build -t networking-lab:s14 ..
```

### 2. Pornire infrastructură completă

```bash
docker-compose up -d
```

Aceasta pornește:
- 2 backend servers (app1, app2)
- 1 load balancer (lb)
- 1 client interactiv
- 1 TCP echo server

### 3. Verificare status

```bash
docker-compose ps
docker-compose logs -f
```

### 4. Acces în container client

```bash
docker-compose exec client bash
```

### 5. Teste din container client

```bash
# Test HTTP prin load balancer
curl http://172.21.0.10:8080/
curl http://172.21.0.10:8080/health
curl http://172.21.0.10:8080/lb-status

# Test TCP echo
python3 /app/python/apps/tcp_echo_client.py --host 172.20.0.20 --port 9000

# Captură trafic
tcpdump -i any -w /app/artifacts/capture.pcap &
curl http://172.21.0.10:8080/
kill %1
```

### 6. Teste de pe host

```bash
# Porturile sunt expuse: 8080 (LB), 9000 (echo)
curl http://localhost:8080/
curl http://localhost:8080/lb-status
```

### 7. Oprire

```bash
docker-compose down
# Sau cu ștergere volume-uri
docker-compose down -v
```

## Topologia rețelei

```
                     HOST
                       │
                       │ port mapping
                       │ 8080, 9000
                       ▼
    frontend_net (172.21.0.0/24)
    ┌─────────────────────────────────────┐
    │                                     │
    │  client                  lb         │
    │  172.21.0.2              172.21.0.10│
    │                          │          │
    └──────────────────────────┼──────────┘
                               │
    backend_net (172.20.0.0/24)│
    ┌──────────────────────────┼──────────┐
    │                          │          │
    │  app1         app2       lb    echo │
    │  172.20.0.2   172.20.0.3      172.20.0.20
    │  :8001        :8001           :9000 │
    │                                     │
    └─────────────────────────────────────┘
```

## Debugging

### Verificare logs per serviciu

```bash
docker-compose logs app1
docker-compose logs app2
docker-compose logs lb
```

### Inspecție rețea

```bash
docker network inspect docker_backend_net
docker network inspect docker_frontend_net
```

### Acces în orice container

```bash
docker-compose exec app1 bash
docker-compose exec lb bash
```

### Test conectivitate din lb

```bash
docker-compose exec lb bash
ping 172.20.0.2   # app1
ping 172.20.0.3   # app2
curl http://172.20.0.2:8001/health
```

## Modificări frecvente

### Adăugare backend server nou

În `docker-compose.yml`, adaugă:

```yaml
  app3:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: netlab-app3
    hostname: app3
    command: python3 /app/python/apps/backend_server.py --port 8001 --id app3
    networks:
      backend_net:
        ipv4_address: 172.20.0.4
```

Și modifică load balancer-ul:
```yaml
  lb:
    command: >
      python3 /app/python/apps/lb_proxy.py
      --listen-port 8080
      --backends 172.20.0.2:8001,172.20.0.3:8001,172.20.0.4:8001
```

### Rebuild după modificări cod

```bash
docker-compose build
docker-compose up -d
```

## Limitări

1. **Nu simulează layer 2 complet** - ARP, broadcast, switching sunt simplificate
2. **Nu suportă rutare custom** - routing între subnets este automat
3. **Nu poți controla delay/bandwidth** - ca în Mininet cu `tc`
4. **tcpdump vede trafic agregat** - nu per-interfață ca în Mininet

## Exerciții recomandate cu Docker

1. **Load balancing verification**: Trimite 100 cereri și verifică distribuția
2. **Health check behavior**: Oprește un backend și observă redistribuirea
3. **Latency measurement**: Măsoară RTT client → lb → backend
4. **Capture analysis**: Capturează trafic și analizează cu tshark

## Resurse

- [Docker Networking Guide](https://docs.docker.com/network/)
- [Docker Compose Networking](https://docs.docker.com/compose/networking/)
- [Mininet vs Docker](https://mininet.org/)

---
*Revolvix&Hypotheticalandrei*
