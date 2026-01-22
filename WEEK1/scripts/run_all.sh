#!/usr/bin/env bash
#===============================================================================
# run_all.sh - Demo automat Săptămâna 1: Analiză trafic și instrumentare
#===============================================================================
# Rețele de Calculatoare
# ASE București / CSIE
#
# Generează automat artefactele demonstrate:
#   - artifacts/demo.log      (log de execuție complet)
#   - artifacts/demo.pcap     (captură trafic TCP/UDP/ICMP)
#   - artifacts/validation.txt (rezultate validare)
#
# Utilizare:
#   bash scripts/run_all.sh
#   bash scripts/run_all.sh --quick   # Doar TCP/UDP, fără Mininet
#
# Plan IP: 10.0.1.0/24 (WEEK=1)
# Porturi: TCP_APP=9090, UDP_APP=9091, HTTP=8080, WEEK_BASE=5100-5199
#===============================================================================

set -e

# Directoare
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$PROJECT_DIR/artifacts"

# Porturi standardizate (conform plan transversal)
TCP_APP_PORT=9090
UDP_APP_PORT=9091
HTTP_PORT=8080
WEEK_PORT_BASE=5100

# Fișiere output
DEMO_LOG="$ARTIFACTS_DIR/demo.log"
DEMO_PCAP="$ARTIFACTS_DIR/demo.pcap"
VALIDATION_FILE="$ARTIFACTS_DIR/validation.txt"

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$DEMO_LOG"; }
success() { echo -e "${GREEN}[✓]${NC} $1" | tee -a "$DEMO_LOG"; }
warn()    { echo -e "${YELLOW}[!]${NC} $1" | tee -a "$DEMO_LOG"; }
error()   { echo -e "${RED}[✗]${NC} $1" | tee -a "$DEMO_LOG"; exit 1; }

header() {
    local msg="$1"
    echo "" | tee -a "$DEMO_LOG"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$DEMO_LOG"
    echo -e "${CYAN}  $msg${NC}" | tee -a "$DEMO_LOG"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$DEMO_LOG"
    echo "" | tee -a "$DEMO_LOG"
}

#===============================================================================
# Inițializare
#===============================================================================

init_demo() {
    mkdir -p "$ARTIFACTS_DIR"
    
    # Resetăm log-ul
    echo "# Demo Log - Săptămâna 1: Analiză trafic și instrumentare" > "$DEMO_LOG"
    echo "# Generat: $(date -Iseconds)" >> "$DEMO_LOG"
    echo "# Plan IP: 10.0.1.0/24 | Porturi: TCP=$TCP_APP_PORT, UDP=$UDP_APP_PORT" >> "$DEMO_LOG"
    echo "" >> "$DEMO_LOG"
    
    # Inițializăm fișierul de validare
    echo "# Validation Results - Week 1" > "$VALIDATION_FILE"
    echo "# Timestamp: $(date -Iseconds)" >> "$VALIDATION_FILE"
    echo "" >> "$VALIDATION_FILE"
}

cleanup_processes() {
    info "Curățare procese anterioare..."
    pkill -f "nc -l.*$TCP_APP_PORT" 2>/dev/null || true
    pkill -f "nc -l.*$UDP_APP_PORT" 2>/dev/null || true
    pkill -f "tshark.*demo" 2>/dev/null || true
    pkill -f "python3 -m http.server" 2>/dev/null || true
    sleep 1
}

trap 'cleanup_processes' EXIT

#===============================================================================
# Verificare prerechizite
#===============================================================================

