# Makefile — Starterkit Săptămâna 14
# Rețele de calculatoare / Networking — CSIE/ASE
# Versiune: 2025-12-31

.PHONY: setup run-demo run-lab capture verify clean reset help

SHELL := /bin/bash
ROOT_DIR := $(shell pwd)
ARTIFACTS := $(ROOT_DIR)/artifacts
PYTHON := python3

# Culori pentru output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

help:
	@echo -e "$(GREEN)Starterkit S14 — Comenzi disponibile:$(NC)"
	@echo ""
	@echo "  make setup      - Instalează dependențele (necesită sudo)"
	@echo "  make verify     - Verifică mediul și dependențele"
	@echo "  make run-demo   - Rulează demo-ul complet (Mininet + trafic + pcap)"
	@echo "  make run-lab    - Pornește topologia interactiv (CLI Mininet)"
	@echo "  make capture    - Pornește doar captura tcpdump"
	@echo "  make clean      - Oprește procese, curăță Mininet"
	@echo "  make reset      - Clean + șterge toate artefactele"
	@echo ""
	@echo -e "$(YELLOW)Notă: run-demo și run-lab necesită sudo.$(NC)"

setup:
	@echo -e "$(GREEN)[setup] Instalare dependențe...$(NC)"
	@sudo bash scripts/setup.sh
	@echo -e "$(GREEN)[setup] Instalare pachete Python...$(NC)"
	@pip3 install -r requirements.txt --break-system-packages 2>/dev/null || pip3 install -r requirements.txt
	@echo -e "$(GREEN)[setup] Done.$(NC)"

verify:
	@echo -e "$(GREEN)[verify] Verificare mediu...$(NC)"
	@bash scripts/verify.sh
	@bash tests/smoke_test.sh

run-demo:
	@echo -e "$(GREEN)[run-demo] Pornire demo automat...$(NC)"
	@mkdir -p $(ARTIFACTS)
	@sudo bash scripts/run_all.sh
	@echo -e "$(GREEN)[run-demo] Artefacte generate în: $(ARTIFACTS)$(NC)"
	@ls -la $(ARTIFACTS)/ 2>/dev/null || true

run-lab:
	@echo -e "$(GREEN)[run-lab] Pornire topologie interactivă (CLI Mininet)...$(NC)"
	@echo -e "$(YELLOW)Tip 'exit' sau Ctrl+D pentru ieșire.$(NC)"
	@sudo $(PYTHON) mininet/topologies/topo_14_recap.py --cli

capture:
	@echo -e "$(GREEN)[capture] Pornire captură standalone...$(NC)"
	@mkdir -p $(ARTIFACTS)
	@sudo bash scripts/capture.sh $(ARTIFACTS)/manual_capture.pcap

clean:
	@echo -e "$(YELLOW)[clean] Oprire procese și curățare Mininet...$(NC)"
	@sudo bash scripts/cleanup.sh
	@echo -e "$(GREEN)[clean] Done.$(NC)"

reset: clean
	@echo -e "$(RED)[reset] Ștergere artefacte...$(NC)"
	@rm -rf $(ARTIFACTS)
	@echo -e "$(GREEN)[reset] Done.$(NC)"

# Target implicit
.DEFAULT_GOAL := help
