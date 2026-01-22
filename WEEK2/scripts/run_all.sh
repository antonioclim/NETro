#!/usr/bin/env bash
# =============================================================================
# run_all.sh - Demo Automat Săptămâna 2: Socket Programming TCP/UDP
# =============================================================================
# Rulează demonstrația completă FĂRĂ input interactiv.
# Produce artefacte în artifacts/:
#   - demo.log      (log complet al demo-ului)
#   - demo.pcap     (captură combinată TCP+UDP)
#   - validation.txt (rezultate validare)
# =============================================================================
# Rețele de Calculatoare - ASE București, CSIE
# Hypotheticalandrei & Rezolvix | MIT License
# =============================================================================

set -euo pipefail

# =============================================================================
# VARIABILE ȘI CONSTANTE (WEEK 2)
# =============================================================================
WEEK=2
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Plan IP pentru WEEK 2: 10.0.2.0/24
NETWORK="10.0.${WEEK}"
SERVER_IP="${NETWORK}.100"
HOST_IP="127.0.0.1"  # Fallback pentru localhost demo

# Plan porturi WEEK 2
# WEEK_PORT_BASE = 5100 + 100*(WEEK-1) = 5200
WEEK_PORT_BASE=$((5100 + 100 * (WEEK - 1)))
TCP_APP_PORT=9090
UDP_APP_PORT=9091

# Directoare
ARTIFACTS_DIR="$PROJECT_ROOT/artifacts"
LOGS_DIR="$PROJECT_ROOT/logs"
PYTHON_APPS="$PROJECT_ROOT/seminar/python/exercises"

# Fișiere exerciții
EX_TCP="$PYTHON_APPS/ex_2_01_tcp.py"
EX_UDP="$PYTHON_APPS/ex_2_02_udp.py"

# Fișiere output
DEMO_LOG="$ARTIFACTS_DIR/demo.log"
DEMO_PCAP="$ARTIFACTS_DIR/demo.pcap"
VALIDATION_FILE="$ARTIFACTS_DIR/validation.txt"

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# =============================================================================
# FUNCȚII UTILITARE
# =============================================================================
timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

log() {
    local level="$1"
    shift
    local msg="$*"
    echo -e "[$(timestamp)][$level] $msg" | tee -a "$DEMO_LOG"
}

log_info() { log "INFO" "$@"; }
log_ok() { log " OK " "$@"; }
log_err() { log "ERR " "$@"; }
log_warn() { log "WARN" "$@"; }

cleanup_processes() {
    pkill -f "ex_2_01_tcp.py" 2>/dev/null || true
    pkill -f "ex_2_02_udp.py" 2>/dev/null || true
    pkill -f "tcpdump.*port.*909" 2>/dev/null || true
}

check_port_free() {
    local port="$1"
    if ss -tuln 2>/dev/null | grep -q ":${port} "; then
        return 1
    fi
    return 0
}

wait_for_port() {
    local port="$1"
    local max_wait="${2:-10}"
    local waited=0
    while ! ss -tuln 2>/dev/null | grep -q ":${port} "; do
        sleep 0.2
        waited=$((waited + 1))
        if [ $waited -ge $((max_wait * 5)) ]; then
            return 1
        fi
    done
    return 0
}

# =============================================================================
# INIȚIALIZARE
# =============================================================================
init() {
    log_info "════════════════════════════════════════════════════════════════"
    log_info " WEEK $WEEK - Demo Automat: Socket Programming TCP/UDP"
    log_info "════════════════════════════════════════════════════════════════"
    
    # Creare directoare
    mkdir -p "$ARTIFACTS_DIR" "$LOGS_DIR"
    
    # Curățare fișiere anterioare
    : > "$DEMO_LOG"
    rm -f "$DEMO_PCAP" "$VALIDATION_FILE" 2>/dev/null || true
    
    # Curățare procese anterioare
    cleanup_processes
    
    log_info "Artefacte vor fi salvate în: $ARTIFACTS_DIR"
    log_info "Network plan: ${NETWORK}.0/24 | Ports: TCP=$TCP_APP_PORT, UDP=$UDP_APP_PORT"
}

