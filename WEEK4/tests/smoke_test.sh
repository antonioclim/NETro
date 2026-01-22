#!/bin/bash
# ==============================================================================
# smoke_test.sh - Verificare rapidă funcționalitate Starterkit S4
# ==============================================================================
# Verifică:
#   1. Mediul Python (versiune, module)
#   2. Sintaxa fișierelor Python
#   3. Funcționalitatea protocoalelor (CRC32, pack/unpack)
#   4. Existența artifacts (demo.log, demo.pcap, validation.txt)
#
# Utilizare:
#   ./tests/smoke_test.sh           # verificare completă
#   ./tests/smoke_test.sh --quick   # doar verificări de bază
#
# Porturi standard WEEK 4: 5400, 5401, 5402
#
# Licență: MIT - Material didactic ASE-CSIE
# ==============================================================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

# Porturi standard WEEK 4
PORT_TEXT=5400
PORT_BIN=5401
PORT_UDP=5402

PASSED=0
FAILED=0
WARNINGS=0

QUICK_MODE=false
if [ "$1" = "--quick" ] || [ "$1" = "-q" ]; then
    QUICK_MODE=true
fi

test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "  ${GREEN}✓ $2${NC}"
        ((PASSED++))
    else
        echo -e "  ${RED}✗ $2${NC}"
        ((FAILED++))
    fi
}

test_warning() {
    echo -e "  ${YELLOW}⚠ $1${NC}"
    ((WARNINGS++))
}

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     SMOKE TEST - STARTERKIT SĂPTĂMÂNA 4 (WEEK 4)             ║${NC}"
echo -e "${CYAN}║     Porturi: TEXT=$PORT_TEXT, BINARY=$PORT_BIN, UDP=$PORT_UDP                    ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ==============================================================================
# Test 1: Python disponibil
# ==============================================================================
echo -e "${YELLOW}1. Verificare Python:${NC}"
python3 --version > /dev/null 2>&1
test_result $? "Python 3 disponibil"

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "     Versiune: Python $PYTHON_VERSION"

# ==============================================================================
# Test 2: Module importabile
# ==============================================================================
echo -e "\n${YELLOW}2. Verificare module Python:${NC}"
python3 -c "import socket, struct, zlib, threading, argparse" > /dev/null 2>&1
test_result $? "Module stdlib disponibile (socket, struct, zlib, threading)"

python3 -c "import sys; sys.path.insert(0, 'python/utils'); from proto_common import crc32, BIN_HEADER_LEN" > /dev/null 2>&1
test_result $? "proto_common.py importabil"

python3 -c "import sys; sys.path.insert(0, 'python/utils'); from io_utils import recv_exact, recv_until" > /dev/null 2>&1
test_result $? "io_utils.py importabil"

# ==============================================================================
# Test 3: Sintaxă Python validă
# ==============================================================================
echo -e "\n${YELLOW}3. Verificare sintaxă Python:${NC}"

python3 -m py_compile python/apps/text_proto_server.py > /dev/null 2>&1
test_result $? "text_proto_server.py sintaxă validă"

python3 -m py_compile python/apps/text_proto_client.py > /dev/null 2>&1
test_result $? "text_proto_client.py sintaxă validă"

python3 -m py_compile python/apps/binary_proto_server.py > /dev/null 2>&1
test_result $? "binary_proto_server.py sintaxă validă"

python3 -m py_compile python/apps/binary_proto_client.py > /dev/null 2>&1
test_result $? "binary_proto_client.py sintaxă validă"

python3 -m py_compile python/apps/udp_sensor_server.py > /dev/null 2>&1
test_result $? "udp_sensor_server.py sintaxă validă"

python3 -m py_compile python/apps/udp_sensor_client.py > /dev/null 2>&1
test_result $? "udp_sensor_client.py sintaxă validă"

