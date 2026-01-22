# Seminar 12: Remote Procedure Call (RPC)

> **Disciplină:** Rețele de Calculatoare  
> **Săptămâna:** 12 din 14  
> **Durata:** 2 ore  
> **Autor:** Revolvix&Hypotheticalandrei

---

## Ce vom învăța

În seminar vom vedea **Remote Procedure Call (RPC)** — mecanismul care permite să apelezi funcții de pe un server la distanță ca și cum ar fi locale. Vom studia:

- Conceptul și arhitectura RPC
- **JSON-RPC 2.0** – specificația modernă, ușoară
- **XML-RPC** – predecesorul XML-based
- **gRPC cu Protocol Buffers** – soluția high-performance
- Analiza traficului RPC cu Wireshark
- Benchmark și comparații de performanță

## De ce contează

RPC este fundamentul arhitecturilor distribuite moderne:
- **Microservicii**: Comunicarea între servicii într-un cluster
- **Blockchain APIs**: Bitcoin, Ethereum expun JSON-RPC
- **IDE extensions**: Language Server Protocol folosește JSON-RPC
- **Internal APIs**: Google, Netflix folosesc gRPC masiv

---

## 1. Conceptul RPC

### 1.1 Definiție

**Remote Procedure Call** abstractizează comunicarea în rețea, permițând apelarea funcțiilor de pe un server la distanță **ca și cum ar fi locale**.

```
Local call:        result = add(2, 3)
Remote call (RPC): result = remote_server.add(2, 3)  # Same syntax!
```

Clientul nu gestionează explicit:
- Conexiuni socket
- Serializare/deserializare
- Protocol de transport
- Error handling la nivel de rețea

### 1.2 Componentele unui sistem RPC

```
┌─────────────────────────────────────────────────────────┐
│                       CLIENT                            │
│  ┌──────────────┐    ┌─────────────┐    ┌───────────┐  │
│  │  Application │───▶│ Client Stub │───▶│ Transport │  │
│  │     Code     │    │  (Proxy)    │    │   Layer   │  │
│  └──────────────┘    └─────────────┘    └─────┬─────┘  │
└────────────────────────────────────────────────│────────┘
                                                 │
                        Network                  │ TCP/HTTP
                                                 │
┌────────────────────────────────────────────────│────────┐
│                       SERVER                   │        │
│  ┌──────────────┐    ┌─────────────┐    ┌─────▼─────┐  │
│  │   Actual     │◀───│ Server Stub │◀───│ Transport │  │
│  │   Methods    │    │ (Dispatcher)│    │   Layer   │  │
│  └──────────────┘    └─────────────┘    └───────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Componente:**

| Component | Rol |
|-----------|-----|
| **Client Stub** | Proxy local care expune metodele remote ca funcții native |
| **Server Stub** | Dispatcher care primește cereri și invocă implementarea reală |
| **Transport** | TCP, HTTP sau alt protocol pentru transmisie |
| **Serializare** | JSON, XML, Protocol Buffers – codifică parametrii și rezultatele |

### 1.3 Fluxul unui apel RPC

1. Clientul apelează metoda pe stub-ul local
2. Stub-ul **serializează** parametrii în formatul specificat
3. Mesajul este **transmis** prin rețea către server
4. Server stub-ul **deserializează** cererea
5. Metoda reală este **executată**
6. Rezultatul este **serializat** și trimis înapoi
7. Client stub-ul **deserializează** și returnează rezultatul

---

## 2. JSON-RPC 2.0

### 2.1 Specificația

JSON-RPC este un protocol RPC stateless, light-weight care utilizează JSON pentru serializare.

**Caracteristici:**
- Transport agnostic (HTTP, WebSocket, TCP raw)
- Suportă cereri singulare și batch
- ID pentru corelare request-response
- Notification (cerere fără așteptare răspuns)

### 2.1.1 Analogie: JSON-RPC ca comandă la restaurant

**CONCRET:** Imaginează-ți că ești la un restaurant:

| Acțiune restaurant | Echivalent JSON-RPC |
|-------------------|---------------------|
| Dai comanda ospătarului | Trimiți cererea HTTP POST |
| Spui „Vreau pizza Margherita" | `"method": "order_pizza"` |
| Specifici „fără ceapă, extra mozzarella" | `"params": {"no_onion": true, "extra_cheese": true}` |
| Primești bon cu numărul comenzii | `"id": 42` |
| Ospătarul aduce pizza | Serverul returnează `"result"` |
| Sau spune „Nu mai avem blat subțire" | Serverul returnează `"error"` |

**Notification** = Spui ospătarului „Mulțumesc!" când pleci — nu aștepți răspuns.

**Batch** = Comanzi pentru toată masa pe un singur bon, nu faci 5 comenzi separate.

### 2.2 Structura cererii

```json
{
    "jsonrpc": "2.0",
    "method": "subtract",
    "params": [42, 23],
    "id": 1
}
```

| Câmp | Obligatoriu | Descriere |
|------|-------------|-----------|
| `jsonrpc` | Da | Versiunea protocolului, întotdeauna "2.0" |
| `method` | Da | Numele metodei de apelat |
| `params` | Nu | Array sau object cu parametrii |
| `id` | Condiționat | Identificator unic; absent pentru notifications |

**Parametri poziționali vs numiți:**

```json
// Poziționali (array)
{"params": [42, 23]}

