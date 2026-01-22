#!/usr/bin/env bash
# =============================================================================
# run_all.sh - Demo Automat Săptămâna 13 (IoT & Securitate)
# =============================================================================
# Produce:
#   - artifacts/demo.log        (log complet al demonstrației)
#   - artifacts/demo.pcap       (captură trafic de rețea)
#   - artifacts/validation.txt  (rezultate validare)
#
# Rulează fără input interactiv. Validat de tests/smoke_test.sh.
#
# Utilizare:
#   ./scripts/run_all.sh              # Demonstrație completă
#   ./scripts/run_all.sh --quick      # Demonstrație rapidă (fără Docker)
#   ./scripts/run_all.sh --mininet    # Demonstrație Mininet (necesită sudo)
#
# Licență: MIT
# Colectiv Didactic ASE-CSIE / Hypotheticalandrei & Rezolvix
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# CONSTANTE
# -----------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$PROJECT_DIR/artifacts"

# Plan unitar de adrese - WEEK 13
WEEK=13
NETWORK="10.0.${WEEK}.0/24"
GATEWAY="10.0.${WEEK}.1"
HOST1="10.0.${WEEK}.11"
HOST2="10.0.${WEEK}.12"
HOST3="10.0.${WEEK}.13"
SERVER="10.0.${WEEK}.100"

# Plan unitar de porturi
TCP_APP_PORT=9090
UDP_APP_PORT=9091
HTTP_PORT=8080
PROXY_PORT=8888
DNS_PORT=5353
FTP_PORT=2121
SSH_PORT=2222
MQTT_PORT=1883
MQTT_TLS_PORT=8883

# Porturi specifice săptămânii (bază + 100*(WEEK-1))
WEEK_PORT_BASE=$((5100 + 100 * (WEEK - 1)))  # 6300
SCAN_RESULT_PORT=$((WEEK_PORT_BASE + 1))      # 6301

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Variabile de control
DEMO_MODE="quick"
DEMO_LOG="$ARTIFACTS_DIR/demo.log"
DEMO_PCAP="$ARTIFACTS_DIR/demo.pcap"
VALIDATION_FILE="$ARTIFACTS_DIR/validation.txt"

# -----------------------------------------------------------------------------
# FUNCȚII HELPER
# -----------------------------------------------------------------------------

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo -e "$msg"
    echo "$msg" >> "$DEMO_LOG"
}

log_info() {
    log "${CYAN}[INFO]${NC} $1"
}

log_success() {
    log "${GREEN}[✓]${NC} $1"
}

log_warning() {
    log "${YELLOW}[!]${NC} $1"
}

log_error() {
    log "${RED}[✗]${NC} $1"
}

log_section() {
    echo "" | tee -a "$DEMO_LOG"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}" | tee -a "$DEMO_LOG"
    echo -e "${BLUE}  $1${NC}" | tee -a "$DEMO_LOG"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}" | tee -a "$DEMO_LOG"
    echo "" | tee -a "$DEMO_LOG"
}

cleanup_on_exit() {
    log_info "Cleanup la ieșire..."
    # Oprire eventuale procese de fundal
    pkill -f "tcpdump.*demo.pcap" 2>/dev/null || true
    pkill -f "tshark.*demo.pcap" 2>/dev/null || true
}

trap cleanup_on_exit EXIT

# -----------------------------------------------------------------------------
# INIȚIALIZARE
# -----------------------------------------------------------------------------

init_demo() {
    log_section "Inițializare Demo S13"
    
    # Creare director artifacts
    mkdir -p "$ARTIFACTS_DIR"
    
    # Inițializare fișiere
    echo "# Demo Log - Săptămâna 13 IoT & Securitate" > "$DEMO_LOG"
    echo "# Început: $(date)" >> "$DEMO_LOG"
    echo "# Network: $NETWORK" >> "$DEMO_LOG"
    echo "" >> "$DEMO_LOG"
    
    echo "# Validation Results - S13" > "$VALIDATION_FILE"
    echo "# Generated: $(date)" >> "$VALIDATION_FILE"
    echo "" >> "$VALIDATION_FILE"
    
    log_success "Directoare și fișiere inițializate"
    log_info "Log: $DEMO_LOG"
    log_info "PCAP: $DEMO_PCAP"
    log_info "Validation: $VALIDATION_FILE"
}

# -----------------------------------------------------------------------------
# VERIFICARE DEPENDENȚE
# -----------------------------------------------------------------------------

