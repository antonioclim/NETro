#!/usr/bin/env python3
"""
Exercițiul 1.02: Server și client TCP simplu
============================================
Rețele de Calculatoare - Săptămâna 1
ASE București

Obiective:
- Înțelegerea modelului client-server
- Utilizarea socket-urilor TCP în Python
- Observarea comportamentului de conectare/deconectare

Nivel: Începător-Mediu
Timp estimat: 25 minute

👥 PAIR PROGRAMMING: Acest exercițiu e ideal pentru lucru în perechi!
   - Driver: scrie codul în editor
   - Navigator: verifică sintaxa, sugerează îmbunătățiri
   - Schimbați rolurile la fiecare funcție nouă
"""

# =============================================================================
# SETUP_ENVIRONMENT
# =============================================================================
import socket
import threading
import time
import sys
from datetime import datetime


# =============================================================================
# SERVER TCP SIMPLU
# =============================================================================

def create_tcp_server(host: str = "127.0.0.1", port: int = 9999) -> None:
    """
    Creează un server TCP simplu care primește și afișează mesaje.
    
    Serverul:
    1. Creează un socket TCP
    2. Îl leagă (bind) la adresă și port
    3. Începe să asculte (listen)
    4. Acceptă conexiuni și procesează mesaje
    
    Args:
        host: Adresa IP pe care ascultă serverul
        port: Portul pe care ascultă
    
    🎯 PREDICȚIE: Ce va afișa `ss -tlnp | grep {port}` după ce pornește serverul?
    """
    # -------------------------------------------------------------------------
    # CREATE_SOCKET
    # -------------------------------------------------------------------------
    # SOCK_STREAM = TCP, AF_INET = IPv4
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # -------------------------------------------------------------------------
    # CONFIGURE_OPTIONS
    # -------------------------------------------------------------------------
    # SO_REUSEADDR permite reutilizarea imediată a portului după închidere
    # Fără această opțiune, portul rămâne în TIME_WAIT ~2 minute
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # ---------------------------------------------------------------------
        # BIND_SOCKET
        # ---------------------------------------------------------------------
        server_socket.bind((host, port))
        print(f"[SERVER] Socket legat la {host}:{port}")
        
        # ---------------------------------------------------------------------
        # START_LISTENING
        # ---------------------------------------------------------------------
        # backlog=5 = maxim 5 conexiuni în așteptare
        server_socket.listen(5)
        print(f"[SERVER] Ascultare activă pe port {port}...")
        print(f"[SERVER] Apăsați Ctrl+C pentru oprire\n")
        
        # ---------------------------------------------------------------------
        # ACCEPT_CONNECTIONS
        # ---------------------------------------------------------------------
        while True:
            # accept() blochează până vine un client
            client_socket, client_address = server_socket.accept()
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] Conexiune nouă de la {client_address}")
            
            # -----------------------------------------------------------------
            # PROCESS_MESSAGES
            # -----------------------------------------------------------------
            try:
                while True:
                    # Primim date (maxim 1024 bytes per apel)
                    data = client_socket.recv(1024)
                    
                    if not data:
                        # Client deconectat (a trimis FIN)
                        print(f"[{timestamp}] Client {client_address} deconectat")
                        break
                    
                    message = data.decode('utf-8').strip()
                    print(f"[{timestamp}] Primit de la {client_address}: {message}")
                    
                    # ---------------------------------------------------------
                    # SEND_RESPONSE
                    # ---------------------------------------------------------
                    response = f"Server a primit: {message}\n"
                    client_socket.sendall(response.encode('utf-8'))
            
            # -----------------------------------------------------------------
            # HANDLE_CLIENT_ERRORS
            # -----------------------------------------------------------------
            except ConnectionResetError:
                print(f"[{timestamp}] Conexiune resetată de {client_address}")
            finally:
                client_socket.close()
    
    # -------------------------------------------------------------------------
    # HANDLE_SHUTDOWN
    # -------------------------------------------------------------------------
    except KeyboardInterrupt:
        print("\n[SERVER] Oprire...")
    finally:
        server_socket.close()
        print("[SERVER] Socket închis.")


