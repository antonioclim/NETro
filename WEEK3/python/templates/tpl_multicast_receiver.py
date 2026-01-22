#!/usr/bin/env python3
"""
================================================================================
TEMPLATE: MULTICAST RECEIVER CU FILTRARE MESAJE
================================================================================
Exercițiu de completat: Receptor multicast care filtrează mesajele primite
pe baza unui prefix configurat. Demonstrează procesarea selectivă a traficului.

OBIECTIVE:
  - Înțelegerea mecanismului de join la grupul multicast
  - Implementarea logicii de filtrare la nivel aplicație
  - Gestionarea mesajelor conform unui protocol simplu
  - Statistici și logging pentru debugging

PROTOCOL MESAJE:
  Mesajele urmează formatul: PREFIX:CONTINUT
  Exemple:
    - "ALERT:Server overload detected"
    - "INFO:User logged in"
    - "DEBUG:Processing request"
    - "METRIC:cpu=75,mem=80"

CERINȚE:
  Python 3.8+

TODO PENTRU STUDENȚI (marcate cu TODO):
  1. Configurarea opțiunii SO_REUSEADDR
  2. Join la grupul multicast folosind IP_ADD_MEMBERSHIP
  3. Parsarea mesajelor pentru extragerea prefix-ului
  4. Logica de filtrare bazată pe prefix
  5. Menținerea statisticilor de mesaje

UTILIZARE:
  python3 tpl_multicast_receiver.py --help
  python3 tpl_multicast_receiver.py --group 239.0.0.1 --port 5001 --prefix ALERT
  python3 tpl_multicast_receiver.py --prefix INFO,DEBUG --stats

AUTOR: Starter Kit S3 - Rețele de Calculatoare ASE-CSIE
================================================================================
"""

import socket
import struct
import argparse
import sys
from datetime import datetime
from typing import Optional, Set, Tuple, Dict

# =============================================================================
# CONSTANTE ȘI CONFIGURARE
# =============================================================================

# Adresa multicast implicită (din rangul administrativ local 239.0.0.0/8)
DEFAULT_MULTICAST_GROUP = "239.0.0.1"
DEFAULT_PORT = 5001
DEFAULT_BUFFER_SIZE = 1024
DEFAULT_PREFIX = "ALL"  # "ALL" = acceptă toate mesajele

# Prefixuri cunoscute (pentru validare și statistici)
KNOWN_PREFIXES = {"ALERT", "INFO", "DEBUG", "METRIC", "ERROR", "WARN", "STATUS"}


# =============================================================================
# FUNCȚII AUXILIARE
# =============================================================================