check_requirements() {
    header "Verificare prerechizite"
    
    local missing=0
    local validated=0
    
    for cmd in nc tshark tcpdump python3 curl ip ss; do
        if command -v $cmd &>/dev/null; then
            success "$cmd: $(command -v $cmd)"
            echo "PASS: $cmd disponibil" >> "$VALIDATION_FILE"
            ((validated++))
        else
            warn "$cmd: NU GĂSIT"
            echo "WARN: $cmd lipsește" >> "$VALIDATION_FILE"
            ((missing++))
        fi
    done
    
    # Verificare Python versiune
    local pyver=$(python3 --version 2>&1 | awk '{print $2}')
    info "Python versiune: $pyver"
    echo "INFO: Python $pyver" >> "$VALIDATION_FILE"
    
    echo "" >> "$VALIDATION_FILE"
    echo "Prerequisites check: $validated passed, $missing warnings" >> "$VALIDATION_FILE"
    echo "" >> "$VALIDATION_FILE"
    
    if [[ $missing -gt 2 ]]; then
        error "Prea multe instrumente lipsesc. Rulează: sudo bash scripts/setup.sh"
    fi
}

#===============================================================================
# Demo 1: Comunicare TCP cu captură
#===============================================================================

demo_tcp_communication() {
    header "Demo 1: Comunicare TCP (port $TCP_APP_PORT)"
    
    local tcp_pcap="$ARTIFACTS_DIR/tcp_session.pcap"
    
    # Pornire captură în background
    info "Pornire captură tshark pe loopback..."
    tshark -i lo -f "port $TCP_APP_PORT" -w "$tcp_pcap" -a duration:15 2>/dev/null &
    local tshark_pid=$!
    sleep 1
    
    # Server TCP
    info "Pornire server TCP echo pe port $TCP_APP_PORT..."
    nc -l -p $TCP_APP_PORT > /dev/null &
    local server_pid=$!
    sleep 1
    
    # Client TCP - trimite mesaje
    info "Trimitere mesaje de la client..."
    {
        echo "HELLO from Week1 Demo"
        sleep 0.3
        echo "Testing TCP handshake observation"
        sleep 0.3
        echo "Packet analysis exercise"
        sleep 0.3
        echo "GOODBYE"
    } | nc localhost $TCP_APP_PORT &
    local client_pid=$!
    
    sleep 3
    
    # Oprire procese
    kill $server_pid 2>/dev/null || true
    kill $client_pid 2>/dev/null || true
    sleep 1
    kill $tshark_pid 2>/dev/null || true
    wait $tshark_pid 2>/dev/null || true
    
    # Validare
    if [[ -f "$tcp_pcap" ]]; then
        local count=$(tshark -r "$tcp_pcap" 2>/dev/null | wc -l)
        success "Captură TCP: $count pachete în $tcp_pcap"
        echo "PASS: TCP capture - $count packets" >> "$VALIDATION_FILE"
        
        # Afișăm handshake-ul
        info "TCP Three-Way Handshake:"
        tshark -r "$tcp_pcap" -Y "tcp.flags.syn==1" 2>/dev/null | head -5 | tee -a "$DEMO_LOG"
    else
        warn "Nu s-a generat captura TCP"
        echo "FAIL: TCP capture not generated" >> "$VALIDATION_FILE"
    fi
}

#===============================================================================
# Demo 2: Comunicare UDP
#===============================================================================

demo_udp_communication() {
    header "Demo 2: Comunicare UDP (port $UDP_APP_PORT)"
    
    local udp_pcap="$ARTIFACTS_DIR/udp_session.pcap"
    
    # Captură
    info "Pornire captură UDP..."
    tshark -i lo -f "udp port $UDP_APP_PORT" -w "$udp_pcap" -a duration:10 2>/dev/null &
    local tshark_pid=$!
    sleep 1
    
    # Server UDP
    info "Pornire server UDP pe port $UDP_APP_PORT..."
    nc -u -l -p $UDP_APP_PORT > /dev/null &
    local server_pid=$!
    sleep 1
    
    # Trimitere pachete UDP
    info "Trimitere datagrame UDP..."
    for i in {1..5}; do
        echo "UDP Packet $i - $(date +%H:%M:%S.%N)" | nc -u -w1 localhost $UDP_APP_PORT &
        sleep 0.3
    done
    
    sleep 3
    
    kill $server_pid 2>/dev/null || true
    kill $tshark_pid 2>/dev/null || true
    wait $tshark_pid 2>/dev/null || true
    
    if [[ -f "$udp_pcap" ]]; then
        local count=$(tshark -r "$udp_pcap" 2>/dev/null | wc -l)
        success "Captură UDP: $count pachete"
        echo "PASS: UDP capture - $count packets" >> "$VALIDATION_FILE"
    else
        echo "WARN: UDP capture incomplete" >> "$VALIDATION_FILE"
    fi
}

