# ============================================================================
# Makefile — Starter Kit Săptămâna 3: Introducere în Programarea de Rețea
# ============================================================================
# Utilizare:
#   make help        - Afișează toate target-urile disponibile
#   make setup       - Instalare dependențe (necesită sudo)
#   make run-demo    - Rulare demo-uri principale
#   make run-lab     - Pornire mod laborator interactiv
#   make capture     - Captură trafic de rețea
#   make verify      - Verificare că mediul e configurat corect
#   make clean       - Curățare procese și fișiere temporare
#   make reset       - Reset complet (clean + reconfigurare)
# ============================================================================

.PHONY: help setup run-demo run-lab capture verify clean reset \
        run-all run-all-quick \
        demo-broadcast demo-multicast demo-tunnel demo-multiclient \
        docker-build docker-run docker-compose-up docker-compose-down \
        lint test mininet-base mininet-extended pack \
        capture-broadcast capture-multicast

# ════════════════════════════════════════════════════════════════════════════
# VARIABILE CONFIGURABILE — WEEK 3 Standard
# ════════════════════════════════════════════════════════════════════════════
PYTHON := python3
MININET_CLI := sudo python3
DOCKER_IMAGE := s3-networking
DOCKER_TAG := latest

# WEEK 3: Plan Porturi Standard
# WEEK_PORT_BASE = 5100 + 100*(WEEK-1) = 5300
WEEK := 3
WEEK_PORT_BASE := 5300
PORT_BROADCAST := 5307
PORT_MULTICAST := 5301
PORT_TUNNEL_LISTEN := 5390
PORT_TUNNEL_TARGET := 5380
PORT_MULTICLIENT := 5333
MULTICAST_GROUP := 239.3.3.3

# Directoare
LOG_DIR := logs
PCAP_DIR := pcap
ARTIFACTS_DIR := artifacts

