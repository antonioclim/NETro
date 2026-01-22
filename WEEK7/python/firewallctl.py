"""Wrapper de compatibilitate.

Implementarea canonică este în python/apps/firewallctl.py.
"""

from python.apps.firewallctl import main


if __name__ == "__main__":
    raise SystemExit(main())
