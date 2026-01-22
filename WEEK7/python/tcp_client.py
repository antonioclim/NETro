"""Wrapper de compatibilitate.

Implementarea canonică este în python/apps/tcp_client.py.
"""

from python.apps.tcp_client import main


if __name__ == "__main__":
    raise SystemExit(main())
