#!/usr/bin/env bash
# =============================================================================
# run_all.sh — Demo Automat Săptămâna 12: Email & RPC
# =============================================================================
# Rulează toate demonstrațiile NON-INTERACTIV și produce artefacte:
#   - artifacts/demo.log
#   - artifacts/demo.pcap
#   - artifacts/validation.txt
#
# Utilizare: ./scripts/run_all.sh [--quick]
# =============================================================================
# Licență: MIT | ASE-CSIE Rețele de Calculatoare
# Hypotheticalandrei & Rezolvix
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# =============================================================================
# CONFIGURARE WEEK 12
# =============================================================================
WEEK=12
WEEK_IP_BASE="10.0.${WEEK}"
WEEK_PORT_BASE=$((5100 + 100 * (WEEK - 1)))  # 6200

# Porturi standard
SMTP_PORT=1025
JSONRPC_PORT=${WEEK_PORT_BASE}       # 6200
XMLRPC_PORT=$((WEEK_PORT_BASE + 1))  # 6201
RPC_PORT=$((WEEK_PORT_BASE + 51))    # 6251 (pentru gRPC)

# Directoare
ARTIFACTS_DIR="${PROJECT_ROOT}/artifacts"
LOG_FILE="${ARTIFACTS_DIR}/demo.log"
PCAP_FILE="${ARTIFACTS_DIR}/demo.pcap"
VALIDATION_FILE="${ARTIFACTS_DIR}/validation.txt"

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# =============================================================================
# FUNCȚII HELPER
# =============================================================================

log() {
    local level="$1"
    shift
    local msg="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${msg}" | tee -a "$LOG_FILE"
}

log_info()    { log "INFO" "$@"; }
log_success() { log "OK  " "$@"; }
log_error()   { log "ERR " "$@"; }
log_section() {
    echo "" | tee -a "$LOG_FILE"
    echo "================================================================" | tee -a "$LOG_FILE"
    echo "$1" | tee -a "$LOG_FILE"
    echo "================================================================" | tee -a "$LOG_FILE"
}

cleanup_processes() {
    log_info "Cleanup procese..."
    pkill -f "smtp_server.py" 2>/dev/null || true
    pkill -f "jsonrpc_server.py" 2>/dev/null || true
    pkill -f "xmlrpc_server.py" 2>/dev/null || true
    pkill -f "tcpdump.*demo.pcap" 2>/dev/null || true
    sleep 0.5
}

wait_for_port() {
    local port=$1
    local max_wait=10
    local waited=0
    while ! nc -z localhost "$port" 2>/dev/null && [ $waited -lt $max_wait ]; do
        sleep 0.5
        waited=$((waited + 1))
    done
    nc -z localhost "$port" 2>/dev/null
}

start_capture() {
    log_info "Pornire captură trafic: $PCAP_FILE"
    if command -v tcpdump &>/dev/null; then
        tcpdump -i lo -w "$PCAP_FILE" \
            "port $SMTP_PORT or port $JSONRPC_PORT or port $XMLRPC_PORT" \
            2>/dev/null &
        TCPDUMP_PID=$!
        sleep 1
        log_success "tcpdump pornit (PID: $TCPDUMP_PID)"
    else
        log_info "tcpdump indisponibil - captură omisă"
        touch "$PCAP_FILE"
        TCPDUMP_PID=""
    fi
}

stop_capture() {
    if [ -n "$TCPDUMP_PID" ]; then
        log_info "Oprire captură..."
        kill "$TCPDUMP_PID" 2>/dev/null || true
        sleep 1
    fi
}

# =============================================================================
# DEMO SMTP
# =============================================================================

run_smtp_demo() {
    log_section "DEMO 1: Server SMTP Didactic"
    
    log_info "Pornire server SMTP pe port $SMTP_PORT..."
    python3 src/email/smtp_server.py --port "$SMTP_PORT" --spool "$ARTIFACTS_DIR/spool" &
    SMTP_PID=$!
    
    if wait_for_port "$SMTP_PORT"; then
        log_success "Server SMTP activ (PID: $SMTP_PID)"
    else
        log_error "Server SMTP nu a pornit!"
        return 1
    fi
    
    sleep 1
    
    # Trimitere email test
    log_info "Trimitere email test..."
    python3 src/email/smtp_client.py \
        --server localhost \
        --port "$SMTP_PORT" \
        --from "demo@week12.local" \
        --to "student@ase.ro" \
        --subject "Test SMTP Week 12 - Demo Automat" \
        --body "Acesta este un email generat automat de run_all.sh.

Conținut:
- Demonstrație protocol SMTP
- Verificare comenzi: EHLO, MAIL FROM, RCPT TO, DATA
- Timestamp: $(date)

Săptămâna 12: Email & RPC
" 2>&1 | tee -a "$LOG_FILE"
    
    log_success "Email trimis!"
    
    # Test cu netcat dacă e disponibil
    if command -v nc &>/dev/null; then
        log_info "Test SMTP cu netcat (EHLO + QUIT)..."
        echo -e "EHLO test.local\r\nQUIT\r\n" | nc -q 2 localhost "$SMTP_PORT" 2>&1 | head -10 | tee -a "$LOG_FILE"
    fi
    
    sleep 1
    kill $SMTP_PID 2>/dev/null || true
    log_success "Demo SMTP complet"
}

