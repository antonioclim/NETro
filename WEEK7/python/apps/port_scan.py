"""Wrapper de compatibilitate.

Acest nume de fișier a existat în versiuni anterioare ale kitului.
Implementarea canonică: python/apps/port_probe.py
"""

from python.apps.port_probe import main

if __name__ == "__main__":
    raise SystemExit(main())