# =============================================================================
# VERIFICĂRI PRE-EXECUȚIE
# =============================================================================
preflight_checks() {
    log_info "─── Verificări pre-execuție ───"
    
    local errors=0
    
    # Python
    if command -v python3 &>/dev/null; then
        log_ok "Python3: $(python3 --version 2>&1)"
    else
        log_err "Python3 nu este instalat"
        errors=$((errors + 1))
    fi
    
    # Exerciții
    if [[ -f "$EX_TCP" ]]; then
        log_ok "Exercițiu TCP: $EX_TCP"
    else
        log_err "Exercițiu TCP lipsă: $EX_TCP"
        errors=$((errors + 1))
    fi
    
    if [[ -f "$EX_UDP" ]]; then
        log_ok "Exercițiu UDP: $EX_UDP"
    else
        log_err "Exercițiu UDP lipsă: $EX_UDP"
        errors=$((errors + 1))
    fi
    
    # tcpdump (opțional dar recomandat)
    if command -v tcpdump &>/dev/null; then
        log_ok "tcpdump disponibil"
    else
        log_warn "tcpdump indisponibil - capturile vor fi sărite"
    fi
    
    # Porturi
    if check_port_free $TCP_APP_PORT; then
        log_ok "Port TCP $TCP_APP_PORT disponibil"
    else
        log_warn "Port TCP $TCP_APP_PORT ocupat - se va încerca eliberarea"
    fi
    
    if check_port_free $UDP_APP_PORT; then
        log_ok "Port UDP $UDP_APP_PORT disponibil"
    else
        log_warn "Port UDP $UDP_APP_PORT ocupat - se va încerca eliberarea"
    fi
    
    if [[ $errors -gt 0 ]]; then
        log_err "Verificări eșuate: $errors erori critice"
        return 1
    fi
    
    log_ok "Toate verificările au trecut"
    return 0
}

# =============================================================================
# DEMO TCP
# =============================================================================
demo_tcp() {
    log_info "─── Demo TCP (Server Concurent) ───"
    
    local tcp_log="$LOGS_DIR/tcp_demo.log"
    local tcp_pcap="$ARTIFACTS_DIR/tcp_demo.pcap"
    
    # Pornire captură (dacă tcpdump disponibil)
    local tcpdump_pid=""
    if command -v tcpdump &>/dev/null; then
        log_info "Pornire captură TCP pe lo:$TCP_APP_PORT"
        tcpdump -i lo -w "$tcp_pcap" "tcp port $TCP_APP_PORT" 2>/dev/null &
        tcpdump_pid=$!
        sleep 0.5
    fi
    
    # Pornire server TCP
    log_info "Pornire server TCP pe 0.0.0.0:$TCP_APP_PORT (threaded)"
    python3 -u "$EX_TCP" server --bind 0.0.0.0 --port $TCP_APP_PORT --mode threaded \
        >> "$tcp_log" 2>&1 &
    local server_pid=$!
    
    # Așteptare server să fie gata
    if wait_for_port $TCP_APP_PORT 5; then
        log_ok "Server TCP activ (PID: $server_pid)"
    else
        log_err "Server TCP nu a pornit în timp util"
        kill $server_pid 2>/dev/null || true
        return 1
    fi
    
    # Trimitere mesaje de test
    log_info "Trimitere mesaje de test (3 clienți secvențiali)"
    
    for i in 1 2 3; do
        local msg="WEEK${WEEK}_TEST_MSG_${i}"
        log_info "  Client $i: $msg"
        python3 "$EX_TCP" client --host $HOST_IP --port $TCP_APP_PORT --message "$msg" \
            >> "$tcp_log" 2>&1 || log_warn "Client $i nu a primit răspuns"
        sleep 0.2
    done
    
    # Test load (5 clienți concurenți)
    log_info "Test încărcare: 5 clienți concurenți"
    python3 "$EX_TCP" load --host $HOST_IP --port $TCP_APP_PORT --clients 5 \
        --message "CONCURRENT_TEST" >> "$tcp_log" 2>&1 || log_warn "Load test parțial eșuat"
    
    # Oprire server
    sleep 0.5
    kill $server_pid 2>/dev/null || true
    wait $server_pid 2>/dev/null || true
    log_ok "Server TCP oprit"
    
    # Oprire captură
    if [[ -n "$tcpdump_pid" ]]; then
        sleep 0.3
        kill $tcpdump_pid 2>/dev/null || true
        wait $tcpdump_pid 2>/dev/null || true
        log_ok "Captură TCP salvată: $tcp_pcap"
    fi
    
    return 0
}