# =============================================================================
# CLIENT TCP SIMPLU
# =============================================================================

def create_tcp_client(
    host: str = "127.0.0.1",
    port: int = 9999,
    messages: list[str] | None = None
) -> list[str]:
    """
    Creează un client TCP care trimite mesaje către server.
    
    Args:
        host: Adresa serverului
        port: Portul serverului
        messages: Lista de mesaje de trimis (sau citește de la stdin)
    
    Returns:
        Lista răspunsurilor primite de la server
    
    🎯 PREDICȚIE: Ce eroare apare dacă serverul nu rulează?
    """
    responses = []
    
    # -------------------------------------------------------------------------
    # CREATE_SOCKET
    # -------------------------------------------------------------------------
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # ---------------------------------------------------------------------
        # CONNECT_TO_SERVER
        # ---------------------------------------------------------------------
        print(f"[CLIENT] Conectare la {host}:{port}...")
        client_socket.connect((host, port))
        print(f"[CLIENT] Conectat!")
        
        # ---------------------------------------------------------------------
        # SEND_MESSAGES
        # ---------------------------------------------------------------------
        if messages:
            # Mod automatizat - trimitem mesajele din listă
            for msg in messages:
                print(f"[CLIENT] Trimit: {msg}")
                client_socket.sendall((msg + "\n").encode('utf-8'))
                
                # ---------------------------------------------------------
                # RECEIVE_RESPONSE
                # ---------------------------------------------------------
                response = client_socket.recv(1024).decode('utf-8').strip()
                print(f"[CLIENT] Răspuns: {response}")
                responses.append(response)
                
                time.sleep(0.1)  # Scurtă pauză între mesaje
        else:
            # Mod interactiv - citim de la stdin
            print("[CLIENT] Introduceți mesaje (Ctrl+D pentru ieșire):")
            try:
                while True:
                    msg = input("> ")
                    if msg:
                        client_socket.sendall((msg + "\n").encode('utf-8'))
                        response = client_socket.recv(1024).decode('utf-8').strip()
                        print(f"< {response}")
                        responses.append(response)
            except EOFError:
                print("\n[CLIENT] Ieșire...")
    
    # -------------------------------------------------------------------------
    # HANDLE_ERRORS
    # -------------------------------------------------------------------------
    except ConnectionRefusedError:
        print(f"[CLIENT] EROARE: Conexiune refuzată - serverul nu rulează?")
    except Exception as e:
        print(f"[CLIENT] EROARE: {e}")
    
    # -------------------------------------------------------------------------
    # CLEANUP_RESOURCES
    # -------------------------------------------------------------------------
    finally:
        client_socket.close()
        print("[CLIENT] Socket închis.")
    
    return responses


# =============================================================================
# SERVER UDP SIMPLU (pentru comparație)
# =============================================================================

def create_udp_server(host: str = "127.0.0.1", port: int = 8888) -> None:
    """
    Creează un server UDP simplu.
    
    Diferențe față de TCP:
    - Nu există connect/accept (connectionless)
    - recvfrom returnează și adresa expeditorului
    - Nu garantează ordinea sau livrarea mesajelor
    
    🎯 PREDICȚIE: Câte pachete va vedea tshark pentru un singur mesaj UDP?
    """
    # -------------------------------------------------------------------------
    # CREATE_SOCKET
    # -------------------------------------------------------------------------
    # SOCK_DGRAM = UDP (datagram)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # ---------------------------------------------------------------------
        # BIND_SOCKET
        # ---------------------------------------------------------------------
        server_socket.bind((host, port))
        print(f"[UDP SERVER] Ascultare pe {host}:{port}")
        print(f"[UDP SERVER] Apăsați Ctrl+C pentru oprire\n")
        
        # ---------------------------------------------------------------------
        # RECEIVE_DATAGRAMS
        # ---------------------------------------------------------------------
        while True:
            # recvfrom returnează (data, address) - nu există accept()!
            data, client_addr = server_socket.recvfrom(1024)
            message = data.decode('utf-8').strip()
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] UDP de la {client_addr}: {message}")
            
            # -----------------------------------------------------------------
            # SEND_RESPONSE
            # -----------------------------------------------------------------
            response = f"UDP Echo: {message}"
            server_socket.sendto(response.encode('utf-8'), client_addr)
    
    # -------------------------------------------------------------------------
    # HANDLE_SHUTDOWN
    # -------------------------------------------------------------------------
    except KeyboardInterrupt:
        print("\n[UDP SERVER] Oprire...")
    finally:
        server_socket.close()


