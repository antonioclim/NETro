# Hartă conceptuală — WEEK3

Completează pe măsură ce avansezi. Ajută la recapitulare.

---

## Structura principală

```
                    SOCKET
                       │
            ┌──────────┴──────────┐
            │                     │
           TCP                   UDP
      SOCK_STREAM            SOCK_DGRAM
            │                     │
            │              ┌──────┼──────┐
            │              │      │      │
         stream        unicast  bcast  mcast
         de bytes       1:1    1:ALL  1:GRUP
```

Completează ce lipsește în tabel:

| Tip | Adresă exemplu | Opțiune sender | Opțiune receiver |
|-----|----------------|----------------|------------------|
| Unicast | 10.0.3.2 | - | - |
| Broadcast | ___________ | ___________ | - |
| Multicast | ___________ | ___________ | ___________ |

---

## Relații cauză-efect

Completează:

Fără SO_BROADCAST → _______________

bind() DUPĂ JOIN → _______________

TTL = 0 pe multicast → _______________

Un thread la tunnel → _______________

---

## Analogii

Conectează:

```
Socket           •          • Grup WhatsApp
Broadcast        •          • Telefon
Multicast        •          • Megafon în sală
TCP Tunnel       •          • Recepționer
```

---

## Ordinea operațiilor

Numerotează corect pentru multicast receiver:

___ recv()
___ socket()
___ bind()
___ JOIN (IP_ADD_MEMBERSHIP)
___ SO_REUSEADDR

---

## Verificare

<details>
<summary>Răspunsuri</summary>

Tabel:
- Broadcast: 255.255.255.255, SO_BROADCAST, -
- Multicast: 224.1.1.1, IP_MULTICAST_TTL, IP_ADD_MEMBERSHIP

Cauză-efect:
- PermissionError
- Poate pierde mesaje
- Nu părăsește host-ul
- Se blochează

Analogii: Socket=Telefon, Broadcast=Megafon, Multicast=WhatsApp, Tunnel=Recepționer

Ordine: 5, 1, 3, 4, 2
</details>
