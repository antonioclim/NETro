# Seminar 11: Load Balancing și Reverse Proxy

## Prezentare Generală

**Săptămâna**: 11 din 14  
**Durata**: 2 ore seminar  
**Tema fișei disciplinei**: Aplicații distribuite cu Nginx, load balancing, reverse proxy pentru containere Docker Compose

---

## 1. Ce Vom Învăța

Arhitecturi distribuite în practică:
- **Reverse Proxy** – intermediar între clienți și servere backend
- **Load Balancing** – distribuirea încărcării între multiple instanțe
- **Docker Compose** – orchestrarea containerelor pentru dezvoltare și testare
- **Nginx** – soluție industrială pentru proxy și load balancing

## 2. De Ce Contează

Aplicațiile moderne rulează pe multiple servere pentru:
- **Scalabilitate** – gestionarea traficului crescut
- **Disponibilitate** – funcționare continuă chiar dacă un server cade
- **Performanță** – distribuirea optimă a resurselor

---

## 3. Concepte Fundamentale

### 3.1 Reverse Proxy

**Definiție**: Un server intermediar care primește cererile de la clienți și le redirecționează către serverele backend.

```
┌──────────┐         ┌──────────────┐         ┌──────────┐
│  Client  │ ──────► │ Reverse Proxy│ ──────► │ Backend  │
│          │ ◄────── │   (Nginx)    │ ◄────── │ Servers  │
└──────────┘         └──────────────┘         └──────────┘
```

**Avantaje**:
- Ascunde structura internă a infrastructurii
- Termină conexiunile TLS (SSL offloading)
- Cache pentru conținut static
- Compresie (gzip/brotli)
- Rate limiting și protecție DDoS

### 3.2 Load Balancing

**Definiție**: Tehnica de distribuire a cererilor între mai multe servere pentru a optimiza utilizarea resurselor.

```
                                    ┌─────────┐
                              ┌────►│Backend 1│
                              │     └─────────┘
┌────────┐    ┌────────────┐  │     ┌─────────┐
│ Client │───►│Load Balancer├─┼────►│Backend 2│
└────────┘    └────────────┘  │     └─────────┘
                              │     ┌─────────┐
                              └────►│Backend 3│
                                    └─────────┘
```

### 3.3 Algoritmi de Load Balancing

| Algoritm | Descriere | Utilizare |
|----------|-----------|-----------|
| **Round Robin** | Rotație circulară: 1→2→3→1→... | Backend-uri identice |
| **Weighted Round Robin** | Rotație cu ponderi (2:1:1) | Servere cu capacități diferite |
| **Least Connections** | Alege serverul cu cele mai puține conexiuni active | Cereri cu durată variabilă |
| **IP Hash** | Hash al IP-ului client → același server | Sticky sessions, state local |
| **Random** | Alegere aleatoare | Simplitate, bună distribuție statistică |
| **Least Time** | Combină conexiuni active + timp răspuns | Performanță optimă (Nginx Plus) |

### 3.4 Health Checks și Failover

**Passive Health Check**:
- Monitorizează răspunsurile backend-urilor
- Marchează un server ca "down" după N eșecuri consecutive
- Reîncearcă după un timeout

**Active Health Check** (Nginx Plus):
- Trimite cereri periodice de verificare
- Detectează probleme înainte de a afecta utilizatorii

```nginx
upstream backend_pool {
    server backend1:80 max_fails=3 fail_timeout=30s;
    server backend2:80 max_fails=3 fail_timeout=30s;
    server backend3:80 backup;  # folosit doar când ceilalți sunt down
}
```

---

## 4. Demo: Load Balancer în Python

### 4.1 Arhitectura Demo-ului

Vom construi un load balancer Python didactic pentru a înțelege mecanismele interne.

**Fișiere relevante**:
- `python/exercises/ex_11_01_backend.py` – server HTTP simplu
- `python/exercises/ex_11_02_loadbalancer.py` – load balancer

### 4.2 Backend HTTP Simplu

```python
# Structura răspunsului
f"Backend {self.id} | Host: {hostname} | Time: {timestamp} | Request #{count}"
```

**Pornire 3 backend-uri**:
```bash
python3 ex_11_01_backend.py --id 1 --port 8081 &
python3 ex_11_01_backend.py --id 2 --port 8082 --delay 0.1 &
python3 ex_11_01_backend.py --id 3 --port 8083 --delay 0.2 &
```

### 4.3 Load Balancer Python

**Caracteristici implementate**:
- Algoritmi: round_robin, least_conn, ip_hash
- Failover pasiv cu max_fails și fail_timeout
- Thread-safe pentru cereri concurente
- Generator de încărcare integrat

**Pornire**:
```bash
python3 ex_11_02_loadbalancer.py \
    --backends localhost:8081,localhost:8082,localhost:8083 \
    --port 8080 \
    --algorithm round_robin
```

### 4.4 Testare

```bash
# Round Robin
for i in {1..6}; do curl -s http://localhost:8080/; echo; done
# Output: Backend 1, 2, 3, 1, 2, 3

# IP Hash (sticky sessions)
for i in {1..5}; do curl -s http://localhost:8080/; echo; done
# Output: Backend X, X, X, X, X (același pentru toate cererile de la același IP)
```

---

## 5. Demo: Nginx Load Balancer (Docker)

### 5.1 Structura Docker Compose

