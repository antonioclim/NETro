# =============================================================================
# Makefile – StarterKit Săptămâna 12: E-mail & RPC
# ASE-CSIE, Rețele de Calculatoare
# Revolvix&Hypotheticalandrei
# =============================================================================

.PHONY: help setup run-demo run-lab capture verify clean reset \
        smtp-server smtp-send smtp-list \
        jsonrpc-server jsonrpc-client \
        xmlrpc-server xmlrpc-client \
        grpc-server grpc-client proto-gen \
        benchmark-rpc \
        docker-up docker-down docker-shell \
        mininet-run selftest

# -----------------------------------------------------------------------------
# Configurații implicite
# -----------------------------------------------------------------------------
PYTHON := python3
SHELL := /bin/bash

# Porturi
SMTP_PORT := 1025
JSONRPC_PORT := 8080
XMLRPC_PORT := 8000
GRPC_PORT := 50051
HOST := 127.0.0.1

# Directoare
SPOOL := ./spool
PCAP_DIR := ./pcap

# Parametri SMTP
FROM := sender@test.local
TO := recipient@test.local
SUBJ := Test S12 Email
BODY := Mesaj de test generat din Makefile - Săptămâna 12

# -----------------------------------------------------------------------------
# Help (target implicit)
# -----------------------------------------------------------------------------
help:
	@echo ""
	@echo "╔═══════════════════════════════════════════════════════════════════════╗"
	@echo "║   StarterKit Săptămâna 12: E-mail & RPC                               ║"
	@echo "║   ASE-CSIE, Rețele de Calculatoare                                    ║"
	@echo "╚═══════════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "SETUP & VERIFICARE:"
	@echo "  make setup          - Instalează dependențele Python"
	@echo "  make verify         - Verifică instalarea și dependențele"
	@echo "  make selftest       - Rulează self-test pe toate modulele"
	@echo "  make clean          - Curăță fișiere temporare"
	@echo "  make reset          - Reset complet (clean + recreare spool)"
	@echo ""
	@echo "DEMO-URI PRINCIPALE:"
	@echo "  make run-demo       - Rulează demo-ul principal (SMTP + RPC)"
	@echo "  make run-lab        - Rulează scenariul de laborator complet"
	@echo "  make capture        - Captură pachete cu tshark"
	@echo ""
	@echo "SMTP (E-MAIL):"
	@echo "  make smtp-server    - Pornește server SMTP pe port $(SMTP_PORT)"
	@echo "  make smtp-send      - Trimite email (TO=x@y SUBJ='...' BODY='...')"
	@echo "  make smtp-list      - Listează mesajele din spool"
	@echo ""
	@echo "JSON-RPC:"
	@echo "  make jsonrpc-server - Pornește server JSON-RPC pe port $(JSONRPC_PORT)"
	@echo "  make jsonrpc-client - Rulează client JSON-RPC"
	@echo ""
	@echo "XML-RPC:"
	@echo "  make xmlrpc-server  - Pornește server XML-RPC pe port $(XMLRPC_PORT)"
	@echo "  make xmlrpc-client  - Rulează client XML-RPC"
	@echo ""
	@echo "gRPC:"
	@echo "  make proto-gen      - Generează cod Python din calculator.proto"
	@echo "  make grpc-server    - Pornește server gRPC pe port $(GRPC_PORT)"
	@echo "  make grpc-client    - Rulează client gRPC"
	@echo ""
	@echo "BENCHMARK & ANALIZĂ:"
	@echo "  make benchmark-rpc  - Benchmark comparativ JSON/XML/gRPC"
	@echo "  make capture-smtp   - Captură trafic SMTP"
	@echo "  make capture-rpc    - Captură trafic JSON-RPC"
	@echo ""
	@echo "DOCKER:"
	@echo "  make docker-up      - Pornește containere"
	@echo "  make docker-down    - Oprește containere"
	@echo "  make docker-shell   - Shell interactiv în container"
	@echo ""
	@echo "MININET:"
	@echo "  make mininet-run    - Pornește topologia Mininet"
	@echo ""

# -----------------------------------------------------------------------------
# Setup & Verificare
# -----------------------------------------------------------------------------
setup:
	@echo "[SETUP] Instalare dependențe Python..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	@echo "[SETUP] Verificare grpcio-tools (opțional)..."
	$(PYTHON) -m pip install grpcio grpcio-tools 2>/dev/null || true
	@mkdir -p $(SPOOL) $(PCAP_DIR)
	@echo "[SETUP] ✓ Instalare completă!"