# ==============================================================================
# Test 4: CRC32 funcționează corect
# ==============================================================================
echo -e "\n${YELLOW}4. Verificare CRC32:${NC}"
RESULT=$(python3 -c "
import sys
sys.path.insert(0, 'python/utils')
from proto_common import crc32
# Test known value: CRC32('Hello World') = 0x4A17B156
data = b'Hello World'
expected = 0x4A17B156
actual = crc32(data)
print('PASS' if actual == expected else f'FAIL: {actual:08x} != {expected:08x}')
")
[ "$RESULT" = "PASS" ]
test_result $? "CRC32 calculat corect (0x4A17B156)"

# ==============================================================================
# Test 5: Pack/unpack UDP sensor
# ==============================================================================
echo -e "\n${YELLOW}5. Verificare protocol UDP senzor:${NC}"
RESULT=$(python3 -c "
import sys
sys.path.insert(0, 'python/utils')
from proto_common import pack_udp_sensor, unpack_udp_sensor, UDP_LEN
# Round-trip test
packet = pack_udp_sensor(1, 23.5, 'Lab1')
if len(packet) != UDP_LEN:
    print(f'FAIL: packet length {len(packet)} != {UDP_LEN}')
else:
    ver, sid, temp, loc = unpack_udp_sensor(packet)
    if sid == 1 and abs(temp - 23.5) < 0.01 and loc == 'Lab1':
        print('PASS')
    else:
        print(f'FAIL: {sid}, {temp}, {loc}')
")
[ "$RESULT" = "PASS" ]
test_result $? "UDP pack/unpack round-trip (23 bytes)"

# ==============================================================================
# Test 6: Pack/unpack Binary header
# ==============================================================================
echo -e "\n${YELLOW}6. Verificare protocol binar TCP:${NC}"
RESULT=$(python3 -c "
import sys
sys.path.insert(0, 'python/utils')
from proto_common import pack_bin_message, unpack_bin_header, validate_bin_message
from proto_common import TYPE_ECHO_REQ, BIN_HEADER_LEN
# Round-trip test
msg = pack_bin_message(TYPE_ECHO_REQ, b'test_payload', 42)
header = unpack_bin_header(msg[:BIN_HEADER_LEN])
payload = msg[BIN_HEADER_LEN:]
if header.mtype == TYPE_ECHO_REQ and header.seq == 42 and header.payload_len == 12:
    if validate_bin_message(header, payload):
        print('PASS')
    else:
        print('FAIL: CRC validation failed')
else:
    print(f'FAIL: header mismatch')
")
[ "$RESULT" = "PASS" ]
test_result $? "Binary pack/unpack round-trip (header 14B + CRC32)"

# ==============================================================================
# Test 7: Verificare porturi standard
# ==============================================================================
if [ "$QUICK_MODE" = false ]; then
    echo -e "\n${YELLOW}7. Verificare porturi standard WEEK 4:${NC}"
    
    for port in $PORT_TEXT $PORT_BIN $PORT_UDP; do
        if lsof -i :$port > /dev/null 2>&1; then
            test_warning "Port $port ocupat (verificați cu: lsof -i :$port)"
        else
            test_result 0 "Port $port liber"
        fi
    done
fi

# ==============================================================================
# Test 8: Verificare artifacts (dacă există)
# ==============================================================================
echo -e "\n${YELLOW}8. Verificare artifacts (după run_all.sh):${NC}"

if [ -d "artifacts" ]; then
    if [ -f "artifacts/demo.log" ]; then
        LINES=$(wc -l < "artifacts/demo.log" 2>/dev/null || echo "0")
        if [ "$LINES" -gt 10 ]; then
            test_result 0 "demo.log există ($LINES linii)"
        else
            test_warning "demo.log prea scurt ($LINES linii)"
        fi
    else
        test_warning "demo.log lipsește (rulați: ./scripts/run_all.sh)"
    fi
    
    if [ -f "artifacts/demo.pcap" ]; then
        SIZE=$(stat -f%z "artifacts/demo.pcap" 2>/dev/null || stat -c%s "artifacts/demo.pcap" 2>/dev/null || echo "0")
        test_result 0 "demo.pcap există ($SIZE bytes)"
    else
        test_warning "demo.pcap lipsește (tcpdump indisponibil sau demo neexecutat)"
    fi
    
    if [ -f "artifacts/validation.txt" ]; then
        test_result 0 "validation.txt există"
        
        # Verificare conținut validation.txt
        if grep -q "\[OK\]" "artifacts/validation.txt" 2>/dev/null; then
            OK_COUNT=$(grep -c "\[OK\]" "artifacts/validation.txt" 2>/dev/null || echo "0")
            echo "       ($OK_COUNT verificări trecute)"
        fi
        
        if grep -q "\[FAIL\]" "artifacts/validation.txt" 2>/dev/null; then
            FAIL_COUNT=$(grep -c "\[FAIL\]" "artifacts/validation.txt" 2>/dev/null || echo "0")
            test_warning "validation.txt conține $FAIL_COUNT eșecuri"
        fi
    else
        test_warning "validation.txt lipsește (rulați: ./scripts/run_all.sh)"
    fi
else
    test_warning "Director artifacts/ lipsește (rulați: ./scripts/run_all.sh)"
fi

# ==============================================================================
# Test 9: Verificare structură directoare
# ==============================================================================
echo -e "\n${YELLOW}9. Verificare structură directoare:${NC}"

for dir in python/apps python/utils python/templates scripts tests docs; do
    if [ -d "$dir" ]; then
        test_result 0 "$dir/ există"
    else
        test_result 1 "$dir/ lipsește"
    fi
done

# ==============================================================================
# Rezumat
# ==============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "REZULTAT: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}, ${YELLOW}$WARNINGS warnings${NC}"
echo "═══════════════════════════════════════════════════════════════"

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}[FAIL] Unele teste au eșuat. Verificați erorile de mai sus.${NC}"
    exit 1
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}[WARN] Teste trecute cu avertismente. Rulați './scripts/run_all.sh' pentru artifacts.${NC}"
fi

echo -e "${GREEN}[PASS] Toate testele critice au trecut!${NC}"
exit 0
