#!/usr/bin/env bash
#==============================================================================
# capture.sh – Captură pachete pentru Săptămâna 10
# Rețele de Calculatoare, ASE București 2025-2026
#==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
PCAP_DIR="$ROOT_DIR/pcap"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

#------------------------------------------------------------------------------
# Verificare privilegii
#------------------------------------------------------------------------------
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Acest script necesită privilegii root pentru captură."
        log_info "Rulați cu: sudo $0 $*"
        exit 1
    fi
}

#------------------------------------------------------------------------------
# Captură DNS
#------------------------------------------------------------------------------
capture_dns() {
    local duration="${1:-10}"
    local output="$PCAP_DIR/dns_${TIMESTAMP}.pcap"
    
    log_info "Captură trafic DNS pentru $duration secunde..."
    log_info "Output: $output"
    
    timeout "$duration" tcpdump -i any -w "$output" 'port 53 or port 5353' 2>/dev/null || true
    
    if [ -f "$output" ]; then
        log_info "Captură completă. Pachete:"
        tcpdump -r "$output" -nn | head -20
    fi
}

#------------------------------------------------------------------------------
# Captură SSH
#------------------------------------------------------------------------------
capture_ssh() {
    local duration="${1:-10}"
    local output="$PCAP_DIR/ssh_${TIMESTAMP}.pcap"
    
    log_info "Captură trafic SSH pentru $duration secunde..."
    log_info "Output: $output"
    
    timeout "$duration" tcpdump -i any -w "$output" 'port 22 or port 2222' 2>/dev/null || true
    
    if [ -f "$output" ]; then
        log_info "Captură completă. Pachete:"
        tcpdump -r "$output" -nn | head -20
    fi
}

#------------------------------------------------------------------------------
# Captură FTP
#------------------------------------------------------------------------------
capture_ftp() {
    local duration="${1:-10}"
    local output="$PCAP_DIR/ftp_${TIMESTAMP}.pcap"
    
    log_info "Captură trafic FTP pentru $duration secunde..."
    log_info "Output: $output"
    
    timeout "$duration" tcpdump -i any -w "$output" 'port 21 or port 2121 or portrange 30000-30009' 2>/dev/null || true
    
    if [ -f "$output" ]; then
        log_info "Captură completă. Pachete:"
        tcpdump -r "$output" -nn -A | head -40
    fi
}

#------------------------------------------------------------------------------
# Captură HTTP
#------------------------------------------------------------------------------
capture_http() {
    local duration="${1:-10}"
    local output="$PCAP_DIR/http_${TIMESTAMP}.pcap"
    
    log_info "Captură trafic HTTP pentru $duration secunde..."
    log_info "Output: $output"
    
    timeout "$duration" tcpdump -i any -w "$output" 'port 80 or port 8000 or port 8080' 2>/dev/null || true
    
    if [ -f "$output" ]; then
        log_info "Captură completă. Pachete:"
        tcpdump -r "$output" -nn -A | head -40
    fi
}

#------------------------------------------------------------------------------
# Captură all (toate protocoalele de interes)
#------------------------------------------------------------------------------
capture_all() {
    local duration="${1:-30}"
    local output="$PCAP_DIR/all_${TIMESTAMP}.pcap"
    
    log_info "Captură tot traficul relevant pentru $duration secunde..."
    log_info "Output: $output"
    
    local filter="port 53 or port 5353 or port 22 or port 2222 or port 21 or port 2121 or port 80 or port 8000 or portrange 30000-30009"
    
    timeout "$duration" tcpdump -i any -w "$output" "$filter" 2>/dev/null || true
    
    if [ -f "$output" ]; then
        log_info "Captură completă."
        echo ""
        log_info "Rezumat:"
        tcpdump -r "$output" -nn | wc -l | xargs -I{} echo "  Total pachete: {}"
        tcpdump -r "$output" -nn 'port 53 or port 5353' | wc -l | xargs -I{} echo "  DNS: {}"
        tcpdump -r "$output" -nn 'port 22 or port 2222' | wc -l | xargs -I{} echo "  SSH: {}"
        tcpdump -r "$output" -nn 'port 21 or port 2121' | wc -l | xargs -I{} echo "  FTP: {}"
        tcpdump -r "$output" -nn 'port 80 or port 8000' | wc -l | xargs -I{} echo "  HTTP: {}"
    fi
}

#------------------------------------------------------------------------------
# Analiză PCAP
#------------------------------------------------------------------------------
analyze() {
    local pcap_file="$1"
    
    if [ ! -f "$pcap_file" ]; then
        log_error "Fișierul nu există: $pcap_file"
        exit 1
    fi
    
    log_info "Analiză: $pcap_file"
    echo ""
    
    log_info "Statistici generale:"
    capinfos "$pcap_file" 2>/dev/null || tcpdump -r "$pcap_file" -nn | wc -l | xargs -I{} echo "Total pachete: {}"
    
    echo ""
    log_info "Protocol breakdown:"
    tcpdump -r "$pcap_file" -nn 2>/dev/null | awk '{print $3}' | cut -d. -f1-4 | sort | uniq -c | sort -rn | head -10
    
    echo ""
    log_info "Primele 20 pachete:"
    tcpdump -r "$pcap_file" -nn | head -20
}

#------------------------------------------------------------------------------
# Usage
#------------------------------------------------------------------------------
usage() {
    cat << EOF
Utilizare: $0 <comandă> [opțiuni]

Comenzi:
  dns [durată]      Captură trafic DNS (default: 10s)
  ssh [durată]      Captură trafic SSH (default: 10s)
  ftp [durată]      Captură trafic FTP (default: 10s)
  http [durată]     Captură trafic HTTP (default: 10s)
  all [durată]      Captură tot traficul (default: 30s)
  analyze <file>    Analizează fișier PCAP

Exemple:
  sudo $0 dns 15      # Captură DNS 15 secunde
  sudo $0 all 60      # Captură tot 60 secunde
  $0 analyze pcap/dns_20241220_143000.pcap

Fișierele sunt salvate în: $PCAP_DIR/
EOF
}

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
main() {
    mkdir -p "$PCAP_DIR"
    
    if [ $# -eq 0 ]; then
        usage
        exit 0
    fi
    
    local cmd="$1"
    shift
    
    case "$cmd" in
        dns)
            check_root
            capture_dns "${1:-10}"
            ;;
        ssh)
            check_root
            capture_ssh "${1:-10}"
            ;;
        ftp)
            check_root
            capture_ftp "${1:-10}"
            ;;
        http)
            check_root
            capture_http "${1:-10}"
            ;;
        all)
            check_root
            capture_all "${1:-30}"
            ;;
        analyze)
            if [ $# -eq 0 ]; then
                log_error "Specificați fișierul PCAP"
                exit 1
            fi
            analyze "$1"
            ;;
        -h|--help|help)
            usage
            ;;
        *)
            log_error "Comandă necunoscută: $cmd"
            usage
            exit 1
            ;;
    esac
}

main "$@"
