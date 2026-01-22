#!/usr/bin/env python3
"""backend_server.py — Server HTTP simplu pentru demonstrații load balancing.

Expune endpoint-uri:
  GET /         → răspuns cu ID-ul backend-ului
  GET /health   → health check (200 OK)
  GET /info     → informații detaliate (JSON)
  GET /slow     → răspuns întârziat (pentru teste latență)

Utilizare:
  python3 backend_server.py --id app1 --port 8000
"""

from __future__ import annotations

import argparse
import json
import socket
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from typing import Dict, Any


class BackendHandler(BaseHTTPRequestHandler):
    """Handler HTTP cu endpoint-uri pentru demo și testare."""

    server_id: str = "backend"
    start_time: float = time.time()
    request_count: int = 0

    def log_message(self, format: str, *args) -> None:
        """Logging cu timestamp și identificator."""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{ts}] [{self.server_id}] {format % args}")

    def _send_response(self, status: int, content_type: str, body: bytes) -> None:
        """Trimite răspuns HTTP complet."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Backend-ID", self.server_id)
        self.send_header("X-Request-Count", str(BackendHandler.request_count))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        """Procesează cereri GET."""
        BackendHandler.request_count += 1
        path = self.path.split("?")[0]  # ignoră query params

        if path == "/" or path == "/index":
            body = f"Hello from {self.server_id}!\n".encode("utf-8")
            self._send_response(200, "text/plain; charset=utf-8", body)

        elif path == "/health":
            body = b"OK\n"
            self._send_response(200, "text/plain; charset=utf-8", body)

        elif path == "/info":
            info: Dict[str, Any] = {
                "id": self.server_id,
                "hostname": socket.gethostname(),
                "uptime_seconds": round(time.time() - BackendHandler.start_time, 2),
                "request_count": BackendHandler.request_count,
                "timestamp": datetime.now().isoformat(),
                "client_address": f"{self.client_address[0]}:{self.client_address[1]}",
            }
            body = json.dumps(info, indent=2, ensure_ascii=False).encode("utf-8")
            self._send_response(200, "application/json; charset=utf-8", body)

        elif path == "/slow":
            # Simulează procesare lentă
            delay = 0.5
            time.sleep(delay)
            body = f"Slow response from {self.server_id} (delay={delay}s)\n".encode("utf-8")
            self._send_response(200, "text/plain; charset=utf-8", body)

        elif path == "/echo":
            # Echo headers pentru debugging
            headers_dict = {k: v for k, v in self.headers.items()}
            body = json.dumps(headers_dict, indent=2).encode("utf-8")
            self._send_response(200, "application/json; charset=utf-8", body)

        else:
            body = f"404 Not Found: {path}\n".encode("utf-8")
            self._send_response(404, "text/plain; charset=utf-8", body)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Server HTTP backend pentru demo load balancing"
    )
    parser.add_argument(
        "--id",
        default="backend",
        help="Identificator unic al backend-ului (default: backend)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Adresa de bind (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Portul de ascultare (default: 8000)"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    BackendHandler.server_id = args.id
    BackendHandler.start_time = time.time()
    BackendHandler.request_count = 0

    server_address = (args.host, args.port)
    httpd = HTTPServer(server_address, BackendHandler)
    
    print(f"[{args.id}] Pornire server HTTP pe {args.host}:{args.port}")
    print(f"[{args.id}] Endpoint-uri: /, /health, /info, /slow, /echo")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n[{args.id}] Oprire...")
    finally:
        httpd.server_close()
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
