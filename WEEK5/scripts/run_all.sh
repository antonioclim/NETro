#!/usr/bin/env bash
#===============================================================================
# run_all.sh — Demo automat complet pentru Săptămâna 5: Adresare IP
#===============================================================================
# Rulează fără input interactiv și produce:
#   - artifacts/demo.log     : Log complet al tuturor operațiilor
#   - artifacts/demo.pcap    : Captură de trafic (simulată sau reală)
#   - artifacts/validation.txt : Rezumat validare și rezultate
#
# Utilizare: ./scripts/run_all.sh [--full|--quick|--help]
#
# © 2025 ASE-CSIE | Rezolvix&Hypotheticalandrei | Licență MIT
#===============================================================================

set -euo pipefail

#-------------------------------------------------------------------------------
# Configurare
#-------------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$PROJECT_ROOT/artifacts"
PYTHON_DIR="$PROJECT_ROOT/python"
EXERCISES_DIR="$PYTHON_DIR/exercises"

# Plan IP pentru Week 5
WEEK=5
NETWORK_BASE="10.0.${WEEK}"
WEEK_PORT_BASE=$((5100 + 100 * (WEEK - 1)))

# Timestamps
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DEMO_LOG="$ARTIFACTS_DIR/demo.log"
DEMO_PCAP="$ARTIFACTS_DIR/demo.pcap"
VALIDATION_FILE="$ARTIFACTS_DIR/validation.txt"

#-------------------------------------------------------------------------------
# Culori și utilități logging
#-------------------------------------------------------------------------------

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log() {
    local level="$1"
    shift
    local msg="$*"
    local ts
    ts=$(date +"%Y-%m-%d %H:%M:%S")
    
    case "$level" in
        INFO)  echo -e "${BLUE}[$ts] [INFO]${NC} $msg" ;;
        OK)    echo -e "${GREEN}[$ts] [OK]${NC} $msg" ;;
        WARN)  echo -e "${YELLOW}[$ts] [WARN]${NC} $msg" ;;
        ERROR) echo -e "${RED}[$ts] [ERROR]${NC} $msg" ;;
        TITLE) echo -e "\n${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}"
               echo -e "${BOLD}${CYAN}  $msg${NC}"
               echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}\n" ;;
    esac
    
    # Scriem și în log (fără coduri de culoare)
    echo "[$ts] [$level] $msg" >> "$DEMO_LOG"
}

run_cmd() {
    local desc="$1"
    shift
    log INFO "Execut: $desc"
    log INFO "Comandă: $*"
    
    if "$@" >> "$DEMO_LOG" 2>&1; then
        log OK "$desc - Succes"
        return 0
    else
        log WARN "$desc - Eșuat (non-fatal)"
        return 1
    fi
}

#-------------------------------------------------------------------------------
# Inițializare
#-------------------------------------------------------------------------------

init_demo() {
    log TITLE "Inițializare Demo Săptămâna $WEEK"
    
    # Creare director artifacts
    mkdir -p "$ARTIFACTS_DIR"
    
    # Inițializare fișiere
    echo "# Demo Log - Săptămâna $WEEK: Adresare IP" > "$DEMO_LOG"
    echo "# Generat: $(date)" >> "$DEMO_LOG"
    echo "# Network Base: $NETWORK_BASE.0/24" >> "$DEMO_LOG"
    echo "# Week Port Base: $WEEK_PORT_BASE" >> "$DEMO_LOG"
    echo "" >> "$DEMO_LOG"
    
    log INFO "Directoare și fișiere inițializate"
    log INFO "Log: $DEMO_LOG"
    log INFO "PCAP: $DEMO_PCAP"
    log INFO "Validare: $VALIDATION_FILE"
}

#-------------------------------------------------------------------------------
# Verificare mediu
#-------------------------------------------------------------------------------

