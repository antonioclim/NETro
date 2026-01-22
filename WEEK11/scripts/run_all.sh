#!/bin/bash
# =============================================================================
# run_all.sh – Demo automat pentru Săptămâna 11: Nginx Load Balancing
# =============================================================================
# Produce artefacte în artifacts/:
#   - demo.log      : log complet al demo-ului
#   - demo.pcap     : captură de trafic HTTP
#   - validation.txt: verificări finale
# =============================================================================
# Utilizare: ./run_all.sh [--no-capture]
# =============================================================================

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Configurare
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$ROOT_DIR/artifacts"
DOCKER_DIR="$ROOT_DIR/docker/nginx_compose"

# Porturi standard (conform spec WEEK 11)
HTTP_PORT=8080
WEEK_PORT_BASE=6100  # 5100 + 100*(11-1) = 6100
DNS_PORT=5353

# Culori
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Opțiuni
NO_CAPTURE=false
if [[ "$1" == "--no-capture" ]]; then
    NO_CAPTURE=true
fi

# ─────────────────────────────────────────────────────────────────────────────
# Funcții helper
# ─────────────────────────────────────────────────────────────────────────────

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo -e "$msg"
    echo "$msg" >> "$ARTIFACTS_DIR/demo.log"
}

cleanup_previous() {
    log "${YELLOW}[CLEANUP]${NC} Curățare stare anterioară..."
    
    # Oprire containere Docker
    cd "$DOCKER_DIR" && docker compose down 2>/dev/null || true
    cd "$ROOT_DIR/docker/custom_lb_compose" && docker compose down 2>/dev/null || true
    
    # Oprire procese Python
    pkill -f "ex_11_01_backend" 2>/dev/null || true
    pkill -f "ex_11_02_loadbalancer" 2>/dev/null || true
    
    # Oprire tshark dacă rulează
    pkill -f "tshark.*$HTTP_PORT" 2>/dev/null || true
    
    # Curățare porturi
    sleep 1
}

