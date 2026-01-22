#!/usr/bin/env bash
#===============================================================================
# capture.sh — Captură pachete simplificată pentru laborator
#===============================================================================
# Utilizare: ./scripts/capture.sh [--interface INTF] [--duration SEC] [--filter EXPR]
#===============================================================================

set -euo pipefail

# Culori
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PCAP_DIR="$PROJECT_ROOT/pcap"

# Defaults
INTERFACE="any"
DURATION=30
FILTER=""
COUNT=100
OUTPUT=""

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

#-------------------------------------------------------------------------------
# Parse arguments
#-------------------------------------------------------------------------------

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -i|--interface)
                INTERFACE="$2"
                shift 2
                ;;
            -d|--duration)
                DURATION="$2"
                shift 2
                ;;
            -f|--filter)
                FILTER="$2"
                shift 2
                ;;
            -c|--count)
                COUNT="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo "Opțiune necunoscută: $1"
                exit 1
                ;;
        esac
    done
}

show_help() {
    cat << 'EOF'
Utilizare: capture.sh [OPȚIUNI]

Opțiuni:
  -i, --interface INTF    Interfața de captură (default: any)
  -d, --duration SEC      Durată captură în secunde (default: 30)
  -f, --filter EXPR       Filtru BPF (ex: "icmp", "port 80", "host 10.0.1.10")
  -c, --count NUM         Număr maxim pachete (default: 100)
  -o, --output FILE       Fișier output (default: auto-generat)
  -h, --help              Afișare ajutor

Exemple:
  ./capture.sh -i eth0 -d 60 -f "icmp"
  ./capture.sh -f "tcp port 80" -c 50
  ./capture.sh --interface r1-eth0 --filter "host 10.0.1.10"

Filtre BPF comune:
  icmp                    Doar ICMP (ping)
  tcp                     Doar TCP
  udp                     Doar UDP
  port 80                 Port 80 (HTTP)
  host 10.0.1.10         Trafic către/de la IP
  net 10.0.1.0/24        Trafic rețea specifică
  tcp and port 22        TCP pe port 22 (SSH)
EOF
}

#-------------------------------------------------------------------------------
# Listare interfețe
#-------------------------------------------------------------------------------

list_interfaces() {
    log_info "Interfețe de rețea disponibile:"
    echo ""
    ip -o link show | awk -F': ' '{print "  " $2}' | grep -v "^  lo$"
    echo ""
    
    # Verificăm și interfețe Mininet (dacă există)
    if ip link show 2>/dev/null | grep -qE "(s[0-9]+-eth|h[0-9]+-eth|r[0-9]+-eth)"; then
        log_info "Interfețe Mininet detectate:"
        ip link show 2>/dev/null | grep -oE "(s[0-9]+-eth[0-9]+|h[0-9]+-eth[0-9]+|r[0-9]+-eth[0-9]+)" | sed 's/^/  /'
        echo ""
    fi
}

#-------------------------------------------------------------------------------
# Captură
#-------------------------------------------------------------------------------

start_capture() {
    # Verificăm tcpdump
    if ! command -v tcpdump &> /dev/null; then
        echo "Eroare: tcpdump nu este instalat"
        exit 1
    fi
    
    # Creăm directorul pcap dacă nu există
    mkdir -p "$PCAP_DIR"
    
    # Generăm numele fișierului dacă nu e specificat
    if [[ -z "$OUTPUT" ]]; then
        local timestamp=$(date +%Y%m%d_%H%M%S)
        local intf_clean=$(echo "$INTERFACE" | tr -c 'a-zA-Z0-9' '_')
        OUTPUT="$PCAP_DIR/capture_${intf_clean}_${timestamp}.pcap"
    fi
    
    # Construim comanda
    local cmd="tcpdump -i $INTERFACE -c $COUNT -w $OUTPUT"
    
    if [[ -n "$FILTER" ]]; then
        cmd="$cmd $FILTER"
    fi
    
    log_info "Pornire captură..."
    echo "  Interfață: $INTERFACE"
    echo "  Durată max: ${DURATION}s"
    echo "  Pachete max: $COUNT"
    echo "  Filtru: ${FILTER:-<toate>}"
    echo "  Output: $OUTPUT"
    echo ""
    log_warn "Apăsați Ctrl+C pentru a opri captura mai devreme"
    echo ""
    
    # Rulăm cu timeout
    if sudo -n true 2>/dev/null; then
        sudo timeout "$DURATION" $cmd || true
    else
        log_warn "Necesită sudo pentru captură"
        sudo timeout "$DURATION" $cmd || true
    fi
    
    echo ""
    
    # Verificăm rezultatul
    if [[ -f "$OUTPUT" ]]; then
        local size=$(du -h "$OUTPUT" | cut -f1)
        local packets=$(tcpdump -r "$OUTPUT" 2>/dev/null | wc -l || echo "?")
        log_success "Captură salvată: $OUTPUT ($size, ~$packets pachete)"
        
        # Afișăm sumar rapid
        echo ""
        log_info "Primele 5 pachete:"
        tcpdump -r "$OUTPUT" -n -c 5 2>/dev/null || true
    else
        log_warn "Nu s-au capturat pachete"
    fi
}

#-------------------------------------------------------------------------------
# Analiză captură existentă
#-------------------------------------------------------------------------------

analyze_capture() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        echo "Fișier nu există: $file"
        exit 1
    fi
    
    log_info "Analiză captură: $file"
    echo ""
    
    # Statistici generale
    echo "=== Statistici generale ==="
    tcpdump -r "$file" -q 2>/dev/null | tail -1 || true
    echo ""
    
    # Protocoale
    echo "=== Distribuție protocoale ==="
    tcpdump -r "$file" -n 2>/dev/null | awk '{print $3}' | sort | uniq -c | sort -rn | head -10
    echo ""
    
    # IP-uri sursă
    echo "=== Top IP-uri sursă ==="
    tcpdump -r "$file" -n 2>/dev/null | grep -oE 'IP [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | awk '{print $2}' | sort | uniq -c | sort -rn | head -5
    echo ""
}

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

main() {
    if [[ $# -eq 0 ]]; then
        echo "╔══════════════════════════════════════════════════════════════╗"
        echo "║              Captură Pachete — Săptămâna 5                   ║"
        echo "╚══════════════════════════════════════════════════════════════╝"
        echo ""
        list_interfaces
        show_help
        exit 0
    fi
    
    # Verificăm pentru comanda analyze
    if [[ "$1" == "analyze" ]] && [[ -n "${2:-}" ]]; then
        analyze_capture "$2"
        exit 0
    fi
    
    parse_args "$@"
    start_capture
}

main "$@"