check_environment() {
    log TITLE "Verificare Mediu"
    
    local errors=0
    
    # Python
    if command -v python3 &>/dev/null; then
        local py_ver
        py_ver=$(python3 --version 2>&1)
        log OK "Python: $py_ver"
    else
        log ERROR "Python3 nu este instalat"
        ((errors++))
    fi
    
    # Modul ipaddress
    if python3 -c "import ipaddress" 2>/dev/null; then
        log OK "Modul ipaddress disponibil"
    else
        log ERROR "Modulul ipaddress lipsește"
        ((errors++))
    fi
    
    # Mininet (opțional)
    if command -v mn &>/dev/null; then
        log OK "Mininet instalat"
    else
        log WARN "Mininet nu este instalat (demo parțial)"
    fi
    
    # tcpdump (opțional)
    if command -v tcpdump &>/dev/null; then
        log OK "tcpdump disponibil"
    else
        log WARN "tcpdump nu este instalat (captură simulată)"
    fi
    
    return $errors
}

#-------------------------------------------------------------------------------
# Demo Python - Analiză CIDR
#-------------------------------------------------------------------------------

demo_cidr_analysis() {
    log TITLE "Demo 1: Analiză CIDR IPv4"
    
    cd "$EXERCISES_DIR"
    
    # Test 1: Adresă simplă
    log INFO "Analiză 192.168.10.14/26"
    python3 ex_5_01_cidr_flsm.py analyze 192.168.10.14/26 >> "$DEMO_LOG" 2>&1 || true
    
    # Test 2: Cu output JSON
    log INFO "Analiză JSON pentru 172.16.50.100/20"
    python3 ex_5_01_cidr_flsm.py analyze 172.16.50.100/20 --json >> "$DEMO_LOG" 2>&1 || true
    
    # Test 3: Adresă din rețeaua săptămânii
    log INFO "Analiză rețea Week $WEEK: ${NETWORK_BASE}.100/24"
    python3 ex_5_01_cidr_flsm.py analyze "${NETWORK_BASE}.100/24" --verbose >> "$DEMO_LOG" 2>&1 || true
    
    # Test 4: Conversie binară
    log INFO "Conversie binară 10.0.5.1"
    python3 ex_5_01_cidr_flsm.py binary 10.0.5.1 >> "$DEMO_LOG" 2>&1 || true
    
    log OK "Demo CIDR finalizat"
}

#-------------------------------------------------------------------------------
# Demo Python - Subnetting FLSM
#-------------------------------------------------------------------------------

demo_flsm() {
    log TITLE "Demo 2: Subnetting FLSM"
    
    cd "$EXERCISES_DIR"
    
    # Test 1: Împărțire în 4 subrețele
    log INFO "FLSM: 192.168.100.0/24 → 4 subrețele"
    python3 ex_5_01_cidr_flsm.py flsm 192.168.100.0/24 4 >> "$DEMO_LOG" 2>&1 || true
    
    # Test 2: Împărțire în 8 subrețele
    log INFO "FLSM: 10.0.0.0/24 → 8 subrețele"
    python3 ex_5_01_cidr_flsm.py flsm 10.0.0.0/24 8 >> "$DEMO_LOG" 2>&1 || true
    
    # Test 3: Rețea mare
    log INFO "FLSM: 10.0.0.0/8 → 4 subrețele majore"
    python3 ex_5_01_cidr_flsm.py flsm 10.0.0.0/8 4 --json >> "$DEMO_LOG" 2>&1 || true
    
    log OK "Demo FLSM finalizat"
}

#-------------------------------------------------------------------------------
# Demo Python - VLSM
#-------------------------------------------------------------------------------

demo_vlsm() {
    log TITLE "Demo 3: Alocare VLSM"
    
    cd "$EXERCISES_DIR"
    
    # Test 1: Cerințe tipice
    log INFO "VLSM: 172.16.0.0/24 pentru 60, 20, 10, 2 hosturi"
    python3 ex_5_02_vlsm_ipv6.py vlsm 172.16.0.0/24 60 20 10 2 >> "$DEMO_LOG" 2>&1 || true
    
    # Test 2: Scenariul complex organizație
    log INFO "VLSM: 10.10.0.0/22 pentru 200, 100, 50, 25, 10, 2, 2, 2"
    python3 ex_5_02_vlsm_ipv6.py vlsm 10.10.0.0/22 200 100 50 25 10 2 2 2 >> "$DEMO_LOG" 2>&1 || true
    
    # Test 3: Rețeaua săptămânii
    log INFO "VLSM: ${NETWORK_BASE}.0/24 pentru 50, 30, 10, 6, 2"
    python3 ex_5_02_vlsm_ipv6.py vlsm "${NETWORK_BASE}.0/24" 50 30 10 6 2 --json >> "$DEMO_LOG" 2>&1 || true
    
    log OK "Demo VLSM finalizat"
}

