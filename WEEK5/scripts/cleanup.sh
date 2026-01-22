#!/usr/bin/env bash
#===============================================================================
# cleanup.sh — Curățare mediu Mininet și fișiere temporare
#===============================================================================
# Utilizare: ./scripts/cleanup.sh [--all|--mininet|--temp|--pcap]
#===============================================================================

set -euo pipefail

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }

#-------------------------------------------------------------------------------
# Curățare Mininet
#-------------------------------------------------------------------------------

cleanup_mininet() {
    log_info "Curățare Mininet..."
    
    # Oprire procese Mininet
    if pgrep -f "mininet" > /dev/null 2>&1; then
        sudo pkill -f "mininet" 2>/dev/null || true
    fi
    
    # Cleanup standard Mininet
    if command -v mn &> /dev/null; then
        sudo mn -c 2>/dev/null || true
        log_success "Mininet cleanup executat"
    else
        log_warning "Comanda mn nu este disponibilă"
    fi
    
    # Curățare interfețe virtuale rămase
    for intf in $(ip link show 2>/dev/null | grep -oE "(s[0-9]+-eth[0-9]+|h[0-9]+-eth[0-9]+|r[0-9]+-eth[0-9]+)" | sort -u); do
        sudo ip link delete "$intf" 2>/dev/null || true
    done
    
    # Curățare namespace-uri de rețea
    for ns in $(ip netns list 2>/dev/null | awk '{print $1}'); do
        if [[ "$ns" =~ ^(h[0-9]+|r[0-9]+|s[0-9]+)$ ]]; then
            sudo ip netns delete "$ns" 2>/dev/null || true
        fi
    done
    
    # Restart Open vSwitch (dacă necesar)
    if systemctl is-active --quiet openvswitch-switch 2>/dev/null; then
        sudo systemctl restart openvswitch-switch
        log_success "Open vSwitch repornit"
    fi
}

#-------------------------------------------------------------------------------
# Curățare fișiere temporare
#-------------------------------------------------------------------------------

cleanup_temp() {
    log_info "Curățare fișiere temporare..."
    
    # Python cache
    find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -type f -name "*.pyo" -delete 2>/dev/null || true
    
    # Fișiere editor
    find "$PROJECT_ROOT" -type f -name "*~" -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -type f -name "*.swp" -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -type f -name "*.swo" -delete 2>/dev/null || true
    
    # Logs temporare
    find "$PROJECT_ROOT" -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    # JSON temporare generate de scripturi
    rm -f "$PROJECT_ROOT"/python/exercises/*.json 2>/dev/null || true
    
    log_success "Fișiere temporare curățate"
}

#-------------------------------------------------------------------------------
# Curățare capturi PCAP
#-------------------------------------------------------------------------------

cleanup_pcap() {
    log_info "Curățare capturi PCAP..."
    
    if [[ -d "$PROJECT_ROOT/pcap" ]]; then
        # Păstrăm doar fișierele mai mici de 1MB și cele din ultimele 7 zile
        find "$PROJECT_ROOT/pcap" -type f -name "*.pcap" -size +1M -delete 2>/dev/null || true
        find "$PROJECT_ROOT/pcap" -type f -name "*.pcap" -mtime +7 -delete 2>/dev/null || true
        log_success "Capturi PCAP mari/vechi șterse"
    fi
    
    # Curățare din /tmp
    sudo rm -f /tmp/*.pcap 2>/dev/null || true
}

#-------------------------------------------------------------------------------
# Curățare completă
#-------------------------------------------------------------------------------

cleanup_all() {
    cleanup_mininet
    cleanup_temp
    cleanup_pcap
    log_success "Curățare completă finalizată!"
}

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              Cleanup Starterkit Săptămâna 5                  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    local mode="${1:---all}"
    
    case "$mode" in
        --all)
            cleanup_all
            ;;
        --mininet)
            cleanup_mininet
            ;;
        --temp)
            cleanup_temp
            ;;
        --pcap)
            cleanup_pcap
            ;;
        --help|-h)
            echo "Utilizare: $0 [--all|--mininet|--temp|--pcap]"
            echo ""
            echo "Opțiuni:"
            echo "  --all      Curățare completă (implicit)"
            echo "  --mininet  Doar curățare Mininet"
            echo "  --temp     Doar fișiere temporare"
            echo "  --pcap     Doar capturi PCAP vechi/mari"
            ;;
        *)
            echo "Opțiune necunoscută: $mode"
            exit 1
            ;;
    esac
}

main "$@"