def get_timestamp() -> str:
    """Returnează timestamp formatat pentru logging."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def log_message(level: str, message: str):
    """
    Afișează mesaj de log formatat.
    
    Args:
        level: Nivelul mesajului (INFO, ERROR, DEBUG, RECV, etc.)
        message: Conținutul mesajului
    """
    colors = {
        "INFO": "\033[94m",    # Albastru
        "ERROR": "\033[91m",   # Roșu
        "DEBUG": "\033[90m",   # Gri
        "RECV": "\033[92m",    # Verde
        "FILTER": "\033[93m",  # Galben
        "STATS": "\033[95m"    # Magenta
    }
    reset = "\033[0m"
    color = colors.get(level, "")
    print(f"[{get_timestamp()}] {color}[{level}]{reset} {message}")


def parse_message(data: bytes) -> Tuple[Optional[str], str]:
    """
    Parsează mesajul primit pentru a extrage prefix-ul și conținutul.
    
    Format mesaj: PREFIX:CONTINUT
    
    Args:
        data: Bytes primiți de la rețea
        
    Returns:
        Tuple (prefix, continut) sau (None, mesaj_complet) dacă nu are prefix
    """
    try:
        message = data.decode('utf-8').strip()
        
        # TODO [3]: Implementați extragerea prefix-ului
        # Indicii:
        #   - Verificați dacă mesajul conține caracterul ':'
        #   - Folosiți split(':', 1) pentru a împărți în prefix și conținut
        #   - Dacă nu există ':', returnați (None, message)
        #   - Prefix-ul ar trebui normalizat (uppercase) pentru consistență
        
        # === ÎNCEPE CODUL TĂU ===
        pass  # Înlocuiește cu implementarea
        # === SFÂRȘIT CODUL TĂU ===
        
        # Placeholder - va fi înlocuit de studenți
        return (None, message)
        
    except UnicodeDecodeError:
        return (None, f"<binary data: {len(data)} bytes>")


def should_accept_message(prefix: Optional[str], filter_prefixes: Set[str]) -> bool:
    """
    Determină dacă mesajul trebuie acceptat bazat pe prefix.
    
    Args:
        prefix: Prefix-ul extras din mesaj (poate fi None)
        filter_prefixes: Set de prefixuri acceptate
        
    Returns:
        True dacă mesajul trebuie procesat, False altfel
    """
    # TODO [4]: Implementați logica de filtrare
    # Indicii:
    #   - Dacă filter_prefixes conține "ALL", acceptă toate mesajele
    #   - Dacă prefix este None și nu avem "ALL", respinge mesajul
    #   - Verificați dacă prefix-ul se află în filter_prefixes
    #   - Comparația ar trebui să fie case-insensitive
    
    # === ÎNCEPE CODUL TĂU ===
    pass  # Înlocuiește cu implementarea
    # === SFÂRȘIT CODUL TĂU ===
    
    # Placeholder - acceptă totul (va fi înlocuit)
    return True


# =============================================================================
# CLASA PRINCIPALĂ: MULTICAST RECEIVER
# =============================================================================

class MulticastReceiver:
    """
    Receptor multicast cu capacitate de filtrare a mesajelor.
    
    Atribute:
        group: Adresa grupului multicast
        port: Portul de ascultare
        filter_prefixes: Set de prefixuri acceptate
        socket: Socket UDP configurat pentru multicast
        stats: Dicționar cu statistici de mesaje
    """
    
    def __init__(
        self,
        group: str = DEFAULT_MULTICAST_GROUP,
        port: int = DEFAULT_PORT,
        filter_prefixes: Optional[Set[str]] = None,
        show_stats: bool = False
    ):
        """
        Inițializează receptorul multicast.
        
        Args:
            group: Adresa grupului multicast (ex: 239.0.0.1)
            port: Portul UDP pentru recepție
            filter_prefixes: Set de prefixuri de acceptat (None = toate)
            show_stats: Afișează statistici periodice
        """
        self.group = group
        self.port = port
        self.filter_prefixes = filter_prefixes or {"ALL"}
        self.show_stats = show_stats
        
        self.socket: Optional[socket.socket] = None
        self.running = False
        
        # TODO [5]: Inițializați structura pentru statistici
        # Indicii:
        #   - Creați un dicționar pentru a număra mesajele per prefix
        #   - Adăugați contoare pentru: total, acceptate, respinse
        
        # === ÎNCEPE CODUL TĂU ===
        self.stats: Dict[str, int] = {}
        # === SFÂRȘIT CODUL TĂU ===
        
        log_message("INFO", f"Receptor inițializat pentru grup {group}:{port}")
        log_message("INFO", f"Filtre active: {', '.join(self.filter_prefixes)}")
    
    def setup_socket(self) -> bool:
        """
        Configurează socket-ul pentru recepție multicast.
        
        Returns:
            True dacă configurarea a reușit, False altfel
        """
        try:
            # Creează socket UDP
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # TODO [1]: Configurați opțiunea SO_REUSEADDR
            # Indicii:
            #   - Aceasta permite mai multor procese să asculte pe același port
            #   - Folosiți setsockopt cu nivelul SOL_SOCKET
            #   - Valoarea ar trebui să fie 1 (activat)
            
            # === ÎNCEPE CODUL TĂU ===
            pass  # Înlocuiește cu: self.socket.setsockopt(...)
            # === SFÂRȘIT CODUL TĂU ===
            
            # Bind pe toate interfețele
            self.socket.bind(('', self.port))
            log_message("INFO", f"Socket bound pe port {self.port}")
            
            # TODO [2]: Join la grupul multicast
            # Indicii:
            #   - Trebuie să construiți o structură ip_mreq folosind struct.pack
            #   - Formatul: 4 bytes pentru adresa grup + 4 bytes pentru interfață
            #   - inet_aton convertește IP string în bytes
            #   - INADDR_ANY (0.0.0.0) pentru a asculta pe toate interfețele
            #   - Folosiți setsockopt cu IPPROTO_IP și IP_ADD_MEMBERSHIP
            
            # === ÎNCEPE CODUL TĂU ===
            # Structura ip_mreq: grup multicast + interfață locală
            # mreq = struct.pack(...)
            # self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            pass  # Înlocuiește cu implementarea
            # === SFÂRȘIT CODUL TĂU ===
            
            log_message("INFO", f"Joined grupul multicast {self.group}")
            return True
            
        except socket.error as e:
            log_message("ERROR", f"Eroare configurare socket: {e}")
            return False
        except Exception as e:
            log_message("ERROR", f"Eroare neașteptată: {e}")
            return False
    
    def process_message(self, data: bytes, addr: Tuple[str, int]):
        """
        Procesează un mesaj primit, aplicând filtrarea.
        
        Args:
            data: Datele primite
            addr: Adresa expeditorului (ip, port)
        """
        sender_ip, sender_port = addr
        
        # Parsează mesajul
        prefix, content = parse_message(data)
        
        # TODO [5 - continuare]: Actualizați statisticile
        # Indicii:
        #   - Incrementați contorul total
        #   - Incrementați contorul pentru prefix-ul specific
        
        # === ÎNCEPE CODUL TĂU ===
        pass  # Actualizare statistici
        # === SFÂRȘIT CODUL TĂU ===
        
        # Aplică filtrarea
        if should_accept_message(prefix, self.filter_prefixes):
            # Mesaj acceptat - afișează
            prefix_display = prefix if prefix else "RAW"
            log_message("RECV", f"[{prefix_display}] {content} (de la {sender_ip})")
            
            # Procesare suplimentară bazată pe prefix
            self._handle_by_prefix(prefix, content, addr)
        else:
            # Mesaj respins de filtru
            log_message("FILTER", f"Respins mesaj cu prefix '{prefix}' de la {sender_ip}")
    
    def _handle_by_prefix(self, prefix: Optional[str], content: str, addr: Tuple[str, int]):
        """
        Procesare specifică bazată pe tipul mesajului.
        
        Această metodă poate fi extinsă pentru a adăuga logică specifică
        pentru diferite tipuri de mesaje (alertare, logging, metrici, etc.).
        """
        if prefix == "ALERT":
            # Alertele ar putea fi logate special sau trimise către un sistem de alertare
            log_message("STATS", f"⚠️  ALERTĂ primită: {content}")
            
        elif prefix == "METRIC":
            # Metricile ar putea fi parsate și stocate
            log_message("STATS", f"📊 Metrică primită: {content}")
            
        elif prefix == "ERROR":
            # Erorile ar putea fi tratate cu prioritate
            log_message("STATS", f"❌ Eroare raportată: {content}")
    
    def print_stats(self):
        """Afișează statisticile curente."""
        log_message("STATS", "=" * 50)
        log_message("STATS", "STATISTICI CURENTE")
        
        total = self.stats.get("total", 0)
        accepted = self.stats.get("accepted", 0)
        rejected = self.stats.get("rejected", 0)
        
        log_message("STATS", f"Total mesaje: {total}")
        log_message("STATS", f"Acceptate: {accepted}")
        log_message("STATS", f"Respinse: {rejected}")
        
        log_message("STATS", "Per prefix:")
        for prefix in KNOWN_PREFIXES:
            count = self.stats.get(f"prefix_{prefix}", 0)
            if count > 0:
                log_message("STATS", f"  {prefix}: {count}")
        
        log_message("STATS", "=" * 50)
    
    def run(self):
        """
        Rulează bucla principală de recepție.
        
        Așteaptă mesaje pe socket și le procesează până la Ctrl+C.
        """
        if not self.setup_socket():
            log_message("ERROR", "Nu pot porni receptorul - verifică configurarea")
            return
        
        self.running = True
        log_message("INFO", "Receptor pornit. Aștept mesaje... (Ctrl+C pentru a opri)")
        
        message_count = 0
        stats_interval = 10  # Afișează statistici la fiecare N mesaje
        
        try:
            while self.running:
                try:
                    # Recepționează date
                    data, addr = self.socket.recvfrom(DEFAULT_BUFFER_SIZE)
                    
                    # Procesează mesajul
                    self.process_message(data, addr)
                    
                    message_count += 1
                    
                    # Statistici periodice
                    if self.show_stats and message_count % stats_interval == 0:
                        self.print_stats()
                        
                except socket.error as e:
                    log_message("ERROR", f"Eroare recepție: {e}")
                    
        except KeyboardInterrupt:
            log_message("INFO", "\nOprire solicitată...")
            
        finally:
            self.cleanup()
            if self.show_stats:
                self.print_stats()
    
    def cleanup(self):
        """Eliberează resursele."""
        self.running = False
        
        if self.socket:
            try:
                # Leave grup multicast (opțional, socket.close() face implicit)
                self.socket.close()
                log_message("INFO", "Socket închis")
            except:
                pass


# =============================================================================
# INTERFAȚĂ LINIE DE COMANDĂ
# =============================================================================

def parse_arguments() -> argparse.Namespace:
    """Parsează argumentele liniei de comandă."""
    parser = argparse.ArgumentParser(
        description="Receptor multicast cu filtrare mesaje",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLE:
  # Ascultă toate mesajele
  python3 tpl_multicast_receiver.py
  
  # Filtrează doar alertele
  python3 tpl_multicast_receiver.py --prefix ALERT
  
  # Filtrează multiple tipuri
  python3 tpl_multicast_receiver.py --prefix ALERT,ERROR,WARN
  
  # Grup și port custom
  python3 tpl_multicast_receiver.py --group 239.1.2.3 --port 5050
  
  # Cu statistici
  python3 tpl_multicast_receiver.py --stats

PREFIXURI CUNOSCUTE:
  ALERT  - Mesaje de alertă urgentă
  ERROR  - Erori și excepții
  WARN   - Avertizări
  INFO   - Informații generale
  DEBUG  - Mesaje de debugging
  METRIC - Date și metrici
  STATUS - Starea sistemelor
        """
    )
    
    parser.add_argument(
        "-g", "--group",
        type=str,
        default=DEFAULT_MULTICAST_GROUP,
        help=f"Adresa grupului multicast (default: {DEFAULT_MULTICAST_GROUP})"
    )
    
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Portul UDP (default: {DEFAULT_PORT})"
    )
    
    parser.add_argument(
        "--prefix",
        type=str,
        default="ALL",
        help="Prefix(uri) de filtrat, separate prin virgulă (default: ALL)"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Afișează statistici periodice"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Output detaliat (debugging)"
    )
    
    return parser.parse_args()