verify:
	@echo "[VERIFY] Verificare mediu..."
	@echo ""
	@echo "Python:"
	@$(PYTHON) --version
	@echo ""
	@echo "Module standard:"
	@$(PYTHON) -c "import json, http.server, xmlrpc.server, smtplib; print('  ✓ Biblioteca standard OK')"
	@echo ""
	@echo "Module externe:"
	@$(PYTHON) -c "import grpc; print('  ✓ grpcio OK')" 2>/dev/null || echo "  ⚠ grpcio LIPSĂ (opțional)"
	@echo ""
	@echo "Structură fișiere:"
	@test -f src/email/smtp_server.py && echo "  ✓ smtp_server.py" || echo "  ✗ smtp_server.py LIPSĂ"
	@test -f src/rpc/jsonrpc/jsonrpc_server.py && echo "  ✓ jsonrpc_server.py" || echo "  ✗ jsonrpc_server.py LIPSĂ"
	@test -f exercises/ex_01_smtp.py && echo "  ✓ ex_01_smtp.py" || echo "  ✗ ex_01_smtp.py LIPSĂ"
	@test -f exercises/ex_02_rpc.py && echo "  ✓ ex_02_rpc.py" || echo "  ✗ ex_02_rpc.py LIPSĂ"
	@echo ""
	@echo "[VERIFY] ✓ Verificare completă!"

selftest:
	@echo "[SELFTEST] Rulare auto-teste..."
	$(PYTHON) exercises/ex_01_smtp.py --selftest
	$(PYTHON) exercises/ex_02_rpc.py --selftest
	@echo "[SELFTEST] ✓ Toate testele au trecut!"

