#!/bin/bash
# ============================================================================
# run_all.sh - Demo automat non-interactiv pentru Săptămâna 6
# Produce: artifacts/demo.log, artifacts/demo.pcap, artifacts/validation.txt
#
# Rezolvix&Hypotheticalandrei
# Licență: MIT | ASE-CSIE 2025-2026
# ============================================================================

set -e

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURAȚIE
# ═══════════════════════════════════════════════════════════════════════════

WEEK=6
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$PROJECT_DIR/artifacts"

# Plan IP Week 6
SUBNET="10.0.6.0/24"
H1_IP="10.0.6.11"
H2_IP="10.0.6.12"
H3_IP="10.0.6.13"

# Plan porturi
TCP_APP_PORT=9090
UDP_APP_PORT=9091
CONTROLLER_PORT=6633

# Timeout-uri
DEMO_TIMEOUT=60
PING_TIMEOUT=3

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ═══════════════════════════════════════════════════════════════════════════
# FUNCȚII UTILITARE
# ═══════════════════════════════════════════════════════════════════════════

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$ARTIFACTS_DIR/demo.log"
}

info() { echo -e "${BLUE}[INFO]${NC} $1"; log "[INFO] $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; log "[OK] $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; log "[WARN] $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; log "[ERROR] $1"; }

header() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    log "=== $1 ==="
}

# ═══════════════════════════════════════════════════════════════════════════
# PRE-VERIFICĂRI
# ═══════════════════════════════════════════════════════════════════════════

check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "Acest script necesită privilegii root"
        echo "Rulează cu: sudo $0"
        exit 1
    fi
}

prepare_artifacts() {
    mkdir -p "$ARTIFACTS_DIR"
    
    # Resetare fișiere
    echo "# Demo Log - Week $WEEK - SDN" > "$ARTIFACTS_DIR/demo.log"
    echo "# Generat: $(date)" >> "$ARTIFACTS_DIR/demo.log"
    echo "" >> "$ARTIFACTS_DIR/demo.log"
    
    echo "# Validation Results - Week $WEEK" > "$ARTIFACTS_DIR/validation.txt"
    echo "# Generat: $(date)" >> "$ARTIFACTS_DIR/validation.txt"
    echo "" >> "$ARTIFACTS_DIR/validation.txt"
    
    success "Directorul artifacts/ pregătit"
}

pre_cleanup() {
    info "Curățare configurație anterioară..."
    
    mn -c 2>/dev/null || true
    pkill -9 -f "topo_sdn.py" 2>/dev/null || true
    pkill -9 -f "topo_nat.py" 2>/dev/null || true
    pkill -f "osken-manager" 2>/dev/null || true
    pkill -f "ryu-manager" 2>/dev/null || true
    fuser -k $CONTROLLER_PORT/tcp 2>/dev/null || true
    
    # Cleanup OVS
    for br in $(ovs-vsctl list-br 2>/dev/null); do
        ovs-vsctl del-br "$br" 2>/dev/null || true
    done
    
    sleep 2
    success "Mediu curățat"
}

