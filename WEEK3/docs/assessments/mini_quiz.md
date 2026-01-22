# Quiz rapid — WEEK3

10-15 minute. Fără notițe.

---

## Partea A: Alegere (8 puncte)

**1.** Ce protocol suportă broadcast?
□ A) TCP □ B) UDP □ C) Ambele

**2.** Care adresă NU e multicast?
□ A) 224.0.0.1 □ B) 239.255.255.255 □ C) 240.0.0.1

**3.** Mărimea header UDP:
□ A) 8 bytes □ B) 20 bytes □ C) 40 bytes

**4.** IP_MULTICAST_TTL = 0 înseamnă:
□ A) Fără limită □ B) Nu părăsește host-ul □ C) Eroare

**5.** recv() returnează b'' când:
□ A) Timeout □ B) Conexiune închisă □ C) Buffer plin

**6.** sendall() vs send():
□ A) Identice □ B) sendall garantează trimiterea completă □ C) send e mai rapid

**7.** TCP păstrează granițele mesajelor?
□ A) Da □ B) Nu

**8.** Clientul prin tunnel — ce IP vede serverul?
□ A) IP client □ B) IP tunnel □ C) localhost

---

## Partea B: Completează (4 puncte)

**9.** Broadcast sender: `setsockopt(SOL_SOCKET, __________, 1)`

**10.** Multicast receiver: `setsockopt(IPPROTO_IP, __________, mreq)`

**11.** Ordinea la multicast receiver: socket → __________ → JOIN → recv

**12.** Câte thread-uri pentru TCP tunnel bidirecțional: __

---

## Partea C: Adevărat/Fals (3 puncte)

**13.** Broadcast trece de routere. □ A □ F

**14.** Multicast necesită JOIN pentru a primi. □ A □ F

**15.** Un thread e suficient pentru tunnel. □ A □ F

---

## Răspunsuri

<details>
<summary>Click după ce termini</summary>

**Partea A:**
1=B, 2=C, 3=A, 4=B, 5=B, 6=B, 7=B, 8=B

**Partea B:**
9=SO_BROADCAST, 10=IP_ADD_MEMBERSHIP, 11=bind, 12=2

**Partea C:**
13=F, 14=A, 15=F

**Punctaj:**
- 14-15: Excelent
- 11-13: Bine
- 8-10: Revizuiește
- <8: Refă materialele
</details>
