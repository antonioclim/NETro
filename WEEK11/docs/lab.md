# Laborator 11: FTP, DNS, SSH + Load Balancing

## Prezentare Generală

**Săptămâna**: 11 din 14  
**Durata**: 2-3 ore laborator practic  
**Obiectiv**: Experimentare hands-on cu protocoale de aplicație și load balancing

---

## Structura Laboratorului

| Pas | Activitate | Durată Est. |
|-----|------------|-------------|
| 0 | Pregătire mediu | 10 min |
| 1 | Verificare sistem | 5 min |
| 2 | Backend HTTP | 10 min |
| 3 | Load Balancer Python | 20 min |
| 4 | Nginx Docker | 15 min |
| 5 | DNS Client manual | 15 min |
| 6 | FTP Activ/Pasiv | 15 min |
| 7 | Mininet Topology | 20 min |
| 8 | Captură trafic | 10 min |
| 9 | Benchmarking | 10 min |
| 10 | Curățare | 5 min |

---

## Pas 0: Pregătirea Mediului

### Cerințe
- Ubuntu 22.04+ (VM sau nativ)
- Python 3.10+
- Docker + Docker Compose v2
- Mininet 2.3+
- tshark/Wireshark

### Instalare rapidă

```bash
cd starterkit
make setup
```

### Verificare

```bash
make verify
```

**Output așteptat**: Toate verificările să treacă (✓).

---

## Pas 1: Verificare Sistem

Rulează scriptul de verificare pentru a confirma că totul este pregătit:

```bash
./scripts/verify.sh --smoke
```

Verifică manual:
```bash
python3 --version       # >= 3.10
docker --version        # >= 24.0
docker compose version  # v2.x
mn --version            # 2.3.x
tshark --version        # 4.x
```

---

## Pas 2: Pornire Backend-uri HTTP

### Manual (3 terminale)

**Terminal 1:**
```bash
python3 python/exercises/ex_11_01_backend.py --id 1 --port 8081
```

**Terminal 2:**
```bash
python3 python/exercises/ex_11_01_backend.py --id 2 --port 8082 --delay 0.1
```

**Terminal 3:**
```bash
python3 python/exercises/ex_11_01_backend.py --id 3 --port 8083 --delay 0.2
```

### Automat (Makefile)

```bash
make backends-start
```

### Testare

```bash
curl http://localhost:8081/
curl http://localhost:8082/
curl http://localhost:8083/
```

**Output așteptat**: Fiecare backend răspunde cu ID-ul său.

> ⚡ **Truc**: Dacă nu vezi răspunsuri diferite, verifică că ai pornit toate 3 backend-urile. E o greșeală frecventă — am văzut studenți debug-uind 20 de minute când de fapt uitaseră să pornească un terminal.

---

## Pas 3: Load Balancer Python

### Pornire LB

```bash
python3 python/exercises/ex_11_02_loadbalancer.py \
    --backends localhost:8081,localhost:8082,localhost:8083 \
    --port 8080 \
    --algorithm round_robin
```

### Test Round Robin

> 🤔 **PREDICȚIE (scrie înainte de a rula)**:
> Vei trimite 6 cereri prin LB cu round_robin. În ce ordine vor răspunde backend-urile?
> 
> Notează predicția ta: ___ ___ ___ ___ ___ ___
> 
> Rulează acum și compară:

```bash
for i in {1..6}; do curl -s http://localhost:8080/; echo; done
```

**Output așteptat**: Backend 1, 2, 3, 1, 2, 3 (rotație).

### Test IP Hash

Oprește LB (Ctrl+C), repornește cu:
```bash
python3 python/exercises/ex_11_02_loadbalancer.py \
    --backends localhost:8081,localhost:8082,localhost:8083 \
    --port 8080 \
    --algorithm ip_hash
```

> 🤔 **PREDICȚIE**:
> Cu ip_hash, toate cererile vin de la localhost (127.0.0.1).
> La ce backend crezi că vor ajunge toate cele 5 cereri?
> 
> Predicție: Backend ___ (1, 2, sau 3)
>
> Rulează și verifică:

```bash
for i in {1..5}; do curl -s http://localhost:8080/; echo; done
```

**Output așteptat**: Același backend pentru toate cererile.

### Simulare Failover

> 🤔 **PREDICȚIE**:
> Trimiți 6 cereri cu round_robin, dar Backend 2 e oprit. Ce crezi că se întâmplă?
> - [ ] Toate cererile eșuează
> - [ ] Doar cererile către Backend 2 eșuează, restul merg
> - [ ] LB detectează și redistribuie automat după prima eroare
> - [ ] Primești eroare 502 Bad Gateway pentru fiecare cerere
>
> Rulează și observă comportamentul:

Cu LB în round_robin, oprește Backend 2 (Ctrl+C în terminalul său):
```bash
for i in {1..6}; do curl -s http://localhost:8080/ 2>/dev/null || echo "EROARE"; done
```

**Output așteptat**: Prima cerere către Backend 2 eșuează, apoi LB îl exclude.

---

## Pas 4: Nginx Load Balancer (Docker)

### Pornire stack

```bash
make demo-nginx
# sau
cd docker/nginx_compose && docker compose up -d
```

### Testare

```bash
for i in {1..6}; do curl -s http://localhost:80/; done
```

**Output așteptat**: Răspunsuri de la web1, web2, web3 în rotație.

### Schimbare algoritm

