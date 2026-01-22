#!/bin/bash
# =============================================================================
# clean.sh - Wrapper pentru cleanup.sh
# =============================================================================
# Păstrat pentru compatibilitate cu scripturi existente.
# Canonical: scripts/cleanup.sh
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Redirecționare către scriptul principal
exec "$SCRIPT_DIR/cleanup.sh" "$@"