# Culori pentru output (ANSI)
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
BOLD := \033[1m
NC := \033[0m

# ════════════════════════════════════════════════════════════════════════════
# HELP (target implicit)
# ════════════════════════════════════════════════════════════════════════════
help:
	@echo ""
	@echo "$(CYAN)╔══════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║  $(BOLD)Starter Kit S3 — WEEK 3: Broadcast/Multicast UDP + TCP Tunnel$(NC)$(CYAN)    ║$(NC)"
	@echo "$(CYAN)╚══════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)$(BOLD)Setup și Verificare:$(NC)"
	@echo "  make setup              Instalare dependențe sistem + Python"
	@echo "  make verify             Verificare mediu (Python, Mininet, tools)"
	@echo "  make test               Rulare smoke test complet"
	@echo "  make lint               Verificare cod Python (flake8)"
	@echo ""
	@echo "$(GREEN)$(BOLD)Demo Automat (produce artefacte):$(NC)"
	@echo "  make run-all            Demo COMPLET → artifacts/demo.{log,pcap}, validation.txt"
	@echo "  make run-all-quick      Demo RAPID (doar localhost, fără Mininet)"
	@echo ""
	@echo "$(GREEN)$(BOLD)Demo-uri Individuale (necesită Mininet):$(NC)"
	@echo "  make run-demo           Rulare TOATE demo-urile secvențial"
	@echo "  make demo-broadcast     Demo UDP broadcast (topologie bază)"
	@echo "  make demo-multicast     Demo UDP multicast (topologie bază)"
	@echo "  make demo-tunnel        Demo TCP tunnel (topologie extinsă)"
	@echo "  make demo-multiclient   Demo server TCP multi-threaded (localhost)"
	@echo ""
	@echo "$(GREEN)$(BOLD)Laborator Interactiv:$(NC)"
	@echo "  make run-lab            Alias pentru mininet-base (CLI interactiv)"
	@echo "  make mininet-base       Pornire topologie bază (3 hosturi, 1 switch)"
	@echo "  make mininet-extended   Pornire topologie extinsă (2 subrețele)"
	@echo ""
	@echo "$(GREEN)$(BOLD)Capturi de Trafic:$(NC)"
	@echo "  make capture            Captură generică (broadcast + multicast)"
	@echo "  make capture-broadcast  Captură tcpdump pentru broadcast"
	@echo "  make capture-multicast  Captură tcpdump pentru multicast + IGMP"
	@echo ""
	@echo "$(GREEN)$(BOLD)Docker (alternativă la Mininet):$(NC)"
	@echo "  make docker-build       Construire imagine Docker"
	@echo "  make docker-run         Rulare container interactiv"
	@echo "  make docker-compose-up  Pornire stack multi-container"
	@echo "  make docker-compose-down Oprire stack"
	@echo ""
	@echo "$(GREEN)$(BOLD)Curățare și Reset:$(NC)"
	@echo "  make clean              Curățare Mininet + procese + temp"
	@echo "  make reset              Reset complet (clean + verify)"
	@echo "  make pack               Creare arhivă .zip pentru distribuție"
	@echo ""
	@echo "$(YELLOW)Porturi WEEK 3: BCAST=$(PORT_BROADCAST) MCAST=$(PORT_MULTICAST) TUNNEL=$(PORT_TUNNEL_LISTEN)$(NC)"
	@echo "$(YELLOW)Notă: Majoritatea comenzilor necesită permisiuni sudo pentru Mininet.$(NC)"
	@echo ""

# ════════════════════════════════════════════════════════════════════════════
# SETUP — Instalare dependențe
# ════════════════════════════════════════════════════════════════════════════
setup:
	@echo "$(CYAN)[SETUP] Instalare dependențe sistem și Python...$(NC)"
	@bash scripts/setup.sh
	@echo "$(GREEN)[OK] Setup complet. Rulați 'make verify' pentru verificare.$(NC)"

setup-python:
	@echo "$(CYAN)[SETUP] Instalare dependențe Python...$(NC)"
	@$(PYTHON) -m pip install --break-system-packages -r requirements.txt 2>/dev/null || \
	$(PYTHON) -m pip install -r requirements.txt
	@echo "$(GREEN)[OK] Dependențe Python instalate.$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# VERIFY — Verificare mediu
# ════════════════════════════════════════════════════════════════════════════
verify:
	@echo "$(CYAN)[VERIFY] Verificare mediu de lucru...$(NC)"
	@bash scripts/verify.sh
	@echo "$(GREEN)[OK] Mediul este configurat corect.$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# TEST — Smoke test
# ════════════════════════════════════════════════════════════════════════════
test:
	@echo "$(CYAN)[TEST] Rulare smoke test...$(NC)"
	@bash tests/smoke_test.sh
	@echo "$(GREEN)[OK] Smoke test complet.$(NC)"

test-python:
	@echo "$(CYAN)[TEST] Verificare sintaxă Python...$(NC)"
	@$(PYTHON) -m py_compile python/examples/*.py
	@$(PYTHON) -m py_compile python/templates/*.py 2>/dev/null || true
	@$(PYTHON) -m py_compile python/utils/*.py
	@echo "$(GREEN)[OK] Sintaxă Python validă.$(NC)"

lint:
	@echo "$(CYAN)[LINT] Verificare cod Python...$(NC)"
	@$(PYTHON) -m flake8 python/ --max-line-length=120 --ignore=E501,W503 || true
	@echo "$(GREEN)[OK] Lint complet.$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# RUN-ALL — Demo automat complet (produce artefacte)
# ════════════════════════════════════════════════════════════════════════════
run-all:
	@echo "$(CYAN)[RUN-ALL] Demo automat complet WEEK $(WEEK)...$(NC)"
	@bash scripts/run_all.sh
	@echo "$(GREEN)[OK] Artefacte generate în $(ARTIFACTS_DIR)/$(NC)"

run-all-quick:
	@echo "$(CYAN)[RUN-ALL] Demo rapid (doar localhost)...$(NC)"
	@bash scripts/run_all.sh --quick
	@echo "$(GREEN)[OK] Demo rapid complet.$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# RUN-DEMO — Rulare demo-uri
# ════════════════════════════════════════════════════════════════════════════
run-demo: demo-broadcast demo-multicast demo-tunnel demo-multiclient
	@echo "$(GREEN)[OK] Toate demo-urile au rulat cu succes.$(NC)"

demo-broadcast:
	@echo "$(CYAN)[DEMO] UDP Broadcast...$(NC)"
	@mkdir -p $(LOG_DIR)
	@echo "$(YELLOW)Pornire topologie bază cu test broadcast...$(NC)"
	$(MININET_CLI) mininet/topologies/topo_base.py --test broadcast 2>&1 | tee $(LOG_DIR)/demo_broadcast.log
	@echo "$(GREEN)[OK] Demo broadcast complet. Log: $(LOG_DIR)/demo_broadcast.log$(NC)"

demo-multicast:
	@echo "$(CYAN)[DEMO] UDP Multicast...$(NC)"
	@mkdir -p $(LOG_DIR)
	@echo "$(YELLOW)Pornire topologie bază cu test multicast...$(NC)"
	$(MININET_CLI) mininet/topologies/topo_base.py --test multicast 2>&1 | tee $(LOG_DIR)/demo_multicast.log
	@echo "$(GREEN)[OK] Demo multicast complet. Log: $(LOG_DIR)/demo_multicast.log$(NC)"

demo-tunnel:
	@echo "$(CYAN)[DEMO] TCP Tunnel...$(NC)"
	@mkdir -p $(LOG_DIR)
	@echo "$(YELLOW)Pornire topologie extinsă cu test tunnel...$(NC)"
	$(MININET_CLI) mininet/topologies/topo_extended.py --test tunnel 2>&1 | tee $(LOG_DIR)/demo_tunnel.log
	@echo "$(GREEN)[OK] Demo tunnel complet. Log: $(LOG_DIR)/demo_tunnel.log$(NC)"

demo-multiclient:
	@echo "$(CYAN)[DEMO] Server TCP Multiclient (localhost)...$(NC)"
	@echo "$(YELLOW)Pornire server în background pentru 10 secunde...$(NC)"
	@timeout 10 $(PYTHON) python/examples/ex05_tcp_multiclient.py &
	@sleep 1
	@echo "test1" | nc -w 1 127.0.0.1 $(PORT_MULTICLIENT) || true
	@echo "test2" | nc -w 1 127.0.0.1 $(PORT_MULTICLIENT) || true
	@echo "test3" | nc -w 1 127.0.0.1 $(PORT_MULTICLIENT) || true
	@echo "$(GREEN)[OK] Demo multiclient complet.$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# RUN-LAB — Laborator interactiv
# ════════════════════════════════════════════════════════════════════════════
run-lab: mininet-base

mininet-base:
	@echo "$(CYAN)[MININET] Pornire topologie BAZĂ (CLI interactiv)...$(NC)"
	@echo ""
	@echo "$(YELLOW)╔══════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(YELLOW)║  Topologie: h1 ─── s1 ─── h2 ─── h3  (10.0.0.0/24)               ║$(NC)"
	@echo "$(YELLOW)╚══════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Comenzi utile în CLI mininet>:$(NC)"
	@echo "  h1 python3 python/examples/ex01_udp_broadcast.py send --count 5"
	@echo "  h2 python3 python/examples/ex01_udp_broadcast.py recv --count 5"
	@echo "  h3 tcpdump -ni h3-eth0 'udp port $(PORT_BROADCAST)'"
	@echo "  pingall"
	@echo "  exit"
	@echo ""
	$(MININET_CLI) mininet/topologies/topo_base.py --cli

mininet-extended:
	@echo "$(CYAN)[MININET] Pornire topologie EXTINSĂ (CLI interactiv)...$(NC)"
	@echo ""
	@echo "$(YELLOW)╔══════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(YELLOW)║  netA: a1,a2 ─── sA ─── r1 ─── sB ─── b1,b2 :netB               ║$(NC)"
	@echo "$(YELLOW)║  10.0.1.0/24           .254 .254           10.0.2.0/24          ║$(NC)"
	@echo "$(YELLOW)╚══════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Comenzi utile pentru TCP tunnel:$(NC)"
	@echo "  b1 python3 python/examples/ex04_echo_server.py --listen 0.0.0.0:8080"
	@echo "  r1 python3 python/examples/ex03_tcp_tunnel.py --listen 0.0.0.0:9090 --target 10.0.2.1:8080"
	@echo "  a1 bash -lc 'echo test | nc 10.0.1.254 9090 -w 2'"
	@echo ""
	$(MININET_CLI) mininet/topologies/topo_extended.py --cli

# ════════════════════════════════════════════════════════════════════════════
# CAPTURE — Capturi de trafic
# ════════════════════════════════════════════════════════════════════════════
capture: capture-broadcast capture-multicast
	@echo "$(GREEN)[OK] Capturi complete în $(PCAP_DIR)/$(NC)"

capture-broadcast:
	@echo "$(CYAN)[CAPTURE] Pornire captură broadcast...$(NC)"
	@mkdir -p $(PCAP_DIR)
	@bash scripts/capture_traffic.sh broadcast $(PORT_BROADCAST) 10

capture-multicast:
	@echo "$(CYAN)[CAPTURE] Pornire captură multicast + IGMP...$(NC)"
	@mkdir -p $(PCAP_DIR)
	@bash scripts/capture_traffic.sh multicast $(PORT_MULTICAST) 10

# ════════════════════════════════════════════════════════════════════════════
# DOCKER
# ════════════════════════════════════════════════════════════════════════════
docker-build:
	@echo "$(CYAN)[DOCKER] Construire imagine $(DOCKER_IMAGE):$(DOCKER_TAG)...$(NC)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) -f docker/Dockerfile .
	@echo "$(GREEN)[OK] Imagine construită: $(DOCKER_IMAGE):$(DOCKER_TAG)$(NC)"

docker-run:
	@echo "$(CYAN)[DOCKER] Rulare container interactiv...$(NC)"
	docker run -it --rm --privileged \
		-v $(PWD):/app \
		--workdir /app \
		--name s3-networking-dev \
		$(DOCKER_IMAGE):$(DOCKER_TAG) bash

docker-compose-up:
	@echo "$(CYAN)[DOCKER] Pornire stack docker-compose...$(NC)"
	docker-compose -f docker/docker-compose.yml up -d
	@echo "$(GREEN)[OK] Stack pornit. Verificați: docker-compose -f docker/docker-compose.yml ps$(NC)"

docker-compose-down:
	@echo "$(CYAN)[DOCKER] Oprire stack docker-compose...$(NC)"
	docker-compose -f docker/docker-compose.yml down

# ════════════════════════════════════════════════════════════════════════════
# CLEAN — Curățare
# ════════════════════════════════════════════════════════════════════════════
clean:
	@echo "$(CYAN)[CLEAN] Curățare...$(NC)"
	@bash scripts/cleanup.sh
	@rm -rf $(LOG_DIR) __pycache__ python/__pycache__ python/*/__pycache__
	@rm -f *.pcap *.pcapng
	@echo "$(GREEN)[OK] Curățare completă.$(NC)"

clean-docker:
	@echo "$(CYAN)[CLEAN] Curățare Docker...$(NC)"
	docker-compose -f docker/docker-compose.yml down -v 2>/dev/null || true
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) 2>/dev/null || true
	@echo "$(GREEN)[OK] Curățare Docker completă.$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# RESET — Reset complet
# ════════════════════════════════════════════════════════════════════════════
reset: clean
	@echo "$(CYAN)[RESET] Verificare mediu după curățare...$(NC)"
	@bash scripts/verify.sh
	@echo "$(GREEN)[OK] Reset complet.$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# PACK — Creare arhivă
# ════════════════════════════════════════════════════════════════════════════
pack:
	@echo "$(CYAN)[PACK] Creare arhivă starterkit_s3.zip...$(NC)"
	@cd .. && zip -r starterkit_s3.zip S3_Starterkit_Final \
		-x "*.pyc" -x "__pycache__/*" -x "*.pcap" -x "logs/*" -x ".git/*"
	@mv ../starterkit_s3.zip . 2>/dev/null || true
	@echo "$(GREEN)[OK] Arhivă creată: starterkit_s3.zip$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# EXPORT VARIABILE DE MEDIU
# ════════════════════════════════════════════════════════════════════════════
.EXPORT_ALL_VARIABLES:
PYTHONDONTWRITEBYTECODE = 1
PYTHONUNBUFFERED = 1
