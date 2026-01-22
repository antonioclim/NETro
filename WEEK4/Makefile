# ==============================================================================
# Makefile - Starterkit Săptămâna 4 (WEEK 4)
# Protocol aplicație text/binar custom peste TCP și UDP
# ==============================================================================
# Plan porturi WEEK 4: 5400 (TEXT), 5401 (BINARY), 5402 (UDP)
# Plan IP (Mininet): 10.0.4.0/24
#
# Utilizare: make [target]
#   make help       - Afișează acest mesaj
#   make setup      - Instalează dependențele
#   make run-demo   - Rulează demo-ul principal
#   make run-lab    - Pornește serverele pentru laborator
#   make capture    - Captură trafic de rețea
#   make verify     - Verifică că mediul funcționează
#   make clean      - Curăță fișierele temporare
#   make reset      - Resetează totul la starea inițială
#
# Licență: MIT - Material didactic ASE-CSIE
# ==============================================================================

.PHONY: help setup run-demo run-lab capture verify clean reset cleanup \
        server-text server-binary server-udp test lint check

# Variabile
PYTHON := python3
SUDO := sudo
ROOT := $(shell pwd)
ARTIFACTS := $(ROOT)/artifacts
RESULTS := $(ROOT)/results
PCAP := $(ROOT)/pcap

# ==============================================================================
# PLAN PORTURI WEEK 4 (Standard Transversal)
# ==============================================================================
# WEEK_PORT_BASE = 5100 + 100*(WEEK-1) = 5100 + 300 = 5400
PORT_TEXT := 5400
PORT_BIN := 5401
PORT_UDP := 5402