// Numiți (object)
{"params": {"minuend": 42, "subtrahend": 23}}
```

### 2.3 Structura răspunsului

**Succes:**
```json
{
    "jsonrpc": "2.0",
    "result": 19,
    "id": 1
}
```

**Eroare:**
```json
{
    "jsonrpc": "2.0",
    "error": {
        "code": -32601,
        "message": "Method not found",
        "data": "subtract_numbers is not a valid method"
    },
    "id": 1
}
```

### 2.4 Coduri de eroare standard

| Cod | Mesaj | Descriere |
|-----|-------|-----------|
| -32700 | Parse error | JSON invalid |
| -32600 | Invalid Request | Structură cerere invalidă |
| -32601 | Method not found | Metoda nu există |
| -32602 | Invalid params | Parametri invalizi (tip/număr) |
| -32603 | Internal error | Eroare internă server |
| -32000 to -32099 | Server error | Erori specifice aplicației |

### 2.5 Batch Requests

Trimite multiple cereri într-un singur HTTP request:

```json
[
    {"jsonrpc": "2.0", "method": "add", "params": [1, 2], "id": 1},
    {"jsonrpc": "2.0", "method": "subtract", "params": [10, 5], "id": 2},
    {"jsonrpc": "2.0", "method": "multiply", "params": [3, 4], "id": 3}
]
```

Răspuns (ordinea poate diferi):
```json
[
    {"jsonrpc": "2.0", "result": 3, "id": 1},
    {"jsonrpc": "2.0", "result": 5, "id": 2},
    {"jsonrpc": "2.0", "result": 12, "id": 3}
]
```

**Avantaje batch:**
- Reduce overhead conexiuni (1 TCP handshake vs 3)
- Reduce latență totală
- Eficient pentru operații multiple dependente

### 2.6 Notifications

Cereri fără `id` nu primesc răspuns:

```json
{"jsonrpc": "2.0", "method": "log_event", "params": ["user_login", "alice"]}
```

Folosire: logging, metrics, fire-and-forget operations.

### 2.7 Când aleg JSON-RPC vs REST?

Personal prefer JSON-RPC pentru:
- API-uri interne între microservicii (mai puțin boilerplate decât REST)
- Operații care nu se mapează natural pe resurse (ex: `calculate_tax`, `send_notification`, `validate_address`)
- Când am nevoie de batch requests — trimit 10 cereri într-un singur HTTP request

REST rămâne alegerea mai bună pentru:
- API-uri publice (convenții cunoscute de toți developerii)
- CRUD simplu pe resurse (GET/POST/PUT/DELETE pe /users, /products)
- Când am nevoie de caching HTTP (GET requests se cachează automat)

---

## 🗳️ PEER INSTRUCTION: Înțelegere RPC

### PI-1: JSON-RPC Notification vs Call

**Scenariu:** Trimitem următoarea cerere către server:
```json
{"jsonrpc": "2.0", "method": "log_event", "params": ["user_login", "alice"]}
```

**Întrebare:** Ce primește clientul ca răspuns?

A) `{"jsonrpc": "2.0", "result": null, "id": null}`  
B) `{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Missing id"}}`  
C) Nimic — serverul nu trimite răspuns  
D) Connection timeout după 30 secunde  

