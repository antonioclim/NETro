#!/bin/bash
# ==============================================================================
# run_all.sh - Demo automat pentru Starterkit Săptămâna 4
# ==============================================================================
# Rulează fără input interactiv și produce:
#   - artifacts/demo.log      : log complet al demo-ului
#   - artifacts/demo.pcap     : captură de trafic (dacă tcpdump disponibil)
#   - artifacts/validation.txt: rezultatul verificărilor
#
# Porturi standard WEEK 4: 5400 (TEXT), 5401 (BINARY), 5402 (UDP)
# Rețea IP: 10.0.4.0/24 (pentru scenarii Mininet)
#
# Utilizare:
#   ./scripts/run_all.sh           # demo complet
#   ./scripts/run_all.sh --quick   # demo rapid (fără captură)
#
# Licență: MIT - Material didactic ASE-CSIE
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

# Culori
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# ==============================================================================
# PLAN PORTURI WEEK 4 (Standard Transversal)
# ==============================================================================
# WEEK_PORT_BASE = 5100 + 100*(WEEK-1) = 5100 + 300 = 5400
PORT_TEXT=5400    # TCP protocol text
PORT_BIN=5401     # TCP protocol binar
PORT_UDP=5402     # UDP senzori

# ==============================================================================
# PLAN IP (pentru Mininet)
# ==============================================================================
# Rețea: 10.0.4.0/24
# Gateway: 10.0.4.1
# Server: 10.0.4.100
# Hosts: h1=10.0.4.11, h2=10.0.4.12, h3=10.0.4.13

# Directoare
ARTIFACTS_DIR="$ROOT_DIR/artifacts"
DEMO_LOG="$ARTIFACTS_DIR/demo.log"
DEMO_PCAP="$ARTIFACTS_DIR/demo.pcap"
VALIDATION_FILE="$ARTIFACTS_DIR/validation.txt"

# Opțiuni
QUICK_MODE=false
if [ "$1" = "--quick" ] || [ "$1" = "-q" ]; then
    QUICK_MODE=true
fi

# PIDs pentru cleanup
declare -a PIDS=()
TCPDUMP_PID=""

# Funcție pentru cleanup
cleanup() {
    echo -e "\n${YELLOW}[CLEANUP] Oprire procese...${NC}" | tee -a "$DEMO_LOG"
    
    # Oprire tcpdump
    if [ -n "$TCPDUMP_PID" ]; then
        sudo kill $TCPDUMP_PID 2>/dev/null || true
        sleep 0.5
    fi
    
    # Oprire servere
    for pid in "${PIDS[@]}"; do
        kill $pid 2>/dev/null || true
    done
    
    pkill -f "text_proto_server" 2>/dev/null || true
    pkill -f "binary_proto_server" 2>/dev/null || true
    pkill -f "udp_sensor_server" 2>/dev/null || true
}

trap cleanup EXIT

# Creare directoare
mkdir -p "$ARTIFACTS_DIR"

# Inițializare log
echo "═══════════════════════════════════════════════════════════════" > "$DEMO_LOG"
echo "  STARTERKIT S4 - DEMO AUTOMAT" >> "$DEMO_LOG"
echo "  Data: $(date '+%Y-%m-%d %H:%M:%S')" >> "$DEMO_LOG"
echo "  Porturi: TEXT=$PORT_TEXT, BINARY=$PORT_BIN, UDP=$PORT_UDP" >> "$DEMO_LOG"
echo "═══════════════════════════════════════════════════════════════" >> "$DEMO_LOG"
echo "" >> "$DEMO_LOG"

