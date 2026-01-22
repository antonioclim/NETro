# Curs 12: Protocoale de Email

> **Disciplină:** Rețele de Calculatoare  
> **Săptămâna:** 12 din 14  
> **Durata:** 2 ore  
> **Autor:** Revolvix&Hypotheticalandrei

---

## Ce vom învăța

Săptămâna aceasta studiem **protocoalele de email** — fundamentul comunicării electronice. Vom înțelege:

- Arhitectura sistemelor de email și componentele acestora
- Protocolul **SMTP** pentru trimiterea mesajelor
- Protocoalele **POP3** și **IMAP** pentru recepție
- Formatul **MIME** pentru atașamente și conținut multimedia
- Mecanismele de securitate: **SPF**, **DKIM**, **DMARC**

## De ce contează

Email-ul rămâne infrastructura critică pentru:
- Comunicare în mediul business și instituțional
- Autentificare (password reset, verificare cont, 2FA)
- Notificări automate din aplicații
- Integrări între sisteme (alerts, reports, workflows)

Înțelegerea protocoalelor subiacente permite:
- Debugging-ul problemelor de livrare ("de ce nu ajung email-urile?")
- Configurarea corectă a serverelor
- Implementarea de soluții custom pentru notificări

---

## 1. Arhitectura sistemelor de email

### 1.1 Componentele principale

| Component | Denumire completă | Rol | Exemple |
|-----------|------------------|-----|---------|
| **MUA** | Mail User Agent | Interfața utilizatorului pentru compunere și citire | Thunderbird, Outlook, Gmail web |
| **MTA** | Mail Transfer Agent | Rutează mesajele între servere | Postfix, Sendmail, Exchange |
| **MDA** | Mail Delivery Agent | Livrează mesajul în mailbox-ul local | Dovecot, Procmail, Cyrus |
| **MSA** | Mail Submission Agent | Primește mesaje de la MUA (port 587) | Adesea integrat în MTA |

### 1.2 Fluxul unui email

```
┌─────────┐    SMTP     ┌─────────┐    SMTP     ┌─────────┐
│   MUA   │───(587)────▶│   MTA   │───(25)────▶│   MTA   │
│ Sender  │             │ Sender  │             │ Receiver│
└─────────┘             └─────────┘             └────┬────┘
                                                     │
                              POP3/IMAP              │ Local
                        ┌─────────────────────────┐  │ delivery
                        │                         ▼  ▼
┌─────────┐    IMAP     │                    ┌─────────┐
│   MUA   │◀──(993)─────│                    │   MDA   │
│Receiver │             │                    │         │
└─────────┘             │                    └─────────┘
                        │                         │
                        └─────────────────────────┘
                              Mailbox storage
```

**Pași detaliați:**

1. Utilizatorul compune mesajul în MUA (Thunderbird)
2. MUA trimite către MSA/MTA local prin SMTP (port 587 cu autentificare)
3. MTA local rezolvă înregistrarea **MX** din DNS pentru domeniul destinatar
4. MTA local trimite către MTA destinatar prin SMTP (port 25)
5. MTA destinatar predă mesajul către MDA pentru stocare
6. Destinatarul accesează mesajul prin POP3 sau IMAP

---

## 2. Envelope vs. Message Headers

**Conceptul fundamental** care diferențiază rutarea de afișare.

### 2.1 Envelope (SMTP)

Informațiile de **rutare** folosite exclusiv de serverele SMTP:

```smtp
MAIL FROM:<alice@sender.com>
RCPT TO:<bob@recipient.com>
```

- Determină unde se livrează efectiv mesajul
- Nevizibil pentru utilizatorul final
- Folosit pentru bounce-uri și rapoarte de livrare

### 2.2 Message Headers

**Metadatele** vizibile în clientul de email:

```
From: Alice Smith <alice@sender.com>
To: Bob Jones <bob@recipient.com>
Subject: Meeting Tomorrow
Date: Mon, 15 Jan 2025 10:30:00 +0200
```

### 2.3 De ce pot diferi?

| Situație | Envelope MAIL FROM | Header From: |
|----------|-------------------|--------------|
| **Mailing list** | listserv@list.com | author@original.com |
| **Forward** | forwarder@domain.com | original@sender.com |
| **Spoofing** | attacker@evil.com | ceo@company.com |

⚠️ **Atenție:** Această diferență este baza **email spoofing**. SPF, DKIM și DMARC verifică alinierea.

---

## 3. SMTP – Simple Mail Transfer Protocol

**RFC 5321** definește protocolul standard pentru trimiterea email-urilor.

### 3.1 Caracteristici

