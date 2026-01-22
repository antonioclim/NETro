"""Wrapper de compatibilitate.

Implementarea canonică este în python/apps/tcp_server.py.
"""

from python.apps.tcp_server import main


if __name__ == "__main__":
    raise SystemExit(main())
