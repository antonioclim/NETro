#!/usr/bin/env python3
"""
================================================================================
TEMPLATE: SIMULARE ANYCAST UDP
================================================================================
Exercițiu de completat: Implementarea conceptului anycast la nivel aplicație.
Anycast = mai multe servere au aceeași "adresă" logică, clientul primește
răspuns de la cel mai "apropiat" (în termeni de latență sau disponibilitate).

CONCEPTE FUNDAMENTALE:
  - Anycast: O adresă, mai multe destinații, rutare către cel mai bun
  - Discovery: Clientul întreabă "cine e disponibil?" via broadcast/multicast
  - Load Balancing: Distribuirea cererilor între servere disponibile
  - Health Check: Verificarea periodică a disponibilității serverelor
  - Failover: Comutare automată la alt server când unul devine indisponibil

ARHITECTURA SIMULATĂ:
  ┌─────────────────────────────────────────────────────────────────────┐
  │                         ANYCAST SIMULATION                          │
  │                                                                     │
  │   Client                        Servers (aceeași funcție)          │
  │   ┌──────┐    DISCOVERY_REQ    ┌──────────┐                        │
  │   │      │ ─────────────────▶  │ Server A │  (replica 1)           │
  │   │      │                     └──────────┘                        │
  │   │      │    DISCOVERY_REQ    ┌──────────┐                        │
  │   │      │ ─────────────────▶  │ Server B │  (replica 2)           │
  │   │      │                     └──────────┘                        │
  │   │      │    DISCOVERY_REQ    ┌──────────┐                        │
  │   │      │ ─────────────────▶  │ Server C │  (replica 3)           │
  │   └──────┘                     └──────────┘                        │
  │      │                              │                              │
  │      │     DISCOVERY_RESP (RTT)     │                              │
  │      │◀─────────────────────────────┘                              │
  │      │                                                             │
  │      │          REQUEST ──▶ Cel mai rapid server                   │
  │      │◀────────── RESPONSE                                         │
  └─────────────────────────────────────────────────────────────────────┘

PROTOCOL:
  DISCOVERY_REQ   - Client întreabă "cine e disponibil?"
  DISCOVERY_RESP  - Server răspunde cu ID, load, și latență simulată
  REQUEST         - Client trimite cerere către serverul selectat
  RESPONSE        - Server procesează și răspunde

CERINȚE:
  Python 3.8+

TODO PENTRU STUDENȚI:
  1. Implementarea trimiterii broadcast pentru discovery
  2. Colectarea răspunsurilor de la servere
  3. Selectarea serverului optim (cel mai rapid)
  4. Implementarea failover la server alternativ
  5. Menținerea cache-ului de servere disponibile

UTILIZARE:
  # Terminal 1, 2, 3 - Pornește 3 servere
  python3 tpl_udp_anycast.py server --id A --port 6001
  python3 tpl_udp_anycast.py server --id B --port 6002
  python3 tpl_udp_anycast.py server --id C --port 6003
  
  # Terminal 4 - Rulează clientul
  python3 tpl_udp_anycast.py client --discover --requests 5

AUTOR: Starter Kit S3 - Rețele de Calculatoare ASE-CSIE
================================================================================
"""

import socket
import struct
import argparse
import sys
import time
import random
import threading
import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict

# =============================================================================
# CONSTANTE ȘI CONFIGURARE
# =============================================================================

# Configurare implicită
DEFAULT_BROADCAST_ADDR = "255.255.255.255"
DEFAULT_DISCOVERY_PORT = 6000  # Port pentru discovery broadcast
DEFAULT_BUFFER_SIZE = 1024
DEFAULT_TIMEOUT = 2.0

# Tipuri de mesaje
MSG_DISCOVERY_REQ = "DISCOVER"
MSG_DISCOVERY_RESP = "AVAILABLE"
MSG_REQUEST = "REQUEST"
MSG_RESPONSE = "RESPONSE"
MSG_HEALTHCHECK = "PING"
MSG_HEALTHCHECK_RESP = "PONG"


# =============================================================================
# STRUCTURI DE DATE
# =============================================================================