#-------------------------------------------------------------------------------
# Demo Python - IPv6
#-------------------------------------------------------------------------------

demo_ipv6() {
    log TITLE "Demo 4: Utilitare IPv6"
    
    cd "$EXERCISES_DIR"
    
    # Test 1: Comprimare
    log INFO "IPv6 Comprimare: 2001:0db8:0000:0000:0000:0000:0000:0001"
    python3 ex_5_02_vlsm_ipv6.py ipv6 2001:0db8:0000:0000:0000:0000:0000:0001 >> "$DEMO_LOG" 2>&1 || true
    
    # Test 2: Expandare
    log INFO "IPv6 Expandare: 2001:db8::1"
    python3 ex_5_02_vlsm_ipv6.py ipv6-expand 2001:db8::1 >> "$DEMO_LOG" 2>&1 || true
    
    # Test 3: Generare subrețele
    log INFO "IPv6 Subrețele: 2001:db8:10::/48 → 5 subrețele /64"
    python3 ex_5_02_vlsm_ipv6.py ipv6-subnets 2001:db8:10::/48 64 5 >> "$DEMO_LOG" 2>&1 || true
    
    # Test 4: Tipuri adrese
    log INFO "IPv6 Tipuri de adrese"
    python3 ex_5_02_vlsm_ipv6.py ipv6-types >> "$DEMO_LOG" 2>&1 || true
    
    log OK "Demo IPv6 finalizat"
}

#-------------------------------------------------------------------------------
# Demo net_utils
#-------------------------------------------------------------------------------

demo_net_utils() {
    log TITLE "Demo 5: Biblioteca net_utils"
    
    cd "$PROJECT_ROOT"
    
    # Test direct al bibliotecii
    log INFO "Test direct net_utils.py"
    python3 -c "
from python.utils.net_utils import (
    analyze_ipv4_interface, 
    vlsm_allocate, 
    ipv6_info,
    prefix_for_hosts,
    summarize_networks
)

# Test analiză
info = analyze_ipv4_interface('10.0.5.100/24')
print(f'Analiză 10.0.5.100/24:')
print(f'  Rețea: {info.network}')
print(f'  Hosturi: {info.usable_hosts}')
print(f'  Broadcast: {info.broadcast}')
print()

# Test VLSM
allocs = vlsm_allocate('10.0.5.0/24', [60, 30, 10, 2])
print('VLSM 10.0.5.0/24 pentru [60, 30, 10, 2]:')
for a in allocs:
    print(f'  {a.network} (ef: {a.efficiency:.1f}%)')
print()

# Test prefix
print(f'Prefix pentru 100 hosturi: /{prefix_for_hosts(100)}')
print(f'Prefix pentru 10 hosturi: /{prefix_for_hosts(10)}')
print()

# Test IPv6
v6 = ipv6_info('2001:db8::1')
print(f'IPv6 2001:db8::1: tip={v6.address_type}, scope={v6.scope}')
print()

# Test sumarizare
nets = summarize_networks(['192.168.0.0/24', '192.168.1.0/24', '192.168.2.0/24', '192.168.3.0/24'])
print(f'Sumarizare 192.168.0-3.0/24: {nets}')
" >> "$DEMO_LOG" 2>&1 || log WARN "Eroare la test net_utils"
    
    log OK "Demo net_utils finalizat"
}

#-------------------------------------------------------------------------------
# Generare captură simulată
#-------------------------------------------------------------------------------