check_dependencies() {
    info "Verificare dependențe..."
    
    local deps_ok=true
    
    for cmd in python3 mn ovs-vsctl tcpdump; do
        if ! command -v $cmd &>/dev/null; then
            error "Lipsește: $cmd"
            deps_ok=false
        fi
    done
    
    if $deps_ok; then
        success "Toate dependențele sunt disponibile"
    else
        error "Dependențe lipsă. Rulează: scripts/setup.sh"
        exit 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# DEMO SDN
# ═══════════════════════════════════════════════════════════════════════════

start_controller() {
    info "Pornire controller SDN..."
    
    local controller_file="$PROJECT_DIR/seminar/python/controllers/sdn_policy_controller.py"
    local controller_log="$ARTIFACTS_DIR/controller.log"
    
    if [[ ! -f "$controller_file" ]]; then
        error "Controller lipsește: $controller_file"
        return 1
    fi
    
    # Determină manager-ul disponibil
    local manager=""
    if command -v osken-manager &>/dev/null; then
        manager="osken-manager"
    elif command -v ryu-manager &>/dev/null; then
        manager="ryu-manager"
    else
        warn "Niciun controller SDN disponibil. Se continuă fără controller."
        return 0
    fi
    
    # Pornire în background
    nohup $manager "$controller_file" > "$controller_log" 2>&1 &
    local pid=$!
    echo "$pid" > /tmp/sdn_controller.pid
    
    sleep 3
    
    if kill -0 $pid 2>/dev/null; then
        success "Controller pornit (PID: $pid)"
        log "Controller SDN activ pe port $CONTROLLER_PORT"
    else
        warn "Controller-ul nu a pornit corect"
        cat "$controller_log" >> "$ARTIFACTS_DIR/demo.log"
    fi
}

run_sdn_demo() {
    header "DEMO SDN - Software-Defined Networking"
    
    local topo_file="$PROJECT_DIR/seminar/mininet/topologies/topo_sdn.py"
    
    if [[ ! -f "$topo_file" ]]; then
        error "Topologie lipsește: $topo_file"
        return 1
    fi
    
    info "Pornire topologie SDN cu capturare trafic..."
    
    # Creează script Python pentru demo automat
    python3 << 'PYTHON_SCRIPT'
import sys
import time
sys.path.insert(0, '${PROJECT_DIR}/seminar/mininet/topologies')

from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.topo import Topo

setLogLevel('warning')

class SDNTopo(Topo):
    def build(self):
        s1 = self.addSwitch("s1", cls=OVSSwitch, protocols="OpenFlow13")
        h1 = self.addHost("h1", ip="10.0.6.11/24")
        h2 = self.addHost("h2", ip="10.0.6.12/24")
        h3 = self.addHost("h3", ip="10.0.6.13/24")
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)

# Creează topologia
topo = SDNTopo()
controller = RemoteController("c0", ip="127.0.0.1", port=6633)
net = Mininet(topo=topo, controller=controller, switch=OVSSwitch, 
              link=TCLink, autoSetMacs=True)

net.start()
time.sleep(3)  # Așteaptă conectarea la controller

h1, h2, h3 = net.get("h1", "h2", "h3")
s1 = net.get("s1")

print("\n=== DEMO SDN AUTOMAT ===\n")

# Test 1: Ping h1 -> h2 (PERMIT)
print("TEST 1: h1 ping h2 (PERMIT expected)")
result1 = h1.cmd("ping -c 3 -W 2 10.0.6.12")
print(result1)
ok1 = "0% packet loss" in result1 or "3 received" in result1

# Test 2: Ping h1 -> h3 (DROP)
print("\nTEST 2: h1 ping h3 (DROP expected)")
result2 = h1.cmd("ping -c 3 -W 2 10.0.6.13")
print(result2)
ok2 = "100% packet loss" in result2 or "0 received" in result2

# Test 3: Flow table
print("\n=== Flow Table ===")
flows = s1.cmd("ovs-ofctl -O OpenFlow13 dump-flows s1")
print(flows)

# Rezultate
print("\n=== REZULTATE ===")
print(f"Test h1→h2 (PERMIT): {'PASS' if ok1 else 'FAIL'}")
print(f"Test h1→h3 (DROP):   {'PASS' if ok2 else 'FAIL'}")

# Salvare rezultate
with open("${ARTIFACTS_DIR}/validation.txt", "a") as f:
    f.write(f"SDN_TEST_H1_H2_PERMIT: {'PASS' if ok1 else 'FAIL'}\n")
    f.write(f"SDN_TEST_H1_H3_DROP: {'PASS' if ok2 else 'FAIL'}\n")
    f.write(f"SDN_FLOWS_INSTALLED: {'YES' if 'priority' in flows else 'NO'}\n")

net.stop()
PYTHON_SCRIPT

    success "Demo SDN completat"
}

# ═══════════════════════════════════════════════════════════════════════════
# DEMO NAT
# ═══════════════════════════════════════════════════════════════════════════

