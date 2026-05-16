#!/usr/bin/env bash
set -euo pipefail

cd /Users/alhinai/om1

if [[ -f hackathon/ara_company_launcher/.env ]]; then
  set -a
  # shellcheck disable=SC1091
  source hackathon/ara_company_launcher/.env
  set +a
fi

IDEA="${1:-Sell baby Band-Aids for \$1 today}"

uv run python hackathon/ara_company_launcher/launch_company.py "$IDEA"