check_dependencies() {
    log_section "Verificare Dependențe"
    
    local deps_ok=true
    
    # Python
    if command -v python3 &>/dev/null; then
        log_success "Python3: $(python3 --version 2>&1)"
        echo "PASS: Python3 available" >> "$VALIDATION_FILE"
    else
        log_error "Python3 nu este instalat"
        echo "FAIL: Python3 missing" >> "$VALIDATION_FILE"
        deps_ok=false
    fi
    
    # Verificare module Python
    for module in socket json concurrent.futures; do
        if python3 -c "import $module" 2>/dev/null; then
            log_success "  Module $module: OK"
        else
            log_warning "  Module $module: Lipsă"
        fi
    done
    
    # Netcat
    if command -v nc &>/dev/null || command -v netcat &>/dev/null; then
        log_success "Netcat: disponibil"
        echo "PASS: Netcat available" >> "$VALIDATION_FILE"
    else
        log_warning "Netcat: nu este disponibil"
        echo "WARN: Netcat missing" >> "$VALIDATION_FILE"
    fi
    
    # tcpdump/tshark pentru captură
    if command -v tcpdump &>/dev/null; then
        log_success "tcpdump: disponibil"
        echo "PASS: tcpdump available" >> "$VALIDATION_FILE"
    elif command -v tshark &>/dev/null; then
        log_success "tshark: disponibil"
        echo "PASS: tshark available" >> "$VALIDATION_FILE"
    else
        log_warning "tcpdump/tshark: nu sunt disponibile (pcap va fi gol)"
        echo "WARN: No packet capture tool" >> "$VALIDATION_FILE"
    fi
    
    # nmap (opțional)
    if command -v nmap &>/dev/null; then
        log_success "nmap: disponibil (opțional)"
    else
        log_info "nmap: nu este instalat (folosim scanner Python)"
    fi
    
    echo "" >> "$VALIDATION_FILE"
}

# -----------------------------------------------------------------------------
# CAPTURĂ TRAFIC
# -----------------------------------------------------------------------------

start_capture() {
    log_info "Pornire captură trafic..."
    
    # Creare pcap gol inițial
    touch "$DEMO_PCAP"
    
    if command -v tcpdump &>/dev/null; then
        # Captură pe loopback și toate interfețele
        sudo tcpdump -i any -w "$DEMO_PCAP" -c 1000 \
            "port $MQTT_PORT or port $HTTP_PORT or port $FTP_PORT or port $SSH_PORT or icmp" \
            2>/dev/null &
        CAPTURE_PID=$!
        log_success "tcpdump pornit (PID: $CAPTURE_PID)"
    elif command -v tshark &>/dev/null; then
        sudo tshark -i any -w "$DEMO_PCAP" -c 500 \
            -f "port $MQTT_PORT or port $HTTP_PORT or port $FTP_PORT" \
            2>/dev/null &
        CAPTURE_PID=$!
        log_success "tshark pornit (PID: $CAPTURE_PID)"
    else
        log_warning "Nu se poate porni captura (tcpdump/tshark lipsă)"
        CAPTURE_PID=""
        # Creăm un pcap minimal valid (header pcap)
        printf '\xd4\xc3\xb2\xa1\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x00\x00\x01\x00\x00\x00' > "$DEMO_PCAP"
    fi
}

stop_capture() {
    if [ -n "$CAPTURE_PID" ] && kill -0 "$CAPTURE_PID" 2>/dev/null; then
        log_info "Oprire captură..."
        sudo kill "$CAPTURE_PID" 2>/dev/null || true
        sleep 1
    fi
    
    if [ -f "$DEMO_PCAP" ] && [ -s "$DEMO_PCAP" ]; then
        local pcap_size=$(stat -c%s "$DEMO_PCAP" 2>/dev/null || stat -f%z "$DEMO_PCAP" 2>/dev/null || echo "0")
        log_success "Captură salvată: $DEMO_PCAP ($pcap_size bytes)"
        echo "PASS: PCAP generated ($pcap_size bytes)" >> "$VALIDATION_FILE"
    else
        # Asigurare pcap minimal valid
        printf '\xd4\xc3\xb2\xa1\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x00\x00\x01\x00\x00\x00' > "$DEMO_PCAP"
        log_warning "Captură goală (trafic insuficient)"
        echo "WARN: Empty PCAP (minimal traffic)" >> "$VALIDATION_FILE"
    fi
}

# -----------------------------------------------------------------------------
# DEMONSTRAȚII SECURITATE
# -----------------------------------------------------------------------------

