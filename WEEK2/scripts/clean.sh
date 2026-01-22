#!/usr/bin/env bash
# =============================================================================
# clean.sh - Curățare mediu după laborator pentru Săptămâna 2
# Rețele de Calculatoare - ASE București, CSIE
# =============================================================================
# Revolvix&Hypotheticalandrei
# =============================================================================

set -euo pipefail
IFS=$'\n\t'

# Culori pentru output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Directorul script-ului și proiect
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# =============================================================================
# Funcții utilitare
# =============================================================================

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

# =============================================================================
# Funcții de curățare
# =============================================================================

cleanup_processes() {
    log_info "Oprire procese Python din demo-uri..."
    
    # Oprire servere TCP/UDP pe porturile standard
    local DEMO_PORTS=(8080 8081 9999 5000)
    local killed=0
    
    for port in "${DEMO_PORTS[@]}"; do
        local pids
        pids=$(lsof -t -i :$port 2>/dev/null || true)
        if [[ -n "$pids" ]]; then
            for pid in $pids; do
                # Verificăm că e un proces Python din proiect
                local cmdline
                cmdline=$(cat /proc/$pid/cmdline 2>/dev/null | tr '\0' ' ' || echo "")
                if [[ "$cmdline" == *python* ]] || [[ "$cmdline" == *ex_2_* ]]; then
                    kill "$pid" 2>/dev/null && killed=$((killed + 1)) || true
                fi
            done
        fi
    done
    
    if [[ $killed -gt 0 ]]; then
        log_success "Oprite $killed procese"
    else
        log_info "Nu au fost găsite procese de demo active"
    fi
}

cleanup_mininet() {
    log_info "Curățare Mininet..."
    
    if command -v mn &> /dev/null; then
        if [[ $EUID -eq 0 ]]; then
            mn -c 2>/dev/null || true
            log_success "Mininet curățat"
        else
            log_warning "Mininet necesită sudo pentru curățare"
            log_info "  Rulați: sudo mn -c"
        fi
    else
        log_info "Mininet nu este instalat, skip"
    fi
}

cleanup_captures() {
    log_info "Curățare fișiere de captură temporare..."
    
    local captures_dir="$PROJECT_ROOT/seminar/captures"
    local pcap_dir="$PROJECT_ROOT/pcap"
    local logs_dir="$PROJECT_ROOT/logs"
    
    local deleted=0
    
    # Șterge capturi temporare (mai vechi de 1 zi)
    if [[ -d "$captures_dir" ]]; then
        deleted=$(find "$captures_dir" -name "*.pcap" -mtime +1 -delete -print 2>/dev/null | wc -l || echo 0)
    fi
    
    # Șterge log-uri vechi
    if [[ -d "$logs_dir" ]]; then
        find "$logs_dir" -name "*.log" -mtime +7 -delete 2>/dev/null || true
    fi
    
    log_success "Șterse $deleted fișiere temporare"
}

cleanup_pycache() {
    log_info "Curățare __pycache__ și .pyc..."
    
    local deleted=0
    
    # Șterge directoarele __pycache__
    while IFS= read -r -d '' dir; do
        rm -rf "$dir"
        deleted=$((deleted + 1))
    done < <(find "$PROJECT_ROOT" -type d -name "__pycache__" -print0 2>/dev/null)
    
    # Șterge fișierele .pyc
    find "$PROJECT_ROOT" -name "*.pyc" -delete 2>/dev/null || true
    
    log_success "Curățate $deleted directoare __pycache__"
}

cleanup_temp() {
    log_info "Curățare fișiere temporare..."
    
    # Fișiere temporare comune
    find "$PROJECT_ROOT" \( \
        -name "*.tmp" -o \
        -name "*.swp" -o \
        -name "*~" -o \
        -name ".DS_Store" -o \
        -name "Thumbs.db" \
    \) -delete 2>/dev/null || true
    
    log_success "Fișiere temporare curățate"
}

reset_logs() {
    log_info "Resetare directoare de log..."
    
    local logs_dir="$PROJECT_ROOT/logs"
    
    if [[ -d "$logs_dir" ]]; then
        rm -rf "${logs_dir:?}"/*
        touch "$logs_dir/.gitkeep"
        log_success "Directorul logs/ resetat"
    fi
}

show_status() {
    echo ""
    log_info "Status actual:"
    
    # Procese pe porturile demo
    echo "  Procese pe porturi demo:"
    for port in 8080 8081 9999 5000; do
        local proc
        proc=$(lsof -i :$port 2>/dev/null | tail -1 | awk '{print $1, $2}' || echo "liber")
        echo "    Port $port: $proc"
    done
    
    # Spațiu folosit
    echo ""
    echo "  Spațiu folosit:"
    echo "    captures/: $(du -sh "$PROJECT_ROOT/seminar/captures" 2>/dev/null | cut -f1 || echo '0')"
    echo "    logs/:     $(du -sh "$PROJECT_ROOT/logs" 2>/dev/null | cut -f1 || echo '0')"
    echo "    pcap/:     $(du -sh "$PROJECT_ROOT/pcap" 2>/dev/null | cut -f1 || echo '0')"
}

# =============================================================================
# Main
# =============================================================================

main() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║           Curățare Mediu - Săptămâna 2: Sockets             ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    local mode="${1:-standard}"
    
    case "$mode" in
        --full|-f)
            log_info "Mod: Curățare COMPLETĂ"
            echo ""
            cleanup_processes
            cleanup_mininet
            cleanup_captures
            cleanup_pycache
            cleanup_temp
            reset_logs
            ;;
        --soft|-s)
            log_info "Mod: Curățare SOFT (păstrează capturi)"
            echo ""
            cleanup_processes
            cleanup_pycache
            cleanup_temp
            ;;
        --status)
            show_status
            exit 0
            ;;
        --help|-h)
            cat << EOF
Utilizare: $0 [opțiune]

Opțiuni:
  (fără)     Curățare standard (procese, mininet, temp)
  --soft     Curățare soft (păstrează capturi și logs)
  --full     Curățare completă (inclusiv capturi și logs)
  --status   Afișează status fără a curăța
  --help     Afișează acest mesaj

EOF
            exit 0
            ;;
        *)
            log_info "Mod: Curățare STANDARD"
            echo ""
            cleanup_processes
            cleanup_mininet
            cleanup_pycache
            cleanup_temp
            ;;
    esac
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}                    Curățare completă!                         ${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    
    show_status
}

main "$@"
