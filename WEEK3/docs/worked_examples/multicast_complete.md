# Exemplu complet: UDP Multicast

Pas cu pas. ATENȚIE la ordinea operațiilor — aici greșesc cei mai mulți.

---

## Ce vrem să facem

Trimitem mesaje la un GRUP. Doar cine s-a înscris în grup primește.

```
h1 (sender) ──► [grup 224.1.1.1] ──► h2 (membru)
                                  ╳  h3 (nu e membru, nu primește)
```

---

## Receiver cu JOIN (pe h2)

```python
import socket
import struct

GRUP = '224.1.1.1'
PORT = 5302

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# ═══════════════════════════════════════════════════
# ORDINEA CONTEAZĂ! bind() ÎNAINTE de JOIN
# ═══════════════════════════════════════════════════

# 1. ÎNTÂI bind
sock.bind(('', PORT))

# 2. APOI JOIN
# Creez structura pentru IP_ADD_MEMBERSHIP
# "4s" = 4 bytes pentru IP-ul grupului
# "l" = long pentru interfață (INADDR_ANY = orice)
mreq = struct.pack("4sl", socket.inet_aton(GRUP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"Sunt în grupul {GRUP}, aștept pe :{PORT}")

while True:
    data, addr = sock.recvfrom(1024)
    print(f"De la {addr[0]}: {data.decode()}")
```

**De ce bind înainte de JOIN?**

Când faci JOIN, kernel-ul trebuie să știe UNDE să livreze pachetele pentru grupul respectiv. Dacă n-ai făcut bind, nu știe.

E ca și cum te-ai înscrie la o revistă dar n-ai dat adresa de livrare.

---

## Sender (pe h1)

```python
import socket

GRUP = '224.1.1.1'
PORT = 5302

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# TTL = câte hop-uri poate face pachetul
# 1 = rămâne în rețeaua locală
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

# Trimit la grup (nu la un IP specific!)
sock.sendto(b"Mesaj pentru grup", (GRUP, PORT))
print("Trimis!")
```

**Sender-ul NU face JOIN!**

JOIN e doar pentru a PRIMI. Ca la WhatsApp: poți trimite într-un grup fără să fii membru (nu chiar, dar ideea e că trimiterea și primirea sunt separate).

---

## Ce se întâmplă în spatele scenei

```
1. h2 face JOIN
   → Trimite IGMP Membership Report
   → Switch-ul notează: "portul 2 vrea 224.1.1.1"
   
2. h1 trimite la 224.1.1.1
   → Switch-ul verifică cine vrea grupul
   → Trimite DOAR la h2
   
3. h3 nu e membru
   → Nu primește nimic
   → Chiar dacă ascultă pe același port!
```

---

## Diferența față de broadcast

| | Broadcast | Multicast |
|---|---|---|
| Cine primește | TOȚI din subnet | Doar cu JOIN |
| Opțiune sender | SO_BROADCAST | IP_MULTICAST_TTL |
| Opțiune receiver | - | IP_ADD_MEMBERSHIP |
| Trece de router | Nu | Da (dacă TTL > 1) |

---

## Greșeli frecvente

**Greșeala 1:** JOIN înainte de bind
```python
# GREȘIT — poate pierde pachete
sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
sock.bind(('', PORT))

# CORECT
sock.bind(('', PORT))
sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
```

**Greșeala 2:** Cred că portul e suficient
```
"Am bind pe 5302, de ce nu primesc?"
→ Pentru că nu ai făcut JOIN la grup
```

**Greșeala 3:** TTL = 0 pe sender
```python
sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 0)
# Pachetul nu părăsește mașina!
```

---

## Verificare IGMP

Poți vedea join-ul:
```bash
ip maddr show
# sau
sudo tshark -i any -f "igmp"
```

---

## Verifică că ai înțeles

Care e ordinea corectă?

□ A) socket → JOIN → bind → recv
□ B) socket → bind → JOIN → recv

Răspuns: ___

<details>
<summary>Verificare</summary>
B — bind() ÎNAINTE de JOIN
</details>
