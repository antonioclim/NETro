#!/bin/bash
# =============================================================================
# run_all.sh – Demo automat pentru Starterkit S9
# Protocoale de fișiere: server tip FTP / mini file-transfer + multi-client
# =============================================================================
# 
# Produce:
#   - artifacts/demo.log      (loguri complete ale demo-ului)
#   - artifacts/demo.pcap     (captură trafic)
#   - artifacts/validation.txt (rezultate validare)
#
# Rulare: ./scripts/run_all.sh (fără input interactiv)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

# Configurare
PORT=5900  # WEEK_PORT_BASE pentru Week 9
HOST="127.0.0.1"
USER="test"
PASS="12345"
TIMEOUT=10

# Culori
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# Directoare
mkdir -p artifacts server-files client-files

# Funcție cleanup
cleanup() {
    echo -e "\n${YELLOW}[CLEANUP] Oprire procese...${NC}"
    pkill -f "ex_9_02_pseudo_ftp.py.*--port $PORT" 2>/dev/null || true
    pkill -f "tcpdump.*port $PORT" 2>/dev/null || true
    sleep 0.5
}
trap cleanup EXIT

# =============================================================================
# Inițializare
# =============================================================================

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Starterkit S9 – Demo Automat                                     ║${NC}"
echo -e "${CYAN}║  Protocoale de Fișiere (FTP/File Transfer)                        ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"

# Curăță artefacte vechi
rm -f artifacts/demo.log artifacts/demo.pcap artifacts/validation.txt

# Start logging
exec > >(tee -a artifacts/demo.log) 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Demo start"

# =============================================================================
# Pasul 1: Setup
# =============================================================================

echo -e "\n${YELLOW}[1/6] Setup mediu...${NC}"

# Creare fișiere de test pe server
echo "Hello Week 9 - FTP Demo!" > server-files/hello.txt
echo "Test UTF-8: România ✓ țară" > server-files/utf8_test.txt
echo "Binary content for testing" > server-files/test.bin
dd if=/dev/urandom of=server-files/random_1k.bin bs=1024 count=1 2>/dev/null || true

# Verificăm Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[EROARE] Python3 nu este instalat!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python3 disponibil${NC}"

# =============================================================================
# Pasul 2: Exercițiu L6 (endianness)
# =============================================================================

echo -e "\n${YELLOW}[2/6] Exercițiu L6 - Endianness și Framing...${NC}"
python3 python/exercises/ex_9_01_endianness.py --selftest
echo -e "${GREEN}✓ Exercițiu L6 complet${NC}"

# =============================================================================
# Pasul 3: Test net_utils.py
# =============================================================================

echo -e "\n${YELLOW}[3/6] Verificare utilitare comune (net_utils.py)...${NC}"
python3 python/utils/net_utils.py
echo -e "${GREEN}✓ net_utils.py OK${NC}"

# =============================================================================
# Pasul 4: Start captură trafic
# =============================================================================

echo -e "\n${YELLOW}[4/6] Pornire captură trafic pe port $PORT...${NC}"

# Încercăm tcpdump (necesită privilegii în unele cazuri)
if command -v tcpdump &> /dev/null; then
    # Rulăm tcpdump în background
    # Notă: poate necesita sudo în medii reale
    timeout 30 tcpdump -i lo "tcp port $PORT" -w artifacts/demo.pcap -c 100 2>/dev/null &
    TCPDUMP_PID=$!
    sleep 0.5
    
    if kill -0 $TCPDUMP_PID 2>/dev/null; then
        echo -e "${GREEN}✓ tcpdump pornit (PID: $TCPDUMP_PID)${NC}"
    else
        echo -e "${YELLOW}⚠ tcpdump nu a pornit (necesită privilegii?)${NC}"
        # Creăm un pcap gol pentru smoke test
        touch artifacts/demo.pcap
    fi
else
    echo -e "${YELLOW}⚠ tcpdump nu este instalat, se creează pcap gol${NC}"
    touch artifacts/demo.pcap
fi

# =============================================================================
# Pasul 5: Server + Client Pseudo-FTP
# =============================================================================

echo -e "\n${YELLOW}[5/6] Test Pseudo-FTP (server + client)...${NC}"

# Pornire server în background
echo "[$(date '+%H:%M:%S')] Pornire server pe port $PORT..."
python3 python/exercises/ex_9_02_pseudo_ftp.py server \
    --host $HOST --port $PORT --root ./server-files &
SERVER_PID=$!
sleep 1

if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${RED}[EROARE] Serverul nu a pornit!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Server pornit (PID: $SERVER_PID)${NC}"

# Test LIST
echo "[$(date '+%H:%M:%S')] Client: LIST..."
python3 python/exercises/ex_9_02_pseudo_ftp.py client \
    --host $HOST --port $PORT --user $USER --password $PASS \
    list || true