# =============================================================================
# SOLUȚII PENTRU TODO-URI (PENTRU INSTRUCTOR)
# =============================================================================

"""
SOLUȚII - NU DISTRIBUIȚI STUDENȚILOR:

TODO [1] - SO_REUSEADDR:
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

TODO [2] - Join multicast:
    mreq = struct.pack(
        "4s4s",
        socket.inet_aton(self.group),
        socket.inet_aton("0.0.0.0")
    )
    self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

TODO [3] - Parsare prefix:
    if ':' in message:
        prefix, content = message.split(':', 1)
        return (prefix.upper().strip(), content.strip())
    else:
        return (None, message)

TODO [4] - Filtrare:
    if "ALL" in filter_prefixes:
        return True
    if prefix is None:
        return False
    return prefix.upper() in {p.upper() for p in filter_prefixes}

TODO [5] - Statistici:
    self.stats = {
        "total": 0,
        "accepted": 0, 
        "rejected": 0
    }
    # În process_message:
    self.stats["total"] = self.stats.get("total", 0) + 1
    if prefix:
        key = f"prefix_{prefix.upper()}"
        self.stats[key] = self.stats.get(key, 0) + 1
"""


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Punct de intrare principal."""
    args = parse_arguments()
    
    # Parsează prefixurile din argument
    filter_prefixes = {p.strip().upper() for p in args.prefix.split(",")}
    
    print("=" * 70)
    print("MULTICAST RECEIVER CU FILTRARE")
    print("=" * 70)
    print(f"Grup multicast: {args.group}")
    print(f"Port: {args.port}")
    print(f"Filtre prefix: {', '.join(filter_prefixes)}")
    print("=" * 70)
    
    # Verifică TODO-uri completate
    print("\n⚠️  ATENȚIE: Acest template conține secțiuni TODO de completat!")
    print("   Verificați că ați implementat:")
    print("   [1] Configurarea SO_REUSEADDR")
    print("   [2] Join la grupul multicast")
    print("   [3] Parsarea prefix-ului din mesaje")
    print("   [4] Logica de filtrare")
    print("   [5] Actualizarea statisticilor")
    print()
    
    # Creează și rulează receptorul
    receiver = MulticastReceiver(
        group=args.group,
        port=args.port,
        filter_prefixes=filter_prefixes,
        show_stats=args.stats
    )
    
    receiver.run()


if __name__ == "__main__":
    main()
