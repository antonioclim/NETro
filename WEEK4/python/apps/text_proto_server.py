#!/usr/bin/env python3
"""
Server TCP concurent cu protocol text (length-prefixed framing).

PROTOCOL:
---------
Framing: <LUNGIME> <PAYLOAD>
  - LUNGIME: numărul de bytes al payload-ului (ASCII decimal)
  - spațiu: separator
  - PAYLOAD: conținutul mesajului (UTF-8)

Exemplu: "11 SET name Alice"
         ^^  ^^^^^^^^^^^^^^
         |   payload (11 bytes)
         lungime payload

COMENZI DISPONIBILE:
--------------------
  PING              → OK pong
  SET <key> <value> → OK stored <key>
  GET <key>         → OK <key> <value> | ERR not_found
  DEL <key>         → OK deleted | OK no_such_key
  COUNT             → OK <n> keys
  KEYS              → OK <key1> <key2> ...
  QUIT              → OK bye (închide conexiunea)

DE CE ACEST DESIGN:
-------------------
- Ușor de debugat: vizibil în tcpdump/tshark
- Framing explicit: elimină ambiguitatea stream-ului TCP
- Human-readable: poate fi testat parțial cu netcat

UTILIZARE:
----------
  python3 text_proto_server.py --port 5400 --verbose

LICENȚĂ: MIT - Material didactic ASE-CSIE
"""
from __future__ import annotations

import argparse
import socket
import threading
import sys
from typing import Dict

# Adăugăm directorul utils la path
sys.path.insert(0, str(__file__).rsplit('/', 2)[0] + '/utils')
from io_utils import recv_until, recv_exact


def recv_framed(conn: socket.socket) -> str:
    """
    Primește un mesaj cu length-prefix framing.
    
    Format: <LEN> <PAYLOAD>
    Unde LEN este lungimea în bytes (ASCII digits) urmată de spațiu.
    
    Raises:
        ConnectionError: Dacă conexiunea este închisă
        ValueError: Dacă formatul nu corespunde
    """
    # Citim până la spațiu (separator după lungime)
    raw = recv_until(conn, b" ", max_bytes=16)
    len_str = raw[:-1].decode("ascii").strip()
    
    if not len_str.isdigit():
        raise ValueError(f"invalid length prefix: {len_str!r}")
    
    payload_len = int(len_str)
    if payload_len > 65535:
        raise ValueError(f"payload too large: {payload_len}")
    
    payload_bytes = recv_exact(conn, payload_len)
    return payload_bytes.decode("utf-8", errors="replace")


def send_framed(conn: socket.socket, payload: str) -> None:
    """
    Trimite un mesaj cu length-prefix framing.
    
    Format: <LEN> <PAYLOAD>
    """
    payload_bytes = payload.encode("utf-8")
    header = f"{len(payload_bytes)} ".encode("ascii")
    conn.sendall(header + payload_bytes)


def process_command(state: Dict[str, str], line: str) -> str:
    """
    Procesează o comandă și returnează răspunsul.
    
    State este dicționarul partajat (thread-safe via lock extern).
    """
    parts = line.strip().split()
    if not parts:
        return "ERR empty_command"
    
    cmd = parts[0].upper()
    
    # PING - test conectivitate
    if cmd == "PING":
        return "OK pong"
    
    # SET <key> <value> - stochează o valoare
    if cmd == "SET":
        if len(parts) < 3:
            return "ERR usage: SET <key> <value>"
        key = parts[1]
        value = " ".join(parts[2:])  # value poate conține spații
        state[key] = value
        return f"OK stored {key}"
    
    # GET <key> - citește o valoare
    if cmd == "GET":
        if len(parts) != 2:
            return "ERR usage: GET <key>"
        key = parts[1]
        if key not in state:
            return "ERR not_found"
        return f"OK {key} {state[key]}"
    
    # DEL <key> - șterge o cheie
    if cmd == "DEL":
        if len(parts) != 2:
            return "ERR usage: DEL <key>"
        key = parts[1]
        existed = key in state
        state.pop(key, None)
        return "OK deleted" if existed else "OK no_such_key"
    
    # COUNT - numărul de chei
    if cmd == "COUNT":
        return f"OK {len(state)} keys"
    
    # KEYS - lista cheilor
    if cmd == "KEYS":
        if not state:
            return "OK"
        return "OK " + " ".join(sorted(state.keys()))
    
    # QUIT - închide conexiunea
    if cmd == "QUIT":
        return "OK bye"
    
    return "ERR unknown_command"


def handle_client(
    conn: socket.socket,
    addr: tuple,
    state: Dict[str, str],
    lock: threading.Lock,
    verbose: bool
) -> None:
    """
    Gestionează comunicarea cu un client.
    
    Loop de procesare:
    1. Primește mesaj framat
    2. Procesează comanda (cu lock pe state)
    3. Trimite răspuns
    4. Repetă până la QUIT sau eroare
    """
    with conn:
        if verbose:
            print(f"[TEXT] + connected {addr[0]}:{addr[1]}")
        
        try:
            while True:
                # 1. Primim mesajul
                try:
                    line = recv_framed(conn)
                except (ConnectionError, ValueError) as e:
                    if verbose:
                        print(f"[TEXT] ! recv error from {addr}: {e}")
                    break
                
                if verbose:
                    print(f"[TEXT] < {addr[0]}:{addr[1]}: {line}")
                
                # 2. Procesăm comanda (thread-safe)
                with lock:
                    response = process_command(state, line)
                
                # 3. Trimitem răspuns
                send_framed(conn, response)
                
                if verbose:
                    print(f"[TEXT] > {addr[0]}:{addr[1]}: {response}")
                
                # 4. QUIT închide conexiunea
                if line.strip().upper() == "QUIT":
                    break
                    
        except Exception as e:
            if verbose:
                print(f"[TEXT] ! error handling {addr}: {e}")
        
        if verbose:
            print(f"[TEXT] - disconnected {addr[0]}:{addr[1]}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Server TCP cu protocol text (length-prefixed framing)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple de utilizare:
  python3 text_proto_server.py --port 5400 --verbose
  
Testare cu client:
  python3 text_proto_client.py --host localhost --port 5400 -c "PING"
        """
    )
    parser.add_argument(
        "--host", default="0.0.0.0",
        help="Adresa de bind (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=5400,
        help="Portul de ascultare (default: 5400 - WEEK4 standard)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Afișează mesajele procesate"
    )
    
    args = parser.parse_args()
    
    # State partajat între thread-uri
    state: Dict[str, str] = {}
    lock = threading.Lock()
    
    # Creare socket server
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        srv.bind((args.host, args.port))
        srv.listen(16)
        
        print(f"[TEXT] Server listening on {args.host}:{args.port}")
        print(f"[TEXT] Protocol: length-prefixed text (<LEN> <PAYLOAD>)")
        print(f"[TEXT] Commands: PING, SET, GET, DEL, COUNT, KEYS, QUIT")
        print(f"[TEXT] Press Ctrl+C to stop")
        
        while True:
            conn, addr = srv.accept()
            t = threading.Thread(
                target=handle_client,
                args=(conn, addr, state, lock, args.verbose),
                daemon=True
            )
            t.start()
            
    except KeyboardInterrupt:
        print("\n[TEXT] Shutting down...")
        return 0
    except Exception as e:
        print(f"[TEXT] Error: {e}")
        return 1
    finally:
        try:
            srv.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