demo_port_scanner() {
    log_section "Demo 1: Scanner de Porturi"
    
    local scanner="$PROJECT_DIR/python/exercises/ex_01_port_scanner.py"
    local scan_output="$ARTIFACTS_DIR/scan_results.json"
    
    if [ ! -f "$scanner" ]; then
        log_error "Scanner nu există: $scanner"
        echo "FAIL: Port scanner script missing" >> "$VALIDATION_FILE"
        return 1
    fi
    
    log_info "Scanare localhost (porturi comune)..."
    
    # Scanare localhost pe porturi comune
    if python3 "$scanner" --target 127.0.0.1 --ports 22,80,443,8080,1883,3306 \
        --timeout 0.5 --workers 10 --json-out "$scan_output" >> "$DEMO_LOG" 2>&1; then
        log_success "Scanare completă"
        
        if [ -f "$scan_output" ]; then
            local open_ports=$(python3 -c "import json; d=json.load(open('$scan_output')); print(len([p for p in d.get('results',{}).values() if p.get('state')=='open']))" 2>/dev/null || echo "0")
            log_info "Porturi deschise găsite: $open_ports"
            echo "PASS: Port scan completed, found $open_ports open ports" >> "$VALIDATION_FILE"
        fi
    else
        log_warning "Scanare cu erori (normal pe sisteme fără servicii)"
        echo "WARN: Port scan had issues (expected on minimal systems)" >> "$VALIDATION_FILE"
    fi
    
    # Test banner grabbing simplu
    log_info "Test banner grabbing pe SSH local..."
    local banner_grabber="$PROJECT_DIR/python/exploits/banner_grabber.py"
    if [ -f "$banner_grabber" ]; then
        timeout 5 python3 "$banner_grabber" --target 127.0.0.1 --port 22 >> "$DEMO_LOG" 2>&1 || true
    fi
}

demo_vulnerability_check() {
    log_section "Demo 2: Verificare Vulnerabilități"
    
    local vuln_checker="$PROJECT_DIR/python/exercises/ex_04_vuln_checker.py"
    local vuln_output="$ARTIFACTS_DIR/vuln_report.json"
    
    if [ ! -f "$vuln_checker" ]; then
        log_warning "Vulnerability checker nu există, skip"
        echo "SKIP: Vulnerability checker not found" >> "$VALIDATION_FILE"
        return
    fi
    
    log_info "Verificare vulnerabilități pe localhost..."
    
    if python3 "$vuln_checker" --target 127.0.0.1 --quick \
        --output "$vuln_output" >> "$DEMO_LOG" 2>&1; then
        log_success "Verificare completă"
        echo "PASS: Vulnerability check completed" >> "$VALIDATION_FILE"
    else
        log_warning "Verificare parțială (unele servicii indisponibile)"
        echo "WARN: Partial vulnerability check" >> "$VALIDATION_FILE"
    fi
}

demo_packet_sniffer() {
    log_section "Demo 3: Packet Sniffer (conceptual)"
    
    local sniffer="$PROJECT_DIR/python/exercises/ex_03_packet_sniffer.py"
    
    if [ ! -f "$sniffer" ]; then
        log_warning "Packet sniffer nu există, skip"
        echo "SKIP: Packet sniffer not found" >> "$VALIDATION_FILE"
        return
    fi
    
    log_info "Verificare sintaxă packet sniffer..."
    
    if python3 -m py_compile "$sniffer" 2>/dev/null; then
        log_success "Sintaxă validă: ex_03_packet_sniffer.py"
        echo "PASS: Packet sniffer syntax OK" >> "$VALIDATION_FILE"
    else
        log_error "Eroare sintaxă în packet sniffer"
        echo "FAIL: Packet sniffer syntax error" >> "$VALIDATION_FILE"
    fi
    
    # Notă: rularea efectivă a sniffer-ului necesită root și scapy
    log_info "Notă: Rularea sniffer-ului necesită: sudo python3 $sniffer -i eth0"
}

demo_network_simulation() {
    log_section "Demo 4: Simulare Trafic de Rețea"
    
    log_info "Generare trafic de test pe localhost..."
    
    # Ping local
    ping -c 3 127.0.0.1 >> "$DEMO_LOG" 2>&1 || true
    
    # Test conexiune TCP
    log_info "Test conexiuni TCP..."
    for port in 22 80 443; do
        if timeout 1 bash -c "echo >/dev/tcp/127.0.0.1/$port" 2>/dev/null; then
            log_success "Port $port: deschis"
        else
            log_info "Port $port: închis/filtrat"
        fi
    done
    
    echo "PASS: Network simulation completed" >> "$VALIDATION_FILE"
}

# -----------------------------------------------------------------------------
# VALIDARE FINALĂ
# -----------------------------------------------------------------------------

