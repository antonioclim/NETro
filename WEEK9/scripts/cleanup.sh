#!/bin/bash
# =============================================================================
# cleanup.sh – Curățare completă pentru Starterkit S9
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║  Cleanup Starterkit S9                                            ║${NC}"
echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════════╝${NC}"

# 1. Oprire procese
echo -e "\n${YELLOW}[1/5] Oprire procese...${NC}"
pkill -f "ex_9_02_pseudo_ftp" 2>/dev/null && echo "  ✓ Oprit: pseudo_ftp" || true
pkill -f "ftp_demo" 2>/dev/null && echo "  ✓ Oprit: ftp_demo" || true
pkill -f "tcpdump" 2>/dev/null && echo "  ✓ Oprit: tcpdump" || true

# 2. Curățare Docker (dacă există)
echo -e "\n${YELLOW}[2/5] Curățare Docker...${NC}"
if command -v docker-compose &> /dev/null && [ -f "docker/docker-compose.yml" ]; then
    cd docker && docker-compose down -v 2>/dev/null && cd .. && echo "  ✓ Docker oprit" || true
else
    echo "  - Docker nu este configurat"
fi

# 3. Curățare Mininet (dacă root)
echo -e "\n${YELLOW}[3/5] Curățare Mininet...${NC}"
if [ "$(id -u)" -eq 0 ]; then
    mn -c 2>/dev/null && echo "  ✓ Mininet curățat" || true
else
    echo "  - Necesită root pentru mn -c"
fi

# 4. Curățare fișiere temporare
echo -e "\n${YELLOW}[4/5] Curățare fișiere temporare...${NC}"
rm -rf __pycache__ python/**/__pycache__ .pytest_cache 2>/dev/null && echo "  ✓ Cache Python" || true
rm -f *.pyc python/**/*.pyc 2>/dev/null && echo "  ✓ Fișiere .pyc" || true
rm -f client-files/*.txt client-files/*.bin 2>/dev/null && echo "  ✓ Fișiere client" || true

# 5. Curățare artefacte (opțional)
echo -e "\n${YELLOW}[5/5] Curățare artefacte...${NC}"
if [ "$1" = "--all" ]; then
    rm -rf artifacts/* 2>/dev/null && echo "  ✓ Artefacte șterse" || true
    rm -rf server-files/* 2>/dev/null && echo "  ✓ Server files șterse" || true
else
    echo "  - Artefacte păstrate (folosiți --all pentru ștergere completă)"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Cleanup complet!${NC}"
echo -e "${GREEN}  Pentru ștergere totală: ./scripts/cleanup.sh --all${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
