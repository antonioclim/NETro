#!/bin/bash
# cleanup.sh — Curăță procesele și rețeaua Mininet
# Rulare: sudo bash scripts/cleanup.sh

echo "=============================================="
echo "  Cleanup S14"
echo "=============================================="

# Oprește procesele din kit
echo "[*] Oprire procese starterkit..."
pkill -f "backend_server.py" 2>/dev/null || true
pkill -f "lb_proxy.py" 2>/dev/null || true
pkill -f "tcp_echo_server.py" 2>/dev/null || true
pkill -f "tcp_echo_client.py" 2>/dev/null || true
pkill -f "http_client.py" 2>/dev/null || true
pkill -f "run_demo.py" 2>/dev/null || true
pkill -f "topo_14" 2>/dev/null || true

# Oprește tcpdump
echo "[*] Oprire tcpdump..."
pkill -f "tcpdump" 2>/dev/null || true

# Curăță Mininet
echo "[*] Curățare Mininet..."
if command -v mn &> /dev/null; then
    mn -c 2>/dev/null || true
fi

# Oprește OVS orphan bridges (opțional)
echo "[*] Verificare OVS..."
if command -v ovs-vsctl &> /dev/null; then
    for br in $(ovs-vsctl list-br 2>/dev/null); do
        if [[ "$br" == s* ]]; then
            echo "    Șterg bridge: $br"
            ovs-vsctl del-br "$br" 2>/dev/null || true
        fi
    done
fi

# Eliberează porturile comune (plan porturi S14)
echo "[*] Verificare porturi..."
for port in 8080 9090 9091; do
    pid=$(ss -lntp 2>/dev/null | grep ":$port " | awk '{print $NF}' | grep -oP 'pid=\K[0-9]+' | head -1)
    if [ -n "$pid" ]; then
        echo "    Eliberez port $port (PID: $pid)"
        kill "$pid" 2>/dev/null || true
    fi
done

sleep 1

echo ""
echo "=============================================="
echo "  Cleanup completat!"
echo "=============================================="
