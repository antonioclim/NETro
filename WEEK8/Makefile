# ═══════════════════════════════════════════════════════════════════════════════
# Makefile - Rețele de Calculatoare - Săptămâna 8
# Nivelul Transport (TCP/UDP/TLS) + Server HTTP + Reverse Proxy
# ═══════════════════════════════════════════════════════════════════════════════
#
# Utilizare rapidă:
#   make help              - Afișează toate comenzile disponibile
#   make setup             - Instalează dependențele necesare
#   make run-demo          - Rulează demo-ul principal
#   make run-lab           - Pornește laboratorul interactiv
#   make capture           - Captură pachete pentru analiză
#   make verify            - Verifică că mediul e OK
#   make clean             - Curățare fișiere temporare
#   make reset             - Reset complet
#
# Autor: Rețele de Calculatoare, ASE București, 2025
# Revolvix&Hypotheticalandrei
# ═══════════════════════════════════════════════════════════════════════════════

# Configurație
PYTHON     := python3
SHELL      := /bin/bash
.SHELLFLAGS := -o pipefail -c

# Porturi (conform standard WEEK=8)
HTTP_PORT       := 8080
BACKEND_PORT_A  := 9001
BACKEND_PORT_B  := 9002
PROXY_PORT      := 8888
WEEK_PORT_BASE  := 5800

# Directoare
SRC_DIR    := python
DEMO_DIR   := $(SRC_DIR)/demos
EXER_DIR   := $(SRC_DIR)/exercises
SCEN_DIR   := scenarios
DOCS_DIR   := docs
OUT_DIR    := output
WWW_DIR    := www
PCAP_DIR   := pcap