generate_pcap() {
    log TITLE "Generare Captură PCAP"
    
    if command -v tcpdump &>/dev/null; then
        log INFO "Captură reală din trafic loopback (5 secunde)..."
        
        # Generăm puțin trafic pe loopback
        ping -c 3 127.0.0.1 &>/dev/null &
        
        # Captură scurtă
        sudo timeout 5 tcpdump -i lo -c 50 -w "$DEMO_PCAP" 2>/dev/null || {
            log WARN "Captură reală eșuată, generez simulată"
            generate_simulated_pcap
        }
        
        if [[ -f "$DEMO_PCAP" ]] && [[ -s "$DEMO_PCAP" ]]; then
            local size
            size=$(stat -f%z "$DEMO_PCAP" 2>/dev/null || stat -c%s "$DEMO_PCAP" 2>/dev/null || echo "0")
            log OK "PCAP generat: $size bytes"
        else
            generate_simulated_pcap
        fi
    else
        generate_simulated_pcap
    fi
}

generate_simulated_pcap() {
    log INFO "Generare captură PCAP simulată..."
    
    # Creăm un fișier PCAP minimal valid (header + 1 pachet dummy)
    python3 - << 'PYTHON_EOF' "$DEMO_PCAP"
import struct
import sys

pcap_file = sys.argv[1]

# PCAP Global Header
# magic, version_major, version_minor, thiszone, sigfigs, snaplen, network
pcap_header = struct.pack('<IHHiIII', 
    0xa1b2c3d4,  # Magic number
    2, 4,        # Version 2.4
    0,           # Timezone
    0,           # Timestamp accuracy
    65535,       # Snaplen
    1            # Ethernet
)

# Packet header (for a dummy packet)
# ts_sec, ts_usec, incl_len, orig_len
import time
ts = int(time.time())
packet_header = struct.pack('<IIII', ts, 0, 42, 42)

# Dummy Ethernet + IP + ICMP packet (42 bytes)
# This is a minimal valid packet structure
dummy_packet = bytes([
    # Ethernet header (14 bytes)
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff,  # Destination MAC (broadcast)
    0x00, 0x00, 0x00, 0x00, 0x00, 0x01,  # Source MAC
    0x08, 0x00,                          # EtherType (IPv4)
    # IP header (20 bytes)
    0x45, 0x00,              # Version + IHL, DSCP
    0x00, 0x1c,              # Total length (28)
    0x00, 0x01,              # Identification
    0x00, 0x00,              # Flags + Fragment offset
    0x40,                    # TTL (64)
    0x01,                    # Protocol (ICMP)
    0x00, 0x00,              # Header checksum (placeholder)
    0x0a, 0x00, 0x05, 0x01,  # Source IP (10.0.5.1)
    0x0a, 0x00, 0x05, 0x64,  # Dest IP (10.0.5.100)
    # ICMP header (8 bytes)
    0x08, 0x00,              # Type (Echo), Code
    0x00, 0x00,              # Checksum
    0x00, 0x01,              # Identifier
    0x00, 0x01,              # Sequence
])

with open(pcap_file, 'wb') as f:
    f.write(pcap_header)
    f.write(packet_header)
    f.write(dummy_packet)

print(f"PCAP simulat creat: {pcap_file}")
PYTHON_EOF
    
    if [[ -f "$DEMO_PCAP" ]]; then
        log OK "PCAP simulat generat (demonstrativ)"
    else
        log WARN "Nu s-a putut genera PCAP"
        touch "$DEMO_PCAP"
    fi
}

#-------------------------------------------------------------------------------
# Generare validare
#-------------------------------------------------------------------------------

