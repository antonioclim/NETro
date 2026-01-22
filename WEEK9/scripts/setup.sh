#!/bin/bash
# =============================================================================
# Setup script pentru Starterkit S9
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Setup Starterkit S9 - Rețele de calculatoare                  ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"

# 1. Verificăm Python
echo -e "\n${YELLOW}[1/4] Verificare Python...${NC}"
if command -v python3 &> /dev/null; then
    PYVER=$(python3 --version)
    echo -e "${GREEN}✓ $PYVER${NC}"
else
    echo "Python3 nu este instalat!"
    exit 1
fi

# 2. Instalăm dependențe Python
echo -e "\n${YELLOW}[2/4] Instalare dependențe Python...${NC}"
python3 -m pip install --break-system-packages -q -r requirements.txt 2>/dev/null || \
    python3 -m pip install -q -r requirements.txt 2>/dev/null || \
    echo "Notă: Instalați manual pyftpdlib dacă e necesar"
echo -e "${GREEN}✓ Dependențe instalate${NC}"

# 3. Creăm directoarele
echo -e "\n${YELLOW}[3/4] Creare directoare...${NC}"
mkdir -p server-files client-files pcap
echo -e "${GREEN}✓ Directoare create${NC}"

# 4. Creăm fișiere de test
echo -e "\n${YELLOW}[4/4] Creare fișiere de test...${NC}"
echo "Hello S9 - Protocoale de fișiere!" > server-files/hello.txt
echo "Test file with UTF-8: România ✓" > server-files/utf8_test.txt
echo "Binary test content" > server-files/test.bin
dd if=/dev/urandom of=server-files/random_100k.bin bs=1024 count=100 2>/dev/null || true
echo -e "${GREEN}✓ Fișiere de test create${NC}"

echo -e "\n${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup complet! Comenzi utile:${NC}"
echo -e "${GREEN}    make server         - Pornește serverul${NC}"
echo -e "${GREEN}    make client-list    - Listează fișierele${NC}"
echo -e "${GREEN}    make help           - Toate comenzile${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
