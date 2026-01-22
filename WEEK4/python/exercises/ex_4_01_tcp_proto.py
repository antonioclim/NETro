#!/usr/bin/env python3
"""
Exercițiul 4.01: Implementare Protocol TCP Custom
==================================================

Obiectiv: Implementați un protocol TEXT modificat care suportă comenzi multiple.

Specificații protocol:
- Format: "<COMMAND> <LENGTH> <PAYLOAD>"
- COMMAND: ECHO, UPPER, LOWER, REVERSE, COUNT
- LENGTH: lungimea payload-ului în bytes
- PAYLOAD: datele text

Exemple:
- "ECHO 5 hello"  -> server răspunde "hello"
- "UPPER 5 hello" -> server răspunde "HELLO"
- "LOWER 5 HELLO" -> server răspunde "hello"
- "REVERSE 5 hello" -> server răspunde "olleh"
- "COUNT 5 hello" -> server răspunde "5" (număr caractere)

TODO-uri de implementat:
1. parse_command() - parsează comanda din mesaj
2. execute_command() - execută comanda și returnează rezultat
3. handle_client() - gestionează comunicarea cu clientul
4. Server principal cu threading

Autor: Revolvix&Hypotheticalandrei
Săptămâna 4 - Exercițiu practic TCP
"""

import socket
import threading
import sys

# Constante protocol
VALID_COMMANDS = {'ECHO', 'UPPER', 'LOWER', 'REVERSE', 'COUNT'}
DEFAULT_PORT = 3334
BUFFER_SIZE = 4096


def parse_command(data: str) -> tuple:
    """
    Parsează mesajul primit și extrage comanda, lungimea și payload-ul.
    
    Args:
        data: String în format "<COMMAND> <LENGTH> <PAYLOAD>"
    
    Returns:
        tuple: (command, length, payload) sau (None, None, None) dacă invalid
    
    Exemple:
        >>> parse_command("ECHO 5 hello")
        ('ECHO', 5, 'hello')
        >>> parse_command("UPPER 11 hello world")
        ('UPPER', 11, 'hello world')
        >>> parse_command("INVALID")
        (None, None, None)
    
    TODO: Implementați această funcție
    Hints:
    - Folosiți split(' ', 2) pentru a separa în maxim 3 părți
    - Validați că prima parte este în VALID_COMMANDS
    - Convertiți a doua parte la int
    - Verificați că lungimea payload-ului corespunde cu valoarea declarată
    """
    # TODO: Implementare
    # Pasul 1: Separați string-ul în părți
    # parts = data.split(' ', 2)
    
    # Pasul 2: Validați numărul de părți
    # if len(parts) < 3:
    #     return (None, None, None)
    
    # Pasul 3: Extrageți și validați comanda
    # command = parts[0].upper()
    # if command not in VALID_COMMANDS:
    #     return (None, None, None)
    
    # Pasul 4: Extrageți și validați lungimea
    # try:
    #     length = int(parts[1])
    # except ValueError:
    #     return (None, None, None)
    
    # Pasul 5: Extrageți payload-ul
    # payload = parts[2]
    
    # Pasul 6: Verificați consistența lungimii
    # if len(payload.encode('utf-8')) != length:
    #     return (None, None, None)
    
    # return (command, length, payload)
    
    pass  # Înlocuiți cu implementarea


def execute_command(command: str, payload: str) -> str:
    """
    Execută comanda specificată pe payload.
    
    Args:
        command: Una din VALID_COMMANDS
        payload: Datele pe care se aplică comanda
    
    Returns:
        str: Rezultatul execuției comenzii
    
    Exemple:
        >>> execute_command('ECHO', 'hello')
        'hello'
        >>> execute_command('UPPER', 'hello')
        'HELLO'
        >>> execute_command('REVERSE', 'hello')
        'olleh'
    
    TODO: Implementați această funcție
    """
    # TODO: Implementare
    # if command == 'ECHO':
    #     return payload
    # elif command == 'UPPER':
    #     return payload.upper()
    # elif command == 'LOWER':
    #     return payload.lower()
    # elif command == 'REVERSE':
    #     return payload[::-1]
    # elif command == 'COUNT':
    #     return str(len(payload))
    # else:
    #     return 'ERROR: Unknown command'
    
    pass  # Înlocuiți cu implementarea


def format_response(result: str) -> str:
    """
    Formatează răspunsul pentru client.
    
    Format: "<LENGTH> <RESULT>"
    
    Args:
        result: Rezultatul de trimis
    
    Returns:
        str: Răspunsul formatat
    
    TODO: Implementați această funcție
    """
    # TODO: Implementare
    # length = len(result.encode('utf-8'))
    # return f"{length} {result}"
    
    pass  # Înlocuiți cu implementarea


