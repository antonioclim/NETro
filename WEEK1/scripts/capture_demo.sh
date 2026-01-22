#!/bin/bash
# =============================================================================
# capture_demo.sh - Generator Capturi Demonstrative
# =============================================================================
# Generează fișiere PCAP exemplu pentru laboratorul de Rețele de Calculatoare
# 
# Utilizare:
#   ./scripts/capture_demo.sh [--all|--tcp|--udp|--http|--mixed]
#
# Fișiere generate:
#   pcap/example_tcp_handshake.pcap  - TCP 3-way handshake
#   pcap/example_udp_dns.pcap        - Interogări DNS
#   pcap/example_http_request.pcap   - Request HTTP
#   pcap/example_mixed_traffic.pcap  - Trafic combinat
#
# Prerechizite:
#   - tshark instalat
#   - netcat (nc) instalat
#   - curl instalat
#   - Python 3 pentru HTTP server
#
# Autor: Revolvix&Hypotheticalandrei
# =============================================================================

set -e

# Culori pentru output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Directoare
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PCAP_DIR="$PROJECT_DIR/pcap"

# Porturi folosite
TCP_PORT=9999
HTTP_PORT=8080
UDP_PORT=9998

# Funcții helper
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
    exit 1
}

header() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Verificare prerechizite
check_requirements() {
    header "Verificare Prerechizite"
    
    local missing=0
    
    for cmd in tshark nc curl python3; do
        if command -v $cmd &>/dev/null; then
            success "$cmd: $(which $cmd)"
        else
            warn "$cmd: NU GĂSIT"
            missing=$((missing + 1))
        fi
    done
    
    # Verificare permisiuni tshark
    if ! tshark -D &>/dev/null 2>&1; then
        warn "tshark poate necesita permisiuni suplimentare"
        warn "Rulează: sudo usermod -aG wireshark \$USER && newgrp wireshark"
    fi
    
    if [ $missing -gt 0 ]; then
        error "Lipsesc $missing instrumente necesare. Instalează-le și reîncearcă."
    fi
    
    # Creare director pcap
    mkdir -p "$PCAP_DIR"
    success "Director pcap: $PCAP_DIR"
}

# Curățare procese anterioare
cleanup_processes() {
    info "Curățare procese anterioare..."
    
    # Kill procese pe porturile folosite
    for port in $TCP_PORT $HTTP_PORT $UDP_PORT; do
        local pid=$(lsof -ti :$port 2>/dev/null || true)
        if [ -n "$pid" ]; then
            kill $pid 2>/dev/null || true
            info "Oprit proces pe portul $port (PID: $pid)"
        fi
    done
    
    # Kill tshark rămase
    pkill -f "tshark.*example_" 2>/dev/null || true
    
    sleep 1
}

# Cleanup la exit
cleanup_on_exit() {
    info "Curățare finală..."
    cleanup_processes
}

trap cleanup_on_exit EXIT

# =============================================================================
# GENERATOARE PCAP
# =============================================================================

generate_tcp_handshake() {
    header "Generare: TCP Handshake (3-way)"
    
    local output="$PCAP_DIR/example_tcp_handshake.pcap"
    
    info "Pornire captură pe loopback, port $TCP_PORT..."
    tshark -i lo -f "port $TCP_PORT" -w "$output" -a duration:10 &
    local tshark_pid=$!
    sleep 1
    
    info "Pornire server TCP..."
    nc -l -p $TCP_PORT &
    local server_pid=$!
    sleep 1
    
    info "Conectare client și transfer date..."
    {
        echo "Mesaj 1: Hello from client"
        sleep 0.5
        echo "Mesaj 2: Testing TCP communication"
        sleep 0.5
        echo "Mesaj 3: Goodbye!"
    } | nc localhost $TCP_PORT &
    local client_pid=$!
    
    sleep 3
    
    # Oprire graceful
    kill $server_pid 2>/dev/null || true
    kill $client_pid 2>/dev/null || true
    sleep 1
    kill $tshark_pid 2>/dev/null || true
    
    wait $tshark_pid 2>/dev/null || true
    
    if [ -f "$output" ]; then
        local count=$(tshark -r "$output" 2>/dev/null | wc -l)
        success "TCP Handshake: $output ($count pachete)"
    else
        warn "Nu s-a generat fișierul TCP"
    fi
}