# Culori pentru output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
BLUE   := \033[0;34m
RED    := \033[0;31m
CYAN   := \033[0;36m
MAGENTA := \033[0;35m
BOLD   := \033[1m
NC     := \033[0m

# ═══════════════════════════════════════════════════════════════════════════════
# Target principal: help
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: help
help:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)$(BOLD)  Rețele de Calculatoare - Săptămâna 8$(NC)"
	@echo "$(BLUE)  Transport Layer (TCP/UDP/TLS) + HTTP Server + Reverse Proxy$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(GREEN)$(BOLD)🔧 Configurare:$(NC)"
	@echo "  make setup              - Instalează dependențele sistem"
	@echo "  make verify             - Verifică dacă totul e instalat corect"
	@echo ""
	@echo "$(GREEN)$(BOLD)🚀 Demo-uri (server + client):$(NC)"
	@echo "  make run-all            - Demo automat complet + artefacte"
	@echo "  make run-all-quick      - Demo automat (fără captură pcap)"
	@echo "  make run-demo           - Demo complet HTTP server + proxy"
	@echo "  make demo-http          - Demo server HTTP simplu"
	@echo "  make demo-proxy         - Demo reverse proxy cu 2 backends"
	@echo ""
	@echo "$(GREEN)$(BOLD)🔬 Laborator:$(NC)"
	@echo "  make run-lab            - Pornește mediul de laborator"
	@echo "  make http-server        - Pornește HTTP server pe port $(HTTP_PORT)"
	@echo "  make proxy-server       - Pornește reverse proxy"
	@echo "  make backend-a          - Pornește backend A pe port $(BACKEND_PORT_A)"
	@echo "  make backend-b          - Pornește backend B pe port $(BACKEND_PORT_B)"
	@echo ""
	@echo "$(GREEN)$(BOLD)📡 Capturi și analiză:$(NC)"
	@echo "  make capture            - Captură trafic HTTP complet"
	@echo "  make capture-handshake  - Captură TCP three-way handshake"
	@echo "  make capture-proxy      - Captură trafic client→proxy→backend"
	@echo "  make analyze            - Analizează ultima captură"
	@echo ""
	@echo "$(GREEN)$(BOLD)🐳 Docker:$(NC)"
	@echo "  make docker-build       - Construiește imaginea Docker"
	@echo "  make docker-up          - Pornește stack-ul complet"
	@echo "  make docker-down        - Oprește stack-ul"
	@echo "  make docker-logs        - Afișează log-uri"
	@echo ""
	@echo "$(GREEN)$(BOLD)📝 Teste:$(NC)"
	@echo "  make test-ex1           - Testează exercițiul 1 (HTTP server)"
	@echo "  make test-ex2           - Testează exercițiul 2 (Reverse proxy)"
	@echo "  make test-all           - Testează toate exercițiile"
	@echo "  make smoke-test         - Test rapid de funcționalitate"
	@echo ""
	@echo "$(GREEN)$(BOLD)🧹 Curățare:$(NC)"
	@echo "  make clean              - Șterge fișierele temporare"
	@echo "  make reset              - Reset complet (include capturi)"
	@echo "  make kill-servers       - Oprește toate serverele active"
	@echo ""
	@echo "$(YELLOW)Notă: Unele comenzi necesită permisiuni sudo (tcpdump).$(NC)"
	@echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Setup și verificare
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: setup
setup:
	@echo "$(BLUE)[setup]$(NC) Instalare dependențe sistem..."
	@./scripts/setup.sh
	@echo "$(GREEN)[setup]$(NC) Finalizat!"

.PHONY: verify
verify:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Verificare Mediu de Lucru$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(CYAN)Esențiale:$(NC)"
	@echo -n "  Python 3:     " && ($(PYTHON) --version 2>/dev/null && echo "$(GREEN)✓$(NC)") || echo "$(RED)✗ LIPSĂ$(NC)"
	@echo -n "  curl:         " && (which curl > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(RED)✗ LIPSĂ$(NC)"
	@echo -n "  netcat:       " && (which nc > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(RED)✗ LIPSĂ$(NC)"
	@echo ""
	@echo "$(CYAN)Analiză trafic:$(NC)"
	@echo -n "  tcpdump:      " && (which tcpdump > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(YELLOW)○ opțional$(NC)"
	@echo -n "  tshark:       " && (which tshark > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(YELLOW)○ opțional$(NC)"
	@echo -n "  wireshark:    " && (which wireshark > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(YELLOW)○ opțional$(NC)"
	@echo ""
	@echo "$(CYAN)Infrastructură:$(NC)"
	@echo -n "  docker:       " && (which docker > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(YELLOW)○ opțional$(NC)"
	@echo -n "  nginx:        " && (which nginx > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(YELLOW)○ opțional$(NC)"
	@echo -n "  mininet:      " && (which mn > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(YELLOW)○ opțional$(NC)"
	@echo ""
	@echo "$(CYAN)Verificare fișiere kit:$(NC)"
	@test -f $(DEMO_DIR)/demo_http_server.py && echo "  demo_http_server.py:    $(GREEN)✓$(NC)" || echo "  demo_http_server.py:    $(RED)✗$(NC)"
	@test -f $(DEMO_DIR)/demo_reverse_proxy.py && echo "  demo_reverse_proxy.py:  $(GREEN)✓$(NC)" || echo "  demo_reverse_proxy.py:  $(RED)✗$(NC)"
	@test -d $(WWW_DIR) && echo "  www/:                   $(GREEN)✓$(NC)" || echo "  www/:                   $(RED)✗$(NC)"
	@echo ""
	@echo "$(GREEN)[verify]$(NC) Verificare completă!"

# ═══════════════════════════════════════════════════════════════════════════════
# Creare directoare
# ═══════════════════════════════════════════════════════════════════════════════
$(OUT_DIR):
	@mkdir -p $(OUT_DIR)

$(PCAP_DIR):
	@mkdir -p $(PCAP_DIR)

# ═══════════════════════════════════════════════════════════════════════════════
# Demo-uri complete
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: run-all
run-all:
	@echo "$(BLUE)[run-all]$(NC) Rulare demo automat complet..."
	@./scripts/run_all.sh

.PHONY: run-all-quick
run-all-quick:
	@echo "$(BLUE)[run-all]$(NC) Rulare demo automat (fără captură)..."
	@./scripts/run_all.sh --quick

.PHONY: run-demo
run-demo: demo-http demo-proxy
	@echo ""
	@echo "$(GREEN)Toate demo-urile finalizate cu succes!$(NC)"

.PHONY: demo-http
demo-http: $(OUT_DIR)
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)$(BOLD)  Demo: Server HTTP Minimal (Socket)$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)[1/5]$(NC) Pornire server HTTP pe portul $(HTTP_PORT)..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 127.0.0.1 --port $(HTTP_PORT) --www $(WWW_DIR) --id demo &
	@sleep 1
	@echo ""
	@echo "$(YELLOW)[2/5]$(NC) Test: GET / (index.html)"
	@curl -s http://127.0.0.1:$(HTTP_PORT)/ | head -5
	@echo ""
	@echo "$(YELLOW)[3/5]$(NC) Test: Headers response"
	@curl -s -D - http://127.0.0.1:$(HTTP_PORT)/ -o /dev/null | head -8
	@echo ""
	@echo "$(YELLOW)[4/5]$(NC) Test: GET /not-found (→ 404)"
	@curl -s -D - http://127.0.0.1:$(HTTP_PORT)/not-found -o /dev/null | head -1
	@echo ""
	@echo "$(YELLOW)[5/5]$(NC) Oprire server..."
	@-pkill -f "demo_http_server.py.*$(HTTP_PORT)" 2>/dev/null || true
	@sleep 0.5
	@echo ""
	@echo "$(GREEN)Demo HTTP finalizat cu succes!$(NC)"

.PHONY: demo-proxy
demo-proxy: $(OUT_DIR)
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)$(BOLD)  Demo: Reverse Proxy cu Round-Robin$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)[1/6]$(NC) Pornire Backend A pe portul $(BACKEND_PORT_A)..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 127.0.0.1 --port $(BACKEND_PORT_A) --www $(WWW_DIR) --id backend-A &
	@sleep 0.5
	@echo ""
	@echo "$(YELLOW)[2/6]$(NC) Pornire Backend B pe portul $(BACKEND_PORT_B)..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 127.0.0.1 --port $(BACKEND_PORT_B) --www $(WWW_DIR) --id backend-B &
	@sleep 0.5
	@echo ""
	@echo "$(YELLOW)[3/6]$(NC) Pornire Reverse Proxy pe portul $(PROXY_PORT)..."
	@$(PYTHON) $(DEMO_DIR)/demo_reverse_proxy.py --listen-port $(PROXY_PORT) \
		--backends 127.0.0.1:$(BACKEND_PORT_A),127.0.0.1:$(BACKEND_PORT_B) &
	@sleep 1
	@echo ""
	@echo "$(YELLOW)[4/6]$(NC) Test: 6 requests prin proxy (observă alternarea)"
	@echo "$(CYAN)───────────────────────────────────────────────────────────────────────$(NC)"
	@for i in 1 2 3 4 5 6; do \
		echo -n "  Request $$i: "; \
		curl -s http://127.0.0.1:$(PROXY_PORT)/ -D - -o /dev/null 2>/dev/null | grep -E "X-Served-By|X-Backend" | head -1; \
	done
	@echo "$(CYAN)───────────────────────────────────────────────────────────────────────$(NC)"
	@echo ""
	@echo "$(YELLOW)[5/6]$(NC) Oprire toate serverele..."
	@-pkill -f "demo_reverse_proxy.py" 2>/dev/null || true
	@-pkill -f "demo_http_server.py.*$(BACKEND_PORT_A)" 2>/dev/null || true
	@-pkill -f "demo_http_server.py.*$(BACKEND_PORT_B)" 2>/dev/null || true
	@sleep 0.5
	@echo ""
	@echo "$(GREEN)Demo Reverse Proxy finalizat cu succes!$(NC)"
	@echo "$(MAGENTA)Observă: Backend-urile alternează (A, B, A, B...) - Round-Robin!$(NC)"

# ═══════════════════════════════════════════════════════════════════════════════
# Servere individuale
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: http-server
http-server:
	@echo "$(BLUE)[http-server]$(NC) Pornire server HTTP pe port $(HTTP_PORT)..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 0.0.0.0 --port $(HTTP_PORT) --www $(WWW_DIR)

.PHONY: proxy-server
proxy-server:
	@echo "$(BLUE)[proxy]$(NC) Pornire reverse proxy pe port $(PROXY_PORT)..."
	@$(PYTHON) $(DEMO_DIR)/demo_reverse_proxy.py --listen-port $(PROXY_PORT) \
		--backends 127.0.0.1:$(BACKEND_PORT_A),127.0.0.1:$(BACKEND_PORT_B)

.PHONY: backend-a
backend-a:
	@echo "$(BLUE)[backend-a]$(NC) Pornire Backend A pe port $(BACKEND_PORT_A)..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 127.0.0.1 --port $(BACKEND_PORT_A) --www $(WWW_DIR) --id backend-A

.PHONY: backend-b
backend-b:
	@echo "$(BLUE)[backend-b]$(NC) Pornire Backend B pe port $(BACKEND_PORT_B)..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 127.0.0.1 --port $(BACKEND_PORT_B) --www $(WWW_DIR) --id backend-B

# ═══════════════════════════════════════════════════════════════════════════════
# Laborator interactiv
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: run-lab
run-lab:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)$(BOLD)  Laborator Interactiv - Săptămâna 8$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(CYAN)Pași recomandați:$(NC)"
	@echo ""
	@echo "  1. Deschide 4 terminale"
	@echo ""
	@echo "  2. Terminal 1 - Backend A:"
	@echo "     $(GREEN)make backend-a$(NC)"
	@echo ""
	@echo "  3. Terminal 2 - Backend B:"
	@echo "     $(GREEN)make backend-b$(NC)"
	@echo ""
	@echo "  4. Terminal 3 - Reverse Proxy:"
	@echo "     $(GREEN)make proxy-server$(NC)"
	@echo ""
	@echo "  5. Terminal 4 - Client (teste):"
	@echo "     $(GREEN)curl -v http://localhost:8080/$(NC)"
	@echo "     $(GREEN)for i in {1..6}; do curl -s localhost:8080/ -D - | grep X-Served-By; done$(NC)"
	@echo ""
	@echo "$(YELLOW)Pentru captură tcpdump:$(NC)"
	@echo "     $(GREEN)sudo tcpdump -i lo 'port 8080 or port 9001 or port 9002' -nn -A$(NC)"
	@echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Capturi de pachete
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: capture
capture: capture-handshake
	@echo "$(GREEN)Captură completată!$(NC)"

.PHONY: capture-handshake
capture-handshake: $(PCAP_DIR)
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)$(BOLD)  Captură: TCP Three-Way Handshake$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)[1/5]$(NC) Pornire server..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 127.0.0.1 --port $(HTTP_PORT) --www $(WWW_DIR) &
	@sleep 1
	@echo ""
	@echo "$(YELLOW)[2/5]$(NC) Pornire captură tcpdump..."
	@sudo tcpdump -i lo port $(HTTP_PORT) -nn -c 20 -w $(PCAP_DIR)/handshake.pcap 2>/dev/null &
	@sleep 1
	@echo ""
	@echo "$(YELLOW)[3/5]$(NC) Generare trafic (curl)..."
	@curl -s http://127.0.0.1:$(HTTP_PORT)/ > /dev/null 2>&1 || true
	@sleep 2
	@echo ""
	@echo "$(YELLOW)[4/5]$(NC) Oprire captură și server..."
	@-sudo pkill -f "tcpdump.*$(HTTP_PORT)" 2>/dev/null || true
	@-pkill -f "demo_http_server.py.*$(HTTP_PORT)" 2>/dev/null || true
	@sleep 1
	@echo ""
	@echo "$(YELLOW)[5/5]$(NC) Analiză handshake:"
	@echo "$(CYAN)───────────────────────────────────────────────────────────────────────$(NC)"
	@-sudo tcpdump -r $(PCAP_DIR)/handshake.pcap -nn 2>/dev/null | head -20 || echo "  (necesită permisiuni sudo pentru citire)"
	@echo "$(CYAN)───────────────────────────────────────────────────────────────────────$(NC)"
	@echo ""
	@echo "$(GREEN)Flag-uri TCP:$(NC)"
	@echo "  [S]    = SYN (inițiere conexiune)"
	@echo "  [S.]   = SYN-ACK (confirmare + acceptare)"
	@echo "  [.]    = ACK (confirmare)"
	@echo "  [P.]   = PSH-ACK (date + confirmare)"
	@echo "  [F.]   = FIN-ACK (închidere)"
	@echo ""
	@echo "$(MAGENTA)Captură salvată în: $(PCAP_DIR)/handshake.pcap$(NC)"

.PHONY: capture-proxy
capture-proxy: $(PCAP_DIR)
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)$(BOLD)  Captură: Client → Proxy → Backend$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)[1/6]$(NC) Pornire backend..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 127.0.0.1 --port $(BACKEND_PORT_A) --www $(WWW_DIR) --id backend &
	@sleep 0.5
	@echo ""
	@echo "$(YELLOW)[2/6]$(NC) Pornire proxy..."
	@$(PYTHON) $(DEMO_DIR)/demo_reverse_proxy.py --listen-port $(PROXY_PORT) --backends 127.0.0.1:$(BACKEND_PORT_A) &
	@sleep 0.5
	@echo ""
	@echo "$(YELLOW)[3/6]$(NC) Pornire captură..."
	@sudo tcpdump -i lo '(port $(PROXY_PORT) or port $(BACKEND_PORT_A))' -nn -w $(PCAP_DIR)/proxy_capture.pcap -c 40 2>/dev/null &
	@sleep 1
	@echo ""
	@echo "$(YELLOW)[4/6]$(NC) Generare trafic..."
	@curl -s http://127.0.0.1:$(PROXY_PORT)/ > /dev/null
	@sleep 2
	@echo ""
	@echo "$(YELLOW)[5/6]$(NC) Oprire procese..."
	@-sudo pkill -f "tcpdump.*$(PROXY_PORT)" 2>/dev/null || true
	@-pkill -f "demo_reverse_proxy.py" 2>/dev/null || true
	@-pkill -f "demo_http_server.py.*$(BACKEND_PORT_A)" 2>/dev/null || true
	@sleep 1
	@echo ""
	@echo "$(YELLOW)[6/6]$(NC) Analiză:"
	@echo "$(CYAN)───────────────────────────────────────────────────────────────────────$(NC)"
	@-sudo tcpdump -r $(PCAP_DIR)/proxy_capture.pcap -nn 2>/dev/null | head -30 || echo "  (necesită sudo)"
	@echo "$(CYAN)───────────────────────────────────────────────────────────────────────$(NC)"
	@echo ""
	@echo "$(GREEN)Observă cele 2 conexiuni TCP:$(NC)"
	@echo "  - Client (port efemer) → Proxy ($(PROXY_PORT))"
	@echo "  - Proxy (port efemer) → Backend ($(BACKEND_PORT_A))"

.PHONY: analyze
analyze:
	@echo "$(BLUE)[analyze]$(NC) Analiză capturi existente..."
	@ls -la $(PCAP_DIR)/*.pcap 2>/dev/null || echo "  Nu există capturi. Rulează: make capture"

# ═══════════════════════════════════════════════════════════════════════════════
# Docker
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: docker-build
docker-build:
	@echo "$(BLUE)[docker]$(NC) Construire imagine..."
	@docker build -t retele-s8 -f docker/Dockerfile .
	@echo "$(GREEN)[docker]$(NC) Imagine construită: retele-s8"

.PHONY: docker-up
docker-up:
	@echo "$(BLUE)[docker]$(NC) Pornire stack..."
	@cd docker && docker-compose up -d
	@echo "$(GREEN)[docker]$(NC) Stack pornit!"
	@echo "  - Nginx: http://localhost:80"
	@echo "  - Backend A: http://localhost:$(BACKEND_PORT_A)"
	@echo "  - Backend B: http://localhost:$(BACKEND_PORT_B)"

.PHONY: docker-down
docker-down:
	@echo "$(BLUE)[docker]$(NC) Oprire stack..."
	@cd docker && docker-compose down
	@echo "$(GREEN)[docker]$(NC) Stack oprit"

.PHONY: docker-logs
docker-logs:
	@cd docker && docker-compose logs -f

# ═══════════════════════════════════════════════════════════════════════════════
# Testare
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: test-ex1
test-ex1:
	@echo "$(BLUE)[test]$(NC) Testare Exercițiu 1 - HTTP Server"
	@$(PYTHON) $(EXER_DIR)/ex_01_http_server.py --selftest 2>/dev/null || echo "$(YELLOW)TODO: Completează exercițiul$(NC)"

.PHONY: test-ex2
test-ex2:
	@echo "$(BLUE)[test]$(NC) Testare Exercițiu 2 - Reverse Proxy"
	@$(PYTHON) $(EXER_DIR)/ex_02_reverse_proxy.py --selftest 2>/dev/null || echo "$(YELLOW)TODO: Completează exercițiul$(NC)"

.PHONY: test-all
test-all: test-ex1 test-ex2
	@echo "$(GREEN)Toate testele rulate!$(NC)"

.PHONY: smoke-test
smoke-test:
	@echo "$(BLUE)[test]$(NC) Smoke test..."
	@./tests/smoke_test.sh

# ═══════════════════════════════════════════════════════════════════════════════
# Curățare
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: clean
clean:
	@echo "$(BLUE)[clean]$(NC) Curățare fișiere temporare..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@rm -f *.log
	@echo "$(GREEN)[clean]$(NC) Fișiere temporare șterse"

.PHONY: reset
reset: clean kill-servers
	@echo "$(BLUE)[reset]$(NC) Reset complet..."
	@rm -rf $(OUT_DIR)
	@rm -f $(PCAP_DIR)/*.pcap
	@echo "$(GREEN)[reset]$(NC) Reset complet efectuat"

.PHONY: kill-servers
kill-servers:
	@echo "$(BLUE)[kill]$(NC) Oprire servere..."
	@-pkill -f "demo_http_server.py" 2>/dev/null || true
	@-pkill -f "demo_reverse_proxy.py" 2>/dev/null || true
	@-pkill -f "ex_01_http_server.py" 2>/dev/null || true
	@-pkill -f "ex_02_reverse_proxy.py" 2>/dev/null || true
	@-sudo pkill -f "tcpdump" 2>/dev/null || true
	@echo "$(GREEN)[kill]$(NC) Servere oprite"

# ═══════════════════════════════════════════════════════════════════════════════
# Default
# ═══════════════════════════════════════════════════════════════════════════════
.DEFAULT_GOAL := help
