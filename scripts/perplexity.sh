#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi
query="${1:-}"
if [[ -z "$query" ]]; then echo 'usage: bash scripts/perplexity.sh "<query>"' >&2; exit 1; fi
if [[ -z "${PERPLEXITY_API_KEY:-}" ]]; then
  echo "WARNING: PERPLEXITY_API_KEY not set. Fall back to WebSearch/manual research." >&2
  exit 3
fi
MODEL="${PERPLEXITY_MODEL:-sonar}"
payload="$(python3 -c 'import json,sys; print(json.dumps({"model":sys.argv[1],"messages":[{"role":"system","content":"You are a precise financial research assistant. Cite every claim. Be concise."},{"role":"user","content":sys.argv[2]}]}))' "$MODEL" "$query")"
key_var="PERPLEXITY_API_KEY"
auth_header="Authorization: Bearer ${!key_var}"
curl -fsS https://api.perplexity.ai/chat/completions \
  -H "$auth_header" \
  -H "Content-Type: application/json" \
  -d "$payload"
echo