```yaml
# docker/nginx_compose/docker-compose.yml
services:
  lb:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - web1
      - web2
      - web3

  web1:
    image: nginx:alpine
    volumes:
      - ./web1/index.html:/usr/share/nginx/html/index.html:ro

  web2:
    image: nginx:alpine
    volumes:
      - ./web2/index.html:/usr/share/nginx/html/index.html:ro

  web3:
    image: nginx:alpine
    volumes:
      - ./web3/index.html:/usr/share/nginx/html/index.html:ro
```

### 5.2 Configurație Nginx

```nginx
# docker/nginx_compose/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend_pool {
        # Algoritm implicit: round_robin
        # least_conn;  # Decomentează pentru least connections
        # ip_hash;     # Decomentează pentru sticky sessions
        
        server web1:80 weight=1;
        server web2:80 weight=1;
        server web3:80 weight=1;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backend_pool;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

### 5.3 Rulare Demo

```bash
cd docker/nginx_compose
docker compose up -d
# Testare
for i in {1..6}; do curl -s http://localhost/; done
# Oprire
docker compose down
```

---

## 6. Comparație: Python LB vs. Nginx

| Aspect | Python LB | Nginx |
|--------|-----------|-------|
| **Performanță** | ~500-1000 req/s | ~50,000+ req/s |
| **Overhead** | Mai mare (interpretare) | Minim (C optimizat) |
| **Configurabilitate** | Cod Python (flexibil) | Fișier config declarativ |
| **Ecosistem** | Didactic, experimentare | Producție, CDN, cache |
| **Health checks** | Pasive (implementare manuală) | Active + pasive (Nginx Plus) |
| **TLS termination** | Posibil cu ssl module | Nativ, optimizat |

> **Notă personală**: În producție folosesc mereu Nginx sau HAProxy. Python LB e util doar pentru a înțelege ce face Nginx "sub capotă". Nu pune LB în Python în producție — serios, am văzut dezastre. E ca și cum ai folosi o bicicletă ca să transporți marfă în loc de camion.

---

## 7. Debugging și Troubleshooting

### 7.1 Verificare Conectivitate

```bash
# Testare backend individual
curl -v http://localhost:8081/

# Verificare porturi deschise
ss -tlnp | grep -E "8080|8081|8082|8083"

# Log-uri Docker
docker compose logs -f lb
```

### 7.2 Captură Trafic

```bash
# Trafic HTTP către load balancer
sudo tshark -i lo -f "tcp port 8080" -Y "http"

# Trafic între LB și backend-uri
sudo tshark -i lo -f "tcp port 8081 or tcp port 8082 or tcp port 8083"
```

### 7.3 Probleme Comune

| Problemă | Cauză | Soluție |
|----------|-------|---------|
| "Connection refused" | Backend oprit | Verifică `ps aux | grep backend` |
| Toate cererile la un backend | IP hash cu un singur client | Testează de la IP-uri diferite |
| Timeout-uri | Backend lent | Crește `proxy_read_timeout` |
| 502 Bad Gateway | Backend indisponibil | Verifică health checks |

---

## 8. Exerciții Practice

### Exercițiul 1: Round Robin Manual
Pornește 3 backend-uri, pornește LB cu round_robin, trimite 9 cereri și verifică distribuția uniformă.

### Exercițiul 2: Simulare Failover
Cu LB în funcțiune, oprește un backend (Ctrl+C) și observă cum traficul se redistribuie.

### Exercițiul 3: Weighted Load Balancing
Modifică nginx.conf pentru `weight=3` la web1 și testează distribuția (3:1:1).

### Exercițiul 4: Sticky Sessions
Configurează `ip_hash` în Nginx și verifică că cererile de la același IP merg la același backend.

### Exercițiul 5: Benchmark
Compară performanța LB Python vs. Nginx folosind Apache Bench:
```bash
ab -n 1000 -c 10 http://localhost:8080/  # Python LB
ab -n 1000 -c 10 http://localhost:80/    # Nginx
```

### Exercițiul 6 (Challenge): Custom Algorithm
Implementează un algoritm de load balancing bazat pe response time în `ex_11_02_loadbalancer.py`.

---

## 9. Rezultate Așteptate

După parcurgerea seminarului, ar trebui să poți:
- Configura Nginx ca reverse proxy și load balancer
- Explica diferențele între algoritmii de load balancing
- Diagnostica probleme de conectivitate în sisteme distribuite
- Dockeriza aplicații multi-container cu Docker Compose

---

## 10. Contribuție la Proiectul de Echipă

**Artefact săptămânal**: Adaugă în proiect:
1. `docker-compose.yml` cu load balancer Nginx și cel puțin 2 backend-uri
2. `nginx.conf` cu upstream configurat
3. Script de health check (`scripts/health_check.sh`)
4. Diagramă arhitectură în README

---

## 11. Bibliografie

| Referință | DOI/Link |
|-----------|----------|
| J. Kurose, K. Ross - Computer Networking, 8th Ed. | ISBN: 978-0135928615 |
| B. Rhodes, J. Goetzen - Foundations of Python Network Programming | DOI: 10.1007/978-1-4302-5855-1 |

**Resurse online**:
- [Nginx Load Balancing Documentation](https://nginx.org/en/docs/http/load_balancing.html)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

*Document generat pentru Seminarul 11 – Rețele de Calculatoare*  
*Revolvix&Hypotheticalandrei*