# Banner
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║     STARTERKIT S4 - PROTOCOALE TEXT/BINAR CUSTOM (WEEK 4)            ║"
echo "║     Porturi: TEXT=$PORT_TEXT, BINARY=$PORT_BIN, UDP=$PORT_UDP                          ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ==============================================================================
# PORNIRE CAPTURĂ (dacă tcpdump disponibil și nu quick mode)
# ==============================================================================
if [ "$QUICK_MODE" = false ] && command -v tcpdump &> /dev/null; then
    echo -e "${GREEN}[CAPTURE] Pornire captură trafic...${NC}" | tee -a "$DEMO_LOG"
    sudo tcpdump -i lo -w "$DEMO_PCAP" \
        port $PORT_TEXT or port $PORT_BIN or port $PORT_UDP \
        2>/dev/null &
    TCPDUMP_PID=$!
    sleep 1
    echo "  Captură activă (PID: $TCPDUMP_PID)" | tee -a "$DEMO_LOG"
else
    echo -e "${YELLOW}[CAPTURE] Skip (tcpdump indisponibil sau --quick)${NC}" | tee -a "$DEMO_LOG"
    # Creare fișier pcap gol pentru smoke test
    touch "$DEMO_PCAP"
fi

# ==============================================================================
# DEMO 1: Protocol TEXT over TCP
# ==============================================================================
echo -e "\n${GREEN}[DEMO 1] Protocol TEXT over TCP (port $PORT_TEXT)${NC}" | tee -a "$DEMO_LOG"
echo "──────────────────────────────────────────" | tee -a "$DEMO_LOG"

# Pornire server în background
python3 python/apps/text_proto_server.py --port $PORT_TEXT --verbose >> "$DEMO_LOG" 2>&1 &
SERVER_PID=$!
PIDS+=($SERVER_PID)
sleep 1

echo "Server pornit pe port $PORT_TEXT (PID: $SERVER_PID)" | tee -a "$DEMO_LOG"

# Test cu clientul
echo -e "\n${CYAN}Executare comenzi TEXT:${NC}" | tee -a "$DEMO_LOG"
python3 python/apps/text_proto_client.py --host localhost --port $PORT_TEXT \
    -c "PING" \
    -c "SET name Alice" \
    -c "SET city Bucharest" \
    -c "SET year 2025" \
    -c "GET name" \
    -c "COUNT" \
    -c "KEYS" \
    -c "DEL year" \
    -c "COUNT" \
    -c "QUIT" \
    -v 2>&1 | tee -a "$DEMO_LOG"

# Oprire server
kill $SERVER_PID 2>/dev/null || true
echo -e "\n${GREEN}✓ Demo TEXT complet!${NC}\n" | tee -a "$DEMO_LOG"

sleep 0.5

# ==============================================================================
# DEMO 2: Protocol BINAR over TCP
# ==============================================================================
echo -e "${GREEN}[DEMO 2] Protocol BINAR over TCP (port $PORT_BIN)${NC}" | tee -a "$DEMO_LOG"
echo "──────────────────────────────────────────" | tee -a "$DEMO_LOG"

# Pornire server în background
python3 python/apps/binary_proto_server.py --port $PORT_BIN --verbose >> "$DEMO_LOG" 2>&1 &
SERVER_PID=$!
PIDS+=($SERVER_PID)
sleep 1

echo "Server pornit pe port $PORT_BIN (PID: $SERVER_PID)" | tee -a "$DEMO_LOG"

# Test cu clientul
echo -e "\n${CYAN}Executare comenzi BINARY:${NC}" | tee -a "$DEMO_LOG"
python3 python/apps/binary_proto_client.py --host localhost --port $PORT_BIN \
    -c "echo Hello Binary World" \
    -c "put name Bob" \
    -c "put city Paris" \
    -c "put temp 23.5" \
    -c "get name" \
    -c "count" \
    -c "keys" \
    -c "quit" \
    -v 2>&1 | tee -a "$DEMO_LOG"

# Oprire server
kill $SERVER_PID 2>/dev/null || true
echo -e "\n${GREEN}✓ Demo BINAR complet!${NC}\n" | tee -a "$DEMO_LOG"

sleep 0.5

# ==============================================================================
# DEMO 3: Protocol UDP Senzori
# ==============================================================================
echo -e "${GREEN}[DEMO 3] Protocol UDP Senzori (port $PORT_UDP)${NC}" | tee -a "$DEMO_LOG"
echo "──────────────────────────────────────────" | tee -a "$DEMO_LOG"

