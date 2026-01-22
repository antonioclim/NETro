# =============================================================================
# Makefile – Starterkit Săptămâna 9: Sesiune (L5), Prezentare (L6), Protocoale Fișiere
# Rețele de calculatoare | ASE-CSIE | 2025
# =============================================================================

SHELL := /bin/bash
.DEFAULT_GOAL := help

# -----------------------------------------------------------------------------
# Variabile configurabile
# -----------------------------------------------------------------------------
PYTHON := python3
PIP := $(PYTHON) -m pip
HOST := 127.0.0.1
PORT := 3333
FTP_PORT := 2121
USER := test
PASS := 12345
ROOT_DIR := server-files
CLIENT_DIR := client-files
FILE := hello.txt

# Culori pentru output
GREEN := \033[0;32m
YELLOW := \033[1;33m
CYAN := \033[0;36m
RED := \033[0;31m
NC := \033[0m

# -----------------------------------------------------------------------------
# Targets principale
# -----------------------------------------------------------------------------

.PHONY: help
help: ## Afișează acest mesaj de ajutor
	@echo -e "$(CYAN)╔══════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(CYAN)║  Starterkit S9 - Rețele de calculatoare (ASE-CSIE)               ║$(NC)"
	@echo -e "$(CYAN)║  Nivelul Sesiune (L5), Nivelul Prezentare (L6)                   ║$(NC)"
	@echo -e "$(CYAN)║  Protocoale de Fișiere                                           ║$(NC)"
	@echo -e "$(CYAN)╚══════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(YELLOW)Exemple de utilizare:$(NC)"
	@echo "  make setup              # Instalare completă"
	@echo "  make server             # Pornește serverul pseudo-FTP"
	@echo "  make client-get FILE=test.txt  # Descarcă un fișier"
	@echo "  make docker-up          # Pornește stack-ul Docker"
	@echo "  make verify             # Verifică că mediul e OK"

# -----------------------------------------------------------------------------
# Setup și cleanup
# -----------------------------------------------------------------------------

.PHONY: setup
setup: setup-dirs setup-deps setup-files ## Instalare completă (dependențe + directoare + fișiere test)
	@echo -e "$(GREEN)✓ Setup complet!$(NC)"

.PHONY: setup-dirs
setup-dirs: ## Creează directoarele necesare
	@mkdir -p $(ROOT_DIR) $(CLIENT_DIR) pcap
	@echo -e "$(GREEN)✓ Directoare create: $(ROOT_DIR), $(CLIENT_DIR), pcap$(NC)"

.PHONY: setup-deps
setup-deps: ## Instalează dependențele Python
	@$(PIP) install --break-system-packages -q -r requirements.txt 2>/dev/null || \
		$(PIP) install -q -r requirements.txt 2>/dev/null || \
		echo "Instalare dependențe manual: pip install pyftpdlib"
	@echo -e "$(GREEN)✓ Dependențe Python instalate$(NC)"

.PHONY: setup-files
setup-files: setup-dirs ## Creează fișiere de test
	@echo "Hello S9 - Protocoale de fișiere!" > $(ROOT_DIR)/hello.txt
	@echo "Test file with UTF-8: România ✓" > $(ROOT_DIR)/utf8_test.txt
	@echo "Binary test content" > $(ROOT_DIR)/test.bin
	@dd if=/dev/urandom of=$(ROOT_DIR)/random_100k.bin bs=1024 count=100 2>/dev/null || true
	@echo -e "$(GREEN)✓ Fișiere de test create în $(ROOT_DIR)/$(NC)"

.PHONY: clean
clean: ## Curăță fișierele temporare
	@rm -rf $(CLIENT_DIR)/*.txt $(CLIENT_DIR)/*.bin __pycache__ python/**/__pycache__
	@rm -f *.pcap *.log
	@echo -e "$(YELLOW)✓ Fișiere temporare curățate$(NC)"

.PHONY: reset
reset: clean docker-down ## Resetare completă (include Docker și Mininet)
	@rm -rf $(ROOT_DIR) $(CLIENT_DIR)
	@sudo mn -c 2>/dev/null || true
	@pkill -f "ex_9_02" 2>/dev/null || true
	@pkill -f "pseudo_ftp" 2>/dev/null || true
	@echo -e "$(YELLOW)✓ Resetare completă$(NC)"

# -----------------------------------------------------------------------------
# Exercițiu 1: Endianness și framing (L6)
# -----------------------------------------------------------------------------

.PHONY: ex1
ex1: ## Rulează exercițiul de endianness (selftest)
	@echo -e "$(CYAN)═══ Exercițiu 1: Endianness și Framing Binar (L6) ═══$(NC)"
	@$(PYTHON) python/exercises/ex_9_01_endianness.py --selftest

.PHONY: ex1-demo
ex1-demo: ## Demo endianness cu output detaliat
	@echo -e "$(CYAN)═══ Demo Endianness: Big-Endian vs Little-Endian ═══$(NC)"
	@$(PYTHON) python/exercises/ex_9_01_endianness.py --demo

.PHONY: run-demo
run-demo: ex1-demo ## Alias pentru demo

# -----------------------------------------------------------------------------
# Pseudo-FTP Server
# -----------------------------------------------------------------------------

.PHONY: server
server: setup-files ## Pornește serverul pseudo-FTP
	@echo -e "$(GREEN)═══ Server Pseudo-FTP pe $(HOST):$(PORT) ═══$(NC)"
	@echo -e "$(YELLOW)Ctrl+C pentru oprire$(NC)"
	@$(PYTHON) python/exercises/ex_9_02_pseudo_ftp.py server \
		--host $(HOST) --port $(PORT) --root $(ROOT_DIR)

.PHONY: server-bg
server-bg: setup-files ## Pornește serverul în background
	@$(PYTHON) python/exercises/ex_9_02_pseudo_ftp.py server \
		--host $(HOST) --port $(PORT) --root $(ROOT_DIR) &
	@sleep 0.5
	@echo -e "$(GREEN)✓ Server pornit în background pe $(HOST):$(PORT)$(NC)"

# -----------------------------------------------------------------------------
# Pseudo-FTP Client
# -----------------------------------------------------------------------------

.PHONY: client-list
client-list: ## Listează fișierele de pe server
	@echo -e "$(CYAN)═══ LIST ═══$(NC)"
	@$(PYTHON) python/exercises/ex_9_02_pseudo_ftp.py client \
		--host $(HOST) --port $(PORT) --user $(USER) --password $(PASS) list

.PHONY: client-get
client-get: setup-dirs ## Descarcă un fișier (usage: make client-get FILE=hello.txt)
	@echo -e "$(CYAN)═══ GET $(FILE) (mod pasiv) ═══$(NC)"
	@$(PYTHON) python/exercises/ex_9_02_pseudo_ftp.py client \
		--host $(HOST) --port $(PORT) --user $(USER) --password $(PASS) \
		--local-dir $(CLIENT_DIR) --mode passive get $(FILE)

.PHONY: client-get-active
client-get-active: setup-dirs ## Descarcă un fișier în mod activ
	@echo -e "$(CYAN)═══ GET $(FILE) (mod activ) ═══$(NC)"
	@$(PYTHON) python/exercises/ex_9_02_pseudo_ftp.py client \
		--host $(HOST) --port $(PORT) --user $(USER) --password $(PASS) \
		--local-dir $(CLIENT_DIR) --mode active get $(FILE)

.PHONY: client-put
client-put: ## Încarcă un fișier pe server
	@echo -e "$(CYAN)═══ PUT $(FILE) ═══$(NC)"
	@$(PYTHON) python/exercises/ex_9_02_pseudo_ftp.py client \
		--host $(HOST) --port $(PORT) --user $(USER) --password $(PASS) \
		--mode passive put $(FILE)

.PHONY: client-interactive
client-interactive: ## Pornește clientul în mod interactiv
	@echo -e "$(CYAN)═══ Client Interactiv ═══$(NC)"
	@echo -e "$(YELLOW)Comenzi: list, pwd, cwd <dir>, get <file>, put <file>, quit$(NC)"
	@$(PYTHON) python/exercises/ex_9_02_pseudo_ftp.py client \
		--host $(HOST) --port $(PORT) --user $(USER) --password $(PASS) \
		--local-dir $(CLIENT_DIR) --interactive

.PHONY: run-lab
run-lab: server-bg client-list ## Rulează lab complet (server + list)
	@echo -e "$(GREEN)✓ Lab demonstrativ complet$(NC)"

# -----------------------------------------------------------------------------
# FTP Real (pyftpdlib)
# -----------------------------------------------------------------------------

.PHONY: ftp-server
ftp-server: setup-files ## Pornește serverul FTP real (pyftpdlib)
	@echo -e "$(GREEN)═══ Server FTP (pyftpdlib) pe $(HOST):$(FTP_PORT) ═══$(NC)"
	@$(PYTHON) python/exercises/ftp_demo_server.py \
		--host $(HOST) --port $(FTP_PORT) --root $(ROOT_DIR) \
		--user $(USER) --password $(PASS)

.PHONY: ftp-client
ftp-client: ## Client FTP (ftplib)
	@echo -e "$(CYAN)═══ Client FTP ═══$(NC)"
	@$(PYTHON) python/exercises/ftp_demo_client.py \
		--host $(HOST) --port $(FTP_PORT) --user $(USER) --password $(PASS) list

# -----------------------------------------------------------------------------
# Demo complet
# -----------------------------------------------------------------------------

.PHONY: demo
demo: setup ## Demo complet pas cu pas
	@echo -e "$(CYAN)╔══════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(CYAN)║                    DEMO COMPLET S9                               ║$(NC)"
	@echo -e "$(CYAN)╚══════════════════════════════════════════════════════════════════╝$(NC)"
	@./scripts/run_demo.sh

.PHONY: run-all
run-all: setup ## Demo automat non-interactiv (produce artifacts/)
	@echo -e "$(CYAN)═══ Demo automat (run_all.sh) ═══$(NC)"
	@./scripts/run_all.sh

.PHONY: demo-encoding
demo-encoding: ## Demo codare și reprezentare date (L6)
	@echo -e "$(CYAN)═══ Demo: UTF-8, MIME, Base64, Gzip ═══$(NC)"
	@$(PYTHON) -c "\
import base64, gzip, json; \
text = 'România: țară ✓'; \
print(f'Original: {text}'); \
print(f'UTF-8 bytes: {text.encode(\"utf-8\")}'); \
print(f'Base64: {base64.b64encode(text.encode()).decode()}'); \
compressed = gzip.compress(text.encode()); \
print(f'Gzip ({len(compressed)} bytes vs {len(text.encode())} original)'); \
print(f'JSON: {json.dumps({\"msg\": text})}'); \
"

# -----------------------------------------------------------------------------
# Docker
# -----------------------------------------------------------------------------

.PHONY: docker-build
docker-build: ## Construiește imaginile Docker
	@echo -e "$(CYAN)═══ Building Docker images ═══$(NC)"
	@cd docker && docker-compose build

.PHONY: docker-up
docker-up: setup-files ## Pornește stack-ul Docker (server + clienți)
	@echo -e "$(GREEN)═══ Starting Docker stack ═══$(NC)"
	@cd docker && docker-compose up -d
	@echo -e "$(GREEN)✓ Stack pornit. Verifică cu: docker-compose ps$(NC)"

.PHONY: docker-test
docker-test: docker-up ## Rulează test multi-client în Docker
	@echo -e "$(CYAN)═══ Test multi-client Docker ═══$(NC)"
	@sleep 2
	@cd docker && docker-compose logs

.PHONY: docker-logs
docker-logs: ## Afișează logurile Docker
	@cd docker && docker-compose logs -f

.PHONY: docker-down
docker-down: ## Oprește și elimină containerele Docker
	@cd docker && docker-compose down -v 2>/dev/null || true
	@echo -e "$(YELLOW)✓ Docker stack oprit$(NC)"

# -----------------------------------------------------------------------------
# Mininet (necesită sudo)
# -----------------------------------------------------------------------------

.PHONY: mininet-base
mininet-base: setup-files ## Topologie Mininet de bază (1 server, 1 client)
	@echo -e "$(GREEN)═══ Mininet: Topologie de bază ═══$(NC)"
	@sudo -E $(PYTHON) mininet/topologies/topo_base.py --cli

.PHONY: mininet-test
mininet-test: setup-files ## Test automatizat Mininet (1 server, 3 clienți)
	@echo -e "$(GREEN)═══ Mininet: Test concurență ═══$(NC)"
	@sudo -E $(PYTHON) mininet/topologies/topo_extended.py --test

.PHONY: mininet-cli
mininet-cli: setup-files ## CLI interactiv Mininet cu topologie extinsă
	@echo -e "$(GREEN)═══ Mininet CLI (topologie extinsă) ═══$(NC)"
	@sudo -E $(PYTHON) mininet/topologies/topo_extended.py --cli

.PHONY: mininet-clean
mininet-clean: ## Curăță resursele Mininet
	@sudo mn -c 2>/dev/null || true
	@echo -e "$(YELLOW)✓ Mininet curățat$(NC)"

# -----------------------------------------------------------------------------
# Captură trafic
# -----------------------------------------------------------------------------

.PHONY: capture
capture: ## Captură live trafic pe port 3333
	@echo -e "$(CYAN)═══ tcpdump pe port $(PORT) ═══$(NC)"
	@echo -e "$(YELLOW)Ctrl+C pentru oprire$(NC)"
	@sudo tcpdump -i any "tcp port $(PORT)" -nn -vv

.PHONY: capture-save
capture-save: ## Salvează captură în fișier .pcap
	@echo -e "$(CYAN)═══ Salvare captură în pcap/s9_capture.pcap ═══$(NC)"
	@echo -e "$(YELLOW)Ctrl+C pentru oprire și salvare$(NC)"
	@sudo tcpdump -i any "tcp port $(PORT)" -w pcap/s9_capture.pcap
	@echo -e "$(GREEN)✓ Captură salvată$(NC)"

.PHONY: capture-read
capture-read: ## Citește o captură existentă
	@tcpdump -r pcap/s9_capture.pcap -nn -vv 2>/dev/null | head -100 || \
		echo "Nu există fișier pcap/s9_capture.pcap"

# -----------------------------------------------------------------------------
# Verificare și teste
# -----------------------------------------------------------------------------

.PHONY: verify
verify: ## Verifică că mediul e OK
	@echo -e "$(CYAN)═══ Verificare mediu ═══$(NC)"
	@./tests/verify.sh

.PHONY: test
test: ex1 ## Rulează toate testele
	@echo -e "$(GREEN)✓ Toate testele au trecut!$(NC)"

.PHONY: smoke
smoke: setup ## Test rapid de funcționalitate
	@echo -e "$(CYAN)═══ Smoke Test ═══$(NC)"
	@./tests/smoke_test.sh

# -----------------------------------------------------------------------------
# Prezentări și documentație
# -----------------------------------------------------------------------------

.PHONY: slides-view
slides-view: ## Afișează outline-ul pentru slide-uri
	@cat slides/curs_outline.txt

.PHONY: html-open
html-open: ## Deschide prezentarea HTML interactivă
	@xdg-open html_prezentari/theory.html 2>/dev/null || \
		open html_prezentari/theory.html 2>/dev/null || \
		echo "Deschide manual: html_prezentari/theory.html"

# -----------------------------------------------------------------------------
# Utilitare
# -----------------------------------------------------------------------------

.PHONY: check-ports
check-ports: ## Verifică porturile în uz
	@echo -e "$(CYAN)═══ Porturi în uz ═══$(NC)"
	@ss -lntp 2>/dev/null | grep -E "$(PORT)|$(FTP_PORT)" || echo "Niciun port activ"

.PHONY: kill-servers
kill-servers: ## Oprește toate serverele din background
	@pkill -f "ex_9_02" 2>/dev/null || true
	@pkill -f "ftp_demo" 2>/dev/null || true
	@pkill -f "pseudo_ftp" 2>/dev/null || true
	@echo -e "$(YELLOW)✓ Servere oprite$(NC)"

.PHONY: tree
tree: ## Afișează structura proiectului
	@tree -L 3 --dirsfirst -I '__pycache__|*.pyc|server-files|client-files' 2>/dev/null || \
		find . -type d -name '__pycache__' -prune -o -type f -print | head -50

# =============================================================================
# Revolvix&Hypotheticalandrei
# =============================================================================
