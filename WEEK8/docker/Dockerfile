# =============================================================================
# Dockerfile: Server HTTP Python
# Seminar 8 - Rețele de Calculatoare, ASE București
# =============================================================================
# Utilizare:
#   docker build -t http-server .
#   docker run -p 8080:8080 http-server
# =============================================================================

FROM python:3.11-slim

LABEL maintainer="ASE CSIE - Rețele de Calculatoare"
LABEL description="Server HTTP demonstrativ pentru Seminar 8"
LABEL version="1.0"

# Variabile de mediu configurabile
ENV HTTP_PORT=8080
ENV WWW_DIR=/var/www

# Directorul de lucru
WORKDIR /app

# Copiază codul serverului
COPY python/utils/net_utils.py /app/python/utils/
COPY python/demos/demo_http_server.py /app/python/demos/

# Creează directorul pentru conținut static
RUN mkdir -p ${WWW_DIR}

# Copiază conținut web implicit
COPY www/ ${WWW_DIR}/

# Expune portul configurat
EXPOSE ${HTTP_PORT}

# Verificare sănătate
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:${HTTP_PORT}/')" || exit 1

# Comandă de pornire
CMD ["python3", "-m", "python.demos.demo_http_server", "--port", "${HTTP_PORT}", "--www", "${WWW_DIR}"]

# Alternativ, pentru shell expansion:
# ENTRYPOINT ["sh", "-c", "python3 -m python.demos.demo_http_server --port ${HTTP_PORT} --www ${WWW_DIR}"]