<details>
<summary>📋 Note instructor (click pentru a expanda)</summary>

**Răspuns corect:** C

**Analiza distractorilor:**
- **A)** Misconceptie: studenții cred că orice cerere primește răspuns
- **B)** Misconceptie: lipsa `id` e tratată ca eroare, nu ca notification
- **D)** Misconceptie: confuzie cu probleme de rețea

**Timing:** Vot 1 min → Discuție perechi 3 min → Revot 30s → Explicație 2 min

**Punct cheie:** Absența câmpului `id` transformă cererea în notification = fire-and-forget. Serverul execută metoda dar NU trimite răspuns.
</details>

---

### PI-2: SMTP Envelope vs Headers

**Scenariu:** Un email are:
- Envelope: `MAIL FROM:<bounce@newsletter.com>`
- Header: `From: CEO <ceo@bigcompany.com>`

**Întrebare:** Ce vede destinatarul în câmpul „From" al clientului de email?

A) `bounce@newsletter.com`  
B) `CEO <ceo@bigcompany.com>`  
C) Ambele adrese, una sub alta  
D) Eroare — email respins automat ca spoofed  

<details>
<summary>📋 Note instructor</summary>

**Răspuns corect:** B

**Analiza distractorilor:**
- **A)** Misconceptie: confuzie între envelope (rutare) și headers (afișare)
- **C)** Misconceptie: fuziune vizuală care nu există în clienții de email
- **D)** Misconceptie: presupun că SPF/DKIM blochează automat (nu e cazul fără DMARC strict)

**Punct cheie:** Asta e exact mecanismul de spoofing! Envelope-ul e pentru rutare și bounce-uri, header-ul e ce vede utilizatorul. De aceea avem nevoie de SPF/DKIM/DMARC.
</details>

---

### PI-3: Batch vs Individual Calls

**Scenariu:** Trebuie să faci 100 de apeluri RPC identice (ex: `get_price` pentru 100 de produse).

**Întrebare:** De ce un batch request e mai rapid decât 100 de apeluri individuale?

A) Batch folosește UDP în loc de TCP  
B) Se face un singur TCP handshake în loc de 100  
C) Serverul are un cache special pentru batch  
D) JSON-ul batch se comprimă automat mai bine  

<details>
<summary>📋 Note instructor</summary>

**Răspuns corect:** B

**Analiza distractorilor:**
- **A)** Misconceptie: JSON-RPC e tot peste TCP/HTTP, nu UDP
- **C)** Misconceptie: nu există cache magic pentru batch
- **D)** Parțial adevărat (mai puține headers HTTP), dar nu e motivul principal

**Demonstrație:** Rulați `make benchmark-rpc` și arătați diferența de latență. Un batch de 10 cereri e aproape la fel de rapid ca o singură cerere!
</details>

---

## 3. XML-RPC

### 3.1 Caracteristici

Predecesorul JSON-RPC, folosind XML pentru serializare.

- Mai verbose decât JSON-RPC
- Suport bun pentru introspecție
- Încă prezent în sisteme legacy (WordPress, many PHP systems)
- Transport exclusiv HTTP POST

### 3.2 Structura cererii

```xml
<?xml version="1.0"?>
<methodCall>
    <methodName>subtract</methodName>
    <params>
        <param><value><int>42</int></value></param>
        <param><value><int>23</int></value></param>
    </params>
</methodCall>
```

### 3.3 Structura răspunsului

**Succes:**
```xml
<?xml version="1.0"?>
<methodResponse>
    <params>
        <param>
            <value><int>19</int></value>
        </param>
    </params>
</methodResponse>
```

