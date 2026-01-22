#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# smoke_test.sh - Test rapid de funcționalitate (Săptămâna 8)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Verifică:
#   - Precondiții (Python, curl, fișiere kit)
#   - Funcționalitate server HTTP
#   - Funcționalitate reverse proxy
#   - Existența artefactelor (demo.log, demo.pcap, validation.txt)
#
# Autor: Rețele de Calculatoare, ASE București
# Hypotheticalandrei & Rezolvix | MIT License
# ═══════════════════════════════════════════════════════════════════════════════

# Note: NOT using set -e because arithmetic operations can return non-zero

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurație
WEEK=8
HTTP_PORT=18080       # Port unic pentru smoke test
PROXY_PORT=18888
BACKEND_PORT=19001

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Smoke Test - Săptămâna 8: HTTP Server + Reverse Proxy               ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

PASSED=0
FAILED=0
WARNED=0

cleanup() {
    pkill -f "demo_http_server.py.*$HTTP_PORT" 2>/dev/null || true
    pkill -f "demo_http_server.py.*$BACKEND_PORT" 2>/dev/null || true
    pkill -f "demo_reverse_proxy.py.*$PROXY_PORT" 2>/dev/null || true
}
trap cleanup EXIT

# ─────────────────────────────────────────────────────────────────────────────
# Secțiunea 1: Precondiții
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${BLUE}[Precondiții]${NC}"

# Test 1: Python 3
echo -n "  [1] Python 3 disponibil... "
if python3 --version &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

# Test 2: Module Python standard
echo -n "  [2] Module Python necesare... "
if python3 -c "import socket, threading, argparse, os, sys" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

# Test 3: curl disponibil
echo -n "  [3] curl disponibil... "
if command -v curl &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

# Test 4: Fișiere kit prezente
echo -n "  [4] Fișiere kit prezente... "
if [ -f "python/demos/demo_http_server.py" ] && \
   [ -f "python/demos/demo_reverse_proxy.py" ] && \
   [ -f "python/utils/net_utils.py" ] && \
   [ -f "www/index.html" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Secțiunea 2: Server HTTP
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${BLUE}[Server HTTP]${NC}"

# Test 5: Pornire server HTTP
echo -n "  [5] Server HTTP pornește... "
python3 python/demos/demo_http_server.py \
    --host 127.0.0.1 \
    --port $HTTP_PORT \
    --www www \
    --mode threaded &
SERVER_PID=$!
sleep 1

if kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

# Test 6: GET / → 200 OK
echo -n "  [6] GET / → 200 OK... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$HTTP_PORT/ 2>/dev/null || echo "000")
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗ (got $RESPONSE)${NC}"
    FAILED=$((FAILED+1))
fi

# Test 7: GET /not-found → 404
echo -n "  [7] GET /not-found → 404... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$HTTP_PORT/not-found 2>/dev/null || echo "000")
if [ "$RESPONSE" = "404" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗ (got $RESPONSE)${NC}"
    FAILED=$((FAILED+1))
fi

# Test 8: Header X-Backend prezent
echo -n "  [8] Header X-Backend prezent... "
HEADER=$(curl -s -D - http://127.0.0.1:$HTTP_PORT/ -o /dev/null 2>/dev/null | grep -i "X-Backend" || echo "")
if [ -n "$HEADER" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

# Oprire server simplu
kill $SERVER_PID 2>/dev/null || true
sleep 0.5

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Secțiunea 3: Reverse Proxy
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${BLUE}[Reverse Proxy]${NC}"

# Pornire backend
echo -n "  [9] Backend pornește... "
python3 python/demos/demo_http_server.py \
    --host 127.0.0.1 \
    --port $BACKEND_PORT \
    --www www \
    --id "test-backend" \
    --mode threaded &
BACKEND_PID=$!
sleep 0.5

if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

# Pornire proxy
echo -n "  [10] Reverse proxy pornește... "
python3 python/demos/demo_reverse_proxy.py \
    --listen-host 127.0.0.1 \
    --listen-port $PROXY_PORT \
    --backends "127.0.0.1:$BACKEND_PORT" &
PROXY_PID=$!
sleep 0.5

if kill -0 $PROXY_PID 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

# Test proxy forwarding
echo -n "  [11] Proxy forwarding funcționează... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$PROXY_PORT/ 2>/dev/null || echo "000")
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗ (got $RESPONSE)${NC}"
    FAILED=$((FAILED+1))
fi

# Test header X-Served-By
echo -n "  [12] Header X-Served-By prezent... "
SERVED_BY=$(curl -s -D - http://127.0.0.1:$PROXY_PORT/ -o /dev/null 2>/dev/null | grep -i "X-Served-By" || echo "")
if [ -n "$SERVED_BY" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${YELLOW}○${NC} (opțional)"
    WARNED=$((WARNED+1))
fi

# Cleanup proxy test
kill $PROXY_PID 2>/dev/null || true
kill $BACKEND_PID 2>/dev/null || true
sleep 0.3

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Secțiunea 4: Artefacte (după run_all.sh)
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${BLUE}[Artefacte]${NC}"

# Test: demo.log există
echo -n "  [13] artifacts/demo.log există... "
if [ -f "artifacts/demo.log" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${YELLOW}○${NC} (rulează run_all.sh)"
    WARNED=$((WARNED+1))
fi

# Test: validation.txt există
echo -n "  [14] artifacts/validation.txt există... "
if [ -f "artifacts/validation.txt" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${YELLOW}○${NC} (rulează run_all.sh)"
    WARNED=$((WARNED+1))
fi

# Test: demo.pcap există
echo -n "  [15] artifacts/demo.pcap există... "
if [ -f "artifacts/demo.pcap" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${YELLOW}○${NC} (necesită tcpdump)"
    WARNED=$((WARNED+1))
fi

# Cleanup final
cleanup

# ─────────────────────────────────────────────────────────────────────────────
# Sumar
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo -e "Rezultate: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}, ${YELLOW}$WARNED warnings${NC}"
echo "═══════════════════════════════════════════════════════════════════════"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}Toate testele critice au trecut!${NC}"
    exit 0
else
    echo -e "${RED}Unele teste au eșuat.${NC}"
    exit 1
fi