def create_udp_client(
    host: str = "127.0.0.1",
    port: int = 8888,
    message: str = "Hello UDP"
) -> str | None:
    """
    Trimite un mesaj UDP și așteaptă răspuns.
    """
    # -------------------------------------------------------------------------
    # CREATE_SOCKET
    # -------------------------------------------------------------------------
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(2.0)  # Timeout 2 secunde
    
    try:
        # ---------------------------------------------------------------------
        # SEND_DATAGRAM
        # ---------------------------------------------------------------------
        print(f"[UDP CLIENT] Trimit către {host}:{port}: {message}")
        client_socket.sendto(message.encode('utf-8'), (host, port))
        
        # ---------------------------------------------------------------------
        # RECEIVE_RESPONSE
        # ---------------------------------------------------------------------
        data, server_addr = client_socket.recvfrom(1024)
        response = data.decode('utf-8')
        print(f"[UDP CLIENT] Răspuns: {response}")
        return response
    
    # -------------------------------------------------------------------------
    # HANDLE_ERRORS
    # -------------------------------------------------------------------------
    except socket.timeout:
        print("[UDP CLIENT] Timeout - niciun răspuns")
        return None
    finally:
        client_socket.close()


# =============================================================================
# DEMO: Server + Client în același script
# =============================================================================

def demo_tcp_communication() -> None:
    """
    Demonstrație: pornește server în background, trimite mesaje de la client.
    """
    HOST = "127.0.0.1"
    PORT = 9876
    
    print("\n" + "="*60)
    print(" Demo: Comunicare TCP client-server ".center(60))
    print("="*60 + "\n")
    
    # -------------------------------------------------------------------------
    # DEFINE_SERVER_THREAD
    # -------------------------------------------------------------------------
    def server_thread():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.settimeout(5.0)  # Timeout pentru accept
        
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"[DEMO SERVER] Ascult pe {HOST}:{PORT}")
        
        try:
            client_sock, addr = server_socket.accept()
            print(f"[DEMO SERVER] Client conectat: {addr}")
            
            while True:
                data = client_sock.recv(1024)
                if not data:
                    break
                msg = data.decode().strip()
                print(f"[DEMO SERVER] Primit: '{msg}'")
                client_sock.sendall(f"ACK:{msg}\n".encode())
                
            client_sock.close()
        except socket.timeout:
            print("[DEMO SERVER] Timeout - niciun client")
        finally:
            server_socket.close()
    
    # -------------------------------------------------------------------------
    # START_SERVER
    # -------------------------------------------------------------------------
    server = threading.Thread(target=server_thread, daemon=True)
    server.start()
    time.sleep(0.5)  # Așteptăm să pornească
    
    # -------------------------------------------------------------------------
    # RUN_CLIENT
    # -------------------------------------------------------------------------
    print(f"\n[DEMO CLIENT] Conectare la {HOST}:{PORT}")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((HOST, PORT))
        print("[DEMO CLIENT] Conectat!")
        
        test_messages = ["Hello", "Testing 123", "Goodbye"]
        
        for msg in test_messages:
            print(f"\n[DEMO CLIENT] Trimit: '{msg}'")
            client_socket.sendall((msg + "\n").encode())
            
            response = client_socket.recv(1024).decode().strip()
            print(f"[DEMO CLIENT] Răspuns: '{response}'")
            
            time.sleep(0.3)
            
    finally:
        client_socket.close()
        print("\n[DEMO CLIENT] Deconectat")
    
    # -------------------------------------------------------------------------
    # CLEANUP
    # -------------------------------------------------------------------------
    server.join(timeout=1)
    print("\n" + "="*60)
    print(" Demo încheiat ".center(60))
    print("="*60)