clean:
	@echo "[CLEAN] Ștergere fișiere temporare..."
	rm -rf __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__
	rm -rf .pytest_cache .mypy_cache
	rm -rf src/rpc/grpc/*_pb2.py src/rpc/grpc/*_pb2_grpc.py
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	@echo "[CLEAN] ✓ Curățare completă!"

reset: clean
	@echo "[RESET] Recreare directoare..."
	rm -rf $(SPOOL)
	mkdir -p $(SPOOL) $(PCAP_DIR)
	@echo "[RESET] ✓ Reset complet!"

# -----------------------------------------------------------------------------
# Demo-uri principale
# -----------------------------------------------------------------------------
run-demo:
	@echo "[DEMO] Pornire demonstrație principală..."
	@echo ""
	@echo "═══════════════════════════════════════════════════════════"
	@echo "Demo 1: Server SMTP"
	@echo "═══════════════════════════════════════════════════════════"
	@mkdir -p $(SPOOL)
	$(PYTHON) src/email/smtp_server.py --port $(SMTP_PORT) --spool $(SPOOL) --demo &
	@sleep 2
	@echo ""
	@echo "Demo 2: Trimitere email de test"
	$(PYTHON) src/email/smtp_client.py --host $(HOST) --port $(SMTP_PORT) \
		--from "$(FROM)" --to "$(TO)" --subject "$(SUBJ)" --body "$(BODY)"
	@echo ""
	@echo "[DEMO] ✓ Demonstrație completă! Verificați $(SPOOL)/"
	@pkill -f "smtp_server.py" 2>/dev/null || true

run-lab:
	@echo "[LAB] Pornire scenariu de laborator complet..."
	./scripts/run_demos.sh

capture:
	@echo "[CAPTURE] Captură trafic..."
	./scripts/capture.sh

# -----------------------------------------------------------------------------
# SMTP Targets
# -----------------------------------------------------------------------------
smtp-server:
	@echo "[SMTP] Pornire server pe port $(SMTP_PORT)..."
	@mkdir -p $(SPOOL)
	$(PYTHON) src/email/smtp_server.py \
		--listen 0.0.0.0 \
		--port $(SMTP_PORT) \
		--spool $(SPOOL)

smtp-send:
	@echo "[SMTP] Trimitere email către $(TO)..."
	$(PYTHON) src/email/smtp_client.py \
		--host $(HOST) \
		--port $(SMTP_PORT) \
		--from "$(FROM)" \
		--to "$(TO)" \
		--subject "$(SUBJ)" \
		--body "$(BODY)"

smtp-list:
	@echo "[SMTP] Listare mesaje din $(SPOOL)..."
	@ls -la $(SPOOL)/ 2>/dev/null || echo "Spool gol sau inexistent"
	@echo ""
	@for f in $(SPOOL)/*.eml 2>/dev/null; do \
		if [ -f "$$f" ]; then \
			echo "═══ $$f ═══"; \
			head -20 "$$f"; \
			echo "..."; \
		fi \
	done

# -----------------------------------------------------------------------------
# JSON-RPC Targets
# -----------------------------------------------------------------------------
jsonrpc-server:
	@echo "[JSON-RPC] Pornire server pe port $(JSONRPC_PORT)..."
	$(PYTHON) src/rpc/jsonrpc/jsonrpc_server.py \
		--listen 0.0.0.0 \
		--port $(JSONRPC_PORT)

jsonrpc-client:
	@echo "[JSON-RPC] Rulare client către $(HOST):$(JSONRPC_PORT)..."
	$(PYTHON) src/rpc/jsonrpc/jsonrpc_client.py \
		--host $(HOST) \
		--port $(JSONRPC_PORT)

# -----------------------------------------------------------------------------
# XML-RPC Targets
# -----------------------------------------------------------------------------
xmlrpc-server:
	@echo "[XML-RPC] Pornire server pe port $(XMLRPC_PORT)..."
	$(PYTHON) src/rpc/xmlrpc/xmlrpc_server.py \
		--listen 0.0.0.0 \
		--port $(XMLRPC_PORT)

xmlrpc-client:
	@echo "[XML-RPC] Rulare client către $(HOST):$(XMLRPC_PORT)..."
	$(PYTHON) src/rpc/xmlrpc/xmlrpc_client.py \
		--host $(HOST) \
		--port $(XMLRPC_PORT)

# -----------------------------------------------------------------------------
# gRPC Targets
# -----------------------------------------------------------------------------
proto-gen:
	@echo "[gRPC] Generare cod din calculator.proto..."
	cd src/rpc/grpc && $(PYTHON) -m grpc_tools.protoc \
		-I. \
		--python_out=. \
		--grpc_python_out=. \
		calculator.proto
	@echo "[gRPC] ✓ Fișiere generate: calculator_pb2.py, calculator_pb2_grpc.py"

grpc-server: proto-gen
	@echo "[gRPC] Pornire server pe port $(GRPC_PORT)..."
	$(PYTHON) src/rpc/grpc/grpc_server.py \
		--port $(GRPC_PORT)

grpc-client:
	@echo "[gRPC] Rulare client către $(HOST):$(GRPC_PORT)..."
	$(PYTHON) src/rpc/grpc/grpc_client.py \
		--host $(HOST) \
		--port $(GRPC_PORT)

# -----------------------------------------------------------------------------
# Benchmark
# -----------------------------------------------------------------------------
benchmark-rpc:
	@echo "[BENCHMARK] Comparație JSON-RPC vs XML-RPC vs gRPC..."
	@echo ""
	@echo "⚠ Asigurați-vă că serverele rulează în terminale separate!"
	@echo "  Terminal 1: make jsonrpc-server"
	@echo "  Terminal 2: make xmlrpc-server"
	@echo "  Terminal 3: make grpc-server (opțional)"
	@echo ""
	./scripts/benchmark_rpc.sh 2>/dev/null || $(PYTHON) -c "\
import time, json, urllib.request; \
print('Benchmark simplificat:'); \
start = time.time(); \
for i in range(100): \
    try: \
        req = urllib.request.Request('http://127.0.0.1:$(JSONRPC_PORT)', \
            data=json.dumps({'jsonrpc':'2.0','method':'add','params':[1,2],'id':i}).encode(), \
            headers={'Content-Type':'application/json'}); \
        urllib.request.urlopen(req, timeout=1); \
    except: pass; \
print(f'JSON-RPC: 100 calls in {time.time()-start:.2f}s')"

# -----------------------------------------------------------------------------
# Captură trafic
# -----------------------------------------------------------------------------
capture-smtp:
	@echo "[CAPTURE] Captură trafic SMTP pe port $(SMTP_PORT)..."
	sudo tcpdump -i lo -nn -A port $(SMTP_PORT) -c 50

capture-rpc:
	@echo "[CAPTURE] Captură trafic JSON-RPC pe port $(JSONRPC_PORT)..."
	sudo tcpdump -i lo -nn -A port $(JSONRPC_PORT) -c 30

# -----------------------------------------------------------------------------
# Docker Targets
# -----------------------------------------------------------------------------
docker-up:
	@echo "[DOCKER] Pornire containere..."
	docker compose -f docker/docker-compose.yml up -d
	@echo "[DOCKER] ✓ Containere pornite. Verificare: docker ps"

docker-down:
	@echo "[DOCKER] Oprire containere..."
	docker compose -f docker/docker-compose.yml down
	@echo "[DOCKER] ✓ Containere oprite."

docker-shell:
	@echo "[DOCKER] Shell interactiv..."
	docker compose -f docker/docker-compose.yml exec lab bash 2>/dev/null || \
		docker run -it --rm -v $$(pwd):/app -w /app python:3.11-slim bash

# -----------------------------------------------------------------------------
# Mininet Target
# -----------------------------------------------------------------------------
mininet-run:
	@echo "[MININET] Pornire topologie..."
	sudo $(PYTHON) mininet/topo_s12.py --cli