def handle_client(client_socket: socket.socket, address: tuple):
    """
    Gestionează comunicarea cu un client.
    
    Args:
        client_socket: Socket-ul clientului
        address: Tuple (ip, port) al clientului
    
    TODO: Implementați această funcție
    Hints:
    - Folosiți un loop while pentru a procesa multiple mesaje
    - Apelați parse_command(), execute_command(), format_response()
    - Gestionați excepțiile (ConnectionResetError, etc.)
    - Închideți socket-ul la final
    """
    print(f"[+] Client conectat: {address}")
    
    # TODO: Implementare
    # try:
    #     while True:
    #         # Primire date
    #         data = client_socket.recv(BUFFER_SIZE)
    #         if not data:
    #             break
    #         
    #         message = data.decode('utf-8').strip()
    #         print(f"[{address}] Primit: {message}")
    #         
    #         # Parsare comandă
    #         command, length, payload = parse_command(message)
    #         
    #         if command is None:
    #             response = format_response("ERROR: Invalid command format")
    #         else:
    #             result = execute_command(command, payload)
    #             response = format_response(result)
    #         
    #         # Trimitere răspuns
    #         client_socket.sendall(response.encode('utf-8'))
    #         print(f"[{address}] Trimis: {response}")
    #         
    # except ConnectionResetError:
    #     print(f"[-] Conexiune resetată: {address}")
    # except Exception as e:
    #     print(f"[!] Eroare: {e}")
    # finally:
    #     client_socket.close()
    #     print(f"[-] Client deconectat: {address}")
    
    pass  # Înlocuiți cu implementarea


def start_server(host: str = '0.0.0.0', port: int = DEFAULT_PORT):
    """
    Pornește serverul TCP multi-threaded.
    
    Args:
        host: Adresa de ascultare
        port: Portul de ascultare
    
    TODO: Implementați această funcție
    """
    # TODO: Implementare
    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 
    # try:
    #     server_socket.bind((host, port))
    #     server_socket.listen(5)
    #     print(f"[*] Server pornit pe {host}:{port}")
    #     print(f"[*] Comenzi acceptate: {', '.join(VALID_COMMANDS)}")
    #     
    #     while True:
    #         client_socket, address = server_socket.accept()
    #         client_thread = threading.Thread(
    #             target=handle_client,
    #             args=(client_socket, address),
    #             daemon=True
    #         )
    #         client_thread.start()
    #         
    # except KeyboardInterrupt:
    #     print("\n[*] Server oprit")
    # finally:
    #     server_socket.close()
    
    pass  # Înlocuiți cu implementarea


# =============================================================================
# CLIENT DE TEST (nu trebuie modificat)
# =============================================================================

def test_client(host: str = 'localhost', port: int = DEFAULT_PORT):
    """
    Client de test pentru verificarea implementării.
    """
    test_cases = [
        ("ECHO 5 hello", "5 hello"),
        ("UPPER 5 hello", "5 HELLO"),
        ("LOWER 5 HELLO", "5 hello"),
        ("REVERSE 5 hello", "5 olleh"),
        ("COUNT 5 hello", "1 5"),
        ("UPPER 11 hello world", "11 HELLO WORLD"),
    ]
    
    print(f"\n{'='*60}")
    print("TEST CLIENT - Verificare implementare")
    print(f"{'='*60}\n")
    
    passed = 0
    failed = 0
    
    for test_input, expected in test_cases:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            
            sock.sendall(test_input.encode('utf-8'))
            response = sock.recv(BUFFER_SIZE).decode('utf-8').strip()
            
            sock.close()
            
            if response == expected:
                print(f"✓ PASS: {test_input}")
                print(f"        Răspuns: {response}")
                passed += 1
            else:
                print(f"✗ FAIL: {test_input}")
                print(f"        Așteptat: {expected}")
                print(f"        Primit:   {response}")
                failed += 1
                
        except Exception as e:
            print(f"✗ ERROR: {test_input}")
            print(f"         {e}")
            failed += 1
        
        print()
    
    print(f"{'='*60}")
    print(f"Rezultat: {passed}/{passed+failed} teste trecute")
    print(f"{'='*60}")
    
    return failed == 0


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Mod test client
        host = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
        port = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_PORT
        success = test_client(host, port)
        sys.exit(0 if success else 1)
    else:
        # Mod server
        port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
        start_server(port=port)
