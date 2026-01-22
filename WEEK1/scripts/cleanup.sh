#!/usr/bin/env bash
#===============================================================================
# cleanup.sh - Curățare mediu după laborator
#===============================================================================
# Rețele de Calculatoare - Săptămâna 1
# ASE București
#
# Utilizare:
#   bash scripts/cleanup.sh          # Curățare normală
#   bash scripts/cleanup.sh --all    # Curățare completă (include capturi)
#   sudo bash scripts/cleanup.sh     # Include cleanup Mininet
#===============================================================================

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }
warn()    { echo -e "${YELLOW}[!]${NC} $1"; }

#===============================================================================
# Funcții de curățare
#===============================================================================

cleanup_temp_files() {
    info "Ștergere fișiere temporare..."
    
    # Fișiere Python compilate
    find . -type f -name "*.pyc" -delete 2>/dev/null
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    
    # Fișiere temporare
    rm -f /tmp/received.txt /tmp/capture*.pcap 2>/dev/null
    rm -f *.tmp *.log 2>/dev/null
    
    success "Fișiere temporare șterse"
}

cleanup_captures() {
    info "Ștergere capturi PCAP..."
    
    # Ștergem doar capturile generate, nu pe cele exemplu
    find . -name "*.pcap" -newer pcap/example_tcp_handshake.pcap -delete 2>/dev/null || true
    rm -f output_*.pcap capture_*.pcap 2>/dev/null
    
    success "Capturi șterse"
}

cleanup_mininet() {
    if [[ $EUID -ne 0 ]]; then
        warn "Cleanup Mininet necesită sudo - skip"
        return
    fi
    
    info "Cleanup Mininet..."
    
    # Oprire procese Mininet rămase
    pkill -9 -f "mininet" 2>/dev/null || true
    pkill -9 -f "ovs-" 2>/dev/null || true
    
    # Cleanup Mininet oficial
    if command -v mn &>/dev/null; then
        mn -c 2>/dev/null || true
    fi
    
    # Ștergere interfețe virtuale rămase
    for intf in $(ip link show 2>/dev/null | grep -oE "(s[0-9]+-eth[0-9]+|h[0-9]+-eth[0-9]+)" | sort -u); do
        ip link delete "$intf" 2>/dev/null || true
    done
    
    success "Mininet curățat"
}

cleanup_netcat_processes() {
    info "Oprire procese netcat rămase..."
    
    pkill -f "nc -l" 2>/dev/null || true
    pkill -f "netcat" 2>/dev/null || true
    
    success "Procese netcat oprite"
}

cleanup_tshark_processes() {
    info "Oprire procese tshark rămase..."
    
    pkill -f "tshark" 2>/dev/null || true
    pkill -f "dumpcap" 2>/dev/null || true
    
    success "Procese tshark oprite"
}

cleanup_docker() {
    if ! command -v docker &>/dev/null; then
        return
    fi
    
    info "Cleanup containere Docker..."
    
    # Oprire containere din acest proiect
    docker ps -q --filter "name=s1_" 2>/dev/null | xargs -r docker stop 2>/dev/null || true
    docker ps -aq --filter "name=s1_" 2>/dev/null | xargs -r docker rm 2>/dev/null || true
    
    success "Containere Docker curățate"
}

release_ports() {
    info "Eliberare porturi utilizate..."
    
    PORTS=(9999 8888 5000 8080)
    
    for port in "${PORTS[@]}"; do
        # Găsim PID-ul care folosește portul
        PID=$(ss -tlnp 2>/dev/null | grep ":$port " | grep -oP 'pid=\K[0-9]+' | head -1)
        if [[ -n "$PID" ]]; then
            kill "$PID" 2>/dev/null && info "  Port $port eliberat (PID $PID)"
        fi
    done
    
    success "Porturi eliberate"
}

#===============================================================================
# Main
#===============================================================================

main() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Cleanup - Starterkit S1 Rețele de Calculatoare               ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    cleanup_temp_files
    cleanup_netcat_processes
    cleanup_tshark_processes
    release_ports
    cleanup_mininet
    
    if [[ "${1:-}" == "--all" ]]; then
        cleanup_captures
        cleanup_docker
    fi
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✅ Cleanup finalizat!                                        ${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

main "$@"