Editează `docker/nginx_compose/nginx.conf`:
```nginx
upstream backend_pool {
    least_conn;  # Decomentează această linie
    server web1:80;
    server web2:80;
    server web3:80;
}
```

Reload Nginx:
```bash
docker compose -f docker/nginx_compose/docker-compose.yml exec lb nginx -s reload
```

### Oprire

```bash
make demo-nginx-stop
```

---

## Pas 5: Client DNS Manual

> 🤔 **PREDICȚIE**:
> Interogarea DNS pentru `google.com` tip A va returna:
> - [ ] Exact 1 IP (Google are un singur server, nu?)
> - [ ] Multiple IP-uri — câte crezi? ___
> - [ ] Eroare (de ce? _________________________)
>
> Rulează și compară:

### Interogare A Record

```bash
python3 python/exercises/ex_11_03_dns_client.py --query google.com --type A --verbose
```

**Output așteptat**: Hexdump pachet trimis + răspuns cu IP-ul/IP-urile Google.

### Alte tipuri de înregistrări

```bash
python3 python/exercises/ex_11_03_dns_client.py --query google.com --type MX
python3 python/exercises/ex_11_03_dns_client.py --query google.com --type TXT
python3 python/exercises/ex_11_03_dns_client.py --query ase.ro --type NS
```

### Comparație cu dig

```bash
dig google.com A +short
dig google.com MX +short
```

---

## Pas 6: FTP Activ vs. Pasiv

> 🤔 **PREDICȚIE**:
> Ești în spatele unui router NAT casnic și încerci FTP către un server public.
> Care mod va funcționa — activ sau pasiv? De ce?
>
> Predicție: _______________ pentru că _______________

### Mod Pasiv (recomandat)

```bash
python3 python/exercises/ex_11_04_ftp_client.py \
    --host ftp.gnu.org \
    --mode passive \
    --command "LIST /"
```

**Output așteptat**: Listing director, cu detalierea conexiunii pasive.

### Mod Activ

```bash
python3 python/exercises/ex_11_04_ftp_client.py \
    --host ftp.gnu.org \
    --mode active \
    --command "LIST /"
```

**Output așteptat**: Probabil timeout (firewall blochează conexiunea incoming).

### Captură FTP

În alt terminal:
```bash
sudo tshark -i any -f "port 21" -Y ftp -c 20
```

Apoi rulează clientul FTP și observă comenzile și răspunsurile.

---

## Pas 7: Mininet Topology

### Pornire demo

```bash
sudo make demo-mininet
# sau
sudo python3 mininet/topologies/topo_11_base.py
```

**Output așteptat**: Topologie creată, backend-uri pornite, test load balancing, simulare failover.

### Mod interactiv

```bash
sudo python3 mininet/topologies/topo_11_base.py --interactive
```

Comenzi în CLI Mininet:
```
mininet> h1 ping -c 3 lb
mininet> h1 curl -s http://10.0.0.1:8080/
mininet> net
mininet> exit
```

---

## Pas 8: Captură Trafic

### Captură HTTP

**Terminal 1 (captură)**:
```bash
sudo tshark -i lo -f "tcp port 8080 or tcp port 8081" -w /tmp/lb.pcap
```

**Terminal 2 (trafic)**:
```bash
for i in {1..10}; do curl -s http://localhost:8080/; done
```

Oprește captura (Ctrl+C) și analizează:
```bash
tshark -r /tmp/lb.pcap -Y "http" -T fields -e ip.src -e ip.dst -e http.request.uri
```

### Script automat

```bash
make capture
```

---

## Pas 9: Benchmarking

### Apache Bench

```bash
ab -n 1000 -c 10 http://localhost:8080/
```

**Metrici de observat**:
- Requests per second
- Time per request (mean)
- Percentile latencies (50%, 95%, 99%)

### Generator integrat

```bash
python3 python/exercises/ex_11_02_loadbalancer.py \
    --backends localhost:8081,localhost:8082,localhost:8083 \
    --load-test --requests 500 --workers 20
```

### Comparație algoritmi

```bash
# Test round_robin
make lb-start-rr && make benchmark && make lb-stop

# Test least_conn
make lb-start-lc && make benchmark && make lb-stop
```

---

## Pas 10: Curățare

```bash
make clean
```

Verifică că nu au rămas procese:
```bash
ps aux | grep -E "backend|loadbalancer" | grep -v grep
docker ps
```

---

## Rezultate Așteptate

| Pas | Ce ar trebui să observi |
|-----|-------------------------|
| 2 | 3 backend-uri răspund pe porturi diferite |
| 3 | Round robin distribuie uniform; IP hash menține sticky sessions |
| 4 | Nginx funcționează similar cu LB Python, dar mai rapid |
| 5 | Construcție manuală pachete DNS, răspunsuri decodificate |
| 6 | Pasiv funcționează, activ eșuează în majoritatea configurațiilor |
| 7 | Topologie virtuală completă în Mininet |
| 8 | Trafic vizibil în tshark, analizabil |
| 9 | Python LB: ~500 req/s; Nginx: ~10,000+ req/s |

---

## Troubleshooting

### Port ocupat

```bash
sudo lsof -i :8080
sudo kill <PID>
```

### Docker permission denied

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Mininet requires root

```bash
sudo mn -c  # Curăță procese vechi
sudo python3 <script>.py
```

---

## Notare

Laboratorul contribuie la nota de seminar conform rubricii din `docs/rubrici.md`.

---

*Document generat pentru Laboratorul 11 – Rețele de Calculatoare*  
*Revolvix&Hypotheticalandrei*