- Protocol **text-based** (human-readable)
- Model **command-response** similar HTTP
- Porturi: **25** (server-to-server), **587** (submission cu auth), **465** (SMTPS legacy)
- Conexiune **TCP** persistentă per sesiune

### 3.2 Comenzi principale

| Comandă | Parametri | Descriere | Răspuns succes |
|---------|-----------|-----------|----------------|
| `EHLO` | hostname | Identificare client, solicită extensions | 250 |
| `MAIL FROM` | `<address>` | Specifică expeditorul (envelope) | 250 |
| `RCPT TO` | `<address>` | Specifică destinatarul (poate fi repetat) | 250 |
| `DATA` | - | Începe transmisia corpului | 354 |
| `QUIT` | - | Închide conexiunea | 221 |
| `RSET` | - | Resetează sesiunea curentă | 250 |
| `VRFY` | user | Verifică existența utilizatorului | 250/550 |

### 3.3 Coduri de răspuns

| Cod | Categorie | Descriere |
|-----|-----------|-----------|
| 2xx | Success | Comandă acceptată |
| 3xx | Intermediate | Aștept continuare (ex: DATA) |
| 4xx | Temporary failure | Retry mai târziu |
| 5xx | Permanent failure | Eroare fatală |

**Exemple comune:**
- `220` – Server ready
- `250` – OK
- `354` – Start mail input
- `421` – Service unavailable (try later)
- `550` – Mailbox unavailable (rejected)
- `554` – Transaction failed

### 3.4 Sesiune SMTP completă

```smtp
S: 220 mail.example.com ESMTP Postfix
C: EHLO client.domain.com
S: 250-mail.example.com
S: 250-SIZE 52428800
S: 250-STARTTLS
S: 250-AUTH PLAIN LOGIN
S: 250 8BITMIME
C: MAIL FROM:<alice@client.domain.com>
S: 250 2.1.0 Ok
C: RCPT TO:<bob@example.com>
S: 250 2.1.5 Ok
C: DATA
S: 354 End data with <CR><LF>.<CR><LF>
C: From: Alice <alice@client.domain.com>
C: To: Bob <bob@example.com>
C: Subject: Test message
C: Date: Mon, 15 Jan 2025 10:30:00 +0200
C: Content-Type: text/plain; charset=utf-8
C: 
C: Hello Bob,
C: This is a test message.
C: 
C: Best regards,
C: Alice
C: .
S: 250 2.0.0 Ok: queued as ABC123
C: QUIT
S: 221 2.0.0 Bye
```

### 3.5 Extensions (ESMTP)

Extensii anunțate în răspunsul EHLO:

| Extension | Descriere |
|-----------|-----------|
| `SIZE` | Limitează dimensiunea mesajului |
| `STARTTLS` | Upgrade la conexiune criptată |
| `AUTH` | Mecanisme de autentificare |
| `8BITMIME` | Suport pentru caractere 8-bit |
| `PIPELINING` | Comenzi multiple fără așteptare răspuns |

### 3.6 Observație practică

Din experiența de predare, cele mai frecvente confuzii la studenți sunt:

1. **Confundarea `MAIL FROM` cu header-ul `From:`** — sunt lucruri diferite! Envelope-ul e pentru rutare, header-ul pentru afișare.
2. **Presupunerea că email-ul ajunge instant** — în realitate, poate trece prin mai multe MTA-uri și poate dura minute sau ore.
3. **Uitarea punctului final (`.`)** care termină comanda DATA — fără el, serverul așteaptă la infinit.

Un truc util: când debuguiezi probleme de email, verifică întâi cu `telnet` sau `nc` dacă serverul răspunde deloc, înainte să cauți în cod.

---

## 4. POP3 – Post Office Protocol v3

**RFC 1939** – Protocol simplu pentru descărcarea mesajelor.

### 4.1 Caracteristici

- Model: **download-and-delete** (implicit)
- Port: **110** (plaintext), **995** (TLS)
- Potrivit pentru: un singur dispozitiv, conexiuni intermitente
- **Nu** menține starea pe server după download

### 4.2 Comenzi principale

| Comandă | Descriere | Răspuns |
|---------|-----------|---------|
| `USER` | Specifică username | +OK |
| `PASS` | Specifică parola | +OK logged in |
| `STAT` | Număr și dimensiune totală mesaje | +OK n size |
| `LIST` | Listează mesajele | +OK (multi-line) |
| `RETR n` | Descarcă mesajul n | +OK (content) |
| `DELE n` | Marchează pentru ștergere | +OK |
| `QUIT` | Aplică ștergerile, închide | +OK |
| `RSET` | Anulează ștergeri marcate | +OK |
| `NOOP` | Keep-alive | +OK |

### 4.3 Sesiune POP3