@dataclass
class ServerInfo:
    """Informații despre un server descoperit."""
    server_id: str
    address: str
    port: int
    load: float  # 0.0 - 1.0 (procent load)
    rtt_ms: float  # Round-trip time în milisecunde
    last_seen: float  # Timestamp ultima comunicare
    capabilities: List[str]  # Lista de servicii oferite
    
    def is_healthy(self, max_age_sec: float = 30.0) -> bool:
        """Verifică dacă serverul este considerat healthy."""
        age = time.time() - self.last_seen
        return age < max_age_sec and self.load < 0.95


@dataclass
class Message:
    """Structura unui mesaj în protocolul anycast."""
    msg_type: str
    sender_id: str
    payload: dict
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
    
    def to_json(self) -> str:
        """Serializează mesajul în JSON."""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, data: str) -> 'Message':
        """Deserializează din JSON."""
        d = json.loads(data)
        return cls(**d)


# =============================================================================
# FUNCȚII AUXILIARE
# =============================================================================

def get_timestamp() -> str:
    """Timestamp formatat pentru logging."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(level: str, message: str):
    """Logging cu culori."""
    colors = {
        "INFO": "\033[94m",
        "ERROR": "\033[91m",
        "DEBUG": "\033[90m",
        "SERVER": "\033[92m",
        "CLIENT": "\033[93m",
        "DISCOVER": "\033[95m"
    }
    reset = "\033[0m"
    color = colors.get(level, "")
    print(f"[{get_timestamp()}] {color}[{level}]{reset} {message}")


# =============================================================================
# SERVER ANYCAST
# =============================================================================

class AnycastServer:
    """
    Server care participă în grupul anycast.
    
    Răspunde la discovery requests și procesează cereri de la clienți.
    """
    
    def __init__(
        self,
        server_id: str,
        port: int,
        discovery_port: int = DEFAULT_DISCOVERY_PORT,
        simulated_load: float = 0.0,
        simulated_latency_ms: float = 0.0
    ):
        """
        Inițializează serverul anycast.
        
        Args:
            server_id: Identificator unic al serverului
            port: Portul pe care ascultă cereri
            discovery_port: Portul pentru discovery (broadcast)
            simulated_load: Load simulat (0.0 - 1.0)
            simulated_latency_ms: Latență adițională simulată
        """
        self.server_id = server_id
        self.port = port
        self.discovery_port = discovery_port
        self.simulated_load = simulated_load
        self.simulated_latency_ms = simulated_latency_ms
        
        self.socket_discovery: Optional[socket.socket] = None
        self.socket_service: Optional[socket.socket] = None
        self.running = False
        
        self.request_count = 0
        self.capabilities = ["echo", "time", "info"]
        
        log("SERVER", f"Server {server_id} inițializat pe port {port}")
    
    def setup_sockets(self) -> bool:
        """Configurează socket-urile pentru discovery și servicii."""
        try:
            # Socket pentru discovery (ascultă broadcast-uri)
            self.socket_discovery = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_discovery.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_discovery.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.socket_discovery.bind(('', self.discovery_port))
            
            # Socket pentru serviciu (cereri directe)
            self.socket_service = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_service.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_service.bind(('', self.port))
            
            log("SERVER", f"Socket-uri configurate (discovery: {self.discovery_port}, service: {self.port})")
            return True
            
        except socket.error as e:
            log("ERROR", f"Eroare configurare socket: {e}")
            return False
    
    def handle_discovery(self, data: bytes, addr: Tuple[str, int]):
        """Procesează o cerere de discovery și răspunde."""
        try:
            msg = Message.from_json(data.decode('utf-8'))
            
            if msg.msg_type == MSG_DISCOVERY_REQ:
                log("DISCOVER", f"Discovery request de la {addr[0]}")
                
                # Simulează latența
                if self.simulated_latency_ms > 0:
                    time.sleep(self.simulated_latency_ms / 1000.0)
                
                # Construiește răspuns
                response = Message(
                    msg_type=MSG_DISCOVERY_RESP,
                    sender_id=self.server_id,
                    payload={
                        "port": self.port,
                        "load": self.simulated_load + (self.request_count * 0.01),
                        "capabilities": self.capabilities,
                        "uptime": time.time()
                    }
                )
                
                self.socket_discovery.sendto(
                    response.to_json().encode('utf-8'),
                    addr
                )
                
                log("DISCOVER", f"Trimis răspuns discovery către {addr[0]}")
                
        except Exception as e:
            log("ERROR", f"Eroare procesare discovery: {e}")
    
    def handle_request(self, data: bytes, addr: Tuple[str, int]):
        """Procesează o cerere de la client."""
        try:
            msg = Message.from_json(data.decode('utf-8'))
            
            if msg.msg_type == MSG_REQUEST:
                self.request_count += 1
                log("SERVER", f"Cerere #{self.request_count} de la {addr[0]}: {msg.payload}")
                
                # Simulează latența de procesare
                if self.simulated_latency_ms > 0:
                    time.sleep(self.simulated_latency_ms / 1000.0)
                
                # Procesează cererea
                result = self.process_request(msg.payload)
                
                # Construiește și trimite răspuns
                response = Message(
                    msg_type=MSG_RESPONSE,
                    sender_id=self.server_id,
                    payload={
                        "result": result,
                        "server_id": self.server_id,
                        "request_num": self.request_count
                    }
                )
                
                self.socket_service.sendto(
                    response.to_json().encode('utf-8'),
                    addr
                )
                
                log("SERVER", f"Răspuns trimis către {addr[0]}")
                
            elif msg.msg_type == MSG_HEALTHCHECK:
                # Health check - răspunde rapid
                response = Message(
                    msg_type=MSG_HEALTHCHECK_RESP,
                    sender_id=self.server_id,
                    payload={"status": "healthy", "load": self.simulated_load}
                )
                self.socket_service.sendto(
                    response.to_json().encode('utf-8'),
                    addr
                )
                
        except Exception as e:
            log("ERROR", f"Eroare procesare cerere: {e}")
    
    def process_request(self, payload: dict) -> str:
        """Procesează payload-ul cererii și returnează rezultat."""
        command = payload.get("command", "echo")
        data = payload.get("data", "")
        
        if command == "echo":
            return f"[Server {self.server_id}] Echo: {data}"
        elif command == "time":
            return f"[Server {self.server_id}] Ora: {datetime.now().isoformat()}"
        elif command == "info":
            return f"[Server {self.server_id}] Cereri procesate: {self.request_count}"
        else:
            return f"[Server {self.server_id}] Comandă necunoscută: {command}"
    
    def run(self):
        """Rulează bucla principală a serverului."""
        if not self.setup_sockets():
            return
        
        self.running = True
        log("SERVER", f"Server {self.server_id} pornit. Aștept cereri...")
        
        # Thread separat pentru discovery
        discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        discovery_thread.start()
        
        # Bucla principală pentru servicii
        try:
            while self.running:
                try:
                    self.socket_service.settimeout(1.0)
                    data, addr = self.socket_service.recvfrom(DEFAULT_BUFFER_SIZE)
                    self.handle_request(data, addr)
                except socket.timeout:
                    continue
                except socket.error as e:
                    if self.running:
                        log("ERROR", f"Eroare recepție: {e}")
                        
        except KeyboardInterrupt:
            log("SERVER", "\nOprire server...")
        finally:
            self.cleanup()
    
    def _discovery_loop(self):
        """Buclă pentru procesarea cererilor de discovery."""
        while self.running:
            try:
                self.socket_discovery.settimeout(1.0)
                data, addr = self.socket_discovery.recvfrom(DEFAULT_BUFFER_SIZE)
                self.handle_discovery(data, addr)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    log("ERROR", f"Eroare în discovery loop: {e}")
    
    def cleanup(self):
        """Eliberează resursele."""
        self.running = False
        if self.socket_discovery:
            self.socket_discovery.close()
        if self.socket_service:
            self.socket_service.close()
        log("SERVER", f"Server {self.server_id} oprit")


# =============================================================================
# CLIENT ANYCAST
# =============================================================================

class AnycastClient:
    """
    Client care descoperă și utilizează servere anycast.
    
    Implementează discovery, selecție bazată pe latență, și failover.
    """
    
    def __init__(
        self,
        discovery_port: int = DEFAULT_DISCOVERY_PORT,
        discovery_timeout: float = DEFAULT_TIMEOUT
    ):
        """
        Inițializează clientul anycast.
        
        Args:
            discovery_port: Portul pentru discovery broadcast
            discovery_timeout: Timeout pentru așteptarea răspunsurilor
        """
        self.discovery_port = discovery_port
        self.discovery_timeout = discovery_timeout
        
        self.socket: Optional[socket.socket] = None
        self.known_servers: Dict[str, ServerInfo] = {}
        self.preferred_server: Optional[ServerInfo] = None
        
        log("CLIENT", "Client anycast inițializat")
    
    def setup_socket(self) -> bool:
        """Configurează socket-ul clientului."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # TODO [1]: Configurați opțiunea SO_BROADCAST
            # Indicii:
            #   - Necesară pentru a trimite pachete broadcast
            #   - Folosiți setsockopt cu SOL_SOCKET
            
            # === ÎNCEPE CODUL TĂU ===
            pass  # self.socket.setsockopt(...)
            # === SFÂRȘIT CODUL TĂU ===
            
            self.socket.bind(('', 0))  # Port efemer
            log("CLIENT", "Socket configurat")
            return True
            
        except socket.error as e:
            log("ERROR", f"Eroare configurare socket: {e}")
            return False
    
    def discover_servers(self) -> List[ServerInfo]:
        """
        Descoperă serverele disponibile prin broadcast.
        
        Returns:
            Lista de servere descoperite, sortate după RTT
        """
        log("DISCOVER", f"Trimit discovery broadcast pe port {self.discovery_port}...")
        
        # TODO [2]: Trimiteți cererea de discovery în broadcast
        # Indicii:
        #   - Construiți un mesaj Message cu tip MSG_DISCOVERY_REQ
        #   - Folosiți sendto către (DEFAULT_BROADCAST_ADDR, self.discovery_port)
        #   - Înregistrați timpul de trimitere pentru calcul RTT
        
        # === ÎNCEPE CODUL TĂU ===
        discovery_msg = Message(
            msg_type=MSG_DISCOVERY_REQ,
            sender_id="client",
            payload={}
        )
        # Trimite broadcast...
        # === SFÂRȘIT CODUL TĂU ===
        
        # TODO [3]: Colectați răspunsurile de la servere
        # Indicii:
        #   - Setați timeout pe socket
        #   - Bucla pentru a primi mai multe răspunsuri
        #   - Pentru fiecare răspuns, calculați RTT
        #   - Creați obiecte ServerInfo și adăugați în known_servers
        
        # === ÎNCEPE CODUL TĂU ===
        servers = []
        # Colectare răspunsuri...
        # === SFÂRȘIT CODUL TĂU ===
        
        # Sortează după RTT
        if self.known_servers:
            servers = sorted(
                self.known_servers.values(),
                key=lambda s: (s.rtt_ms, s.load)
            )
            
            log("DISCOVER", f"Descoperite {len(servers)} servere:")
            for s in servers:
                log("DISCOVER", f"  {s.server_id}: {s.address}:{s.port} "
                              f"(RTT: {s.rtt_ms:.1f}ms, load: {s.load:.1%})")
        else:
            log("DISCOVER", "Niciun server descoperit")
        
        return servers
    
    def select_best_server(self) -> Optional[ServerInfo]:
        """
        Selectează cel mai bun server disponibil.
        
        Returns:
            ServerInfo pentru cel mai bun server sau None
        """
        # TODO [4]: Implementați selecția serverului optim
        # Indicii:
        #   - Filtrați serverele care sunt healthy (is_healthy())
        #   - Sortați după criteriu (RTT, load, sau combinație)
        #   - Returnați primul din listă sau None
        
        # === ÎNCEPE CODUL TĂU ===
        pass  # Implementare selecție
        # === SFÂRȘIT CODUL TĂU ===
        
        # Placeholder
        if self.known_servers:
            servers = sorted(
                self.known_servers.values(),
                key=lambda s: s.rtt_ms
            )
            self.preferred_server = servers[0]
            log("CLIENT", f"Server selectat: {self.preferred_server.server_id}")
            return self.preferred_server
        
        return None
    
    def send_request(
        self,
        command: str,
        data: str = "",
        server: Optional[ServerInfo] = None
    ) -> Optional[str]:
        """
        Trimite o cerere către un server anycast.
        
        Args:
            command: Comanda de executat (echo, time, info)
            data: Date asociate comenzii
            server: Server specific sau None pentru auto-select
            
        Returns:
            Răspunsul serverului sau None
        """
        # Selectează server dacă nu e specificat
        target = server or self.preferred_server
        
        if not target:
            log("ERROR", "Niciun server disponibil")
            return None
        
        # Construiește cererea
        request = Message(
            msg_type=MSG_REQUEST,
            sender_id="client",
            payload={"command": command, "data": data}
        )
        
        try:
            log("CLIENT", f"Trimit cerere către {target.server_id} ({target.address}:{target.port})")
            
            self.socket.sendto(
                request.to_json().encode('utf-8'),
                (target.address, target.port)
            )
            
            # Așteaptă răspuns
            self.socket.settimeout(self.discovery_timeout)
            data_recv, addr = self.socket.recvfrom(DEFAULT_BUFFER_SIZE)
            
            response = Message.from_json(data_recv.decode('utf-8'))
            
            if response.msg_type == MSG_RESPONSE:
                result = response.payload.get("result", "")
                log("CLIENT", f"Răspuns primit: {result}")
                return result
            
        except socket.timeout:
            log("ERROR", f"Timeout așteptând răspuns de la {target.server_id}")
            
            # TODO [5]: Implementați failover la alt server
            # Indicii:
            #   - Eliminați serverul curent din known_servers
            #   - Selectați alt server cu select_best_server()
            #   - Reîncercați cererea (cu limită de reîncercări)
            
            # === ÎNCEPE CODUL TĂU ===
            pass  # Failover...
            # === SFÂRȘIT CODUL TĂU ===
            
        except Exception as e:
            log("ERROR", f"Eroare: {e}")
        
        return None
    
    def run_demo(self, num_requests: int = 5):
        """Rulează o demonstrație a clientului anycast."""
        if not self.setup_socket():
            return
        
        log("CLIENT", "Pornesc demonstrație anycast...")
        
        # Discovery
        servers = self.discover_servers()
        
        if not servers:
            log("CLIENT", "Nu am găsit servere. Asigură-te că rulează servere.")
            return
        
        # Selectează cel mai bun server
        self.select_best_server()
        
        # Trimite cereri
        commands = ["echo", "time", "info"]
        
        for i in range(num_requests):
            cmd = random.choice(commands)
            data = f"Cerere #{i+1}"
            
            log("CLIENT", f"\n--- Cerere {i+1}/{num_requests} ---")
            result = self.send_request(cmd, data)
            
            if result:
                log("CLIENT", f"✓ Succes: {result}")
            else:
                log("CLIENT", "✗ Eșec")
            
            time.sleep(0.5)
        
        self.cleanup()
        log("CLIENT", "\nDemonstrație completă!")
    
    def cleanup(self):
        """Eliberează resursele."""
        if self.socket:
            self.socket.close()