**Eroare:**
```xml
<?xml version="1.0"?>
<methodResponse>
    <fault>
        <value>
            <struct>
                <member>
                    <name>faultCode</name>
                    <value><int>-32601</int></value>
                </member>
                <member>
                    <name>faultString</name>
                    <value><string>Method not found</string></value>
                </member>
            </struct>
        </value>
    </fault>
</methodResponse>
```

### 3.4 Tipuri de date XML-RPC

| Tag XML | Tip | Exemplu |
|---------|-----|---------|
| `<int>` sau `<i4>` | Integer | `<int>42</int>` |
| `<double>` | Float | `<double>3.14</double>` |
| `<string>` | String | `<string>hello</string>` |
| `<boolean>` | Boolean | `<boolean>1</boolean>` |
| `<base64>` | Binary | `<base64>SGVsbG8=</base64>` |
| `<dateTime.iso8601>` | DateTime | `<dateTime.iso8601>20250115T10:30:00</dateTime.iso8601>` |
| `<array>` | Array | `<array><data>...</data></array>` |
| `<struct>` | Object/Map | `<struct><member>...</member></struct>` |

### 3.5 Introspecție

XML-RPC definește metode standard pentru descoperirea API-ului:

| Metodă | Returnează |
|--------|------------|
| `system.listMethods` | Array cu toate metodele disponibile |
| `system.methodSignature` | Semnăturile unei metode |
| `system.methodHelp` | Documentație text pentru metodă |

```xml
<methodCall>
    <methodName>system.listMethods</methodName>
    <params></params>
</methodCall>
```

---

## 4. gRPC cu Protocol Buffers

### 4.1 Caracteristici

gRPC (Google RPC) este framework-ul de înaltă performanță dezvoltat de Google.

| Aspect | Valoare |
|--------|---------|
| **Serializare** | Protocol Buffers (binary) |
| **Transport** | HTTP/2 obligatoriu |
| **Streaming** | Unary, server, client, bidirectional |
| **Code generation** | Automat din .proto files |
| **Performance** | 2-10x mai rapid decât JSON-RPC |

### 4.2 Protocol Buffers

Definire serviciu în fișier `.proto`:

```protobuf
syntax = "proto3";

package calculator;

service Calculator {
    // Unary RPC
    rpc Subtract(SubtractRequest) returns (SubtractResponse);
    
    // Server streaming
    rpc GetPrimes(RangeRequest) returns (stream PrimeNumber);
    
    // Bidirectional streaming
    rpc Chat(stream Message) returns (stream Message);
}

message SubtractRequest {
    int32 minuend = 1;
    int32 subtrahend = 2;
}

message SubtractResponse {
    int32 result = 1;
}

message RangeRequest {
    int32 start = 1;
    int32 end = 2;
}

message PrimeNumber {
    int32 value = 1;
}

message Message {
    string content = 1;
    string sender = 2;
}
```

### 4.3 Tipuri de apeluri gRPC

| Tip | Client | Server | Use case |
|-----|--------|--------|----------|
| **Unary** | 1 request | 1 response | CRUD operations |
| **Server streaming** | 1 request | stream responses | Download file, list items |
| **Client streaming** | stream requests | 1 response | Upload file, aggregation |
| **Bidirectional** | stream | stream | Chat, real-time sync |

### 4.4 Avantaje Protocol Buffers

- **Dimensiune mică**: ~3-10x mai mic decât JSON
- **Viteză parsing**: ~5-100x mai rapid
- **Schema strictă**: Erori la compile-time
- **Evoluție**: Backward compatibility cu field numbers

### 4.5 Exemplu Python (grpcio)

**Server:**
```python
import grpc
from concurrent import futures
import calculator_pb2
import calculator_pb2_grpc

class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):
    def Subtract(self, request, context):
        result = request.minuend - request.subtrahend
        return calculator_pb2.SubtractResponse(result=result)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(
        CalculatorServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
```

**Client:**
```python
import grpc
import calculator_pb2
import calculator_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = calculator_pb2_grpc.CalculatorStub(channel)

request = calculator_pb2.SubtractRequest(minuend=42, subtrahend=23)
response = stub.Subtract(request)
print(f"Result: {response.result}")  # Result: 19
```