# Culori pentru output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
CYAN := \033[0;36m
NC := \033[0m

# ==============================================================================
# Target principal: help
# ==============================================================================

help:
	@echo "$(CYAN)╔══════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║  Starterkit Săptămâna 4 - Protocoale TEXT/BINARY Custom (WEEK 4)     ║$(NC)"
	@echo "$(CYAN)║  Porturi: TEXT=$(PORT_TEXT), BINARY=$(PORT_BIN), UDP=$(PORT_UDP)                           ║$(NC)"
	@echo "$(CYAN)╚══════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)SETUP ȘI VERIFICARE:$(NC)"
	@echo "  make setup          Instalează dependențele"
	@echo "  make verify         Verifică mediul (Python, porturi, module)"
	@echo "  make check          Verifică sintaxa Python"
	@echo "  make lint           Analizează stilul codului"
	@echo ""
	@echo "$(YELLOW)RULARE SERVERE:$(NC)"
	@echo "  make server-text    Pornește serverul TEXT pe port $(PORT_TEXT)"
	@echo "  make server-binary  Pornește serverul BINAR pe port $(PORT_BIN)"
	@echo "  make server-udp     Pornește serverul UDP pe port $(PORT_UDP)"
	@echo "  make run-lab        Pornește toate serverele (în background)"
	@echo ""
	@echo "$(YELLOW)DEMO ȘI CAPTURĂ:$(NC)"
	@echo "  make run-demo       Rulează demo-ul complet cu clienți"
	@echo "  make capture        Captură trafic pe lo (5 secunde)"
	@echo "  make analyze        Analizează ultima captură"
	@echo ""
	@echo "$(YELLOW)CURĂȚARE:$(NC)"
	@echo "  make clean          Șterge fișiere temporare"
	@echo "  make cleanup        Oprește serverele și curăță"
	@echo "  make reset          Resetare completă (kill servere, curățare)"
	@echo ""
	@echo "$(GREEN)COMENZI RAPIDE:$(NC)"
	@echo "  make test           Rulează smoke test rapid"
	@echo ""
	@echo "$(GREEN)PLAN IP (Mininet):$(NC)"
	@echo "  Rețea: 10.0.4.0/24, Gateway: 10.0.4.1, Server: 10.0.4.100"
	@echo ""

# ==============================================================================
# Setup și Instalare
# ==============================================================================

setup:
	@echo "$(GREEN)[SETUP] Instalare dependențe...$(NC)"
	@chmod +x scripts/*.sh 2>/dev/null || true
	@./scripts/setup.sh || (echo "$(RED)Setup failed!$(NC)" && exit 1)
	@echo "$(GREEN)[SETUP] Complet!$(NC)"

# ==============================================================================
# Verificare mediu
# ==============================================================================

verify:
	@echo "$(GREEN)[VERIFY] Verificare mediu...$(NC)"
	@echo ""
	@echo "Python: $$($(PYTHON) --version 2>&1)"
	@echo ""
	@echo "Module Python necesare:"
	@$(PYTHON) -c "import socket; print('  ✓ socket')"
	@$(PYTHON) -c "import struct; print('  ✓ struct')"
	@$(PYTHON) -c "import zlib; print('  ✓ zlib')"
	@$(PYTHON) -c "import threading; print('  ✓ threading')"
	@$(PYTHON) -c "import dataclasses; print('  ✓ dataclasses')"
	@echo ""
	@echo "Verificare porturi libere (WEEK 4: 5400-5402):"
	@(lsof -i :$(PORT_TEXT) > /dev/null 2>&1 && echo "  ⚠ Port $(PORT_TEXT) OCUPAT") || echo "  ✓ Port $(PORT_TEXT) liber"
	@(lsof -i :$(PORT_BIN) > /dev/null 2>&1 && echo "  ⚠ Port $(PORT_BIN) OCUPAT") || echo "  ✓ Port $(PORT_BIN) liber"
	@(lsof -i :$(PORT_UDP) > /dev/null 2>&1 && echo "  ⚠ Port $(PORT_UDP) OCUPAT") || echo "  ✓ Port $(PORT_UDP) liber"
	@echo ""
	@echo "$(GREEN)[VERIFY] Verificare completă!$(NC)"

check:
	@echo "$(GREEN)[CHECK] Verificare sintaxă Python...$(NC)"
	@$(PYTHON) -m py_compile python/apps/text_proto_server.py && echo "  ✓ text_proto_server.py"
	@$(PYTHON) -m py_compile python/apps/text_proto_client.py && echo "  ✓ text_proto_client.py"
	@$(PYTHON) -m py_compile python/apps/binary_proto_server.py && echo "  ✓ binary_proto_server.py"
	@$(PYTHON) -m py_compile python/apps/binary_proto_client.py && echo "  ✓ binary_proto_client.py"
	@$(PYTHON) -m py_compile python/apps/udp_sensor_server.py && echo "  ✓ udp_sensor_server.py"
	@$(PYTHON) -m py_compile python/apps/udp_sensor_client.py && echo "  ✓ udp_sensor_client.py"
	@$(PYTHON) -m py_compile python/utils/proto_common.py && echo "  ✓ proto_common.py"
	@$(PYTHON) -m py_compile python/utils/io_utils.py && echo "  ✓ io_utils.py"
	@echo "$(GREEN)[CHECK] Toate fișierele sunt valide!$(NC)"

lint:
	@echo "$(GREEN)[LINT] Verificare stil cod...$(NC)"
	@$(PYTHON) -m pyflakes python/apps/*.py python/utils/*.py 2>/dev/null || true
	@echo "$(GREEN)[LINT] Complet!$(NC)"

# ==============================================================================
# Rulare Servere
# ==============================================================================

server-text:
	@echo "$(GREEN)[SERVER] Pornire server TEXT pe port $(PORT_TEXT)...$(NC)"
	@$(PYTHON) python/apps/text_proto_server.py --port $(PORT_TEXT) --verbose

server-binary:
	@echo "$(GREEN)[SERVER] Pornire server BINAR pe port $(PORT_BIN)...$(NC)"
	@$(PYTHON) python/apps/binary_proto_server.py --port $(PORT_BIN) --verbose

server-udp:
	@echo "$(GREEN)[SERVER] Pornire server UDP pe port $(PORT_UDP)...$(NC)"
	@$(PYTHON) python/apps/udp_sensor_server.py --port $(PORT_UDP) --verbose

run-lab:
	@echo "$(GREEN)[LAB] Pornire servere în background...$(NC)"
	@mkdir -p $(RESULTS) $(ARTIFACTS)
	@$(PYTHON) python/apps/text_proto_server.py --port $(PORT_TEXT) > $(RESULTS)/text_server.log 2>&1 &
	@echo "  TEXT server: port $(PORT_TEXT) (PID: $$!)"
	@$(PYTHON) python/apps/binary_proto_server.py --port $(PORT_BIN) > $(RESULTS)/binary_server.log 2>&1 &
	@echo "  BINARY server: port $(PORT_BIN) (PID: $$!)"
	@$(PYTHON) python/apps/udp_sensor_server.py --port $(PORT_UDP) > $(RESULTS)/udp_server.log 2>&1 &
	@echo "  UDP server: port $(PORT_UDP) (PID: $$!)"
	@echo ""
	@echo "$(GREEN)Serverele rulează în background. Folosiți 'make cleanup' pentru oprire.$(NC)"

# ==============================================================================
# Demo
# ==============================================================================

run-demo:
	@echo "$(GREEN)[DEMO] Rulare demo complet...$(NC)"
	@mkdir -p $(ARTIFACTS)
	@chmod +x scripts/run_all.sh
	@./scripts/run_all.sh || echo "$(YELLOW)Demo completat cu avertismente$(NC)"
	@echo "$(GREEN)[DEMO] Complet! Verificați $(ARTIFACTS)/$(NC)"

# ==============================================================================
# Captură și Analiză
# ==============================================================================

capture:
	@echo "$(GREEN)[CAPTURE] Pornire captură pe lo (5 secunde)...$(NC)"
	@mkdir -p $(PCAP)
	@$(SUDO) tcpdump -i lo -w $(PCAP)/capture_$$(date +%Y%m%d_%H%M%S).pcap \
		-c 100 port $(PORT_TEXT) or port $(PORT_BIN) or port $(PORT_UDP) &
	@echo "Captură activă. Generați trafic apoi așteptați 5 secunde."
	@sleep 5
	@echo "$(GREEN)[CAPTURE] Captură completă în $(PCAP)/$(NC)"

analyze:
	@echo "$(GREEN)[ANALYZE] Analiză ultima captură...$(NC)"
	@LATEST=$$(ls -t $(PCAP)/*.pcap 2>/dev/null | head -1); \
	if [ -n "$$LATEST" ]; then \
		echo "Fișier: $$LATEST"; \
		tshark -r "$$LATEST" -q -z io,stat,1 2>/dev/null || \
		tcpdump -r "$$LATEST" -n | head -20; \
	else \
		echo "$(RED)Nu există capturi în $(PCAP)/$(NC)"; \
	fi

# ==============================================================================
# Test
# ==============================================================================

test:
	@echo "$(GREEN)[TEST] Smoke test rapid...$(NC)"
	@chmod +x tests/smoke_test.sh
	@./tests/smoke_test.sh

# ==============================================================================
# Curățare
# ==============================================================================

clean:
	@echo "$(YELLOW)[CLEAN] Curățare fișiere temporare...$(NC)"
	@rm -rf $(RESULTS)/*.log 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)[CLEAN] Complet!$(NC)"

cleanup:
	@echo "$(YELLOW)[CLEANUP] Oprire servere și curățare...$(NC)"
	@chmod +x scripts/cleanup.sh
	@./scripts/cleanup.sh
	@echo "$(GREEN)[CLEANUP] Complet!$(NC)"

reset: cleanup clean
	@echo "$(YELLOW)[RESET] Resetare completă...$(NC)"
	@rm -rf $(ARTIFACTS)/* 2>/dev/null || true
	@rm -rf $(PCAP)/*.pcap 2>/dev/null || true
	@mkdir -p $(RESULTS) $(PCAP) $(ARTIFACTS)
	@echo "$(GREEN)[RESET] Complet!$(NC)"