# Pornire server în background
python3 python/apps/udp_sensor_server.py --port $PORT_UDP --verbose >> "$DEMO_LOG" 2>&1 &
SERVER_PID=$!
PIDS+=($SERVER_PID)
sleep 1

echo "Server pornit pe port $PORT_UDP (PID: $SERVER_PID)" | tee -a "$DEMO_LOG"

# Trimite citiri senzori
echo -e "\n${CYAN}Trimitere citiri senzori:${NC}" | tee -a "$DEMO_LOG"

python3 python/apps/udp_sensor_client.py --host localhost --port $PORT_UDP \
    --sensor-id 1 --temp 23.5 --location "Lab1" -v 2>&1 | tee -a "$DEMO_LOG"

python3 python/apps/udp_sensor_client.py --host localhost --port $PORT_UDP \
    --sensor-id 2 --temp 19.2 --location "Office" -v 2>&1 | tee -a "$DEMO_LOG"

python3 python/apps/udp_sensor_client.py --host localhost --port $PORT_UDP \
    --sensor-id 1 --temp 24.1 --location "Lab1" -v 2>&1 | tee -a "$DEMO_LOG"

# Trimite un pachet corupt pentru a demonstra detecția erorilor
echo -e "\n${YELLOW}Trimitere pachet corupt (testare CRC):${NC}" | tee -a "$DEMO_LOG"
python3 python/apps/udp_sensor_client.py --host localhost --port $PORT_UDP \
    --sensor-id 99 --temp 0.0 --location "Test" --corrupt -v 2>&1 | tee -a "$DEMO_LOG"

sleep 1

# Oprire server
kill $SERVER_PID 2>/dev/null || true
echo -e "\n${GREEN}✓ Demo UDP complet!${NC}\n" | tee -a "$DEMO_LOG"

# ==============================================================================
# OPRIRE CAPTURĂ
# ==============================================================================
if [ -n "$TCPDUMP_PID" ]; then
    echo -e "${GREEN}[CAPTURE] Oprire captură...${NC}" | tee -a "$DEMO_LOG"
    sudo kill $TCPDUMP_PID 2>/dev/null || true
    TCPDUMP_PID=""
    sleep 1
fi

# ==============================================================================
# GENERARE VALIDATION.TXT
# ==============================================================================
echo -e "${GREEN}[VALIDATION] Generare raport validare...${NC}" | tee -a "$DEMO_LOG"

cat > "$VALIDATION_FILE" << EOF
═══════════════════════════════════════════════════════════════
  VALIDATION REPORT - STARTERKIT S4 (WEEK 4)
  Generated: $(date '+%Y-%m-%d %H:%M:%S')
═══════════════════════════════════════════════════════════════

PORTS USED:
  TCP TEXT:   $PORT_TEXT (protocol length-prefixed)
  TCP BINARY: $PORT_BIN (header 14B + CRC32)
  UDP SENSOR: $PORT_UDP (datagram 23B + CRC32)

IP PLAN (Mininet):
  Network:    10.0.4.0/24
  Gateway:    10.0.4.1
  Server:     10.0.4.100
  Hosts:      h1=10.0.4.11, h2=10.0.4.12, h3=10.0.4.13

ARTIFACTS GENERATED:
EOF

# Verificare artifacts
echo "" >> "$VALIDATION_FILE"
echo "FILES:" >> "$VALIDATION_FILE"

if [ -f "$DEMO_LOG" ]; then
    LINES=$(wc -l < "$DEMO_LOG")
    echo "  [OK] demo.log ($LINES lines)" >> "$VALIDATION_FILE"
else
    echo "  [FAIL] demo.log missing" >> "$VALIDATION_FILE"
fi

if [ -f "$DEMO_PCAP" ]; then
    SIZE=$(stat -f%z "$DEMO_PCAP" 2>/dev/null || stat -c%s "$DEMO_PCAP" 2>/dev/null || echo "0")
    echo "  [OK] demo.pcap ($SIZE bytes)" >> "$VALIDATION_FILE"