```pop3
S: +OK POP3 server ready
C: USER bob
S: +OK
C: PASS secret123
S: +OK Logged in
C: STAT
S: +OK 3 12500
C: LIST
S: +OK 3 messages
S: 1 4200
S: 2 3800
S: 3 4500
S: .
C: RETR 1
S: +OK 4200 octets
S: From: alice@example.com
S: Subject: Hello
S: ...message content...
S: .
C: DELE 1
S: +OK Marked for deletion
C: QUIT
S: +OK Bye
```

### 4.4 Limitări POP3

POP3 are câteva limitări importante de înțeles:

1. **Un singur folder** — doar INBOX, fără structură de directoare sau etichete
2. **Fără sincronizare** — ce descarci pe laptop nu apare automat pe telefon
3. **Căutare doar locală** — trebuie să ai toate emailurile descărcate ca să cauți în ele

Ștergerea e definitivă: odată executat `DELE` urmat de `QUIT`, mesajul dispare de pe server și nu poate fi recuperat.

---

## 5. IMAP – Internet Message Access Protocol

**RFC 3501** – Acces complet la mailbox cu sincronizare.

### 5.1 Caracteristici

- Model: **server-side storage** (mesajele rămân pe server)
- Port: **143** (plaintext), **993** (TLS)
- Suportă: foldere, flags, search, partial fetch
- Ideal pentru: multi-device, webmail

### 5.2 Comparație POP3 vs IMAP

| Aspect | POP3 | IMAP |
|--------|------|------|
| **Model** | Download-and-delete | Server-side storage |
| **Multi-device** | Nu | Da, sincronizat |
| **Foldere** | Nu | Da, ierarhie completă |
| **Search** | Client-side | Server-side |
| **Bandwidth** | Download complet | FETCH selectiv |
| **Offline** | După download | Necesită sync |
| **Complexity** | Simplu | Complex |

---

### 🗳️ PEER INSTRUCTION: POP3 vs IMAP

**Scenariu:** Maria citește un email pe laptop și îl marchează ca „citit". Apoi deschide aplicația de email pe telefon.

**Întrebare:** Ce vede Maria pe telefon dacă folosește POP3? Dar dacă folosește IMAP?

A) POP3: citit, IMAP: citit  
B) POP3: necitit, IMAP: citit  
C) POP3: emailul nu mai există, IMAP: citit  
D) Ambele: necitit (flag-urile sunt întotdeauna locale)

<details>
<summary>📋 Note instructor (click pentru a expanda)</summary>

**Răspuns corect:** B (sau C dacă POP3 e configurat download-and-delete)

**Analiza distractorilor:**
- **A)** Misconceptie: studenții cred că POP3 sincronizează starea
- **C)** Parțial corect pentru POP3 cu delete, dar nu e comportamentul default
- **D)** Misconceptie: nu înțeleg că IMAP păstrează flag-uri pe server

**Timing:** Vot 1 min → Discuție perechi 3 min → Revot 30s → Explicație 2 min

**Punct cheie:** 
- POP3: starea e locală per dispozitiv, nu se sincronizează
- IMAP: flag-urile (`\Seen`) sunt pe server, toate dispozitivele le văd

**Întrebare follow-up:** „De ce Gmail/Outlook folosesc IMAP sau protocol proprietar, nu POP3?"
</details>

---

### 5.3 Comenzi IMAP esențiale

| Comandă | Descriere |
|---------|-----------|
| `LOGIN user pass` | Autentificare |
| `LIST "" "*"` | Listează toate folderele |
| `SELECT folder` | Deschide un folder |
| `FETCH n:m (BODY[])` | Descarcă mesaje |
| `SEARCH criteria` | Caută mesaje |
| `STORE n +FLAGS (\Seen)` | Setează flag-uri |
| `CREATE folder` | Creează folder |
| `LOGOUT` | Deconectare |

### 5.4 Flags IMAP

| Flag | Semnificație |
|------|--------------|
| `\Seen` | Mesaj citit |
| `\Answered` | S-a răspuns |
| `\Flagged` | Marcat important |
| `\Deleted` | Marcat pentru ștergere |
| `\Draft` | Ciornă |

---

## 6. MIME – Multipurpose Internet Mail Extensions

Extinde formatul email pentru conținut non-ASCII și atașamente.

### 6.1 Headers MIME

```
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="----=_Part_123"
Content-Transfer-Encoding: base64
```

### 6.2 Content-Type comune

| Type | Descriere |
|------|-----------|
| `text/plain` | Text simplu |
| `text/html` | Conținut HTML |
| `multipart/mixed` | Mesaj cu atașamente |
| `multipart/alternative` | Versiuni alternative (text + HTML) |
| `application/pdf` | Document PDF |
| `image/png` | Imagine PNG |

### 6.3 Structură multipart

