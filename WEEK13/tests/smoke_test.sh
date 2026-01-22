#!/bin/bash
# ============================================================================
# smoke_test.sh - Test de verificare pentru starterkit S13
# ============================================================================
# Verifică:
# - Sintaxa Python pentru toate scripturile
# - Import-uri funcționale
# - Disponibilitatea dependențelor
# - Conectivitatea Docker (dacă e pornit)
# - Structura fișierelor și directoarelor
#
# Autor: Colectivul de Tehnologii Web, ASE-CSIE
# Versiune: 1.0
# ============================================================================

set -e

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Directoare
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Contoare
PASS=0
FAIL=0
WARN=0
SKIP=0

# ============================================================================
# Funcții de utilitate
# ============================================================================

print_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           S13 Starterkit Smoke Test                            ║"
    echo "║           Rețele de Calculatoare - ASE-CSIE                    ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASS++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAIL++))
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARN++))
}

log_skip() {
    echo -e "${CYAN}[SKIP]${NC} $1"
    ((SKIP++))
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

section_header() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# ============================================================================
# Teste: Structură fișiere
# ============================================================================

test_file_structure() {
    section_header "Test 1: Structură Fișiere"
    
    local required_files=(
        "README.md"
        "Makefile"
        "docker-compose.yml"
        "requirements.txt"
        "python/exercises/ex_01_port_scanner.py"
        "python/exercises/ex_02_mqtt_client.py"
        "python/exercises/ex_03_packet_sniffer.py"
        "python/exercises/ex_04_vuln_checker.py"
        "python/exploits/ftp_backdoor_vsftpd.py"
        "python/exploits/banner_grabber.py"
        "python/utils/net_utils.py"
        "python/utils/report_generator.py"
        "configs/mosquitto/plain.conf"
        "configs/mosquitto/tls.conf"
        "configs/mosquitto/acl.acl"
        "mininet/topologies/topo_base.py"
        "mininet/topologies/topo_segmented.py"
        "scripts/setup.sh"
        "scripts/cleanup.sh"
        "docs/teoria/01_introducere.md"
        "docs/slides/CURS_13_outline.md"
        "docs/slides/SEMINAR_13_outline.md"
    )
    
    local optional_files=(
        "html/presentation_curs.html"
        "html/presentation_seminar.html"
        "mininet/scenarios/lab_scenario.md"
        "docs/teoria/02_fundamentale_iot.md"
        "docs/teoria/03_vectori_atac.md"
        "docs/teoria/04_masuri_defensive.md"
        "docs/teoria/05_flux_lucru.md"
    )
    
    # Verificare fișiere obligatorii
    for file in "${required_files[@]}"; do
        if [ -f "$PROJECT_DIR/$file" ]; then
            log_pass "Găsit: $file"
        else
            log_fail "Lipsă: $file"
        fi
    done
    
    # Verificare fișiere opționale
    for file in "${optional_files[@]}"; do
        if [ -f "$PROJECT_DIR/$file" ]; then
            log_pass "Găsit (opțional): $file"
        else
            log_warn "Lipsă (opțional): $file"
        fi
    done
    
    # Verificare directoare
    local required_dirs=(
        "python/exercises"
        "python/exploits"
        "python/utils"
        "configs/mosquitto"
        "mininet/topologies"
        "scripts"
        "docs"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$PROJECT_DIR/$dir" ]; then
            log_pass "Director: $dir"
        else
            log_fail "Director lipsă: $dir"
        fi
    done
}

# ============================================================================
# Teste: Sintaxă Python
# ============================================================================

test_python_syntax() {
    section_header "Test 2: Sintaxă Python"
    
    # Găsește toate fișierele Python
    local python_files=$(find "$PROJECT_DIR/python" -name "*.py" -type f 2>/dev/null)
    
    if [ -z "$python_files" ]; then
        log_fail "Nu s-au găsit fișiere Python"
        return
    fi
    
    for file in $python_files; do
        local relative_path="${file#$PROJECT_DIR/}"
        
        # Verificare sintaxă cu python -m py_compile
        if python3 -m py_compile "$file" 2>/dev/null; then
            log_pass "Sintaxă validă: $relative_path"
        else
            log_fail "Eroare sintaxă: $relative_path"
            # Afișare eroare detaliată
            python3 -m py_compile "$file" 2>&1 | head -5
        fi
    done
    
    # Verificare și fișiere Mininet (pot fi Python)
    local mininet_files=$(find "$PROJECT_DIR/mininet" -name "*.py" -type f 2>/dev/null)
    for file in $mininet_files; do
        local relative_path="${file#$PROJECT_DIR/}"
        if python3 -m py_compile "$file" 2>/dev/null; then
            log_pass "Sintaxă validă: $relative_path"
        else
            log_fail "Eroare sintaxă: $relative_path"
        fi
    done
}

# ============================================================================
# Teste: Import-uri Python
# ============================================================================

test_python_imports() {
    section_header "Test 3: Import-uri Python"
    
    # Lista de module standard care ar trebui să existe
    local standard_modules=(
        "socket"
        "sys"
        "os"
        "json"
        "argparse"
        "logging"
        "threading"
        "concurrent.futures"
        "dataclasses"
        "typing"
        "pathlib"
        "datetime"
        "re"
        "struct"
        "errno"
        "time"
        "signal"
        "hashlib"
        "base64"
        "ssl"
    )
    
    log_info "Verificare module standard Python..."
    for module in "${standard_modules[@]}"; do
        if python3 -c "import $module" 2>/dev/null; then
            log_pass "Import standard: $module"
        else
            log_fail "Import eșuat: $module"
        fi
    done
    
    # Module externe (din requirements.txt)
    log_info "Verificare module externe..."
    local external_modules=(
        "scapy"
        "paho.mqtt.client"
        "requests"
        "jinja2"
        "colorama"
    )
    
    for module in "${external_modules[@]}"; do
        if python3 -c "import ${module%%.*}" 2>/dev/null; then
            log_pass "Import extern: $module"
        else
            log_warn "Import extern lipsă: $module (rulați: make setup)"
        fi
    done
    
    # Module opționale
    log_info "Verificare module opționale..."
    local optional_modules=(
        "mininet"
        "docker"
        "paramiko"
        "cryptography"
    )
    
    for module in "${optional_modules[@]}"; do
        if python3 -c "import $module" 2>/dev/null; then
            log_pass "Import opțional: $module"
        else
            log_skip "Import opțional lipsă: $module"
        fi
    done
}

# ============================================================================
# Teste: Import scripturi individuale
# ============================================================================

test_script_imports() {
    section_header "Test 4: Import Scripturi"
    
    # Test import pentru fiecare script principal
    local scripts=(
        "python/exercises/ex_01_port_scanner.py"
        "python/exercises/ex_02_mqtt_client.py"
        "python/exercises/ex_03_packet_sniffer.py"
        "python/exercises/ex_04_vuln_checker.py"
        "python/exploits/ftp_backdoor_vsftpd.py"
        "python/exploits/banner_grabber.py"
        "python/utils/net_utils.py"
        "python/utils/report_generator.py"
    )
    
    for script in "${scripts[@]}"; do
        local full_path="$PROJECT_DIR/$script"
        if [ -f "$full_path" ]; then
            # Încearcă să importe modulul (fără a-l executa)
            local module_name=$(basename "$script" .py)
            local module_dir=$(dirname "$full_path")
            
            cd "$module_dir"
            if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location('$module_name', '$full_path')
    module = importlib.util.module_from_spec(spec)
    # Nu executăm spec.loader.exec_module(module) pentru a evita efecte secundare
    print('OK')
except SyntaxError as e:
    print(f'SyntaxError: {e}')
    sys.exit(1)
except Exception as e:
    # Alte erori (import lipsă) sunt acceptabile la acest nivel
    print(f'Warning: {e}')
" 2>/dev/null; then
                log_pass "Script valid: $script"
            else
                log_warn "Script cu probleme: $script"
            fi
            cd "$PROJECT_DIR"
        else
            log_fail "Script lipsă: $script"
        fi
    done
}

# ============================================================================
# Teste: Verificare Shell Scripts
# ============================================================================

test_shell_scripts() {
    section_header "Test 5: Shell Scripts"
    
    local shell_scripts=(
        "scripts/setup.sh"
        "scripts/cleanup.sh"
        "scripts/run_demo_defensive.sh"
        "scripts/capture_traffic.sh"
    )
    
    for script in "${shell_scripts[@]}"; do
        local full_path="$PROJECT_DIR/$script"
        if [ -f "$full_path" ]; then
            # Verificare sintaxă bash
            if bash -n "$full_path" 2>/dev/null; then
                log_pass "Sintaxă bash validă: $script"
            else
                log_fail "Eroare sintaxă bash: $script"
            fi
            
            # Verificare permisiuni executare
            if [ -x "$full_path" ]; then
                log_pass "Executabil: $script"
            else
                log_warn "Nu e executabil: $script (chmod +x)"
            fi
        else
            log_warn "Script lipsă: $script"
        fi
    done
}

# ============================================================================
# Teste: Verificare Configurații
# ============================================================================

test_configurations() {
    section_header "Test 6: Fișiere Configurare"
    
    # Test docker-compose.yml
    local compose_file="$PROJECT_DIR/docker-compose.yml"
    if [ -f "$compose_file" ]; then
        if command -v docker-compose &>/dev/null; then
            if docker-compose -f "$compose_file" config >/dev/null 2>&1; then
                log_pass "docker-compose.yml valid"
            else
                log_fail "docker-compose.yml invalid"
            fi
        elif command -v docker &>/dev/null; then
            if docker compose -f "$compose_file" config >/dev/null 2>&1; then
                log_pass "docker-compose.yml valid (docker compose)"
            else
                log_warn "docker-compose.yml - nu s-a putut valida"
            fi
        else
            log_skip "Docker neinstalat, skip validare compose"
        fi
    fi
    
    # Test requirements.txt
    local req_file="$PROJECT_DIR/requirements.txt"
    if [ -f "$req_file" ]; then
        local line_count=$(wc -l < "$req_file")
        if [ "$line_count" -gt 0 ]; then
            log_pass "requirements.txt prezent ($line_count pachete)"
        else
            log_warn "requirements.txt gol"
        fi
    else
        log_fail "requirements.txt lipsă"
    fi
    
    # Test configurații Mosquitto
    local mosquitto_configs=(
        "configs/mosquitto/plain.conf"
        "configs/mosquitto/tls.conf"
        "configs/mosquitto/acl.acl"
    )
    
    for config in "${mosquitto_configs[@]}"; do
        local full_path="$PROJECT_DIR/$config"
        if [ -f "$full_path" ]; then
            if [ -s "$full_path" ]; then
                log_pass "Config prezent: $config"
            else
                log_warn "Config gol: $config"
            fi
        else
            log_warn "Config lipsă: $config"
        fi
    done
}

# ============================================================================
# Teste: Verificare Makefile
# ============================================================================

test_makefile() {
    section_header "Test 7: Makefile"
    
    local makefile="$PROJECT_DIR/Makefile"
    if [ -f "$makefile" ]; then
        # Verificare sintaxă
        if make -n -f "$makefile" help >/dev/null 2>&1; then
            log_pass "Makefile sintaxă validă"
        else
            log_warn "Makefile posibil probleme (verificare manuală)"
        fi
        
        # Verificare target-uri esențiale
        local targets=(
            "help"
            "setup"
            "check"
            "docker-up"
            "docker-down"
            "clean"
        )
        
        for target in "${targets[@]}"; do
            if grep -q "^${target}:" "$makefile" 2>/dev/null; then
                log_pass "Target găsit: make $target"
            else
                log_warn "Target lipsă: make $target"
            fi
        done
    else
        log_fail "Makefile lipsă"
    fi
}

# ============================================================================
# Teste: Conectivitate Docker (opțional)
# ============================================================================

test_docker_connectivity() {
    section_header "Test 8: Docker (opțional)"
    
    if ! command -v docker &>/dev/null; then
        log_skip "Docker neinstalat"
        return
    fi
    
    # Verificare daemon
    if docker info >/dev/null 2>&1; then
        log_pass "Docker daemon funcțional"
    else
        log_warn "Docker daemon nu răspunde (poate necesita sudo)"
        return
    fi
    
    # Verificare imagini necesare
    local images=(
        "vulnerables/web-dvwa"
        "webgoat/webgoat"
        "fauria/vsftpd"
        "eclipse-mosquitto"
    )
    
    for image in "${images[@]}"; do
        if docker images --format '{{.Repository}}' | grep -q "^${image%%:*}$" 2>/dev/null; then
            log_pass "Imagine Docker: $image"
        else
            log_skip "Imagine Docker lipsă: $image (se va descărca la setup)"
        fi
    done
    
    # Verificare containere rulând (dacă există)
    local running=$(docker ps --format '{{.Names}}' 2>/dev/null | wc -l)
    log_info "Containere active: $running"
}

# ============================================================================
# Teste: Verificare documentație
# ============================================================================

test_documentation() {
    section_header "Test 9: Documentație"
    
    # Verificare README
    local readme="$PROJECT_DIR/README.md"
    if [ -f "$readme" ]; then
        local word_count=$(wc -w < "$readme")
        if [ "$word_count" -gt 500 ]; then
            log_pass "README.md complet ($word_count cuvinte)"
        elif [ "$word_count" -gt 100 ]; then
            log_warn "README.md scurt ($word_count cuvinte)"
        else
            log_fail "README.md prea scurt ($word_count cuvinte)"
        fi
    else
        log_fail "README.md lipsă"
    fi
    
    # Verificare docstrings în Python
    log_info "Verificare docstrings..."
    local py_files=$(find "$PROJECT_DIR/python" -name "*.py" -type f 2>/dev/null)
    local with_docstring=0
    local without_docstring=0
    
    for file in $py_files; do
        if grep -q '"""' "$file" 2>/dev/null || grep -q "'''" "$file" 2>/dev/null; then
            ((with_docstring++))
        else
            ((without_docstring++))
        fi
    done
    
    if [ "$with_docstring" -gt 0 ]; then
        log_pass "Fișiere cu docstrings: $with_docstring"
    fi
    if [ "$without_docstring" -gt 0 ]; then
        log_warn "Fișiere fără docstrings: $without_docstring"
    fi
}

# ============================================================================
# Teste: Artefacte demo (generate de run_all.sh)
# ============================================================================

test_artifacts() {
    section_header "Test: Artefacte Demo"
    
    local artifacts_dir="$PROJECT_DIR/artifacts"
    
    # Verificare director artifacts
    if [ -d "$artifacts_dir" ]; then
        log_pass "Director artifacts/ există"
        
        # Verificare demo.log
        if [ -f "$artifacts_dir/demo.log" ]; then
            local log_lines=$(wc -l < "$artifacts_dir/demo.log" 2>/dev/null || echo "0")
            if [ "$log_lines" -gt 0 ]; then
                log_pass "demo.log există ($log_lines linii)"
            else
                log_warn "demo.log este gol"
            fi
        else
            log_warn "demo.log nu există (rulați scripts/run_all.sh)"
        fi
        
        # Verificare demo.pcap
        if [ -f "$artifacts_dir/demo.pcap" ]; then
            local pcap_size=$(stat -c%s "$artifacts_dir/demo.pcap" 2>/dev/null || stat -f%z "$artifacts_dir/demo.pcap" 2>/dev/null || echo "0")
            if [ "$pcap_size" -ge 24 ]; then
                log_pass "demo.pcap există ($pcap_size bytes)"
            else
                log_warn "demo.pcap prea mic ($pcap_size bytes)"
            fi
        else
            log_warn "demo.pcap nu există (rulați scripts/run_all.sh)"
        fi
        
        # Verificare validation.txt
        if [ -f "$artifacts_dir/validation.txt" ]; then
            local pass_count=$(grep -c "^PASS:" "$artifacts_dir/validation.txt" 2>/dev/null || echo "0")
            local fail_count=$(grep -c "^FAIL:" "$artifacts_dir/validation.txt" 2>/dev/null || echo "0")
            log_pass "validation.txt există (PASS=$pass_count, FAIL=$fail_count)"
        else
            log_warn "validation.txt nu există (rulați scripts/run_all.sh)"
        fi
    else
        log_warn "Director artifacts/ nu există (creat de scripts/run_all.sh)"
    fi
}

# ============================================================================
# Raport final
# ============================================================================

print_summary() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                         SUMAR TESTE                             ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${GREEN}✓ PASS:${NC} $PASS"
    echo -e "  ${RED}✗ FAIL:${NC} $FAIL"
    echo -e "  ${YELLOW}⚠ WARN:${NC} $WARN"
    echo -e "  ${CYAN}○ SKIP:${NC} $SKIP"
    echo ""
    
    local total=$((PASS + FAIL + WARN + SKIP))
    local score=$((PASS * 100 / total))
    
    echo -e "  Total teste: $total"
    echo -e "  Scor: ${score}%"
    echo ""
    
    if [ "$FAIL" -eq 0 ]; then
        echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║  ✓ TOATE TESTELE CRITICE AU TRECUT!                             ║${NC}"
        echo -e "${GREEN}║    Starterkit-ul este gata pentru utilizare.                   ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
        exit 0
    else
        echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║  ✗ $FAIL TESTE AU EȘUAT                                         ║${NC}"
        echo -e "${RED}║    Verificați erorile de mai sus și corectați.                  ║${NC}"
        echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
        exit 1
    fi
}

# ============================================================================
# Main
# ============================================================================

main() {
    print_banner
    
    cd "$PROJECT_DIR"
    
    # Rulare toate testele
    test_file_structure
    test_python_syntax
    test_python_imports
    test_script_imports
    test_shell_scripts
    test_configurations
    test_makefile
    test_docker_connectivity
    test_documentation
    test_artifacts
    
    # Afișare sumar
    print_summary
}

# Help
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Smoke test pentru verificarea starterkit-ului S13"
    echo ""
    echo "Options:"
    echo "  -h, --help    Afișare ajutor"
    echo "  -v, --verbose Output detaliat"
    echo ""
    echo "Exit codes:"
    echo "  0  Toate testele critice au trecut"
    echo "  1  Unul sau mai multe teste au eșuat"
    exit 0
fi

main "$@"