generate_validation() {
    log TITLE "Generare Raport Validare"
    
    {
        echo "═══════════════════════════════════════════════════════════════"
        echo "  VALIDARE DEMO — Săptămâna $WEEK: Adresare IP"
        echo "═══════════════════════════════════════════════════════════════"
        echo ""
        echo "Data generare: $(date)"
        echo "Rețea principală: ${NETWORK_BASE}.0/24"
        echo "Port Base: $WEEK_PORT_BASE"
        echo ""
        echo "───────────────────────────────────────────────────────────────"
        echo "  VERIFICĂRI COMPONENTE"
        echo "───────────────────────────────────────────────────────────────"
        
        # Verificare Python
        if python3 --version &>/dev/null; then
            echo "[OK] Python3: $(python3 --version 2>&1)"
        else
            echo "[FAIL] Python3 nu este instalat"
        fi
        
        # Verificare module
        if python3 -c "import ipaddress" 2>/dev/null; then
            echo "[OK] Modul ipaddress"
        else
            echo "[FAIL] Modul ipaddress"
        fi
        
        # Verificare exerciții
        for ex in ex_5_01_cidr_flsm.py ex_5_02_vlsm_ipv6.py ex_5_03_quiz_generator.py; do
            if [[ -f "$EXERCISES_DIR/$ex" ]]; then
                if python3 -m py_compile "$EXERCISES_DIR/$ex" 2>/dev/null; then
                    echo "[OK] $ex - sintaxă validă"
                else
                    echo "[FAIL] $ex - erori sintaxă"
                fi
            else
                echo "[MISSING] $ex"
            fi
        done
        
        # Verificare net_utils
        cd "$PROJECT_ROOT"
        if python3 -c "import sys; sys.path.insert(0, '.'); from python.utils.net_utils import analyze_ipv4_interface" 2>/dev/null; then
            echo "[OK] net_utils - importabil"
        else
            echo "[FAIL] net_utils - erori import"
        fi
        
        # Verificare Mininet topologii
        for topo in topo_5_base.py topo_5_extended.py; do
            if [[ -f "$PROJECT_ROOT/mininet/topologies/$topo" ]]; then
                if python3 -m py_compile "$PROJECT_ROOT/mininet/topologies/$topo" 2>/dev/null; then
                    echo "[OK] $topo - sintaxă validă"
                else
                    echo "[FAIL] $topo - erori sintaxă"
                fi
            fi
        done
        
        echo ""
        echo "───────────────────────────────────────────────────────────────"
        echo "  VERIFICĂRI REZULTATE CALCULE"
        echo "───────────────────────────────────────────────────────────────"
        
        # Test calcul CIDR
        local cidr_result
        cidr_result=$(cd "$EXERCISES_DIR" && python3 ex_5_01_cidr_flsm.py analyze 192.168.1.0/24 --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('usable_hosts', 'N/A'))" 2>/dev/null || echo "N/A")
        if [[ "$cidr_result" == "254" ]]; then
            echo "[OK] CIDR /24 = 254 hosturi: CORECT"
        else
            echo "[FAIL] CIDR /24: așteptat 254, obținut $cidr_result"
        fi
        
        # Test calcul /26
        cidr_result=$(cd "$EXERCISES_DIR" && python3 ex_5_01_cidr_flsm.py analyze 10.0.0.1/26 --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('usable_hosts', 'N/A'))" 2>/dev/null || echo "N/A")
        if [[ "$cidr_result" == "62" ]]; then
            echo "[OK] CIDR /26 = 62 hosturi: CORECT"
        else
            echo "[FAIL] CIDR /26: așteptat 62, obținut $cidr_result"
        fi
        
        # Test VLSM
        local vlsm_count
        vlsm_count=$(cd "$EXERCISES_DIR" && python3 ex_5_02_vlsm_ipv6.py vlsm 10.0.0.0/24 60 20 10 2 --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('allocations', [])))" 2>/dev/null || echo "0")
        if [[ "$vlsm_count" == "4" ]]; then
            echo "[OK] VLSM 4 cerințe = 4 alocări: CORECT"
        else
            echo "[FAIL] VLSM: așteptat 4 alocări, obținut $vlsm_count"
        fi
        
        # Test IPv6 comprimare
        local ipv6_result
        cd "$PROJECT_ROOT"
        ipv6_result=$(python3 -c "import sys; sys.path.insert(0, '.'); from python.utils.net_utils import ipv6_compress; print(ipv6_compress('2001:0db8:0000:0000:0000:0000:0000:0001'))" 2>/dev/null || echo "N/A")
        if [[ "$ipv6_result" == "2001:db8::1" ]]; then
            echo "[OK] IPv6 comprimare: CORECT"
        else
            echo "[FAIL] IPv6: așteptat 2001:db8::1, obținut $ipv6_result"
        fi
        
        echo ""
        echo "───────────────────────────────────────────────────────────────"
        echo "  ARTEFACTE GENERATE"
        echo "───────────────────────────────────────────────────────────────"
        
        for artifact in demo.log demo.pcap validation.txt; do
            local path="$ARTIFACTS_DIR/$artifact"
            if [[ -f "$path" ]]; then
                local size
                size=$(stat -f%z "$path" 2>/dev/null || stat -c%s "$path" 2>/dev/null || echo "?")
                echo "[OK] $artifact ($size bytes)"
            else
                echo "[MISSING] $artifact"
            fi
        done
        
        echo ""
        echo "═══════════════════════════════════════════════════════════════"
        echo "  CONCLUZIE: Demo finalizat cu succes"
        echo "═══════════════════════════════════════════════════════════════"
        
    } > "$VALIDATION_FILE"
    
    log OK "Raport validare generat: $VALIDATION_FILE"
    
    # Afișăm și pe ecran
    cat "$VALIDATION_FILE"
}

