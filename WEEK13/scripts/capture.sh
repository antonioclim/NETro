#!/bin/bash
# =============================================================================
# capture.sh - Wrapper pentru capture_traffic.sh
# =============================================================================
# Păstrat pentru compatibilitate cu scripturi existente.
# Canonical: scripts/capture_traffic.sh
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Redirecționare către scriptul principal
exec "$SCRIPT_DIR/capture_traffic.sh" "$@"