# =============================================================================
# SOLUȚII PENTRU TODO-URI (PENTRU INSTRUCTOR)
# =============================================================================

"""
SOLUȚII - NU DISTRIBUIȚI STUDENȚILOR:

TODO [1] - SO_BROADCAST:
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

TODO [2] - Trimitere broadcast:
    discovery_msg = Message(
        msg_type=MSG_DISCOVERY_REQ,
        sender_id="client",
        payload={}
    )
    send_time = time.time()
    self.socket.sendto(
        discovery_msg.to_json().encode('utf-8'),
        (DEFAULT_BROADCAST_ADDR, self.discovery_port)
    )

TODO [3] - Colectare răspunsuri:
    self.socket.settimeout(self.discovery_timeout)
    end_time = time.time() + self.discovery_timeout
    
    while time.time() < end_time:
        try:
            data, addr = self.socket.recvfrom(DEFAULT_BUFFER_SIZE)
            rtt = (time.time() - send_time) * 1000
            
            msg = Message.from_json(data.decode('utf-8'))
            if msg.msg_type == MSG_DISCOVERY_RESP:
                server = ServerInfo(
                    server_id=msg.sender_id,
                    address=addr[0],
                    port=msg.payload["port"],
                    load=msg.payload["load"],
                    rtt_ms=rtt,
                    last_seen=time.time(),
                    capabilities=msg.payload.get("capabilities", [])
                )
                self.known_servers[server.server_id] = server
        except socket.timeout:
            break

TODO [4] - Selecție server:
    healthy = [s for s in self.known_servers.values() if s.is_healthy()]
    if not healthy:
        return None
    healthy.sort(key=lambda s: (s.rtt_ms, s.load))
    self.preferred_server = healthy[0]
    return self.preferred_server

TODO [5] - Failover:
    if target.server_id in self.known_servers:
        del self.known_servers[target.server_id]
    new_server = self.select_best_server()
    if new_server and retry_count < 3:
        return self.send_request(command, data, new_server, retry_count + 1)
"""