```mime
From: alice@example.com
To: bob@example.com
Subject: Document attached
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="----=_Boundary"

------=_Boundary
Content-Type: text/plain; charset=utf-8

Please find attached the document.

------=_Boundary
Content-Type: application/pdf; name="document.pdf"
Content-Disposition: attachment; filename="document.pdf"
Content-Transfer-Encoding: base64

JVBERi0xLjQKJcOkw7zDtsOfCjIgMCBvYmoKPDwvTGVu...
------=_Boundary--
```

---

## 7. Securitate: SPF, DKIM, DMARC

### 7.1 SPF – Sender Policy Framework

**Ce verifică:** IP-ul expeditorului este autorizat să trimită pentru domeniu.

**Cum funcționează:**
1. Serverul receiver extrage domeniul din envelope MAIL FROM
2. Interogează înregistrarea DNS TXT pentru domeniu
3. Verifică dacă IP-ul sender-ului este în lista

**Exemplu înregistrare SPF:**
```dns
example.com. IN TXT "v=spf1 ip4:192.0.2.0/24 include:_spf.google.com -all"
```

**Analogie concretă — SPF ca listă de curieri autorizați:**

Imaginează-ți că domeniul tău e sediul unei companii:
- Înregistrarea SPF e ca o listă la recepție: „Pachetele pentru noi pot veni doar de la DHL, FedEx sau curierul intern"
- Când ajunge un pachet (email), recepționerul verifică dacă curierul (IP-ul expeditor) e pe listă
- Dacă nu e pe listă → respinge sau marchează ca suspect

În exemplul de mai sus: „Acceptă de la IP-urile noastre (192.0.2.0/24), de la Google (_spf.google.com), și respinge (`-all`) orice altceva."

### 7.2 DKIM – DomainKeys Identified Mail

**Ce verifică:** Mesajul nu a fost modificat în tranzit.

**Cum funcționează:**
1. Serverul sender semnează digital header-ele și body-ul
2. Semnătura este adăugată ca header `DKIM-Signature`
3. Cheia publică este publicată în DNS
4. Serverul receiver verifică semnătura

**Header DKIM:**
```
DKIM-Signature: v=1; a=rsa-sha256; d=example.com; s=selector1;
  h=from:to:subject:date; bh=47DEQpj8HBSa...;
  b=dzdVyOfAKCdLX...
```

### 7.3 DMARC – Domain-based Message Authentication

**Ce verifică:** Alinierea SPF/DKIM și specifică politica la eșec.

**Politici:**
- `none` – Monitorizare, fără acțiune
- `quarantine` – Marchează ca spam
- `reject` – Respinge mesajul

**Exemplu:**
```dns
_dmarc.example.com. IN TXT "v=DMARC1; p=quarantine; rua=mailto:reports@example.com"
```

---

## 8. WebMail și API-uri moderne

### 8.1 WebMail

Clientul de email rulează în browser, comunicând cu backend-ul prin:
- **IMAP** (traditional) pentru acces la mailbox
- **Proprietary APIs** (Gmail API, Outlook REST API)

### 8.2 Servicii de email transactional

Pentru notificări programatice:
- **SendGrid**, **Mailgun**, **AWS SES**, **Postmark**
- API REST pentru trimitere
- Webhook-uri pentru tracking (delivery, open, click)

---

## Ce am învățat

- Arhitectura email: **MUA → MTA → MDA** și rolul fiecărei componente
- Diferența critică **envelope** vs **headers** și implicațiile de securitate
- **SMTP** pentru trimitere: comenzi, răspunsuri, sesiune completă
- **POP3** pentru download simplu, **IMAP** pentru acces sincronizat
- **MIME** pentru conținut multimedia și atașamente
- **SPF/DKIM/DMARC** pentru autentificare și anti-spoofing

---

## La ce ne ajută

| Rol | Aplicabilitate |
|-----|----------------|
| **Backend Developer** | Integrare notificări email, debugging deliverability |
| **DevOps/SRE** | Configurare servere mail, monitoring, SPF/DKIM setup |
| **Security** | Înțelegerea vectorilor de atac, configurare DMARC |
| **Product** | Design flows autentificare, onboarding |

---

## Bibliografie

1. Kurose, J. & Ross, K. (2021). *Computer Networking: A Top-Down Approach*, 8th Edition.
2. RFC 5321 – Simple Mail Transfer Protocol
3. RFC 1939 – Post Office Protocol Version 3
4. RFC 3501 – Internet Message Access Protocol
5. RFC 7208 – Sender Policy Framework (SPF)
6. RFC 6376 – DomainKeys Identified Mail (DKIM)

---

*Material didactic — Rețele de Calculatoare, ASE-CSIE*