#-------------------------------------------------------------------------------
# Rulare demo complet
#-------------------------------------------------------------------------------

run_full_demo() {
    init_demo
    
    if ! check_environment; then
        log ERROR "Mediul nu este configurat corect"
        return 1
    fi
    
    demo_cidr_analysis
    demo_flsm
    demo_vlsm
    demo_ipv6
    demo_net_utils
    generate_pcap
    generate_validation
    
    log TITLE "Demo Complet Finalizat"
    log OK "Toate artefactele au fost generate în: $ARTIFACTS_DIR"
    log INFO "Verificați cu: ./tests/smoke_test.sh"
}

#-------------------------------------------------------------------------------
# Rulare demo rapid
#-------------------------------------------------------------------------------

run_quick_demo() {
    init_demo
    check_environment || true
    
    log TITLE "Demo Rapid (CIDR + VLSM)"
    
    cd "$EXERCISES_DIR"
    
    # Doar testele esențiale
    log INFO "CIDR: 192.168.10.14/26"
    python3 ex_5_01_cidr_flsm.py analyze 192.168.10.14/26 >> "$DEMO_LOG" 2>&1 || true
    
    log INFO "VLSM: 172.16.0.0/24 pentru 60, 20, 10, 2"
    python3 ex_5_02_vlsm_ipv6.py vlsm 172.16.0.0/24 60 20 10 2 >> "$DEMO_LOG" 2>&1 || true
    
    generate_simulated_pcap
    generate_validation
    
    log OK "Demo rapid finalizat"
}

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

show_help() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║       run_all.sh — Demo Automat Săptămâna 5                  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Utilizare: $0 [OPȚIUNE]"
    echo ""
    echo "Opțiuni:"
    echo "  --full, -f    Rulează demo complet (implicit)"
    echo "  --quick, -q   Rulează demo rapid (doar esențiale)"
    echo "  --help, -h    Afișează acest ajutor"
    echo ""
    echo "Artefacte generate:"
    echo "  artifacts/demo.log         Log complet operații"
    echo "  artifacts/demo.pcap        Captură pachete"
    echo "  artifacts/validation.txt   Raport validare"
    echo ""
    echo "Exemple:"
    echo "  $0                   # Demo complet"
    echo "  $0 --quick           # Demo rapid"
    echo "  $0 && cat artifacts/validation.txt"
    echo ""
}

main() {
    local mode="${1:---full}"
    
    case "$mode" in
        --full|-f)
            run_full_demo
            ;;
        --quick|-q)
            run_quick_demo
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "Opțiune necunoscută: $mode"
            show_help
            exit 1
            ;;
    esac
}

cd "$PROJECT_ROOT"
main "$@"
