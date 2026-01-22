#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# setup.sh - Configurare mediu pentru Săptămâna 8
# ═══════════════════════════════════════════════════════════════════════════════

set -e

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║  Setup - Rețele de Calculatoare - Săptămâna 8                         ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Detectare sistem
if [ -f /etc/debian_version ]; then
    PKG_MANAGER="apt"
    INSTALL_CMD="sudo apt-get install -y"
elif [ -f /etc/redhat-release ]; then
    PKG_MANAGER="yum"
    INSTALL_CMD="sudo yum install -y"
else
    echo "[WARN] Sistem necunoscut. Instalează manual: curl, netcat, tcpdump"
    PKG_MANAGER="unknown"
fi

echo "[INFO] Verificare Python 3..."
if command -v python3 &> /dev/null; then
    echo "  ✓ Python 3 găsit: $(python3 --version)"
else
    echo "  ✗ Python 3 lipsește!"
    if [ "$PKG_MANAGER" = "apt" ]; then
        echo "[INFO] Instalare Python 3..."
        $INSTALL_CMD python3 python3-pip
    fi
fi

echo ""
echo "[INFO] Verificare curl..."
if command -v curl &> /dev/null; then
    echo "  ✓ curl găsit"
else
    echo "  ✗ curl lipsește"
    if [ "$PKG_MANAGER" = "apt" ]; then
        $INSTALL_CMD curl
    fi
fi

echo ""
echo "[INFO] Verificare netcat..."
if command -v nc &> /dev/null; then
    echo "  ✓ netcat găsit"
else
    echo "  ✗ netcat lipsește"
    if [ "$PKG_MANAGER" = "apt" ]; then
        $INSTALL_CMD netcat-openbsd
    fi
fi

echo ""
echo "[INFO] Verificare tcpdump (opțional)..."
if command -v tcpdump &> /dev/null; then
    echo "  ✓ tcpdump găsit"
else
    echo "  ○ tcpdump lipsește (opțional, pentru capturi)"
    if [ "$PKG_MANAGER" = "apt" ]; then
        echo "    Poți instala cu: sudo apt-get install tcpdump"
    fi
fi

echo ""
echo "[INFO] Verificare tshark/wireshark (opțional)..."
if command -v tshark &> /dev/null; then
    echo "  ✓ tshark găsit"
else
    echo "  ○ tshark lipsește (opțional)"
fi

echo ""
echo "[INFO] Verificare Docker (opțional)..."
if command -v docker &> /dev/null; then
    echo "  ✓ Docker găsit"
else
    echo "  ○ Docker lipsește (opțional, pentru scenarii avansate)"
fi

echo ""
echo "[INFO] Creare directoare necesare..."
mkdir -p output pcap artifacts

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║  Setup completat!                                                      ║"
echo "║                                                                        ║"
echo "║  Următorii pași:                                                       ║"
echo "║    1. make verify         - Verifică instalarea                        ║"
echo "║    2. ./scripts/run_all.sh - Rulează demo-ul automat                   ║"
echo "║    3. make help           - Vezi toate comenzile                       ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
