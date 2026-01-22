# Expected Outputs - Săptămâna 12: Email & RPC

## 1. demo.log (artefact principal)

Fișierul `artifacts/demo.log` trebuie să conțină:

```
[INFO] SĂPTĂMÂNA 12: DEMO AUTOMAT EMAIL & RPC
[INFO] Project root: ...
[OK] Server SMTP activ
[OK] Email trimis!
[OK] Demo SMTP complet
[OK] Server JSON-RPC activ
[OK] Demo JSON-RPC complet
[OK] Server XML-RPC activ
[OK] Demo XML-RPC complet
```

### Verificare minimală:
- Minim 50 de linii
- Conține „SMTP" cel puțin o dată
- Conține „JSON-RPC" cel puțin o dată
- Conține „[OK]" cel puțin 5 ori
- Nu conține „[ERR]" (sau maxim 1-2 erori non-critice)

## 2. demo.pcap (captură trafic)

Fișierul `artifacts/demo.pcap` trebuie să conțină:

- Pachete TCP pe porturile: 1025 (SMTP), 6200 (JSON-RPC), 6201 (XML-RPC)
- Dimensiune minimă: >1KB (cu trafic real)
- Format: pcap valid (verificabil cu `tcpdump -r demo.pcap`)

### Verificare:
```bash
tcpdump -r artifacts/demo.pcap -c 10
```

Dacă tcpdump nu este disponibil, fișierul poate fi gol (touch).

## 3. validation.txt (raport validare)

Fișierul `artifacts/validation.txt` trebuie să conțină:

```
VALIDATION REPORT - Week 12: Email & RPC
Generated: ...

[ARTIFACTS]
  demo.log: OK
  demo.pcap: OK

[PYTHON MODULES]
  smtp_server: OK
  jsonrpc_server: OK
  ...

[CONFIGURATION]
  WEEK: 12
  IP_BASE: 10.0.12.0/24
  PORT_BASE: 6200
  ...

VALIDATION: PASSED
```

### Verificare minimală:
- Conține „WEEK: 12"
- Conține „VALIDATION: PASSED" sau „VALIDATION: PARTIAL"
- Toate modulele Python sunt OK

## 4. Output exerciții

### ex_01_smtp.py --selftest

```
SELFTEST: ex_01_smtp.py
[TEST 1] Inițializare server... ✓
[TEST 2] Pornire server în background... ✓
[TEST 3] Conectare client... ✓
SELFTEST: TOATE TESTELE AU TRECUT ✓
```

### ex_02_rpc.py --selftest

```
SELFTEST: ex_02_rpc.py
[TEST 1] JSON-RPC add(2, 3) = 5... ✓
[TEST 2] JSON-RPC echo... ✓
[TEST 3] Error handling... ✓
SELFTEST: TOATE TESTELE AU TRECUT ✓
```

## 5. JSON-RPC Response Examples

### Request: add(5, 3)
```json
{"jsonrpc":"2.0","result":8,"id":1}
```

### Request: echo("Hello RPC")
```json
{"jsonrpc":"2.0","result":"Hello RPC","id":3}
```

### Request: get_server_info()
```json
{
  "jsonrpc": "2.0",
  "result": {
    "name": "S12 JSON-RPC Server",
    "version": "1.0.0",
    "protocol": "JSON-RPC 2.0"
  },
  "id": 4
}
```

### Request: nonexistent method
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32601,
    "message": "Method 'nonexistent' not found"
  },
  "id": 99
}
```

## 6. XML-RPC Response Example

### Request: add(15, 25)
```xml
<?xml version="1.0"?>
<methodResponse>
  <params>
    <param>
      <value><int>40</int></value>
    </param>
  </params>
</methodResponse>
```

## 7. Smoke Test Output

```
==============================================
SMOKE TEST - Săptămâna 12: Email & RPC
==============================================
--- Structură directoare ---
[PASS] artifacts/ exists
[PASS] scripts/ exists
[PASS] src/ exists
...
--- Artefacte demo ---
[PASS] demo.log exists
[PASS] demo.pcap exists
[PASS] validation.txt exists
...
--- Module Python ---
[PASS] Python import: src.email.smtp_server
[PASS] Python import: src.rpc.jsonrpc.jsonrpc_server
...
==============================================
REZULTAT SMOKE TEST
==============================================
Passed:   XX
Failed:   0
Warnings: X

SMOKE TEST: PASSED
```

## Criterii de validare

| Criteriu | Așteptat | Critic |
|----------|----------|--------|
| demo.log există | Da | Da |
| demo.log >10 linii | Da | Da |
| demo.pcap există | Da | Nu* |
| validation.txt există | Da | Da |
| Module Python importabile | Da | Da |
| Exerciții --help funcționează | Da | Da |
| smoke_test.sh PASSED | Da | Da |

*demo.pcap poate fi gol dacă tcpdump nu este disponibil.
