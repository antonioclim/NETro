#!/bin/bash
# verify.sh — Verifică mediul și dependențele pentru Starterkit S14
# Rulare: bash scripts/verify.sh

echo "=============================================="
echo "  Verificare mediu S14"
echo "=============================================="
echo ""

ERRORS=0

# Funcție pentru verificare comandă
check_cmd() {
    local cmd=$1
    local required=$2
    
    if command -v "$cmd" &> /dev/null; then
        version=$($cmd --version 2>&1 | head -1 || echo "installed")
        echo "  ✓ $cmd: $version"
    else
        if [ "$required" = "required" ]; then
            echo "  ✗ $cmd: LIPSEȘTE (obligatoriu)"
            ERRORS=$((ERRORS + 1))
        else
            echo "  ○ $cmd: lipsește (opțional)"
        fi
    fi
}

# Verifică Python
echo "[*] Python:"
check_cmd python3 required
if command -v python3 &> /dev/null; then
    PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [ "$(echo "$PY_VERSION >= 3.8" | bc)" -eq 1 ] 2>/dev/null || python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" 2>/dev/null; then
        echo "    Versiune OK (>= 3.8)"
    else
        echo "    Versiune prea veche (necesită >= 3.8)"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Verifică pip
echo ""
echo "[*] Pip:"
check_cmd pip3 required

# Verifică Mininet
echo ""
echo "[*] Mininet & OVS:"
check_cmd mn required
check_cmd ovs-vsctl required

if command -v ovs-vsctl &> /dev/null; then
    if systemctl is-active --quiet openvswitch-switch 2>/dev/null; then
        echo "    openvswitch-switch: activ"
    else
        echo "    openvswitch-switch: INACTIV"
        echo "    Rulează: sudo systemctl start openvswitch-switch"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Verifică instrumente de rețea
echo ""
echo "[*] Instrumente de rețea:"
check_cmd ip required
check_cmd ping required
check_cmd ss required
check_cmd tcpdump required
check_cmd tshark optional
check_cmd nc optional
check_cmd curl optional
check_cmd ab optional

# Verifică permisiuni
echo ""
echo "[*] Permisiuni:"
if [ "$EUID" -eq 0 ]; then
    echo "  ✓ Rulează ca root"
else
    echo "  ○ Nu rulează ca root (demo-ul necesită sudo)"
fi

# Verifică porturi
echo ""
echo "[*] Porturi (8000, 8080, 9000):"
for port in 8000 8080 9000; do
    if ss -lntp 2>/dev/null | grep -q ":$port "; then
        echo "  ✗ Port $port: OCUPAT"
        ss -lntp 2>/dev/null | grep ":$port " | head -1
    else
        echo "  ✓ Port $port: liber"
    fi
done

# Sumar
echo ""
echo "=============================================="
if [ $ERRORS -eq 0 ]; then
    echo "  Verificare completă: OK"
    echo "=============================================="
    exit 0
else
    echo "  Verificare completă: $ERRORS erori"
    echo "=============================================="
    echo ""
    echo "Rulează 'sudo bash scripts/setup.sh' pentru a instala dependențele."
    exit 1
fi
