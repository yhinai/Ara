#!/usr/bin/env bash
set -euo pipefail

pbcopy < /Users/alhinai/om1/hackathon/ara_company_launcher/ARA_ONE_LINE_PROMPT.txt
open -a Ara

cat <<'MSG'
Ara is open. A strict execution prompt is copied to your clipboard.
Paste it into Ara exactly.
If Ara still responds conversationally, double-click this backup runner:
/Users/alhinai/om1/hackathon/ara_company_launcher/bin/run_baby_band_aids.command
MSG