# =============================================================================
# INTERFAȚĂ LINIE DE COMANDĂ
# =============================================================================

def parse_arguments() -> argparse.Namespace:
    """Parsează argumentele liniei de comandă."""
    parser = argparse.ArgumentParser(
        description="Simulare Anycast UDP - Server și Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLE:
  # Pornește servere (în terminale separate)
  python3 tpl_udp_anycast.py server --id A --port 6001
  python3 tpl_udp_anycast.py server --id B --port 6002 --load 0.5
  python3 tpl_udp_anycast.py server --id C --port 6003 --latency 100
  
  # Rulează client
  python3 tpl_udp_anycast.py client --discover
  python3 tpl_udp_anycast.py client --requests 10
        """
    )
    
    subparsers = parser.add_subparsers(dest="mode", help="Mod de operare")
    
    # Server
    server_parser = subparsers.add_parser("server", help="Pornește un server anycast")
    server_parser.add_argument("--id", type=str, required=True, help="ID unic server")
    server_parser.add_argument("--port", type=int, required=True, help="Port serviciu")
    server_parser.add_argument("--discovery-port", type=int, default=DEFAULT_DISCOVERY_PORT,
                               help=f"Port discovery (default: {DEFAULT_DISCOVERY_PORT})")
    server_parser.add_argument("--load", type=float, default=0.0,
                               help="Load simulat 0.0-1.0 (default: 0.0)")
    server_parser.add_argument("--latency", type=float, default=0.0,
                               help="Latență simulată în ms (default: 0)")
    
    # Client
    client_parser = subparsers.add_parser("client", help="Rulează client anycast")
    client_parser.add_argument("--discover", action="store_true", help="Doar discovery")
    client_parser.add_argument("--requests", type=int, default=5, help="Număr cereri (default: 5)")
    client_parser.add_argument("--discovery-port", type=int, default=DEFAULT_DISCOVERY_PORT,
                               help=f"Port discovery (default: {DEFAULT_DISCOVERY_PORT})")
    client_parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                               help=f"Timeout (default: {DEFAULT_TIMEOUT}s)")
    
    return parser.parse_args()


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Punct de intrare principal."""
    args = parse_arguments()
    
    if not args.mode:
        print("Utilizare: python3 tpl_udp_anycast.py {server|client} --help")
        print("\n⚠️  Acest template conține secțiuni TODO de completat!")
        sys.exit(1)
    
    if args.mode == "server":
        server = AnycastServer(
            server_id=args.id,
            port=args.port,
            discovery_port=args.discovery_port,
            simulated_load=args.load,
            simulated_latency_ms=args.latency
        )
        server.run()
        
    elif args.mode == "client":
        client = AnycastClient(
            discovery_port=args.discovery_port,
            discovery_timeout=args.timeout
        )
        
        if args.discover:
            # Doar discovery
            if client.setup_socket():
                client.discover_servers()
                client.cleanup()
        else:
            client.run_demo(num_requests=args.requests)


if __name__ == "__main__":
    main()