generate_udp_traffic() {
    header "Generare: Trafic UDP"
    
    local output="$PCAP_DIR/example_udp_dns.pcap"
    
    info "Pornire captură UDP pe loopback..."
    tshark -i lo -f "udp port $UDP_PORT" -w "$output" -a duration:8 &
    local tshark_pid=$!
    sleep 1
    
    info "Pornire server UDP echo..."
    # Server UDP simplu cu netcat
    nc -u -l -p $UDP_PORT > /dev/null &
    local server_pid=$!
    sleep 1
    
    info "Trimitere pachete UDP..."
    for i in {1..5}; do
        echo "UDP Packet $i: $(date +%H:%M:%S.%N)" | nc -u -w1 localhost $UDP_PORT &
        sleep 0.3
    done
    
    sleep 3
    
    kill $server_pid 2>/dev/null || true
    kill $tshark_pid 2>/dev/null || true
    
    wait $tshark_pid 2>/dev/null || true
    
    if [ -f "$output" ]; then
        local count=$(tshark -r "$output" 2>/dev/null | wc -l)
        success "UDP Traffic: $output ($count pachete)"
    else
        warn "Nu s-a generat fișierul UDP"
    fi
}

generate_http_request() {
    header "Generare: HTTP Request"
    
    local output="$PCAP_DIR/example_http_request.pcap"
    
    info "Pornire captură HTTP pe loopback..."
    tshark -i lo -f "port $HTTP_PORT" -w "$output" -a duration:15 &
    local tshark_pid=$!
    sleep 1
    
    info "Pornire server HTTP Python..."
    cd "$PROJECT_DIR"
    python3 -m http.server $HTTP_PORT --bind 127.0.0.1 &>/dev/null &
    local http_pid=$!
    sleep 2
    
    info "Executare requests HTTP..."
    
    # GET request
    curl -s -o /dev/null http://127.0.0.1:$HTTP_PORT/ || true
    sleep 0.5
    
    # GET README
    curl -s -o /dev/null http://127.0.0.1:$HTTP_PORT/README.md || true
    sleep 0.5
    
    # HEAD request
    curl -s -I -o /dev/null http://127.0.0.1:$HTTP_PORT/ || true
    sleep 0.5
    
    # 404 request
    curl -s -o /dev/null http://127.0.0.1:$HTTP_PORT/nonexistent.html || true
    
    sleep 3
    
    kill $http_pid 2>/dev/null || true
    kill $tshark_pid 2>/dev/null || true
    
    wait $tshark_pid 2>/dev/null || true
    
    if [ -f "$output" ]; then
        local count=$(tshark -r "$output" 2>/dev/null | wc -l)
        success "HTTP Request: $output ($count pachete)"
    else
        warn "Nu s-a generat fișierul HTTP"
    fi
}

generate_mixed_traffic() {
    header "Generare: Trafic Mixt (100+ pachete)"
    
    local output="$PCAP_DIR/example_mixed_traffic.pcap"
    
    info "Pornire captură multi-protocol..."
    tshark -i lo -f "port $TCP_PORT or port $UDP_PORT or port $HTTP_PORT" -w "$output" -a duration:30 &
    local tshark_pid=$!
    sleep 1
    
    # Server TCP
    info "Pornire servere..."
    nc -l -p $TCP_PORT > /dev/null &
    local tcp_server=$!
    
    nc -u -l -p $UDP_PORT > /dev/null &
    local udp_server=$!
    
    cd "$PROJECT_DIR"
    python3 -m http.server $HTTP_PORT --bind 127.0.0.1 &>/dev/null &
    local http_server=$!
    
    sleep 2
    
    info "Generare trafic TCP (20 mesaje)..."
    for i in {1..20}; do
        echo "TCP message $i" | nc -w1 localhost $TCP_PORT &
        sleep 0.2
    done
    
    sleep 1
    
    info "Generare trafic UDP (15 pachete)..."
    for i in {1..15}; do
        echo "UDP packet $i" | nc -u -w1 localhost $UDP_PORT &
        sleep 0.2
    done
    
    sleep 1
    
    info "Generare trafic HTTP (10 requests)..."
    for i in {1..10}; do
        curl -s -o /dev/null http://127.0.0.1:$HTTP_PORT/ &
        sleep 0.3
    done
    
    sleep 5
    
    # Oprire servere
    kill $tcp_server $udp_server $http_server 2>/dev/null || true
    sleep 2
    kill $tshark_pid 2>/dev/null || true
    
    wait $tshark_pid 2>/dev/null || true
    
    if [ -f "$output" ]; then
        local count=$(tshark -r "$output" 2>/dev/null | wc -l)
        success "Mixed Traffic: $output ($count pachete)"
        
        # Statistici detaliate
        info "Statistici captură:"
        echo "  - TCP: $(tshark -r "$output" -Y 'tcp' 2>/dev/null | wc -l) pachete"
        echo "  - UDP: $(tshark -r "$output" -Y 'udp' 2>/dev/null | wc -l) pachete"
        echo "  - HTTP: $(tshark -r "$output" -Y 'http' 2>/dev/null | wc -l) pachete"
    else
        warn "Nu s-a generat fișierul mixed"
    fi
}

