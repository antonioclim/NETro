#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# cleanup.sh - Curățare mediu Săptămâna 8
# ═══════════════════════════════════════════════════════════════════════════════
#
# Oprește toate procesele și curăță fișierele temporare.
# Include și cleanup Mininet dacă e cazul.
#
# Autor: Rețele de Calculatoare, ASE București
# Hypotheticalandrei & Rezolvix | MIT License
# ═══════════════════════════════════════════════════════════════════════════════

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║  Cleanup - Săptămâna 8                                                ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Oprire servere Python
echo "[cleanup] Oprire servere HTTP..."
pkill -f "demo_http_server.py" 2>/dev/null || true
pkill -f "demo_reverse_proxy.py" 2>/dev/null || true
pkill -f "ex01_http_server.py" 2>/dev/null || true
pkill -f "ex02_reverse_proxy.py" 2>/dev/null || true
pkill -f "ex03_post_support.py" 2>/dev/null || true
pkill -f "ex04_rate_limiting.py" 2>/dev/null || true
pkill -f "ex05_caching_proxy.py" 2>/dev/null || true

# Oprire tcpdump (dacă rulează)
echo "[cleanup] Oprire tcpdump..."
sudo pkill -f "tcpdump" 2>/dev/null || true

# Oprire procese pe porturile folosite
echo "[cleanup] Eliberare porturi 8080, 8888, 9001, 9002..."
for port in 8080 8888 9001 9002 5800 5801 5802; do
    fuser -k "$port/tcp" 2>/dev/null || true
done

# Cleanup Docker (dacă e cazul)
if command -v docker &>/dev/null; then
    echo "[cleanup] Verificare containere Docker..."
    if docker ps -q --filter "label=com.ase.project=seminar8" | grep -q .; then
        echo "[cleanup] Oprire containere seminar8..."
        docker stop $(docker ps -q --filter "label=com.ase.project=seminar8") 2>/dev/null || true
    fi
fi

# Cleanup Mininet (dacă e instalat)
if command -v mn &>/dev/null; then
    echo "[cleanup] Cleanup Mininet..."
    sudo mn -c 2>/dev/null || true
fi

# Ștergere fișiere temporare Python
echo "[cleanup] Ștergere fișiere temporare Python..."
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Ștergere loguri (opțional - păstrăm artifacts/)
echo "[cleanup] Ștergere loguri temporare..."
rm -f *.log 2>/dev/null || true
rm -f output/*.log 2>/dev/null || true

echo ""
echo "[cleanup] ✓ Gata!"
echo ""
echo "Pentru reset complet (inclusiv artifacts/):"
echo "  rm -rf artifacts/*"