---

## 5. Comparație JSON-RPC vs XML-RPC vs gRPC

| Aspect | JSON-RPC | XML-RPC | gRPC |
|--------|----------|---------|------|
| **Format** | JSON (text) | XML (text) | Protobuf (binary) |
| **Overhead** | ~50-100 bytes | ~200-500 bytes | ~20-50 bytes |
| **Transport** | HTTP/WS/TCP | HTTP POST | HTTP/2 |
| **Schema** | Opțional | Nu | Obligatoriu (.proto) |
| **Streaming** | Nu nativ | Nu | Da, bidirectional |
| **Browser** | Da | Da | grpc-web (proxy) |
| **Debugging** | Ușor (human-readable) | Ușor | Necesită tools |
| **Performance** | Mediu | Scăzut | Ridicat |
| **Tipare** | Dinamic | Dinamic | Static |

### Când folosești fiecare?

| Situație | Recomandare |
|----------|-------------|
| API public, simplitate | JSON-RPC |
| Sistem legacy PHP/WordPress | XML-RPC |
| Microservicii interne | gRPC |
| Browser client nativ | JSON-RPC |
| Real-time bidirectional | gRPC streaming |
| Bandwidth limitat | gRPC |
| Rapid prototyping | JSON-RPC |

---

## 6. Implementare Python

### 6.1 Server JSON-RPC

```python
"""
JSON-RPC 2.0 Server - Educational Implementation
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class JSONRPCHandler(BaseHTTPRequestHandler):
    methods = {}
    
    @classmethod
    def register(cls, name, func):
        cls.methods[name] = func
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            self.send_error_response(-32700, "Parse error", None)
            return
        
        # Handle batch requests
        if isinstance(request, list):
            responses = [self.handle_single(req) for req in request]
            responses = [r for r in responses if r is not None]
            self.send_response_json(responses)
        else:
            response = self.handle_single(request)
            if response:
                self.send_response_json(response)
    
    def handle_single(self, request):
        # Validate request
        if not isinstance(request, dict):
            return self.make_error(-32600, "Invalid Request", None)
        
        if request.get('jsonrpc') != '2.0':
            return self.make_error(-32600, "Invalid Request", request.get('id'))
        
        method = request.get('method')
        if not method or not isinstance(method, str):
            return self.make_error(-32600, "Invalid Request", request.get('id'))
        
        # Check if notification (no id)
        is_notification = 'id' not in request
        req_id = request.get('id')
        
        # Find method
        if method not in self.methods:
            if is_notification:
                return None
            return self.make_error(-32601, "Method not found", req_id)
        
        # Execute
        params = request.get('params', [])
        try:
            if isinstance(params, list):
                result = self.methods[method](*params)
            else:
                result = self.methods[method](**params)
        except TypeError as e:
            if is_notification:
                return None
            return self.make_error(-32602, f"Invalid params: {e}", req_id)
        except Exception as e:
            if is_notification:
                return None
            return self.make_error(-32603, f"Internal error: {e}", req_id)
        
        if is_notification:
            return None
        
        return {"jsonrpc": "2.0", "result": result, "id": req_id}
    
    def make_error(self, code, message, req_id):
        return {
            "jsonrpc": "2.0",
            "error": {"code": code, "message": message},
            "id": req_id
        }
    
    def send_response_json(self, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)
    
    def send_error_response(self, code, message, req_id):
        self.send_response_json(self.make_error(code, message, req_id))

# Register methods
def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b): return a / b if b != 0 else None

JSONRPCHandler.register('add', add)
JSONRPCHandler.register('subtract', subtract)
JSONRPCHandler.register('multiply', multiply)
JSONRPCHandler.register('divide', divide)

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), JSONRPCHandler)
    print("JSON-RPC server running on http://localhost:8000")
    server.serve_forever()
```

### 6.2 Client JSON-RPC

