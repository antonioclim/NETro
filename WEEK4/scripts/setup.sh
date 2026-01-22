#!/bin/bash
# ==============================================================================
# setup.sh - Instalare dependențe pentru Starterkit S4 (WEEK 4)
# ==============================================================================
# Verifică mediul și pregătește directoarele necesare.
# Nu face modificări ireversibile fără confirmare.
#
# Porturi standard WEEK 4: 5400, 5401, 5402
# Rețea IP (Mininet): 10.0.4.0/24
#
# Utilizare:
#   ./scripts/setup.sh           # setup normal
#   ./scripts/setup.sh --check   # doar verificare, fără modificări
#
# Licență: MIT - Material didactic ASE-CSIE
# ==============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Porturi standard WEEK 4
PORT_TEXT=5400
PORT_BIN=5401
PORT_UDP=5402

CHECK_ONLY=false
if [ "$1" = "--check" ] || [ "$1" = "-c" ]; then
    CHECK_ONLY=true
fi

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     SETUP - STARTERKIT SĂPTĂMÂNA 4 (WEEK 4)                  ║${NC}"
echo -e "${CYAN}║     Protocol: TEXT/BINARY custom peste TCP/UDP               ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ==============================================================================
# Verificare Python 3
# ==============================================================================
echo -e "${GREEN}[1/6] Verificare Python 3...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 nu este instalat!${NC}"
    echo "Instalați cu: sudo apt install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}[ERROR] Python 3.8+ necesar (găsit: $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION găsit"

# ==============================================================================
# Verificare module Python necesare (toate în stdlib)
# ==============================================================================
echo -e "\n${GREEN}[2/6] Verificare module Python...${NC}"

MODULES="socket struct zlib threading argparse dataclasses typing"
for mod in $MODULES; do
    if python3 -c "import $mod" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $mod"
    else
        echo -e "  ${RED}✗${NC} $mod (lipsește!)"
        exit 1
    fi
done

# ==============================================================================
# Verificare instrumente de rețea (opționale)
# ==============================================================================
echo -e "\n${GREEN}[3/6] Verificare instrumente de rețea...${NC}"

if command -v tcpdump &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} tcpdump găsit"
else
    echo -e "  ${YELLOW}⚠${NC} tcpdump nu este instalat (opțional pentru capturi)"
    echo "    Instalați cu: sudo apt install tcpdump"
fi

if command -v tshark &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} tshark găsit"
else
    echo -e "  ${YELLOW}⚠${NC} tshark nu este instalat (opțional pentru analiză)"
    echo "    Instalați cu: sudo apt install tshark"
fi

if command -v nc &> /dev/null || command -v netcat &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} netcat găsit"
else
    echo -e "  ${YELLOW}⚠${NC} netcat nu este instalat (opțional pentru debug)"
    echo "    Instalați cu: sudo apt install netcat"
fi

# ==============================================================================
# Verificare porturi disponibile
# ==============================================================================
echo -e "\n${GREEN}[4/6] Verificare porturi standard WEEK 4...${NC}"

for port in $PORT_TEXT $PORT_BIN $PORT_UDP; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠${NC} Port $port OCUPAT"
        echo "    Eliberați cu: kill \$(lsof -t -i :$port)"
    else
        echo -e "  ${GREEN}✓${NC} Port $port liber"
    fi
done

# ==============================================================================
# Creare directoare necesare
# ==============================================================================
echo -e "\n${GREEN}[5/6] Creare directoare...${NC}"

if [ "$CHECK_ONLY" = false ]; then
    mkdir -p artifacts pcap results
    echo -e "  ${GREEN}✓${NC} artifacts/ (demo.log, demo.pcap, validation.txt)"
    echo -e "  ${GREEN}✓${NC} pcap/ (capturi de trafic)"
    echo -e "  ${GREEN}✓${NC} results/ (loguri servere - legacy)"
else
    echo -e "  ${YELLOW}─${NC} Skip (mod --check)"
fi

# ==============================================================================
# Setare permisiuni executabile
# ==============================================================================
echo -e "\n${GREEN}[6/6] Setare permisiuni...${NC}"

if [ "$CHECK_ONLY" = false ]; then
    chmod +x scripts/*.sh 2>/dev/null || true
    chmod +x tests/*.sh 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} Permisiuni executabile setate pentru scripts/ și tests/"
else
    echo -e "  ${YELLOW}─${NC} Skip (mod --check)"
fi

# ==============================================================================
# Rezumat
# ==============================================================================
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
if [ "$CHECK_ONLY" = true ]; then
    echo -e "${GREEN}  Verificare completă! (mod --check, fără modificări)${NC}"
else
    echo -e "${GREEN}  Setup complet!${NC}"
fi
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Plan porturi WEEK 4:"
echo "  TCP TEXT:   $PORT_TEXT"
echo "  TCP BINARY: $PORT_BIN"
echo "  UDP SENSOR: $PORT_UDP"
echo ""
echo "Plan IP (Mininet):"
echo "  Rețea:      10.0.4.0/24"
echo "  Gateway:    10.0.4.1"
echo "  Server:     10.0.4.100"
echo "  Hosts:      h1=10.0.4.11, h2=10.0.4.12, h3=10.0.4.13"
echo ""
echo "Comenzi utile:"
echo "  make verify      - Verifică mediul"
echo "  make test        - Rulează smoke test"
echo "  make run-demo    - Demo complet"
echo "  make server-text - Pornește server TEXT"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