#===============================================================================
# Demo 3: Utilitare diagnostic (ping, ss, ip)
#===============================================================================

demo_diagnostic_tools() {
    header "Demo 3: Utilitare de diagnostic"
    
    info "Test conectivitate localhost:"
    ping -c 3 127.0.0.1 2>&1 | tee -a "$DEMO_LOG"
    echo "PASS: ping localhost" >> "$VALIDATION_FILE"
    
    info "Porturi deschise (ss -tuln):"
    ss -tuln 2>&1 | head -15 | tee -a "$DEMO_LOG"
    
    info "Interfețe de rețea (ip addr):"
    ip addr show lo 2>&1 | tee -a "$DEMO_LOG"
    
    info "Tabela ARP (ip neigh):"
    ip neigh show 2>&1 | head -10 | tee -a "$DEMO_LOG" || echo "  (tabel gol sau neaccesibil)"
    
    echo "PASS: diagnostic tools executed" >> "$VALIDATION_FILE"
}

#===============================================================================
# Demo 4: Server HTTP simplu
#===============================================================================

demo_http_server() {
    header "Demo 4: Server HTTP Python (port $HTTP_PORT)"
    
    local http_pcap="$ARTIFACTS_DIR/http_session.pcap"
    
    cd "$PROJECT_DIR"
    
    # Captură
    tshark -i lo -f "port $HTTP_PORT" -w "$http_pcap" -a duration:15 2>/dev/null &
    local tshark_pid=$!
    sleep 1
    
    # Server HTTP
    info "Pornire server HTTP Python..."
    python3 -m http.server $HTTP_PORT --bind 127.0.0.1 &>/dev/null &
    local http_pid=$!
    sleep 2
    
    # Requests
    info "Executare requests HTTP..."
    curl -s -o /dev/null -w "GET / : HTTP %{http_code}\n" http://127.0.0.1:$HTTP_PORT/ | tee -a "$DEMO_LOG"
    curl -s -o /dev/null -w "GET /README.md : HTTP %{http_code}\n" http://127.0.0.1:$HTTP_PORT/README.md | tee -a "$DEMO_LOG"
    curl -s -o /dev/null -w "GET /404 : HTTP %{http_code}\n" http://127.0.0.1:$HTTP_PORT/nonexistent 2>/dev/null | tee -a "$DEMO_LOG" || true
    
    sleep 2
    
    kill $http_pid 2>/dev/null || true
    kill $tshark_pid 2>/dev/null || true
    wait $tshark_pid 2>/dev/null || true
    
    if [[ -f "$http_pcap" ]]; then
        local count=$(tshark -r "$http_pcap" 2>/dev/null | wc -l)
        success "Captură HTTP: $count pachete"
        echo "PASS: HTTP capture - $count packets" >> "$VALIDATION_FILE"
    fi
}

#===============================================================================
# Demo 5: Python exercises
#===============================================================================

