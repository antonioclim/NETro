# Exemplu complet: TCP Tunnel

Pas cu pas. Focus pe DE CE 2 thread-uri.

---

## Ce vrem să facem

Clientul se conectează la tunnel. Tunnel-ul retransmite la server. Serverul nu știe de client.

```
[Client h1] ──► [Tunnel h2:9090] ──► [Server h3:8080]
```

E ca un recepționer: suni la numărul principal, el te pune în legătură.

---

## De ce 2 thread-uri?

Hai să vedem ce nu merge cu un singur thread.

```python
# ÎNCERCARE NAIVĂ (nu funcționează bine)
while True:
    data = client.recv(1024)  # STAU AICI până clientul trimite
    server.sendall(data)
    response = server.recv(1024)  # Dacă serverul a trimis ÎNTRE TIMP?
    client.sendall(response)
```

Problema: recv() e BLOCANT. Când aștepți de la client, nu poți primi de la server.

**Scenariul dezastru:**
1. Clientul se conectează
2. Serverul trimite "Welcome!"
3. Noi stăm la client.recv() — nu vedem mesajul serverului
4. Clientul așteaptă welcome-ul care nu vine...
5. Deadlock.

**Soluția:** Două thread-uri. Unul ascultă de la client, altul de la server. Rulează simultan.

---

## Funcția forward

```python
import threading

def forward(src, dst, label):
    """
    Citește de la src, trimite la dst.
    Rulează într-un thread separat.
    """
    try:
        while True:
            data = src.recv(4096)
            
            # b'' înseamnă că cealaltă parte a închis
            if not data:
                print(f"[{label}] Conexiune închisă")
                break
            
            # sendall garantează că trimite TOT
            # send() poate trimite parțial
            dst.sendall(data)
            print(f"[{label}] {len(data)} bytes")
            
    except Exception as e:
        print(f"[{label}] Eroare: {e}")
        
    finally:
        # Închidem ambele — asta va opri și celălalt thread
        src.close()
        dst.close()
```

---

## Server-ul tunnel

```python
import socket
import threading

def forward(src, dst, label):
    # ... codul de mai sus ...
    pass

def main():
    # Socket TCP server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', 9090))
    server.listen(5)
    
    print("Tunnel: :9090 → 10.0.3.3:8080")
    
    while True:
        # Aștept client
        client, addr = server.accept()
        print(f"Client: {addr}")
        
        # Mă conectez la destinație
        target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target.connect(('10.0.3.3', 8080))
        
        # Pornesc 2 thread-uri
        t1 = threading.Thread(target=forward, args=(client, target, "C→S"))
        t2 = threading.Thread(target=forward, args=(target, client, "S→C"))
        t1.start()
        t2.start()
        
        # NU fac join() aici — altfel n-aș putea accepta alți clienți

if __name__ == "__main__":
    main()
```

---

## Diagrama

```
┌─────────────────────────────────────────────────────┐
│                    TUNNEL                           │
│                                                     │
│   accept() ──► client socket                        │
│                     │                               │
│   connect() ──► target socket                       │
│                     │                               │
│        ┌────────────┼────────────┐                  │
│        │                         │                  │
│   Thread 1                  Thread 2                │
│   client.recv()             target.recv()           │
│        │                         │                  │
│        ▼                         ▼                  │
│   target.sendall()          client.sendall()        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Test

Terminal h3 — server echo:
```bash
nc -l -p 8080 -k
```

Terminal h2 — tunnel:
```bash
python3 tunnel.py
```

Terminal h1 — client:
```bash
nc 10.0.3.2 9090
# Scrie ceva, primești echo
```

---

## Ce IP vede serverul?

Serverul vede IP-ul TUNNEL-ULUI, nu al clientului.

De ce? Tunnel-ul face o nouă conexiune TCP. Din perspectiva serverului, "clientul" e tunnel-ul.

Implicații:
- Logging-ul pe server arată IP greșit
- Rate limiting per-IP nu merge
- Trebuie mecanisme speciale (X-Forwarded-For header)

---

## Greșeli frecvente

**Greșeala 1:** Un singur thread
```python
# Blocat dacă server trimite primul
while True:
    data = client.recv()
    server.send(data)
```

**Greșeala 2:** send() în loc de sendall()
```python
server.send(data)  # Poate trimite parțial!
server.sendall(data)  # Garantează tot
```

**Greșeala 3:** Nu închid ambele socket-uri
```python
# Doar src.close() — celălalt thread rămâne blocat
# Trebuie: src.close() ȘI dst.close()
```

---

## Verifică că ai înțeles

De ce un thread nu e suficient?

□ A) Python nu permite
□ B) recv() blochează și nu poți asculta în două locuri
□ C) TCP e half-duplex
□ D) Performanță

Răspuns: ___

<details>
<summary>Verificare</summary>
B — recv() e blocant. Nu poți asculta de la client ȘI de la server simultan cu un thread.
</details>
