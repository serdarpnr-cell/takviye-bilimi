#!/bin/bash
# Cloud oturumları temiz başlar; graphify CLI'ı (graphifyy paketi) her seferinde kurulur.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

pip install --quiet --disable-pip-version-check graphifyy