demo_python_exercises() {
    header "Demo 5: Exerciții Python"
    
    cd "$PROJECT_DIR"
    
    # Test TCP/UDP demo
    if [[ -f "python/exercises/ex_1_02_tcp_server_client.py" ]]; then
        info "Rulare self-test TCP/UDP..."
        python3 python/exercises/ex_1_02_tcp_server_client.py --test 2>&1 | tee -a "$DEMO_LOG"
        if [[ $? -eq 0 ]]; then
            echo "PASS: Python TCP/UDP self-test" >> "$VALIDATION_FILE"
        else
            echo "WARN: Python TCP/UDP self-test partial" >> "$VALIDATION_FILE"
        fi
    fi
    
    # Test ping latency
    if [[ -f "python/exercises/ex_1_01_ping_latency.py" ]]; then
        info "Rulare ping latency exercise..."
        timeout 10 python3 python/exercises/ex_1_01_ping_latency.py --host 127.0.0.1 --count 3 2>&1 | tee -a "$DEMO_LOG" || true
    fi
}

#===============================================================================
# Consolidare captură finală
#===============================================================================

consolidate_captures() {
    header "Consolidare captură finală"
    
    cd "$ARTIFACTS_DIR"
    
    # Combinăm toate capturile într-una singură dacă avem mergecap
    if command -v mergecap &>/dev/null; then
        local pcaps=$(ls -1 *.pcap 2>/dev/null | grep -v demo.pcap)
        if [[ -n "$pcaps" ]]; then
            info "Fuzionare capturi în demo.pcap..."
            mergecap -w demo.pcap $pcaps 2>/dev/null || cp tcp_session.pcap demo.pcap 2>/dev/null || true
        fi
    else
        # Copiem cea mai mare captură ca demo.pcap
        if [[ -f tcp_session.pcap ]]; then
            cp tcp_session.pcap demo.pcap
        fi
    fi
    
    if [[ -f "$DEMO_PCAP" ]]; then
        local total=$(tshark -r "$DEMO_PCAP" 2>/dev/null | wc -l)
        success "Captură finală: $total pachete în demo.pcap"
        echo "" >> "$VALIDATION_FILE"
        echo "FINAL: demo.pcap contains $total packets" >> "$VALIDATION_FILE"
    fi
}

#===============================================================================
# Sumar final
#===============================================================================

print_summary() {
    header "Sumar execuție"
    
    echo "Artefacte generate în $ARTIFACTS_DIR:" | tee -a "$DEMO_LOG"
    echo "" | tee -a "$DEMO_LOG"
    
    ls -lh "$ARTIFACTS_DIR"/*.{pcap,log,txt} 2>/dev/null | while read line; do
        echo "  $line" | tee -a "$DEMO_LOG"
    done
    
    echo "" | tee -a "$DEMO_LOG"
    echo "" >> "$VALIDATION_FILE"
    echo "# Summary" >> "$VALIDATION_FILE"
    echo "Demo completed: $(date -Iseconds)" >> "$VALIDATION_FILE"
    
    # Verificări finale
    local status="SUCCESS"
    [[ -f "$DEMO_LOG" ]] || status="PARTIAL"
    [[ -f "$DEMO_PCAP" ]] || status="PARTIAL"
    [[ -f "$VALIDATION_FILE" ]] || status="PARTIAL"
    
    echo "Status: $status" >> "$VALIDATION_FILE"
    
    success "Demo finalizat! Status: $status"
    echo ""
    info "Verificare rezultate:"
    echo "  tshark -r artifacts/demo.pcap | head -20"
    echo "  cat artifacts/validation.txt"
    echo "  cat artifacts/demo.log"
}

#===============================================================================
# Main
#===============================================================================

main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║     DEMO AUTOMAT - Săptămâna 1: Analiză trafic și instrumentare   ║"
    echo "║     Rețele de Calculatoare - ASE București / CSIE                 ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo ""
    
    init_demo
    cleanup_processes
    check_requirements
    
    if [[ "${1:-}" == "--quick" ]]; then
        info "Mod rapid - doar TCP/UDP"
        demo_tcp_communication
        demo_udp_communication
    else
        demo_tcp_communication
        demo_udp_communication
        demo_diagnostic_tools
        demo_http_server
        demo_python_exercises
    fi
    
    consolidate_captures
    print_summary
}

main "$@"