# =============================================================================
# DEMO JSON-RPC
# =============================================================================

run_jsonrpc_demo() {
    log_section "DEMO 2: Server JSON-RPC 2.0"
    
    log_info "Pornire server JSON-RPC pe port $JSONRPC_PORT..."
    python3 src/rpc/jsonrpc/jsonrpc_server.py --port "$JSONRPC_PORT" &
    JSONRPC_PID=$!
    
    if wait_for_port "$JSONRPC_PORT"; then
        log_success "Server JSON-RPC activ (PID: $JSONRPC_PID)"
    else
        log_error "Server JSON-RPC nu a pornit!"
        return 1
    fi
    
    sleep 1
    
    # Teste RPC
    log_info "Test 1: add(5, 3)..."
    curl -s -X POST -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"add","params":[5,3],"id":1}' \
        http://localhost:$JSONRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    log_info "Test 2: multiply(7, 8)..."
    curl -s -X POST -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"multiply","params":[7,8],"id":2}' \
        http://localhost:$JSONRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    log_info "Test 3: echo('Hello RPC')..."
    curl -s -X POST -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"echo","params":["Hello RPC"],"id":3}' \
        http://localhost:$JSONRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    log_info "Test 4: get_server_info()..."
    curl -s -X POST -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"get_server_info","params":[],"id":4}' \
        http://localhost:$JSONRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    log_info "Test 5: Batch request..."
    curl -s -X POST -H "Content-Type: application/json" \
        -d '[{"jsonrpc":"2.0","method":"add","params":[1,2],"id":10},{"jsonrpc":"2.0","method":"subtract","params":[10,4],"id":11}]' \
        http://localhost:$JSONRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    log_info "Test 6: Eroare - metodă inexistentă..."
    curl -s -X POST -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"nonexistent","params":[],"id":99}' \
        http://localhost:$JSONRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    kill $JSONRPC_PID 2>/dev/null || true
    log_success "Demo JSON-RPC complet"
}

# =============================================================================
# DEMO XML-RPC
# =============================================================================

run_xmlrpc_demo() {
    log_section "DEMO 3: Server XML-RPC"
    
    log_info "Pornire server XML-RPC pe port $XMLRPC_PORT..."
    python3 src/rpc/xmlrpc/xmlrpc_server.py --port "$XMLRPC_PORT" &
    XMLRPC_PID=$!
    
    if wait_for_port "$XMLRPC_PORT"; then
        log_success "Server XML-RPC activ (PID: $XMLRPC_PID)"
    else
        log_error "Server XML-RPC nu a pornit!"
        return 1
    fi
    
    sleep 1
    
    log_info "Test XML-RPC: add(15, 25)..."
    curl -s -X POST -H "Content-Type: text/xml" \
        -d '<?xml version="1.0"?><methodCall><methodName>add</methodName><params><param><value><int>15</int></value></param><param><value><int>25</int></value></param></params></methodCall>' \
        http://localhost:$XMLRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    log_info "Test XML-RPC: echo('XML-RPC Test')..."
    curl -s -X POST -H "Content-Type: text/xml" \
        -d '<?xml version="1.0"?><methodCall><methodName>echo</methodName><params><param><value><string>XML-RPC Test</string></value></param></params></methodCall>' \
        http://localhost:$XMLRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    kill $XMLRPC_PID 2>/dev/null || true
    log_success "Demo XML-RPC complet"
}

# =============================================================================
# VALIDARE
# =============================================================================

