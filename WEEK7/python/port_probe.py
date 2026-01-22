"""Wrapper de compatibilitate.

Implementarea canonică este în python/apps/port_probe.py.
"""

from python.apps.port_probe import main


if __name__ == "__main__":
    raise SystemExit(main())