```python
"""
JSON-RPC 2.0 Client - Educational Implementation
"""
import json
import urllib.request

class JSONRPCClient:
    def __init__(self, url):
        self.url = url
        self._id = 0
    
    def _next_id(self):
        self._id += 1
        return self._id
    
    def call(self, method, *args, **kwargs):
        """Make a single RPC call."""
        params = args if args else kwargs if kwargs else None
        
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self._next_id()
        }
        if params:
            request["params"] = params
        
        response = self._send(request)
        
        if "error" in response:
            raise Exception(f"RPC Error {response['error']['code']}: {response['error']['message']}")
        
        return response.get("result")
    
    def batch(self, calls):
        """
        Make multiple RPC calls in a single request.
        calls: list of (method, *args) or (method, **kwargs) tuples
        """
        requests = []
        for call in calls:
            method = call[0]
            params = call[1:] if len(call) > 1 else None
            
            req = {
                "jsonrpc": "2.0",
                "method": method,
                "id": self._next_id()
            }
            if params:
                req["params"] = list(params)
            requests.append(req)
        
        responses = self._send(requests)
        
        # Sort responses by id to match request order
        responses.sort(key=lambda r: r.get("id", 0))
        
        results = []
        for r in responses:
            if "error" in r:
                results.append(Exception(f"RPC Error: {r['error']['message']}"))
            else:
                results.append(r.get("result"))
        
        return results
    
    def notify(self, method, *args, **kwargs):
        """Send a notification (no response expected)."""
        params = args if args else kwargs if kwargs else None
        
        request = {
            "jsonrpc": "2.0",
            "method": method
        }
        if params:
            request["params"] = params
        
        # Send without expecting response
        self._send(request, expect_response=False)
    
    def _send(self, data, expect_response=True):
        body = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            self.url,
            data=body,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            if expect_response:
                return json.loads(response.read().decode('utf-8'))
            return None

# Usage example
if __name__ == '__main__':
    client = JSONRPCClient('http://localhost:8000')
    
    # Single calls
    print(f"add(2, 3) = {client.call('add', 2, 3)}")
    print(f"subtract(10, 4) = {client.call('subtract', 10, 4)}")
    
    # Batch call
    results = client.batch([
        ('add', 1, 2),
        ('multiply', 3, 4),
        ('divide', 10, 2)
    ])
    print(f"Batch results: {results}")
```

---

## 7. Analiza traficului cu Wireshark

### 7.1 Filtre utile

```wireshark
# Tot traficul HTTP POST (RPC calls)
http.request.method == "POST"

# Cereri JSON-RPC
http contains "jsonrpc"

# Cereri XML-RPC
http contains "methodCall"

# Răspunsuri cu eroare JSON-RPC
http contains "error"

# Traffic pe port specific
tcp.port == 8000
```

### 7.2 Ce să observați

1. **Request headers**: Content-Type (application/json vs text/xml)
2. **Payload size**: Comparați JSON vs XML pentru aceeași cerere
3. **Response time**: Latența per call
4. **Batch efficiency**: Un request batch vs multiple singulare

---

## Ce am învățat

- **RPC** abstractizează apelurile de funcții peste rețea
- **JSON-RPC 2.0** este simplu, light-weight, ideal pentru APIs publice
- **XML-RPC** e mai verbose dar oferă introspecție
- **gRPC** oferă performanță maximă cu Protocol Buffers
- **Batch requests** reduc overhead-ul semnificativ
- Alegerea depinde de context: simplitate vs performanță vs compatibilitate

---

## La ce ne ajută

| Situație | Tehnologie |
|----------|------------|
| API blockchain | JSON-RPC |
| Microservicii interne | gRPC |
| Legacy integration | XML-RPC |
| Real-time bidirectional | gRPC streaming |
| Browser-first API | JSON-RPC |
| Mobile app backend | gRPC (smaller payloads) |

---

## Bibliografie

1. JSON-RPC 2.0 Specification – https://www.jsonrpc.org/specification
2. gRPC Documentation – https://grpc.io/docs/
3. Protocol Buffers Language Guide – https://protobuf.dev/
4. Birrell, A. D., & Nelson, B. J. (1984). Implementing remote procedure calls. ACM TOCS.

---

*Material didactic — Rețele de Calculatoare, ASE-CSIE*