generate_validation() {
    log_section "GENERARE VALIDARE"
    
    {
        echo "==============================================="
        echo "VALIDATION REPORT - Week 12: Email & RPC"
        echo "Generated: $(date)"
        echo "==============================================="
        echo ""
        
        echo "[ARTIFACTS]"
        echo "  demo.log: $([ -f "$LOG_FILE" ] && echo "OK ($(wc -l < "$LOG_FILE") lines)" || echo "MISSING")"
        echo "  demo.pcap: $([ -f "$PCAP_FILE" ] && echo "OK ($(stat -c%s "$PCAP_FILE" 2>/dev/null || echo 0) bytes)" || echo "MISSING")"
        echo ""
        
        echo "[PYTHON MODULES]"
        echo "  smtp_server: $(python3 -c 'import src.email.smtp_server' 2>/dev/null && echo "OK" || echo "FAIL")"
        echo "  smtp_client: $(python3 -c 'import src.email.smtp_client' 2>/dev/null && echo "OK" || echo "FAIL")"
        echo "  jsonrpc_server: $(python3 -c 'import src.rpc.jsonrpc.jsonrpc_server' 2>/dev/null && echo "OK" || echo "FAIL")"
        echo "  jsonrpc_client: $(python3 -c 'import src.rpc.jsonrpc.jsonrpc_client' 2>/dev/null && echo "OK" || echo "FAIL")"
        echo "  xmlrpc_server: $(python3 -c 'import src.rpc.xmlrpc.xmlrpc_server' 2>/dev/null && echo "OK" || echo "FAIL")"
        echo "  xmlrpc_client: $(python3 -c 'import src.rpc.xmlrpc.xmlrpc_client' 2>/dev/null && echo "OK" || echo "FAIL")"
        echo "  net_utils: $(python3 -c 'import src.common.net_utils' 2>/dev/null && echo "OK" || echo "FAIL")"
        echo ""
        
        echo "[EXERCISES]"
        echo "  ex_01_smtp: $(python3 exercises/ex_01_smtp.py --help &>/dev/null && echo "OK" || echo "FAIL")"
        echo "  ex_02_rpc: $(python3 exercises/ex_02_rpc.py --help &>/dev/null && echo "OK" || echo "FAIL")"
        echo ""
        
        echo "[TOOLS]"
        echo "  python3: $(python3 --version 2>&1)"
        echo "  curl: $(command -v curl &>/dev/null && echo "OK" || echo "MISSING")"
        echo "  netcat: $(command -v nc &>/dev/null && echo "OK" || echo "MISSING")"
        echo "  tcpdump: $(command -v tcpdump &>/dev/null && echo "OK" || echo "MISSING")"
        echo ""
        
        echo "[DEMO RESULTS]"
        if [ -f "$LOG_FILE" ]; then
            echo "  SMTP tests: $(grep -c '\[OK\].*SMTP' "$LOG_FILE" 2>/dev/null || echo 0) passed"
            echo "  JSON-RPC tests: $(grep -c 'result' "$LOG_FILE" 2>/dev/null || echo 0) results"
            echo "  Errors: $(grep -c '\[ERR\]' "$LOG_FILE" 2>/dev/null || echo 0)"
        fi
        echo ""
        
        echo "[CONFIGURATION]"
        echo "  WEEK: $WEEK"
        echo "  IP_BASE: $WEEK_IP_BASE.0/24"
        echo "  PORT_BASE: $WEEK_PORT_BASE"
        echo "  SMTP_PORT: $SMTP_PORT"
        echo "  JSONRPC_PORT: $JSONRPC_PORT"
        echo "  XMLRPC_PORT: $XMLRPC_PORT"
        echo ""
        
        echo "==============================================="
        echo "VALIDATION: $([ -f "$LOG_FILE" ] && [ -f "$PCAP_FILE" ] && echo "PASSED" || echo "PARTIAL")"
        echo "==============================================="
        
    } > "$VALIDATION_FILE"
    
    log_success "Validare generată: $VALIDATION_FILE"
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    local quick_mode=false
    
    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --quick) quick_mode=true ;;
            --help|-h)
                echo "Usage: $0 [--quick]"
                echo ""
                echo "Options:"
                echo "  --quick    Skip XML-RPC demo"
                echo ""
                exit 0
                ;;
        esac
        shift
    done
    
    # Setup
    cleanup_processes
    mkdir -p "$ARTIFACTS_DIR" "$ARTIFACTS_DIR/spool"
    
    # Clear previous logs
    > "$LOG_FILE"
    
    log_section "SĂPTĂMÂNA 12: DEMO AUTOMAT EMAIL & RPC"
    log_info "Project root: $PROJECT_ROOT"
    log_info "Artifacts: $ARTIFACTS_DIR"
    log_info "Quick mode: $quick_mode"
    
    # Start capture
    start_capture
    
    # Run demos
    trap 'cleanup_processes; stop_capture' EXIT
    
    run_smtp_demo || log_error "Demo SMTP eșuat"
    sleep 1
    
    run_jsonrpc_demo || log_error "Demo JSON-RPC eșuat"
    sleep 1
    
    if [ "$quick_mode" = false ]; then
        run_xmlrpc_demo || log_error "Demo XML-RPC eșuat"
    fi
    
    # Stop capture
    stop_capture
    
    # Generate validation
    generate_validation
    
    # Summary
    log_section "SUMAR"
    log_success "Demo complet!"
    log_info "Artefacte generate:"
    log_info "  - $LOG_FILE"
    log_info "  - $PCAP_FILE"
    log_info "  - $VALIDATION_FILE"
    
    echo ""
    echo "Pentru validare, rulați: ./tests/smoke_test.sh"
}

main "$@"