# =============================================================================
# AUTO-TEST
# =============================================================================

def run_self_test() -> bool:
    """Rulează auto-testele."""
    print("\n" + "="*60)
    print(" AUTO-TEST ".center(60, "="))
    print("="*60 + "\n")
    
    tests_passed = 0
    tests_total = 3
    
    # -------------------------------------------------------------------------
    # TEST_TCP_SOCKET_CREATION
    # -------------------------------------------------------------------------
    print("[TEST 1] Creare socket TCP...", end=" ")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.close()
        print("✓ PASS")
        tests_passed += 1
    except Exception as e:
        print(f"✗ FAIL ({e})")
    
    # -------------------------------------------------------------------------
    # TEST_BIND_RANDOM_PORT
    # -------------------------------------------------------------------------
    print("[TEST 2] Bind pe port aleator...", end=" ")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", 0))  # Port 0 = sistemul alege
        port = sock.getsockname()[1]
        sock.close()
        print(f"✓ PASS (port {port})")
        tests_passed += 1
    except Exception as e:
        print(f"✗ FAIL ({e})")
    
    # -------------------------------------------------------------------------
    # TEST_UDP_LOOPBACK
    # -------------------------------------------------------------------------
    print("[TEST 3] UDP send/recv loopback...", end=" ")
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind(("127.0.0.1", 0))
        port = server.getsockname()[1]
        
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.sendto(b"test", ("127.0.0.1", port))
        
        server.settimeout(1.0)
        data, addr = server.recvfrom(1024)
        
        server.close()
        client.close()
        
        if data == b"test":
            print("✓ PASS")
            tests_passed += 1
        else:
            print("✗ FAIL (date corupte)")
    except Exception as e:
        print(f"✗ FAIL ({e})")
    
    # -------------------------------------------------------------------------
    # DISPLAY_SUMMARY
    # -------------------------------------------------------------------------
    print(f"\nRezultat: {tests_passed}/{tests_total} teste trecute")
    return tests_passed == tests_total


# =============================================================================
# MAIN
# =============================================================================

def print_usage():
    print("""
Utilizare:
    python ex_1_02_tcp_server_client.py server [port]
    python ex_1_02_tcp_server_client.py client [host] [port]
    python ex_1_02_tcp_server_client.py udp-server [port]
    python ex_1_02_tcp_server_client.py udp-client [host] [port] [message]
    python ex_1_02_tcp_server_client.py demo
    python ex_1_02_tcp_server_client.py --test
    
Exemple:
    Terminal 1: python ex_1_02_tcp_server_client.py server 9999
    Terminal 2: python ex_1_02_tcp_server_client.py client localhost 9999
    
👥 PAIR PROGRAMMING TIP: Rulați serverul pe calculatorul Driver-ului,
   clientul pe calculatorul Navigator-ului (dacă sunteți în aceeași rețea).
""")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "--test":
        success = run_self_test()
        sys.exit(0 if success else 1)
    
    elif command == "server":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
        create_tcp_server(port=port)
    
    elif command == "client":
        host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 9999
        create_tcp_client(host=host, port=port)
    
    elif command == "udp-server":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8888
        create_udp_server(port=port)
    
    elif command == "udp-client":
        host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8888
        msg = sys.argv[4] if len(sys.argv) > 4 else "Hello UDP"
        create_udp_client(host=host, port=port, message=msg)
    
    elif command == "demo":
        demo_tcp_communication()
    
    else:
        print_usage()
