#!/bin/bash
echo "[CLEAN] Curățare Mininet..."
sudo mn -c 2>/dev/null || true
echo "[CLEAN] Oprire procese Python..."
sudo pkill -f "ex0[1-8]" 2>/dev/null || true
sudo pkill -f "topo_" 2>/dev/null || true
echo "[CLEAN] Curățare fișiere temporare..."
rm -rf __pycache__ python/__pycache__ logs/ *.pcap *.pcapng
echo "[OK] Curățare completă."
