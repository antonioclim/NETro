#!/bin/bash
# =============================================================================
# cleanup.sh – Curățare mediu pentru Săptămâna 11
# =============================================================================
# Curăță: containere Docker, procese Python, Mininet, fișiere temporare
# =============================================================================

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}[CLEANUP]${NC} Curățare mediu WEEK 11..."

# Docker containers - toate demo-urile
echo -e "${YELLOW}[1/5]${NC} Oprire containere Docker..."
cd "$ROOT_DIR/docker/nginx_compose" && docker compose down 2>/dev/null || true
cd "$ROOT_DIR/docker/custom_lb_compose" && docker compose down 2>/dev/null || true
cd "$ROOT_DIR/docker/dns_demo" && docker compose down 2>/dev/null || true
cd "$ROOT_DIR/docker/ftp_demo" && docker compose down 2>/dev/null || true
cd "$ROOT_DIR/docker/ssh_demo" && docker compose down 2>/dev/null || true

# Python processes
echo -e "${YELLOW}[2/5]${NC} Oprire procese Python..."
pkill -f "ex_11_01_backend" 2>/dev/null || true
pkill -f "ex_11_02_loadbalancer" 2>/dev/null || true
pkill -f "ex_11_03_dns_client" 2>/dev/null || true

# Mininet
echo -e "${YELLOW}[3/5]${NC} Curățare Mininet..."
sudo mn -c 2>/dev/null || true

# Temp files
echo -e "${YELLOW}[4/5]${NC} Ștergere fișiere temporare..."
rm -f /tmp/backend*.log /tmp/lb.log /tmp/s11_*.log /tmp/*.pid 2>/dev/null || true
rm -f "$ROOT_DIR/pcap/"*.pcap 2>/dev/null || true

# Artifacts (opțional - comentat pentru păstrare)
echo -e "${YELLOW}[5/5]${NC} Artefacte păstrate în artifacts/..."
# Pentru ștergere: decomentați linia de mai jos
# rm -f "$ROOT_DIR/artifacts/"*.log "$ROOT_DIR/artifacts/"*.pcap "$ROOT_DIR/artifacts/"*.txt 2>/dev/null || true

echo -e "${GREEN}[OK]${NC} Curățare completă."
echo -e "${YELLOW}[INFO]${NC} Pentru a șterge și artefactele: rm -rf artifacts/*.{log,pcap,txt}"

# Revolvix&Hypotheticalandrei