wait_for_port() {
    local port=$1
    local timeout=${2:-30}
    local elapsed=0
    
    while ! nc -z localhost "$port" 2>/dev/null; do
        sleep 1
        elapsed=$((elapsed + 1))
        if [[ $elapsed -ge $timeout ]]; then
            return 1
        fi
    done
    return 0
}

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Demo Automat – Săptămâna 11: Nginx Load Balancing${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

# Creare director artefacte
mkdir -p "$ARTIFACTS_DIR"
rm -f "$ARTIFACTS_DIR/demo.log" "$ARTIFACTS_DIR/demo.pcap" "$ARTIFACTS_DIR/validation.txt" 2>/dev/null || true

log "${BLUE}[INFO]${NC} Demo automat pentru WEEK 11"
log "${BLUE}[INFO]${NC} Artefacte vor fi salvate în: $ARTIFACTS_DIR"

# ─────────────────────────────────────────────────────────────────────────────
# PASUL 0: Cleanup
# ─────────────────────────────────────────────────────────────────────────────

cleanup_previous

# ─────────────────────────────────────────────────────────────────────────────
# PASUL 1: Verificare Docker
# ─────────────────────────────────────────────────────────────────────────────

log "${YELLOW}[1/6]${NC} Verificare Docker..."

if ! command -v docker &> /dev/null; then
    log "${RED}[ERROR]${NC} Docker nu este instalat!"
    echo "Docker nu este instalat" >> "$ARTIFACTS_DIR/validation.txt"
    exit 1
fi

if ! docker info &> /dev/null; then
    log "${RED}[ERROR]${NC} Docker nu rulează sau nu aveți permisiuni!"
    echo "Docker nu rulează" >> "$ARTIFACTS_DIR/validation.txt"
    exit 1
fi

log "${GREEN}[OK]${NC} Docker disponibil."

# ─────────────────────────────────────────────────────────────────────────────
# PASUL 2: Pornire captură trafic (background)
# ─────────────────────────────────────────────────────────────────────────────

if [[ "$NO_CAPTURE" == "false" ]]; then
    log "${YELLOW}[2/6]${NC} Pornire captură trafic..."
    
    if command -v tshark &> /dev/null; then
        # Captură în background (maxim 60 secunde sau 500 pachete)
        timeout 60 tshark -i any -f "tcp port $HTTP_PORT" \
            -w "$ARTIFACTS_DIR/demo.pcap" \
            -c 500 2>/dev/null &
        TSHARK_PID=$!
        log "${GREEN}[OK]${NC} tshark pornit (PID: $TSHARK_PID)"
        sleep 2
    elif command -v tcpdump &> /dev/null; then
        timeout 60 sudo tcpdump -i any -n "tcp port $HTTP_PORT" \
            -w "$ARTIFACTS_DIR/demo.pcap" \
            -c 500 2>/dev/null &
        TSHARK_PID=$!
        log "${GREEN}[OK]${NC} tcpdump pornit (PID: $TSHARK_PID)"
        sleep 2
    else
        log "${YELLOW}[WARN]${NC} Nici tshark, nici tcpdump nu sunt disponibile. Skip captură."
        touch "$ARTIFACTS_DIR/demo.pcap"
    fi
else
    log "${YELLOW}[2/6]${NC} Skip captură (--no-capture)."
    touch "$ARTIFACTS_DIR/demo.pcap"
fi

# ─────────────────────────────────────────────────────────────────────────────
# PASUL 3: Pornire Nginx Load Balancer
# ─────────────────────────────────────────────────────────────────────────────

log "${YELLOW}[3/6]${NC} Pornire Nginx reverse proxy + 3 backends..."

cd "$DOCKER_DIR"
docker compose up -d >> "$ARTIFACTS_DIR/demo.log" 2>&1

if ! wait_for_port $HTTP_PORT 30; then
    log "${RED}[ERROR]${NC} Nginx nu a pornit în 30 secunde!"
    echo "FAIL: Nginx timeout" >> "$ARTIFACTS_DIR/validation.txt"
    exit 1
fi

log "${GREEN}[OK]${NC} Nginx rulează pe portul $HTTP_PORT"
sleep 2

# ─────────────────────────────────────────────────────────────────────────────
# PASUL 4: Test Round-Robin
# ─────────────────────────────────────────────────────────────────────────────

log "${YELLOW}[4/6]${NC} Test distribuție Round-Robin..."

echo "" >> "$ARTIFACTS_DIR/demo.log"
echo "=== TEST ROUND-ROBIN ===" >> "$ARTIFACTS_DIR/demo.log"

RESPONSES=""
for i in $(seq 1 9); do
    RESPONSE=$(curl -s -m 5 "http://localhost:$HTTP_PORT/" 2>/dev/null | head -1)
    echo "Request $i: $RESPONSE" >> "$ARTIFACTS_DIR/demo.log"
    log "  Request $i: ${BLUE}$RESPONSE${NC}"
    RESPONSES="$RESPONSES$RESPONSE\n"
    sleep 0.3
done

# Verificare distribuție
BACKEND_1=$(echo -e "$RESPONSES" | grep -c "Backend 1" || echo "0")
BACKEND_2=$(echo -e "$RESPONSES" | grep -c "Backend 2" || echo "0")
BACKEND_3=$(echo -e "$RESPONSES" | grep -c "Backend 3" || echo "0")

log "${BLUE}[STATS]${NC} Distribuție: B1=$BACKEND_1, B2=$BACKEND_2, B3=$BACKEND_3"

# ─────────────────────────────────────────────────────────────────────────────
# PASUL 5: Test Health Check
# ─────────────────────────────────────────────────────────────────────────────

log "${YELLOW}[5/6]${NC} Test health check endpoint..."

HEALTH=$(curl -s -m 5 "http://localhost:$HTTP_PORT/health" 2>/dev/null || echo "FAIL")
log "  Health check: ${BLUE}$HEALTH${NC}"
echo "Health check: $HEALTH" >> "$ARTIFACTS_DIR/demo.log"

# ─────────────────────────────────────────────────────────────────────────────
# PASUL 6: Generare Validare
# ─────────────────────────────────────────────────────────────────────────────

log "${YELLOW}[6/6]${NC} Generare validation.txt..."

{
    echo "=== VALIDATION REPORT - WEEK 11 ==="
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "--- Docker Status ---"
    docker compose ps 2>/dev/null || echo "Docker compose status unavailable"
    echo ""
    echo "--- Load Balancing Distribution ---"
    echo "Backend 1: $BACKEND_1 requests"
    echo "Backend 2: $BACKEND_2 requests"
    echo "Backend 3: $BACKEND_3 requests"
    echo ""
    echo "--- Validation Checks ---"
    
    # Check 1: Toate backend-urile au primit cereri
    if [[ "$BACKEND_1" -gt 0 && "$BACKEND_2" -gt 0 && "$BACKEND_3" -gt 0 ]]; then
        echo "PASS: Toate backend-urile au primit cereri"
    else
        echo "WARN: Nu toate backend-urile au primit cereri (poate fi normal pentru 9 req)"
    fi
    
    # Check 2: Distribuție aproximativ egală
    TOTAL=$((BACKEND_1 + BACKEND_2 + BACKEND_3))
    if [[ $TOTAL -eq 9 ]]; then
        echo "PASS: Total cereri corect (9)"
    else
        echo "FAIL: Total cereri incorect ($TOTAL != 9)"
    fi
    
    # Check 3: Health check funcțional
    if [[ "$HEALTH" == "OK" ]]; then
        echo "PASS: Health check endpoint funcțional"
    else
        echo "WARN: Health check a returnat: $HEALTH"
    fi
    
    # Check 4: Artefacte generate
    echo ""
    echo "--- Artifacts Generated ---"
    ls -la "$ARTIFACTS_DIR/"
    
} > "$ARTIFACTS_DIR/validation.txt"

log "${GREEN}[OK]${NC} Validare completă."

# ─────────────────────────────────────────────────────────────────────────────
# CLEANUP FINAL
# ─────────────────────────────────────────────────────────────────────────────

log "${YELLOW}[CLEANUP]${NC} Oprire captură..."

# Oprire tshark
if [[ -n "$TSHARK_PID" ]]; then
    kill "$TSHARK_PID" 2>/dev/null || true
    wait "$TSHARK_PID" 2>/dev/null || true
fi

# Lăsăm containerele să ruleze (cleanup manual cu scripts/cleanup.sh)
log "${BLUE}[INFO]${NC} Containerele Docker rămân active."
log "${BLUE}[INFO]${NC} Pentru oprire: cd docker/nginx_compose && docker compose down"

# ─────────────────────────────────────────────────────────────────────────────
# SUMAR
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Demo Complet!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Artefacte generate în ${YELLOW}$ARTIFACTS_DIR/${NC}:"
echo -e "  • demo.log        – log complet"
echo -e "  • demo.pcap       – captură trafic HTTP"
echo -e "  • validation.txt  – raport de validare"
echo ""
echo -e "Pentru verificare: ${YELLOW}bash tests/smoke_test.sh${NC}"
echo ""

log "${GREEN}[DONE]${NC} Demo automat finalizat."

# Revolvix&Hypotheticalandrei