validate_results() {
    log_section "Validare Rezultate"
    
    local all_ok=true
    
    # Verificare demo.log
    if [ -f "$DEMO_LOG" ] && [ -s "$DEMO_LOG" ]; then
        local log_lines=$(wc -l < "$DEMO_LOG")
        log_success "demo.log: $log_lines linii"
        echo "PASS: demo.log exists ($log_lines lines)" >> "$VALIDATION_FILE"
    else
        log_error "demo.log: lipsă sau gol"
        echo "FAIL: demo.log missing or empty" >> "$VALIDATION_FILE"
        all_ok=false
    fi
    
    # Verificare demo.pcap
    if [ -f "$DEMO_PCAP" ]; then
        local pcap_size=$(stat -c%s "$DEMO_PCAP" 2>/dev/null || stat -f%z "$DEMO_PCAP" 2>/dev/null || echo "0")
        if [ "$pcap_size" -ge 24 ]; then
            log_success "demo.pcap: $pcap_size bytes"
            echo "PASS: demo.pcap exists ($pcap_size bytes)" >> "$VALIDATION_FILE"
        else
            log_warning "demo.pcap: prea mic ($pcap_size bytes)"
            echo "WARN: demo.pcap too small" >> "$VALIDATION_FILE"
        fi
    else
        log_error "demo.pcap: lipsă"
        echo "FAIL: demo.pcap missing" >> "$VALIDATION_FILE"
        all_ok=false
    fi
    
    # Verificare validation.txt
    if [ -f "$VALIDATION_FILE" ] && [ -s "$VALIDATION_FILE" ]; then
        local pass_count=$(grep -c "^PASS:" "$VALIDATION_FILE" || echo "0")
        local fail_count=$(grep -c "^FAIL:" "$VALIDATION_FILE" || echo "0")
        local warn_count=$(grep -c "^WARN:" "$VALIDATION_FILE" || echo "0")
        
        echo "" >> "$VALIDATION_FILE"
        echo "# Summary" >> "$VALIDATION_FILE"
        echo "TOTAL_PASS: $pass_count" >> "$VALIDATION_FILE"
        echo "TOTAL_FAIL: $fail_count" >> "$VALIDATION_FILE"
        echo "TOTAL_WARN: $warn_count" >> "$VALIDATION_FILE"
        
        log_success "validation.txt: PASS=$pass_count, FAIL=$fail_count, WARN=$warn_count"
    fi
    
    echo "" >> "$VALIDATION_FILE"
    echo "# End: $(date)" >> "$VALIDATION_FILE"
    
    if [ "$all_ok" = true ] && [ "$fail_count" -eq 0 ]; then
        log_success "Toate validările au trecut!"
        return 0
    else
        log_warning "Unele validări au eșuat (verificați $VALIDATION_FILE)"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║   DEMO AUTOMAT - Săptămâna 13: IoT & Securitate                  ║"
    echo "║   Rețele de Calculatoare - ASE-CSIE                              ║"
    echo "║   Network: $NETWORK                                       ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

usage() {
    echo "Utilizare: $0 [opțiuni]"
    echo ""
    echo "Opțiuni:"
    echo "  --quick       Demonstrație rapidă (fără Docker)"
    echo "  --full        Demonstrație completă (necesită Docker)"
    echo "  --mininet     Demonstrație Mininet (necesită sudo)"
    echo "  --help        Afișare acest mesaj"
    echo ""
    echo "Output:"
    echo "  artifacts/demo.log        - Log demonstrație"
    echo "  artifacts/demo.pcap       - Captură trafic"
    echo "  artifacts/validation.txt  - Rezultate validare"
}

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick)
                DEMO_MODE="quick"
                shift
                ;;
            --full)
                DEMO_MODE="full"
                shift
                ;;
            --mininet)
                DEMO_MODE="mininet"
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                log_warning "Opțiune necunoscută: $1"
                shift
                ;;
        esac
    done
    
    print_banner
    
    # Schimbare în directorul proiectului
    cd "$PROJECT_DIR"
    
    # Inițializare
    init_demo
    
    # Verificare dependențe
    check_dependencies
    
    # Pornire captură
    start_capture
    
    # Rulare demonstrații
    demo_port_scanner
    demo_vulnerability_check
    demo_packet_sniffer
    demo_network_simulation
    
    # Oprire captură
    stop_capture
    
    # Validare finală
    validate_results
    
    log_section "Demo Complet"
    log_success "Artefacte generate în: $ARTIFACTS_DIR/"
    log_info "Verificare: ./tests/smoke_test.sh"
    
    echo ""
    echo "Fișiere generate:"
    ls -la "$ARTIFACTS_DIR/" 2>/dev/null || true
}

main "$@"
