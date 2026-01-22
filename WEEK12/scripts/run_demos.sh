#!/usr/bin/env bash
# =============================================================================
# run_demos.sh — Săptămâna 12: Demonstrații Email și RPC
# =============================================================================
# Rulează toate demonstrațiile în ordine
# Utilizare: ./scripts/run_demos.sh [--email | --rpc | --all]
# =============================================================================

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Culori pentru output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configurare
SMTP_PORT=${SMTP_PORT:-1025}
JSONRPC_PORT=${JSONRPC_PORT:-8000}
XMLRPC_PORT=${XMLRPC_PORT:-8001}
DELAY=${DELAY:-2}

# Funcții helper
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_section() { echo -e "\n${CYAN}═══════════════════════════════════════════════════════════════${NC}"; echo -e "${CYAN}$1${NC}"; echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"; }

cleanup() {
    log_info "Cleaning up background processes..."
    pkill -f "smtp_server.py" 2>/dev/null || true
    pkill -f "jsonrpc_server.py" 2>/dev/null || true
    pkill -f "xmlrpc_server.py" 2>/dev/null || true
    log_success "Cleanup complete"
}

trap cleanup EXIT

wait_for_port() {
    local port=$1
    local max_wait=10
    local waited=0
    while ! nc -z localhost "$port" 2>/dev/null && [ $waited -lt $max_wait ]; do
        sleep 0.5
        waited=$((waited + 1))
    done
    if nc -z localhost "$port" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# =============================================================================
# DEMO EMAIL (SMTP)
# =============================================================================
run_email_demo() {
    log_section "DEMO 1: SMTP Email Server & Client"
    
    # Pornire server SMTP
    log_info "Starting SMTP server on port $SMTP_PORT..."
    python src/email/smtp_server.py --port "$SMTP_PORT" &
    SMTP_PID=$!
    
    if wait_for_port "$SMTP_PORT"; then
        log_success "SMTP server started (PID: $SMTP_PID)"
    else
        log_error "Failed to start SMTP server"
        return 1
    fi
    
    sleep "$DELAY"
    
    # Trimitere email test
    log_info "Sending test email..."
    python src/email/smtp_client.py \
        --server localhost \
        --port "$SMTP_PORT" \
        --from "demo@local.test" \
        --to "student@local.test" \
        --subject "Test Email from Demo" \
        --body "This is an automated test email from the Week 12 demo script.

Contents:
- SMTP protocol demonstration
- Email header structure
- Envelope vs message headers

Sent at: $(date)"
    
    log_success "Email sent successfully!"
    sleep "$DELAY"
    
    # Listare mailbox
    log_info "Listing mailbox contents..."
    python src/email/smtp_client.py --list-mailbox
    
    # Vizualizare ultimul email
    log_info "Displaying last received email..."
    python src/email/smtp_client.py --view-last
    
    # Oprire server
    log_info "Stopping SMTP server..."
    kill $SMTP_PID 2>/dev/null || true
    log_success "SMTP demo complete!"
}

# =============================================================================
# DEMO RPC (JSON-RPC)
# =============================================================================
run_jsonrpc_demo() {
    log_section "DEMO 2: JSON-RPC Server & Client"
    
    # Pornire server JSON-RPC
    log_info "Starting JSON-RPC server on port $JSONRPC_PORT..."
    python src/rpc/jsonrpc/jsonrpc_server.py --port "$JSONRPC_PORT" &
    JSONRPC_PID=$!
    
    if wait_for_port "$JSONRPC_PORT"; then
        log_success "JSON-RPC server started (PID: $JSONRPC_PID)"
    else
        log_error "Failed to start JSON-RPC server"
        return 1
    fi
    
    sleep "$DELAY"
    
    # Test individual calls
    log_info "Testing JSON-RPC methods..."
    
    echo -e "\n${YELLOW}1. Method: add(5, 3)${NC}"
    python src/rpc/jsonrpc/jsonrpc_client.py --method add --params 5 3
    
    echo -e "\n${YELLOW}2. Method: subtract(10, 4)${NC}"
    python src/rpc/jsonrpc/jsonrpc_client.py --method subtract --params 10 4
    
    echo -e "\n${YELLOW}3. Method: multiply(7, 8)${NC}"
    python src/rpc/jsonrpc/jsonrpc_client.py --method multiply --params 7 8
    
    echo -e "\n${YELLOW}4. Method: divide(20, 4)${NC}"
    python src/rpc/jsonrpc/jsonrpc_client.py --method divide --params 20 4
    
    echo -e "\n${YELLOW}5. Method: echo(\"Hello RPC\")${NC}"
    python src/rpc/jsonrpc/jsonrpc_client.py --method echo --params "Hello RPC"
    
    # Test batch request
    log_info "Testing batch request..."
    python src/rpc/jsonrpc/jsonrpc_client.py --batch '[
        {"jsonrpc":"2.0","method":"add","params":[1,2],"id":1},
        {"jsonrpc":"2.0","method":"multiply","params":[3,4],"id":2},
        {"jsonrpc":"2.0","method":"subtract","params":[10,5],"id":3}
    ]'
    
    # Test error handling
    log_info "Testing error handling..."
    echo -e "\n${YELLOW}6. Method: divide(10, 0) - Division by zero${NC}"
    python src/rpc/jsonrpc/jsonrpc_client.py --method divide --params 10 0 || true
    
    echo -e "\n${YELLOW}7. Method: unknown() - Method not found${NC}"
    python src/rpc/jsonrpc/jsonrpc_client.py --method unknown --params || true
    
    # Oprire server
    log_info "Stopping JSON-RPC server..."
    kill $JSONRPC_PID 2>/dev/null || true
    log_success "JSON-RPC demo complete!"
}

# =============================================================================
# DEMO RPC (XML-RPC)
# =============================================================================
run_xmlrpc_demo() {
    log_section "DEMO 3: XML-RPC Server & Client"
    
    # Pornire server XML-RPC
    log_info "Starting XML-RPC server on port $XMLRPC_PORT..."
    python src/rpc/xmlrpc/xmlrpc_server.py --port "$XMLRPC_PORT" &
    XMLRPC_PID=$!
    
    if wait_for_port "$XMLRPC_PORT"; then
        log_success "XML-RPC server started (PID: $XMLRPC_PID)"
    else
        log_error "Failed to start XML-RPC server"
        return 1
    fi
    
    sleep "$DELAY"
    
    # Test methods
    log_info "Testing XML-RPC methods..."
    
    echo -e "\n${YELLOW}1. Introspection: system.listMethods()${NC}"
    python src/rpc/xmlrpc/xmlrpc_client.py --introspect
    
    echo -e "\n${YELLOW}2. Method: add(15, 25)${NC}"
    python src/rpc/xmlrpc/xmlrpc_client.py --method add --params 15 25
    
    echo -e "\n${YELLOW}3. Method: multiply(6, 7)${NC}"
    python src/rpc/xmlrpc/xmlrpc_client.py --method multiply --params 6 7
    
    echo -e "\n${YELLOW}4. Method: echo(\"XML-RPC Test\")${NC}"
    python src/rpc/xmlrpc/xmlrpc_client.py --method echo --params "XML-RPC Test"
    
    # Oprire server
    log_info "Stopping XML-RPC server..."
    kill $XMLRPC_PID 2>/dev/null || true
    log_success "XML-RPC demo complete!"
}

# =============================================================================
# DEMO COMPARISON
# =============================================================================
run_comparison_demo() {
    log_section "DEMO 4: Protocol Comparison"
    
    # Pornire ambele servere
    log_info "Starting both RPC servers..."
    python src/rpc/jsonrpc/jsonrpc_server.py --port "$JSONRPC_PORT" &
    JSONRPC_PID=$!
    python src/rpc/xmlrpc/xmlrpc_server.py --port "$XMLRPC_PORT" &
    XMLRPC_PID=$!
    
    wait_for_port "$JSONRPC_PORT"
    wait_for_port "$XMLRPC_PORT"
    sleep "$DELAY"
    
    # Comparație simplă
    log_info "Comparing response sizes and formats..."
    
    echo -e "\n${YELLOW}JSON-RPC Request/Response:${NC}"
    echo "Request:  {\"jsonrpc\":\"2.0\",\"method\":\"add\",\"params\":[100,200],\"id\":1}"
    JSONRPC_RESP=$(curl -s -X POST -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"add","params":[100,200],"id":1}' \
        http://localhost:$JSONRPC_PORT/)
    echo "Response: $JSONRPC_RESP"
    echo "Size: $(echo "$JSONRPC_RESP" | wc -c) bytes"
    
    echo -e "\n${YELLOW}XML-RPC Request/Response:${NC}"
    XMLRPC_REQ='<?xml version="1.0"?><methodCall><methodName>add</methodName><params><param><value><int>100</int></value></param><param><value><int>200</int></value></param></params></methodCall>'
    echo "Request:  (XML format, $(echo "$XMLRPC_REQ" | wc -c) bytes)"
    XMLRPC_RESP=$(curl -s -X POST -H "Content-Type: text/xml" \
        -d "$XMLRPC_REQ" \
        http://localhost:$XMLRPC_PORT/)
    echo "Response: (XML format)"
    echo "Size: $(echo "$XMLRPC_RESP" | wc -c) bytes"
    
    echo -e "\n${GREEN}Summary:${NC}"
    echo "- JSON-RPC: More compact, human-readable JSON"
    echo "- XML-RPC: More verbose, structured XML"
    echo "- For detailed benchmark, run: make benchmark-rpc"
    
    # Cleanup
    kill $JSONRPC_PID $XMLRPC_PID 2>/dev/null || true
    log_success "Comparison demo complete!"
}

# =============================================================================
# MAIN
# =============================================================================
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

OPTIONS:
    --email     Run only email (SMTP) demo
    --jsonrpc   Run only JSON-RPC demo
    --xmlrpc    Run only XML-RPC demo
    --compare   Run protocol comparison demo
    --all       Run all demos (default)
    --help      Show this help message

ENVIRONMENT VARIABLES:
    SMTP_PORT     SMTP server port (default: 1025)
    JSONRPC_PORT  JSON-RPC server port (default: 8000)
    XMLRPC_PORT   XML-RPC server port (default: 8001)
    DELAY         Delay between demo steps in seconds (default: 2)

EXAMPLES:
    $0                    # Run all demos
    $0 --email            # Run only SMTP demo
    $0 --jsonrpc --xmlrpc # Run both RPC demos
    DELAY=1 $0 --all      # Run faster with 1s delay

EOF
}

main() {
    local run_email=false
    local run_jsonrpc=false
    local run_xmlrpc=false
    local run_compare=false
    
    # Parse arguments
    if [ $# -eq 0 ]; then
        run_email=true
        run_jsonrpc=true
        run_xmlrpc=true
        run_compare=true
    else
        while [ $# -gt 0 ]; do
            case "$1" in
                --email)     run_email=true ;;
                --jsonrpc)   run_jsonrpc=true ;;
                --xmlrpc)    run_xmlrpc=true ;;
                --compare)   run_compare=true ;;
                --all)
                    run_email=true
                    run_jsonrpc=true
                    run_xmlrpc=true
                    run_compare=true
                    ;;
                --help|-h)
                    show_usage
                    exit 0
                    ;;
                *)
                    log_error "Unknown option: $1"
                    show_usage
                    exit 1
                    ;;
            esac
            shift
        done
    fi
    
    log_section "SĂPTĂMÂNA 12: DEMO-URI EMAIL ȘI RPC"
    log_info "Starting demonstrations..."
    log_info "Project root: $PROJECT_ROOT"
    
    # Run selected demos
    if $run_email; then
        run_email_demo
    fi
    
    if $run_jsonrpc; then
        run_jsonrpc_demo
    fi
    
    if $run_xmlrpc; then
        run_xmlrpc_demo
    fi
    
    if $run_compare; then
        run_comparison_demo
    fi
    
    log_section "ALL DEMOS COMPLETE"
    log_success "All requested demonstrations finished successfully!"
    echo ""
    log_info "Next steps:"
    echo "  1. Review the captured output above"
    echo "  2. Try modifying parameters and re-running"
    echo "  3. Use tshark to capture traffic: make capture"
    echo "  4. Run benchmark: make benchmark-rpc"
    echo "  5. Complete exercises in exercises/ directory"
}

main "$@"
