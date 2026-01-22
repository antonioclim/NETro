"""Wrapper de compatibilitate.

Implementarea canonică este în python/apps/port_scan.py.
"""

from python.apps.port_scan import main


if __name__ == "__main__":
    raise SystemExit(main())