# =============================================================================
# DEMO UDP
# =============================================================================
demo_udp() {
    log_info "─── Demo UDP (Protocol Aplicație Custom) ───"
    
    local udp_log="$LOGS_DIR/udp_demo.log"
    local udp_pcap="$ARTIFACTS_DIR/udp_demo.pcap"
    
    # Pornire captură (dacă tcpdump disponibil)
    local tcpdump_pid=""
    if command -v tcpdump &>/dev/null; then
        log_info "Pornire captură UDP pe lo:$UDP_APP_PORT"
        tcpdump -i lo -w "$udp_pcap" "udp port $UDP_APP_PORT" 2>/dev/null &
        tcpdump_pid=$!
        sleep 0.5
    fi
    
    # Pornire server UDP
    log_info "Pornire server UDP pe 0.0.0.0:$UDP_APP_PORT"
    python3 -u "$EX_UDP" server --bind 0.0.0.0 --port $UDP_APP_PORT \
        >> "$udp_log" 2>&1 &
    local server_pid=$!
    
    sleep 0.5
    log_ok "Server UDP activ (PID: $server_pid)"
    
    # Testare comenzi protocol
    log_info "Testare comenzi protocol UDP"
    
    local cmds=("ping" "time" "upper:hello_week${WEEK}" "reverse:network" "help")
    for cmd in "${cmds[@]}"; do
        log_info "  Comandă: $cmd"
        python3 "$EX_UDP" client --host $HOST_IP --port $UDP_APP_PORT --once "$cmd" \
            >> "$udp_log" 2>&1 || log_warn "Comandă '$cmd' fără răspuns"
        sleep 0.1
    done
    
    # Oprire server
    sleep 0.3
    kill $server_pid 2>/dev/null || true
    wait $server_pid 2>/dev/null || true
    log_ok "Server UDP oprit"
    
    # Oprire captură
    if [[ -n "$tcpdump_pid" ]]; then
        sleep 0.3
        kill $tcpdump_pid 2>/dev/null || true
        wait $tcpdump_pid 2>/dev/null || true
        log_ok "Captură UDP salvată: $udp_pcap"
    fi
    
    return 0
}

# =============================================================================
# COMBINARE CAPTURI
# =============================================================================
merge_captures() {
    log_info "─── Combinare capturi ───"
    
    local tcp_pcap="$ARTIFACTS_DIR/tcp_demo.pcap"
    local udp_pcap="$ARTIFACTS_DIR/udp_demo.pcap"
    
    if command -v mergecap &>/dev/null; then
        if [[ -f "$tcp_pcap" && -f "$udp_pcap" ]]; then
            mergecap -w "$DEMO_PCAP" "$tcp_pcap" "$udp_pcap" 2>/dev/null
            log_ok "Capturi combinate în: $DEMO_PCAP"
        elif [[ -f "$tcp_pcap" ]]; then
            cp "$tcp_pcap" "$DEMO_PCAP"
            log_ok "Doar captură TCP disponibilă: $DEMO_PCAP"
        elif [[ -f "$udp_pcap" ]]; then
            cp "$udp_pcap" "$DEMO_PCAP"
            log_ok "Doar captură UDP disponibilă: $DEMO_PCAP"
        else
            log_warn "Nicio captură disponibilă"
        fi
    else
        # Fallback: copiază TCP dacă există
        if [[ -f "$tcp_pcap" ]]; then
            cp "$tcp_pcap" "$DEMO_PCAP"
            log_ok "mergecap indisponibil, copiat TCP: $DEMO_PCAP"
        elif [[ -f "$udp_pcap" ]]; then
            cp "$udp_pcap" "$DEMO_PCAP"
            log_ok "mergecap indisponibil, copiat UDP: $DEMO_PCAP"
        else
            # Creare pcap gol pentru validare
            touch "$DEMO_PCAP"
            log_warn "Nicio captură - fișier gol creat"
        fi
    fi
}