run_nat_demo() {
    header "DEMO NAT - Network Address Translation"
    
    local topo_file="$PROJECT_DIR/seminar/mininet/topologies/topo_nat.py"
    
    if [[ ! -f "$topo_file" ]]; then
        error "Topologie NAT lipsește: $topo_file"
        return 1
    fi
    
    info "Rulare test NAT automat..."
    
    # Rulează topologia NAT în mod test
    if python3 "$topo_file" --test 2>&1 | tee -a "$ARTIFACTS_DIR/demo.log"; then
        echo "NAT_TEST: PASS" >> "$ARTIFACTS_DIR/validation.txt"
        success "Demo NAT completat"
    else
        echo "NAT_TEST: FAIL" >> "$ARTIFACTS_DIR/validation.txt"
        warn "Demo NAT a avut probleme"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# CAPTURARE TRAFIC
# ═══════════════════════════════════════════════════════════════════════════

capture_demo_traffic() {
    header "CAPTURARE TRAFIC DEMONSTRATIV"
    
    info "Generare captură demo.pcap..."
    
    # Capturare simplă cu topologie minimală
    python3 << 'PYTHON_SCRIPT'
import subprocess
import time
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.topo import LinearTopo
from mininet.log import setLogLevel

setLogLevel('warning')

# Topologie simplă pentru captură
net = Mininet(topo=LinearTopo(k=2), switch=OVSSwitch, 
              link=TCLink, controller=None)
net.start()

h1, h2 = net.get("h1", "h2")

# Pornește tcpdump pe h1
h1.cmd("tcpdump -i h1-eth0 -c 10 -w /tmp/demo_capture.pcap &")
time.sleep(1)

# Generează trafic
h1.cmd("ping -c 5 " + h2.IP())

# Așteaptă captura
time.sleep(2)
h1.cmd("pkill tcpdump || true")

net.stop()
PYTHON_SCRIPT

    # Copiază captura
    if [[ -f /tmp/demo_capture.pcap ]]; then
        cp /tmp/demo_capture.pcap "$ARTIFACTS_DIR/demo.pcap"
        success "Captură salvată: artifacts/demo.pcap"
        echo "PCAP_GENERATED: YES" >> "$ARTIFACTS_DIR/validation.txt"
    else
        # Creează captură placeholder
        touch "$ARTIFACTS_DIR/demo.pcap"
        warn "Captură placeholder creată"
        echo "PCAP_GENERATED: PLACEHOLDER" >> "$ARTIFACTS_DIR/validation.txt"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# FINALIZARE
# ═══════════════════════════════════════════════════════════════════════════

stop_controller() {
    info "Oprire controller..."
    
    if [[ -f /tmp/sdn_controller.pid ]]; then
        local pid=$(cat /tmp/sdn_controller.pid)
        kill $pid 2>/dev/null || true
        rm -f /tmp/sdn_controller.pid
    fi
    
    pkill -f "osken-manager" 2>/dev/null || true
    pkill -f "ryu-manager" 2>/dev/null || true
}

final_cleanup() {
    info "Curățare finală..."
    
    stop_controller
    mn -c 2>/dev/null || true
    
    success "Cleanup complet"
}

generate_summary() {
    header "SUMAR DEMO"
    
    echo ""
    echo "Artefacte generate:"
    echo "  - artifacts/demo.log"
    echo "  - artifacts/demo.pcap"  
    echo "  - artifacts/validation.txt"
    echo ""
    
    if [[ -f "$ARTIFACTS_DIR/validation.txt" ]]; then
        echo "Rezultate validare:"
        cat "$ARTIFACTS_DIR/validation.txt" | grep -v "^#" | grep -v "^$"
    fi
    
    echo ""
    log "=== DEMO COMPLET ==="
    success "Demo finalizat cu succes!"
}

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

main() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   Demo Automat - Săptămâna $WEEK: SDN & NAT                    ║${NC}"
    echo -e "${CYAN}║   Rețele de Calculatoare - ASE-CSIE 2025-2026                 ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    check_root
    prepare_artifacts
    check_dependencies
    pre_cleanup
    
    # Demo principal
    start_controller
    run_sdn_demo
    
    # Cleanup între demo-uri
    mn -c 2>/dev/null || true
    sleep 2
    
    run_nat_demo
    
    # Curățare și captură finală
    mn -c 2>/dev/null || true
    sleep 2
    
    capture_demo_traffic
    
    # Finalizare
    final_cleanup
    generate_summary
}

# Trap pentru cleanup la eroare
trap final_cleanup EXIT

# Rulare
main "$@"
