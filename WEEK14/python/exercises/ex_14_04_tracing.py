#!/usr/bin/env python3
"""ex_14_04_tracing.py — Exerciții de urmărire a execuției codului.

Aceste exerciții NU necesită rularea codului. Citești codul și prezici
ce se întâmplă, apoi verifici răspunsul.

Utilizare:
  python3 ex_14_04_tracing.py --show 1      # afișează exercițiul 1
  python3 ex_14_04_tracing.py --check 1     # verifică răspunsul
  python3 ex_14_04_tracing.py --all         # toate exercițiile
"""

from __future__ import annotations
import argparse

EXERCISES = [
    {
        "id": 1,
        "title": "TCP Echo Server - Ce linii se execută?",
        "code": '''
import socket

def handle_client(conn, addr):          # L1
    print(f"Conectat: {addr}")          # L2
    data = conn.recv(1024)              # L3
    if data:                            # L4
        conn.sendall(data)              # L5
    conn.close()                        # L6

sock = socket.socket()                  # L7
sock.bind(('0.0.0.0', 9000))            # L8
sock.listen(1)                          # L9
print("Aștept conexiuni...")            # L10
conn, addr = sock.accept()              # L11 ← BLOCARE
handle_client(conn, addr)               # L12
sock.close()                            # L13
''',
        "question": """Serverul pornește. Un client trimite "hello" și închide conexiunea.
Care linii se execută, în ordine? (ex: L7, L8, ...)""",
        "answer": "L7, L8, L9, L10, L11 (așteaptă), L11 (revine), L12, L1, L2, L3, L4, L5, L6, L13",
        "explanation": """
1. L7-L10: Setup server (socket, bind, listen, print)
2. L11: accept() blochează până vine clientul
3. L12: apelează handle_client()
4. L1-L6: În handle_client - primește, trimite echo, închide
5. L13: Închide socket-ul serverului

Notă: L4 este True pentru că data='hello' (non-empty bytes).
"""
    },
    {
        "id": 2,
        "title": "Connection Refused - Ce apare în pcap?",
        "code": '''
# Client încearcă să se conecteze la un server inexistent
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
sock.connect(('10.0.0.5', 9999))  # ← Nimeni nu ascultă pe acest port
''',
        "question": """Pe 10.0.0.5 NU rulează niciun server pe portul 9999.
Ce pachete vei vedea în tcpdump? Câte și ce flags?""",
        "answer": "2 pachete: SYN (client→server), RST-ACK (server→client)",
        "explanation": """
1. Clientul trimite SYN către 10.0.0.5:9999
2. OS-ul de pe 10.0.0.5 vede că portul nu e în LISTEN
3. Kernel-ul răspunde automat cu RST-ACK ("nu ascult aici")
4. Clientul primește RST și ridică ConnectionRefusedError

NU e timeout — RST vine imediat (sub 1ms pe LAN).
"""
    },
    {
        "id": 3,
        "title": "HTTP Request - Ce trimite clientul?",
        "code": '''
import http.client
conn = http.client.HTTPConnection("example.com", 80)
conn.request("GET", "/index.html", headers={"User-Agent": "Test"})
response = conn.getresponse()
''',
        "question": """Ce bytes exacte trimite clientul pe socket? (primele 3 linii)""",
        "answer": """GET /index.html HTTP/1.1\\r\\n
Host: example.com\\r\\n
User-Agent: Test\\r\\n""",
        "explanation": """
HTTP/1.1 adaugă automat header-ul Host (obligatoriu).
Fiecare linie se termină cu \\r\\n (CRLF).
După headers, urmează o linie goală (\\r\\n) și apoi body (gol pentru GET).

Ordinea exactă a header-elor poate varia, dar Host e mereu prezent.
"""
    },
    {
        "id": 4,
        "title": "Load Balancer - Câte conexiuni TCP?",
        "code": '''
# Topologie: Client → LB → [Backend1, Backend2]
# LB face round-robin, proxy HTTP

# Clientul trimite:
for i in range(4):
    requests.get("http://lb:8080/api")
''',
        "question": """Câte conexiuni TCP distincte se stabilesc în total?
(presupunem HTTP/1.1 fără keep-alive pe backend)""",
        "answer": "8 conexiuni: 4 (client→LB) + 4 (LB→backends)",
        "explanation": """
Pentru FIECARE request:
1. Client deschide conexiune TCP către LB (1 conexiune)
2. LB deschide conexiune TCP către backend-ul ales (1 conexiune)

4 requests × 2 conexiuni/request = 8 conexiuni TCP în total.

Cu HTTP keep-alive ar fi mai puține (reutilizare conexiuni).
Round-robin: Backend1, Backend2, Backend1, Backend2.
"""
    },
]


def show_exercise(ex_id: int) -> None:
    """Afișează un exercițiu fără răspuns."""
    ex = next((e for e in EXERCISES if e["id"] == ex_id), None)
    if not ex:
        print(f"Exercițiul {ex_id} nu există. Disponibile: 1-{len(EXERCISES)}")
        return
    
    print(f"\n{'='*60}")
    print(f"EXERCIȚIUL {ex['id']}: {ex['title']}")
    print('='*60)
    print("\nCOD:")
    print(ex['code'])
    print("\nÎNTREBARE:")
    print(ex['question'])
    print("\n" + "-"*60)
    print("Gândește-te înainte să verifici răspunsul!")
    print(f"Verificare: python3 ex_14_04_tracing.py --check {ex_id}")


def check_exercise(ex_id: int) -> None:
    """Afișează răspunsul și explicația pentru un exercițiu."""
    ex = next((e for e in EXERCISES if e["id"] == ex_id), None)
    if not ex:
        print(f"Exercițiul {ex_id} nu există.")
        return
    
    print(f"\n{'='*60}")
    print(f"RĂSPUNS EXERCIȚIUL {ex['id']}")
    print('='*60)
    print(f"\nRĂSPUNS: {ex['answer']}")
    print(f"\nEXPLICAȚIE:{ex['explanation']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Exerciții tracing S14")
    parser.add_argument("--show", type=int, help="Afișează exercițiul N")
    parser.add_argument("--check", type=int, help="Verifică răspunsul pentru N")
    parser.add_argument("--all", action="store_true", help="Afișează toate exercițiile")
    parser.add_argument("--list", action="store_true", help="Listează titlurile")
    args = parser.parse_args()
    
    if args.list:
        print("\nExerciții disponibile:")
        for ex in EXERCISES:
            print(f"  {ex['id']}. {ex['title']}")
        return 0
    
    if args.show:
        show_exercise(args.show)
        return 0
    
    if args.check:
        check_exercise(args.check)
        return 0
    
    if args.all:
        for ex in EXERCISES:
            show_exercise(ex["id"])
            input("\n[Enter pentru următorul exercițiu...]")
            check_exercise(ex["id"])
        return 0
    
    print("Utilizare:")
    print("  python3 ex_14_04_tracing.py --list       # listează exercițiile")
    print("  python3 ex_14_04_tracing.py --show 1     # afișează exercițiul 1")
    print("  python3 ex_14_04_tracing.py --check 1    # verifică răspunsul")
    print("  python3 ex_14_04_tracing.py --all        # parcurge toate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