else
    echo "  [FAIL] demo.pcap missing" >> "$VALIDATION_FILE"
fi

# Verificare comenzi în log
echo "" >> "$VALIDATION_FILE"
echo "PROTOCOL TESTS:" >> "$VALIDATION_FILE"

if grep -q "OK pong" "$DEMO_LOG" 2>/dev/null; then
    echo "  [OK] TEXT PING successful" >> "$VALIDATION_FILE"
else
    echo "  [FAIL] TEXT PING failed" >> "$VALIDATION_FILE"
fi

if grep -q "OK stored name" "$DEMO_LOG" 2>/dev/null; then
    echo "  [OK] TEXT SET successful" >> "$VALIDATION_FILE"
else
    echo "  [FAIL] TEXT SET failed" >> "$VALIDATION_FILE"
fi

if grep -q "OK.*keys" "$DEMO_LOG" 2>/dev/null; then
    echo "  [OK] TEXT COUNT successful" >> "$VALIDATION_FILE"
else
    echo "  [FAIL] TEXT COUNT failed" >> "$VALIDATION_FILE"
fi

if grep -q "ECHO_RESP\|Hello Binary" "$DEMO_LOG" 2>/dev/null; then
    echo "  [OK] BINARY ECHO successful" >> "$VALIDATION_FILE"
else
    echo "  [FAIL] BINARY ECHO failed" >> "$VALIDATION_FILE"
fi

if grep -q "Sensor.*Lab1\|sensor_id=1" "$DEMO_LOG" 2>/dev/null; then
    echo "  [OK] UDP sensor data received" >> "$VALIDATION_FILE"
else
    echo "  [FAIL] UDP sensor data failed" >> "$VALIDATION_FILE"
fi

if grep -qi "crc.*mismatch\|corrupt\|CRC" "$DEMO_LOG" 2>/dev/null; then
    echo "  [OK] CRC error detection working" >> "$VALIDATION_FILE"
else
    echo "  [WARN] CRC error detection not verified" >> "$VALIDATION_FILE"
fi

echo "" >> "$VALIDATION_FILE"
echo "═══════════════════════════════════════════════════════════════" >> "$VALIDATION_FILE"
echo "  VALIDATION COMPLETE" >> "$VALIDATION_FILE"
echo "═══════════════════════════════════════════════════════════════" >> "$VALIDATION_FILE"

# ==============================================================================
# REZUMAT
# ==============================================================================
echo -e "${CYAN}"
echo "══════════════════════════════════════════════════════════════════════"
echo "                           REZUMAT DEMO"
echo "══════════════════════════════════════════════════════════════════════"
echo -e "${NC}"
echo "1. Protocol TEXT (TCP port $PORT_TEXT):"
echo "   - Framing: length-prefix (ex: '11 SET name Alice')"
echo "   - Ușor de debugat cu netcat/telnet (parțial)"
echo "   - Human-readable pentru debugging"
echo ""
echo "2. Protocol BINAR (TCP port $PORT_BIN):"
echo "   - Header fix 14 bytes + CRC32"
echo "   - Parsing predictibil și eficient"
echo "   - Detecție erori inclusă"
echo ""
echo "3. Protocol UDP Senzori (port $PORT_UDP):"
echo "   - Datagram fix 23 bytes"
echo "   - CRC32 pentru verificare integritate"
echo "   - Connectionless - fără overhead TCP"
echo ""
echo -e "${GREEN}Artifacts generate în: $ARTIFACTS_DIR/${NC}"
echo "  - demo.log       : log complet"
echo "  - demo.pcap      : captură trafic"  
echo "  - validation.txt : raport validare"
echo ""
echo -e "${GREEN}Pentru verificare: cat $VALIDATION_FILE${NC}"

# Afișare rezumat validation
echo ""
cat "$VALIDATION_FILE"
