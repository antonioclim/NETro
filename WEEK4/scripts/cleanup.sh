#!/bin/bash
# ==============================================================================
# cleanup.sh - Cleanup complet pentru Starterkit S4
# ==============================================================================
# Oprește toate serverele și curăță fișierele temporare.
# Sigur de rulat de mai multe ori (idempotent).
#
# Utilizare:
#   ./scripts/cleanup.sh         # cleanup normal
#   ./scripts/cleanup.sh --full  # cleanup + ștergere artifacts
#
# Licență: MIT - Material didactic ASE-CSIE
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

FULL_CLEANUP=false
if [ "$1" = "--full" ] || [ "$1" = "-f" ]; then
    FULL_CLEANUP=true
fi

echo -e "${YELLOW}[CLEANUP] Starterkit Săptămâna 4${NC}"
echo "════════════════════════════════════════════"

# 1. Oprire servere Python
echo -e "\n${YELLOW}[1/5] Oprire servere Python...${NC}"
pkill -f "text_proto_server" 2>/dev/null && echo "  ✓ text_proto_server oprit" || echo "  - text_proto_server nu rula"
pkill -f "binary_proto_server" 2>/dev/null && echo "  ✓ binary_proto_server oprit" || echo "  - binary_proto_server nu rula"
pkill -f "udp_sensor_server" 2>/dev/null && echo "  ✓ udp_sensor_server oprit" || echo "  - udp_sensor_server nu rula"

# 2. Oprire procese pe porturile WEEK4 (5400-5499)
echo -e "\n${YELLOW}[2/5] Eliberare porturi WEEK4 (5400-5402)...${NC}"
for port in 5400 5401 5402; do
    pid=$(lsof -t -i :$port 2>/dev/null || true)
    if [ -n "$pid" ]; then
        kill -9 $pid 2>/dev/null && echo "  ✓ Port $port eliberat (PID: $pid)" || true
    else
        echo "  - Port $port deja liber"
    fi
done

# 3. Cleanup Mininet (dacă există)
echo -e "\n${YELLOW}[3/5] Cleanup Mininet...${NC}"
if command -v mn &> /dev/null; then
    sudo mn -c 2>/dev/null && echo "  ✓ Mininet cleanup completat" || echo "  - mn -c (probabil nu era nevoie)"
else
    echo "  - Mininet nu este instalat (skip)"
fi

# 4. Curățare fișiere temporare
echo -e "\n${YELLOW}[4/5] Curățare fișiere temporare...${NC}"

# Ștergere __pycache__ și .pyc
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "  ✓ Cache Python șters"

# Ștergere loguri din results/ (legacy)
rm -f results/*.log 2>/dev/null && echo "  ✓ Loguri vechi șterse (results/)" || true

# Curățare capturi temporare din pcap/ (păstrează doar cele denumite explicit)
find pcap/ -name "capture_*.pcap" -mmin +60 -delete 2>/dev/null || true
echo "  ✓ Capturi vechi șterse"

# 5. Curățare artifacts (doar cu --full)
echo -e "\n${YELLOW}[5/5] Curățare artifacts...${NC}"
if [ "$FULL_CLEANUP" = true ]; then
    rm -rf artifacts/* 2>/dev/null && echo "  ✓ artifacts/ golit (--full)" || true
else
    echo "  - Skip (folosiți --full pentru ștergere completă)"
    echo "    Artifacts existente:"
    ls -la artifacts/ 2>/dev/null | head -5 || echo "    (director gol sau inexistent)"
fi

# Recreare directoare necesare
mkdir -p artifacts pcap results

# Rezumat
echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}[CLEANUP] Complet!${NC}"
echo ""
echo "Directoare curățate:"
echo "  artifacts/  - artefacte demo (demo.log, demo.pcap, validation.txt)"
echo "  pcap/       - capturi de trafic"
echo "  results/    - loguri servere (legacy)"
echo ""
if [ "$FULL_CLEANUP" = true ]; then
    echo -e "${YELLOW}Mod: FULL (artifacts șterse)${NC}"
else
    echo "Pentru cleanup complet inclusiv artifacts: ./scripts/cleanup.sh --full"
fi
echo -e "${GREEN}════════════════════════════════════════════${NC}"