# =============================================================================
# VALIDARE
# =============================================================================
validate() {
    log_info "─── Validare artefacte ───"
    
    {
        echo "═══════════════════════════════════════════════════════════════"
        echo " WEEK $WEEK - Socket Programming: Validare Demo"
        echo " Generat: $(timestamp)"
        echo "═══════════════════════════════════════════════════════════════"
        echo ""
        
        # Verificare fișiere
        echo "─── Verificare fișiere artefacte ───"
        local all_ok=true
        
        if [[ -f "$DEMO_LOG" && -s "$DEMO_LOG" ]]; then
            local lines=$(wc -l < "$DEMO_LOG")
            echo "[OK] demo.log prezent ($lines linii)"
        else
            echo "[FAIL] demo.log lipsă sau gol"
            all_ok=false
        fi
        
        if [[ -f "$DEMO_PCAP" ]]; then
            local size=$(stat -f%z "$DEMO_PCAP" 2>/dev/null || stat -c%s "$DEMO_PCAP" 2>/dev/null || echo "0")
            if [[ "$size" -gt 0 ]]; then
                echo "[OK] demo.pcap prezent ($size bytes)"
            else
                echo "[WARN] demo.pcap gol (tcpdump indisponibil?)"
            fi
        else
            echo "[FAIL] demo.pcap lipsă"
            all_ok=false
        fi
        
        echo ""
        
        # Verificare log-uri TCP/UDP
        echo "─── Verificare execuție demo ───"
        
        local tcp_log="$LOGS_DIR/tcp_demo.log"
        local udp_log="$LOGS_DIR/udp_demo.log"
        
        if [[ -f "$tcp_log" ]]; then
            if grep -q "OK:" "$tcp_log" 2>/dev/null; then
                local ok_count=$(grep -c "OK:" "$tcp_log" 2>/dev/null || echo "0")
                echo "[OK] Server TCP: $ok_count răspunsuri OK"
            else
                echo "[WARN] Server TCP: niciun răspuns OK găsit"
            fi
        else
            echo "[FAIL] Log TCP lipsă"
            all_ok=false
        fi
        
        if [[ -f "$udp_log" ]]; then
            if grep -qi "PONG\|time\|upper" "$udp_log" 2>/dev/null; then
                echo "[OK] Server UDP: răspunsuri protocol validate"
            else
                echo "[WARN] Server UDP: răspunsuri incomplete"
            fi
        else
            echo "[FAIL] Log UDP lipsă"
            all_ok=false
        fi
        
        echo ""
        
        # Analiză pcap (dacă tshark disponibil)
        echo "─── Analiză trafic (dacă tshark disponibil) ───"
        if command -v tshark &>/dev/null && [[ -f "$DEMO_PCAP" && -s "$DEMO_PCAP" ]]; then
            local tcp_pkts=$(tshark -r "$DEMO_PCAP" -Y "tcp" 2>/dev/null | wc -l || echo "0")
            local udp_pkts=$(tshark -r "$DEMO_PCAP" -Y "udp" 2>/dev/null | wc -l || echo "0")
            echo "[INFO] Pachete TCP: $tcp_pkts"
            echo "[INFO] Pachete UDP: $udp_pkts"
            
            # Verificare handshake TCP (SYN packets)
            local syn_pkts=$(tshark -r "$DEMO_PCAP" -Y "tcp.flags.syn==1" 2>/dev/null | wc -l || echo "0")
            if [[ "$syn_pkts" -gt 0 ]]; then
                echo "[OK] Handshake TCP detectat ($syn_pkts SYN flags)"
            fi
        else
            echo "[SKIP] tshark indisponibil sau pcap gol"
        fi
        
        echo ""
        echo "═══════════════════════════════════════════════════════════════"
        if $all_ok; then
            echo " REZULTAT: VALIDARE REUȘITĂ"
        else
            echo " REZULTAT: VALIDARE PARȚIALĂ (verificați warnings)"
        fi
        echo "═══════════════════════════════════════════════════════════════"
        
    } > "$VALIDATION_FILE"
    
    log_ok "Validare completă: $VALIDATION_FILE"
    cat "$VALIDATION_FILE"
}

# =============================================================================
# MAIN
# =============================================================================
main() {
    init
    
    if ! preflight_checks; then
        log_err "Verificări pre-execuție eșuate. Abandonare."
        exit 1
    fi
    
    # Execuție demo-uri
    demo_tcp || log_warn "Demo TCP cu avertismente"
    demo_udp || log_warn "Demo UDP cu avertismente"
    
    # Combinare capturi
    merge_captures
    
    # Validare
    validate
    
    # Curățare finală
    cleanup_processes
    
    log_info "════════════════════════════════════════════════════════════════"
    log_info " Demo WEEK $WEEK complet"
    log_info " Artefacte: $ARTIFACTS_DIR"
    log_info "════════════════════════════════════════════════════════════════"
}

# Trap pentru curățare la exit
trap cleanup_processes EXIT

main "$@"