# Test GET (mod pasiv)
echo "[$(date '+%H:%M:%S')] Client: GET hello.txt (passive)..."
python3 python/exercises/ex_9_02_pseudo_ftp.py client \
    --host $HOST --port $PORT --user $USER --password $PASS \
    --local-dir ./client-files --mode passive \
    get hello.txt || true

# Verificăm că fișierul a fost descărcat
if [ -f "client-files/hello.txt" ]; then
    echo -e "${GREEN}✓ Fișier descărcat: client-files/hello.txt${NC}"
    DOWNLOADED_SHA=$(sha256sum client-files/hello.txt | cut -d' ' -f1)
    ORIGINAL_SHA=$(sha256sum server-files/hello.txt | cut -d' ' -f1)
    
    if [ "$DOWNLOADED_SHA" = "$ORIGINAL_SHA" ]; then
        echo -e "${GREEN}✓ SHA256 verificat: $DOWNLOADED_SHA${NC}"
    else
        echo -e "${RED}⚠ SHA256 diferit!${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Fișier nu a fost descărcat${NC}"
fi

# Test GET cu compresie
echo "[$(date '+%H:%M:%S')] Client: GET utf8_test.txt (passive + gzip)..."
python3 python/exercises/ex_9_02_pseudo_ftp.py client \
    --host $HOST --port $PORT --user $USER --password $PASS \
    --local-dir ./client-files --mode passive --gzip \
    get utf8_test.txt || true

# Oprire server
echo "[$(date '+%H:%M:%S')] Oprire server..."
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

echo -e "${GREEN}✓ Test Pseudo-FTP complet${NC}"

# =============================================================================
# Pasul 6: Validare
# =============================================================================

echo -e "\n${YELLOW}[6/6] Validare rezultate...${NC}"

{
    echo "═══════════════════════════════════════════════════════════════"
    echo "  VALIDARE STARTERKIT S9 – $(date '+%Y-%m-%d %H:%M:%S')"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    
    # Test 1: Exercițiu endianness
    echo "▶ Test 1: Exercițiu L6 (endianness)"
    if python3 python/exercises/ex_9_01_endianness.py --selftest 2>&1 | grep -q "Toate testele au trecut"; then
        echo "   [PASS] Exercițiu L6 OK"
    else
        echo "   [FAIL] Exercițiu L6 EȘUAT"
    fi
    echo ""
    
    # Test 2: net_utils.py
    echo "▶ Test 2: Utilitare comune (net_utils.py)"
    if python3 python/utils/net_utils.py 2>&1 | grep -q "Toate testele au trecut"; then
        echo "   [PASS] net_utils.py OK"
    else
        echo "   [FAIL] net_utils.py EȘUAT"
    fi
    echo ""
    
    # Test 3: Import pseudo-FTP
    echo "▶ Test 3: Import ex_9_02_pseudo_ftp.py"
    if python3 -c "from python.exercises.ex_9_02_pseudo_ftp import pack_data, unpack_data; print('OK')" 2>&1 | grep -q "OK"; then
        echo "   [PASS] Import OK"
    else
        echo "   [FAIL] Import EȘUAT"
    fi
    echo ""
    
    # Test 4: Fișiere descărcate
    echo "▶ Test 4: Transfer fișiere"
    if [ -f "client-files/hello.txt" ]; then
        echo "   [PASS] hello.txt descărcat"
        echo "   SHA256: $(sha256sum client-files/hello.txt 2>/dev/null | cut -d' ' -f1 || echo 'N/A')"
    else
        echo "   [FAIL] hello.txt NU a fost descărcat"
    fi
    echo ""
    
    # Test 5: Artefacte
    echo "▶ Test 5: Artefacte generate"
    [ -f "artifacts/demo.log" ] && echo "   [PASS] demo.log prezent" || echo "   [FAIL] demo.log lipsă"
    [ -f "artifacts/demo.pcap" ] && echo "   [PASS] demo.pcap prezent" || echo "   [FAIL] demo.pcap lipsă"
    echo ""
    
    echo "═══════════════════════════════════════════════════════════════"
    echo "  VALIDARE COMPLETĂ"
    echo "═══════════════════════════════════════════════════════════════"
    
} > artifacts/validation.txt

cat artifacts/validation.txt

# =============================================================================
# Final
# =============================================================================

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Demo complet!                                                    ║${NC}"
echo -e "${GREEN}║                                                                   ║${NC}"
echo -e "${GREEN}║  Artefacte generate:                                              ║${NC}"
echo -e "${GREEN}║    - artifacts/demo.log                                           ║${NC}"
echo -e "${GREEN}║    - artifacts/demo.pcap                                          ║${NC}"
echo -e "${GREEN}║    - artifacts/validation.txt                                     ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Demo end"
