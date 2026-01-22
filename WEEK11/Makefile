# =============================================================================
# Makefile – StarterKit Săptămâna 11 (Rețele de Calculatoare)
# =============================================================================
# Automatizare completă: setup, run-demo, run-lab, capture, verify, clean, reset
# Utilizare: make help
# =============================================================================

.PHONY: help setup setup-full run-demo run-lab capture verify clean reset \
        demo-nginx demo-nginx-stop demo-custom-lb demo-custom-lb-stop \
        demo-mininet demo-mininet-cli demo-dns demo-ftp demo-ssh demo-all \
        backends-start backends-stop lb-start lb-stop \
        benchmark benchmark-heavy test capture-traffic

SHELL := /bin/bash
ROOT_DIR := $(shell pwd)
PYTHON := python3
DOCKER_COMPOSE := docker compose

# Ports
LB_PORT := 8080
B1_PORT := 8001
B2_PORT := 8002
B3_PORT := 8003

# Colors
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
BLUE := \033[0;34m
NC := \033[0m

# =============================================================================
# HELP
# =============================================================================

help:
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════════════════════╗"
	@echo "║     StarterKit Săptămâna 11 – Rețele de Calculatoare                     ║"
	@echo "║     Protocoale Aplicație (FTP/DNS/SSH) + Load Balancing                  ║"
	@echo "╚══════════════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "$(GREEN)SETUP & VERIFICARE$(NC)"
	@echo "  make setup          Instalare baseline (Python deps, instrumente)"
	@echo "  make setup-full     Instalare completă (+ Docker + Mininet)"
	@echo "  make verify         Verificare mediu (toate componentele)"
	@echo ""
	@echo "$(GREEN)DEMO AUTOMAT (STANDARD)$(NC)"
	@echo "  make run-all        Demo automat complet → artifacts/*.{log,pcap,txt}"
	@echo "  make smoke-test     Verificare artefacte și sintaxă"
	@echo ""
	@echo "$(GREEN)DEMO-URI PRINCIPALE$(NC)"
	@echo "  make run-demo       Rulează demonstrația completă (seminar)"
	@echo "  make run-lab        Rulează laboratorul pas cu pas"
	@echo "  make demo-all       Rulează toate demo-urile secvențial"
	@echo ""
	@echo "$(BLUE)─── Demo-uri Seminar (Load Balancing) ───$(NC)"
	@echo "  make demo-nginx     Demo Nginx reverse proxy (Docker)"
	@echo "  make demo-custom-lb Demo LB custom Python (Docker)"
	@echo "  make demo-mininet   Demo topologie Mininet cu LB"
	@echo ""
	@echo "$(BLUE)─── Demo-uri Curs (Protocoale Aplicație) ───$(NC)"
	@echo "  make demo-dns       Demo client DNS didactic"
	@echo "  make demo-ftp       Demo FTP activ/pasiv (Docker)"
	@echo "  make demo-ssh       Demo SSH provisioning (Docker)"
	@echo ""
	@echo "$(GREEN)EXERCIȚII PYTHON (standalone)$(NC)"
	@echo "  make backends-start Pornește 3 backends HTTP locale"
	@echo "  make backends-stop  Oprește backend-urile"
	@echo "  make lb-start       Pornește load balancer (round-robin)"
	@echo "  make lb-start-lc    Pornește load balancer (least_conn)"
	@echo "  make lb-start-ip    Pornește load balancer (ip_hash)"
	@echo "  make lb-stop        Oprește load balancer-ul"
	@echo ""
	@echo "$(GREEN)TESTE & BENCHMARK$(NC)"
	@echo "  make test           Rulează smoke tests"
	@echo "  make benchmark      Apache Bench (1000 req, 10 concurent)"
	@echo "  make benchmark-heavy Heavy benchmark (10000 req, 50 concurent)"
	@echo ""
	@echo "$(GREEN)INSTRUMENTARE$(NC)"
	@echo "  make capture        Captură trafic simplificată"
	@echo "  make capture-traffic Captură tcpdump pe portul 8080"
	@echo ""
	@echo "$(GREEN)CURĂȚARE$(NC)"
	@echo "  make clean          Oprire containere + cleanup Mininet"
	@echo "  make reset          Curățare completă + ștergere imagini Docker"
	@echo ""

# =============================================================================
# SETUP & VERIFY
# =============================================================================

setup:
	@echo "$(GREEN)[SETUP]$(NC) Instalare dependențe baseline..."
	@bash $(ROOT_DIR)/scripts/setup.sh
	@echo "$(GREEN)[OK]$(NC) Setup baseline complet."

setup-full:
	@echo "$(GREEN)[SETUP]$(NC) Instalare completă (toate componentele)..."
	@bash $(ROOT_DIR)/scripts/setup.sh --full
	@echo "$(GREEN)[OK]$(NC) Setup complet finalizat."

verify:
	@echo "$(GREEN)[VERIFY]$(NC) Verificare mediu..."
	@bash $(ROOT_DIR)/scripts/verify.sh
	@echo "$(GREEN)[OK]$(NC) Verificare completă."

# =============================================================================
# DEMO AUTOMAT STANDARD (run-all, smoke-test)
# =============================================================================

run-all:
	@echo "$(GREEN)[RUN-ALL]$(NC) Demo automat complet..."
	@bash $(ROOT_DIR)/scripts/run_all.sh
	@echo "$(GREEN)[OK]$(NC) Artefacte generate în artifacts/"

run-all-no-capture:
	@echo "$(GREEN)[RUN-ALL]$(NC) Demo automat fără captură..."
	@bash $(ROOT_DIR)/scripts/run_all.sh --no-capture
	@echo "$(GREEN)[OK]$(NC) Artefacte generate în artifacts/"

smoke-test:
	@echo "$(GREEN)[SMOKE-TEST]$(NC) Verificare artefacte și sintaxă..."
	@bash $(ROOT_DIR)/tests/smoke_test.sh
	@echo "$(GREEN)[OK]$(NC) Smoke test complet."

# =============================================================================
# DEMO PRINCIPAL (run-demo, run-lab)
# =============================================================================

run-demo: demo-nginx
	@echo ""
	@echo "$(GREEN)[DEMO]$(NC) Demo seminar complet."
	@echo "$(YELLOW)[INFO]$(NC) Stack Nginx rulează. Testați cu: curl http://localhost:$(LB_PORT)/"
	@echo "$(YELLOW)[INFO]$(NC) Pentru oprire: make clean"

run-lab:
	@echo "$(GREEN)[LAB]$(NC) Laborator pas cu pas..."
	@echo ""
	@echo "$(BLUE)═══ PASUL 0: Verificare mediu ═══$(NC)"
	@make verify || (echo "$(RED)[!] Rulați 'make setup' întâi$(NC)" && exit 1)
	@echo ""
	@echo "$(BLUE)═══ PASUL 1: Demo Nginx ═══$(NC)"
	@echo "Porniți demo-ul cu: make demo-nginx"
	@echo "Testați cu: curl http://localhost:8080/"
	@echo ""
	@echo "$(BLUE)═══ PASUL 2: Demo LB Custom ═══$(NC)"
	@echo "Opriți Nginx: make demo-nginx-stop"
	@echo "Porniți LB custom: make demo-custom-lb"
	@echo ""
	@echo "$(BLUE)═══ PASUL 3: Exerciții Python ═══$(NC)"
	@echo "make backends-start && make lb-start"
	@echo "curl http://localhost:8080/ (repetați de mai multe ori)"
	@echo ""
	@echo "$(BLUE)═══ PASUL 4: Mininet (necesită sudo) ═══$(NC)"
	@echo "make demo-mininet"
	@echo ""
	@echo "$(GREEN)[INFO]$(NC) Consultați docs/lab.md pentru instrucțiuni detaliate."

# =============================================================================
# DEMO-URI DOCKER (SEMINAR)
# =============================================================================

demo-nginx:
	@echo "$(GREEN)[DEMO]$(NC) Pornire Nginx reverse proxy..."
	@cd $(ROOT_DIR)/docker/nginx_compose && $(DOCKER_COMPOSE) up -d
	@sleep 3
	@echo ""
	@echo "$(YELLOW)[TEST]$(NC) Trimitem 9 cereri (așteptăm round-robin):"
	@for i in 1 2 3 4 5 6 7 8 9; do \
		response=$$(curl -s http://localhost:$(LB_PORT)/ 2>/dev/null | head -1); \
		echo "  Request $$i: $$response"; \
	done
	@echo ""
	@echo "$(GREEN)[INFO]$(NC) Stack Nginx rulează pe portul $(LB_PORT)"
	@echo "$(GREEN)[INFO]$(NC) Logs: cd docker/nginx_compose && docker compose logs -f"

demo-nginx-stop:
	@echo "$(YELLOW)[STOP]$(NC) Oprire Nginx stack..."
	@cd $(ROOT_DIR)/docker/nginx_compose && $(DOCKER_COMPOSE) down 2>/dev/null || true
	@echo "$(GREEN)[OK]$(NC) Nginx oprit."

demo-custom-lb:
	@echo "$(GREEN)[DEMO]$(NC) Pornire LB custom Python în Docker..."
	@cd $(ROOT_DIR)/docker/custom_lb_compose && $(DOCKER_COMPOSE) up -d --build
	@sleep 4
	@echo ""
	@echo "$(YELLOW)[TEST]$(NC) Trimitem 9 cereri:"
	@for i in 1 2 3 4 5 6 7 8 9; do \
		response=$$(curl -s http://localhost:$(LB_PORT)/ 2>/dev/null | head -1); \
		echo "  Request $$i: $$response"; \
	done
	@echo ""
	@echo "$(GREEN)[INFO]$(NC) Stack LB custom rulează pe portul $(LB_PORT)"

demo-custom-lb-stop:
	@echo "$(YELLOW)[STOP]$(NC) Oprire LB custom stack..."
	@cd $(ROOT_DIR)/docker/custom_lb_compose && $(DOCKER_COMPOSE) down 2>/dev/null || true
	@echo "$(GREEN)[OK]$(NC) LB custom oprit."

# =============================================================================
# DEMO-URI DOCKER (CURS - Protocoale)
# =============================================================================

demo-dns:
	@echo "$(GREEN)[DEMO]$(NC) Client DNS didactic..."
	@echo ""
	@echo "$(BLUE)─── Query A pentru google.com ───$(NC)"
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_03_dns_client.py --query google.com --type A 2>/dev/null || \
		echo "$(YELLOW)[INFO]$(NC) Instalați dnspython: pip3 install dnspython"
	@echo ""
	@echo "$(BLUE)─── Query MX pentru google.com ───$(NC)"
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_03_dns_client.py --query google.com --type MX 2>/dev/null || true
	@echo ""
	@echo "$(BLUE)─── Query NS pentru ase.ro ───$(NC)"
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_03_dns_client.py --query ase.ro --type NS 2>/dev/null || true

demo-ftp:
	@echo "$(GREEN)[DEMO]$(NC) FTP Demo (necesită Docker)..."
	@if [ -d "$(ROOT_DIR)/docker/ftp_demo" ] && [ -f "$(ROOT_DIR)/docker/ftp_demo/docker-compose.yml" ]; then \
		cd $(ROOT_DIR)/docker/ftp_demo && $(DOCKER_COMPOSE) up -d; \
		sleep 3; \
		echo "$(YELLOW)[INFO]$(NC) Server FTP pornit. Conectare: ftp localhost 2121"; \
	else \
		echo "$(YELLOW)[INFO]$(NC) Demo FTP: consultați docker/ftp_demo/README.md"; \
	fi

demo-ssh:
	@echo "$(GREEN)[DEMO]$(NC) SSH Provisioning Demo..."
	@if [ -d "$(ROOT_DIR)/docker/ssh_demo" ] && [ -f "$(ROOT_DIR)/docker/ssh_demo/docker-compose.yml" ]; then \
		cd $(ROOT_DIR)/docker/ssh_demo && $(DOCKER_COMPOSE) up -d; \
		sleep 3; \
		echo "$(YELLOW)[INFO]$(NC) Containere SSH pornite. Vedeți docker/ssh_demo/README.md"; \
	else \
		echo "$(YELLOW)[INFO]$(NC) Demo SSH: consultați docker/ssh_demo/README.md"; \
	fi

# =============================================================================
# DEMO MININET
# =============================================================================

demo-mininet:
	@echo "$(GREEN)[DEMO]$(NC) Curățare Mininet prealabilă..."
	@sudo mn -c 2>/dev/null || true
	@echo "$(GREEN)[DEMO]$(NC) Pornire topologie Mininet cu test automat..."
	@cd $(ROOT_DIR) && sudo $(PYTHON) mininet/topologies/topo_11_base.py --test
	@echo "$(GREEN)[OK]$(NC) Demo Mininet finalizat."

demo-mininet-cli:
	@echo "$(GREEN)[DEMO]$(NC) Intrare în CLI Mininet (exit pentru a ieși)..."
	@sudo mn -c 2>/dev/null || true
	@cd $(ROOT_DIR) && sudo $(PYTHON) mininet/topologies/topo_11_base.py --cli

demo-mininet-extended:
	@echo "$(GREEN)[DEMO]$(NC) Topologie extinsă cu failover..."
	@sudo mn -c 2>/dev/null || true
	@cd $(ROOT_DIR) && sudo $(PYTHON) mininet/topologies/topo_11_extended.py --test

# =============================================================================
# DEMO ALL
# =============================================================================

demo-all: 
	@echo "$(GREEN)[DEMO-ALL]$(NC) Rulare toate demo-urile..."
	@echo ""
	@echo "$(BLUE)═══ 1. Demo Nginx ═══$(NC)"
	@make demo-nginx
	@sleep 3
	@make demo-nginx-stop
	@echo ""
	@echo "$(BLUE)═══ 2. Demo LB Custom ═══$(NC)"
	@make demo-custom-lb
	@sleep 3
	@make demo-custom-lb-stop
	@echo ""
	@echo "$(BLUE)═══ 3. Demo DNS ═══$(NC)"
	@make demo-dns
	@echo ""
	@echo "$(GREEN)[OK]$(NC) Toate demo-urile Docker finalizate."
	@echo "$(YELLOW)[INFO]$(NC) Pentru Mininet: make demo-mininet (necesită sudo)"

# =============================================================================
# EXERCIȚII PYTHON STANDALONE
# =============================================================================

backends-start:
	@echo "$(GREEN)[START]$(NC) Pornire 3 backends HTTP locale..."
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_01_backend.py --id 1 --port $(B1_PORT) > /tmp/backend1.log 2>&1 &
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_01_backend.py --id 2 --port $(B2_PORT) > /tmp/backend2.log 2>&1 &
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_01_backend.py --id 3 --port $(B3_PORT) > /tmp/backend3.log 2>&1 &
	@sleep 1
	@echo "$(GREEN)[OK]$(NC) Backends pornite pe porturile $(B1_PORT), $(B2_PORT), $(B3_PORT)"
	@echo "$(YELLOW)[INFO]$(NC) Logs în /tmp/backend{1,2,3}.log"
	@echo "$(YELLOW)[INFO]$(NC) Test: curl http://localhost:$(B1_PORT)/"

backends-stop:
	@echo "$(YELLOW)[STOP]$(NC) Oprire backends..."
	@pkill -f "ex_11_01_backend" 2>/dev/null || true
	@echo "$(GREEN)[OK]$(NC) Backends oprite."

lb-start:
	@echo "$(GREEN)[START]$(NC) Pornire load balancer (round-robin)..."
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_02_loadbalancer.py \
		--listen 0.0.0.0:$(LB_PORT) \
		--backends 127.0.0.1:$(B1_PORT),127.0.0.1:$(B2_PORT),127.0.0.1:$(B3_PORT) \
		--algo rr > /tmp/lb.log 2>&1 &
	@sleep 1
	@echo "$(GREEN)[OK]$(NC) LB pornit pe portul $(LB_PORT) (algoritm: round-robin)"
	@echo "$(YELLOW)[INFO]$(NC) Test: curl http://localhost:$(LB_PORT)/"

lb-start-lc:
	@echo "$(GREEN)[START]$(NC) Pornire load balancer (least_conn)..."
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_02_loadbalancer.py \
		--listen 0.0.0.0:$(LB_PORT) \
		--backends 127.0.0.1:$(B1_PORT),127.0.0.1:$(B2_PORT),127.0.0.1:$(B3_PORT) \
		--algo least_conn > /tmp/lb.log 2>&1 &
	@sleep 1
	@echo "$(GREEN)[OK]$(NC) LB pornit pe portul $(LB_PORT) (algoritm: least_conn)"

lb-start-ip:
	@echo "$(GREEN)[START]$(NC) Pornire load balancer (ip_hash)..."
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_02_loadbalancer.py \
		--listen 0.0.0.0:$(LB_PORT) \
		--backends 127.0.0.1:$(B1_PORT),127.0.0.1:$(B2_PORT),127.0.0.1:$(B3_PORT) \
		--algo ip_hash > /tmp/lb.log 2>&1 &
	@sleep 1
	@echo "$(GREEN)[OK]$(NC) LB pornit pe portul $(LB_PORT) (algoritm: ip_hash)"

lb-stop:
	@echo "$(YELLOW)[STOP]$(NC) Oprire load balancer..."
	@pkill -f "ex_11_02_loadbalancer" 2>/dev/null || true
	@echo "$(GREEN)[OK]$(NC) LB oprit."

# =============================================================================
# TESTE & BENCHMARK
# =============================================================================

test:
	@echo "$(GREEN)[TEST]$(NC) Rulare smoke tests..."
	@bash $(ROOT_DIR)/scripts/verify.sh --smoke
	@echo "$(GREEN)[OK]$(NC) Smoke tests complete."

benchmark:
	@echo "$(GREEN)[BENCH]$(NC) Apache Bench: 1000 requests, 10 concurrent..."
	@if command -v ab &> /dev/null; then \
		ab -n 1000 -c 10 http://127.0.0.1:$(LB_PORT)/ 2>/dev/null | grep -E "(Requests per second|Time per request|Failed)"; \
	else \
		echo "$(YELLOW)[INFO]$(NC) ab nu e instalat. Rulăm load generator Python..."; \
		$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_02_loadbalancer.py loadgen --url http://127.0.0.1:$(LB_PORT)/ --n 1000 --c 10; \
	fi

benchmark-heavy:
	@echo "$(GREEN)[BENCH]$(NC) Heavy benchmark: 10000 requests, 50 concurrent..."
	@if command -v ab &> /dev/null; then \
		ab -n 10000 -c 50 http://127.0.0.1:$(LB_PORT)/ 2>/dev/null | grep -E "(Requests per second|Time per request|Failed)"; \
	else \
		$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_02_loadbalancer.py loadgen --url http://127.0.0.1:$(LB_PORT)/ --n 10000 --c 50; \
	fi

# =============================================================================
# INSTRUMENTARE
# =============================================================================

capture:
	@echo "$(GREEN)[CAPTURE]$(NC) Captură trafic simplificată..."
	@bash $(ROOT_DIR)/scripts/capture.sh

capture-traffic:
	@echo "$(GREEN)[CAPTURE]$(NC) tcpdump pe portul $(LB_PORT) (Ctrl+C pentru stop)..."
	@if command -v tcpdump &> /dev/null; then \
		sudo tcpdump -i any -n tcp port $(LB_PORT) -c 20; \
	elif command -v tshark &> /dev/null; then \
		sudo tshark -i any -f "tcp port $(LB_PORT)" -c 20; \
	else \
		echo "$(RED)[!]$(NC) Nici tcpdump, nici tshark nu sunt instalate."; \
	fi

# =============================================================================
# CURĂȚARE
# =============================================================================

clean:
	@echo "$(YELLOW)[CLEAN]$(NC) Curățare completă..."
	@# Docker stacks
	@cd $(ROOT_DIR)/docker/nginx_compose && $(DOCKER_COMPOSE) down 2>/dev/null || true
	@cd $(ROOT_DIR)/docker/custom_lb_compose && $(DOCKER_COMPOSE) down 2>/dev/null || true
	@cd $(ROOT_DIR)/docker/ftp_demo && $(DOCKER_COMPOSE) down 2>/dev/null || true
	@cd $(ROOT_DIR)/docker/dns_demo && $(DOCKER_COMPOSE) down 2>/dev/null || true
	@cd $(ROOT_DIR)/docker/ssh_demo && $(DOCKER_COMPOSE) down 2>/dev/null || true
	@# Procese Python
	@pkill -f "ex_11_01_backend" 2>/dev/null || true
	@pkill -f "ex_11_02_loadbalancer" 2>/dev/null || true
	@# Mininet
	@sudo mn -c 2>/dev/null || true
	@# Fișiere temporare
	@rm -f /tmp/backend*.log /tmp/lb.log /tmp/s11_*.log /tmp/*.pid 2>/dev/null || true
	@rm -f $(ROOT_DIR)/pcap/*.pcap 2>/dev/null || true
	@echo "$(GREEN)[OK]$(NC) Curățare finalizată."

reset: clean
	@echo "$(YELLOW)[RESET]$(NC) Reset complet + ștergere imagini Docker..."
	@docker system prune -f 2>/dev/null || true
	@docker volume prune -f 2>/dev/null || true
	@echo "$(GREEN)[OK]$(NC) Reset complet finalizat."

# =============================================================================
# FOOTER
# =============================================================================
# Revolvix&Hypotheticalandrei
# =============================================================================