# =============================================================================
# RAPORT FINAL
# =============================================================================

print_summary() {
    header "Sumar Fișiere Generate"
    
    echo "Director: $PCAP_DIR"
    echo ""
    
    printf "%-35s %10s %15s\n" "Fișier" "Dimensiune" "Pachete"
    printf "%-35s %10s %15s\n" "-----------------------------------" "----------" "---------------"
    
    for pcap in "$PCAP_DIR"/*.pcap; do
        if [ -f "$pcap" ]; then
            local name=$(basename "$pcap")
            local size=$(du -h "$pcap" | cut -f1)
            local count=$(tshark -r "$pcap" 2>/dev/null | wc -l)
            printf "%-35s %10s %15s\n" "$name" "$size" "$count"
        fi
    done
    
    echo ""
    success "Capturi generate cu succes!"
    echo ""
    info "Utilizare:"
    echo "  tshark -r pcap/example_tcp_handshake.pcap"
    echo "  tshark -r pcap/example_mixed_traffic.pcap -Y 'tcp.flags.syn==1'"
}

# =============================================================================
# MAIN
# =============================================================================

usage() {
    cat << EOF
Utilizare: $0 [OPȚIUNE]

Opțiuni:
  --all      Generează toate capturile (implicit)
  --tcp      Doar TCP handshake
  --udp      Doar trafic UDP
  --http     Doar HTTP requests
  --mixed    Doar trafic mixt
  --help     Afișează acest mesaj

Exemple:
  $0              # Generează toate
  $0 --tcp        # Doar TCP
  $0 --tcp --udp  # TCP și UDP

EOF
}

main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║          GENERATOR CAPTURI DEMONSTRATIVE - S1                     ║"
    echo "║          Rețele de Calculatoare - ASE București                   ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo ""
    
    check_requirements
    cleanup_processes
    
    local do_tcp=0
    local do_udp=0
    local do_http=0
    local do_mixed=0
    
    # Parsare argumente
    if [ $# -eq 0 ]; then
        do_tcp=1
        do_udp=1
        do_http=1
        do_mixed=1
    else
        while [ $# -gt 0 ]; do
            case "$1" in
                --all)
                    do_tcp=1
                    do_udp=1
                    do_http=1
                    do_mixed=1
                    ;;
                --tcp)
                    do_tcp=1
                    ;;
                --udp)
                    do_udp=1
                    ;;
                --http)
                    do_http=1
                    ;;
                --mixed)
                    do_mixed=1
                    ;;
                --help|-h)
                    usage
                    exit 0
                    ;;
                *)
                    error "Opțiune necunoscută: $1"
                    ;;
            esac
            shift
        done
    fi
    
    # Execuție generatoare
    [ $do_tcp -eq 1 ] && generate_tcp_handshake
    [ $do_udp -eq 1 ] && generate_udp_traffic
    [ $do_http -eq 1 ] && generate_http_request
    [ $do_mixed -eq 1 ] && generate_mixed_traffic
    
    print_summary
}

main "$@"
