"""Wrapper de compatibilitate.

Implementarea canonică este în python/apps/udp_server.py.
"""

from python.apps.udp_server import main


if __name__ == "__main__":
    raise SystemExit(main())
