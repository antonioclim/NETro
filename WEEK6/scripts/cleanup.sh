#!/bin/bash
# ============================================================================
# cleanup.sh - Curățare completă a mediului după laborator
# Autor: Revolvix&Hypotheticalandrei
# ============================================================================

set -e

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

echo "=============================================="
echo "  Cleanup - Săptămâna 6: NAT/PAT & SDN"
echo "=============================================="
echo ""

# Oprire controller SDN
cleanup_controller() {
    info "Oprire controller SDN..."
    
    pkill -f "osken-manager" 2>/dev/null && success "osken-manager oprit" || true
    pkill -f "ryu-manager" 2>/dev/null && success "ryu-manager oprit" || true
    pkill -f "sdn_policy_controller" 2>/dev/null || true
    
    # Verificare port 6633
    if netstat -tlnp 2>/dev/null | grep -q ":6633"; then
        warn "Port 6633 încă ocupat, se forțează eliberarea..."
        fuser -k 6633/tcp 2>/dev/null || true
    fi
}

# Curățare Mininet
cleanup_mininet() {
    info "Curățare Mininet..."
    
    # Curățare standard Mininet
    sudo mn -c 2>/dev/null || true
    success "Mininet curățat"
    
    # Oprire procese Python din Mininet
    sudo pkill -9 -f "python.*topo_nat" 2>/dev/null || true
    sudo pkill -9 -f "python.*topo_sdn" 2>/dev/null || true
}

# Curățare Open vSwitch
cleanup_ovs() {
    info "Curățare Open vSwitch..."
    
    # Listare și ștergere bridge-uri
    for br in $(sudo ovs-vsctl list-br 2>/dev/null); do
        sudo ovs-vsctl del-br "$br" 2>/dev/null && info "Șters bridge: $br"
    done
    
    # Reset OVS
    sudo ovs-vsctl --if-exists del-br s1 2>/dev/null || true
    sudo ovs-vsctl --if-exists del-br s2 2>/dev/null || true
    
    success "OVS curățat"
}

# Curățare procese Python
cleanup_python() {
    info "Oprire procese Python din lab..."
    
    PATTERNS=(
        "nat_observer"
        "tcp_echo"
        "udp_echo"
        "sdn_policy"
    )
    
    for pattern in "${PATTERNS[@]}"; do
        pkill -f "$pattern" 2>/dev/null && info "Oprit: $pattern" || true
    done
}

# Curățare reguli iptables NAT (doar cele adăugate de lab)
cleanup_iptables() {
    info "Curățare reguli iptables temporare..."
    
    # Nu ștergem tot, doar regulile specifice lab-ului
    # Regulile Mininet sunt în namespace-uri separate, deci nu afectează host-ul
    
    # Verificare dacă sunt reguli MASQUERADE pentru rețelele lab
    if sudo iptables -t nat -L POSTROUTING -n 2>/dev/null | grep -q "10.0.1.0/24"; then
        warn "Reguli NAT lab detectate în host (neobișnuit)"
        info "Verifică manual cu: sudo iptables -t nat -L -n"
    fi
    
    success "iptables verificat"
}

# Curățare fișiere temporare
cleanup_temp_files() {
    info "Curățare fișiere temporare..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    # Curățare capturi vechi (păstrăm ultimele)
    if [[ -d "$PROJECT_DIR/pcap" ]]; then
        find "$PROJECT_DIR/pcap" -name "*.pcap" -mtime +1 -delete 2>/dev/null || true
    fi
    
    # Curățare loguri vechi
    if [[ -d "$PROJECT_DIR/logs" ]]; then
        find "$PROJECT_DIR/logs" -name "*.log" -mtime +1 -delete 2>/dev/null || true
    fi
    
    # Fișiere temporare sistem
    rm -f /tmp/pre_nat.pcap /tmp/post_nat.pcap 2>/dev/null || true
    rm -f /tmp/osken.log /tmp/controller.log 2>/dev/null || true
    
    success "Fișiere temporare curățate"
}

# Curățare interfețe de rețea virtuale
cleanup_network_interfaces() {
    info "Curățare interfețe virtuale..."
    
    # Ștergere veth pairs create de Mininet
    for iface in $(ip link show 2>/dev/null | grep -oP 'veth\w+' | sort -u); do
        sudo ip link delete "$iface" 2>/dev/null && info "Șters: $iface" || true
    done
    
    # Ștergere interfețe h1-eth0, h2-eth0, etc.
    for iface in $(ip link show 2>/dev/null | grep -oP 'h\d+-eth\d+' | sort -u); do
        sudo ip link delete "$iface" 2>/dev/null && info "Șters: $iface" || true
    done
    
    success "Interfețe virtuale curățate"
}

# Verificare finală
verify_cleanup() {
    echo ""
    echo "=============================================="
    echo "  Verificare Cleanup"
    echo "=============================================="
    
    # Verificare procese
    if pgrep -f "osken-manager|ryu-manager" > /dev/null 2>&1; then
        warn "Controller SDN încă rulează"
    else
        success "Niciun controller SDN activ"
    fi
    
    # Verificare Mininet
    if pgrep -f "mininet" > /dev/null 2>&1; then
        warn "Procese Mininet încă active"
    else
        success "Mininet oprit complet"
    fi
    
    # Verificare OVS bridges
    BR_COUNT=$(sudo ovs-vsctl list-br 2>/dev/null | wc -l)
    if [[ $BR_COUNT -gt 0 ]]; then
        warn "$BR_COUNT bridge-uri OVS încă active"
    else
        success "Niciun bridge OVS activ"
    fi
    
    # Verificare port 6633
    if netstat -tlnp 2>/dev/null | grep -q ":6633"; then
        warn "Port 6633 încă ocupat"
    else
        success "Port 6633 liber"
    fi
    
    echo "=============================================="
    success "Cleanup complet!"
    echo "=============================================="
}

# Funcție principală
main() {
    cleanup_controller
    cleanup_mininet
    cleanup_ovs
    cleanup_python
    cleanup_iptables
    cleanup_temp_files
    cleanup_network_interfaces
    verify_cleanup
}

# Rulare
main "$@"
