#!/usr/bin/env bash
set -euo pipefail

URL="${URL:-https://sensespace-did-mcp-974618882715.us-central1.run.app/mcp}"
PROTO_VER="${PROTO_VER:-2025-06-18}"
TOKEN="eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NTYxMTM4ODAuODUyMTUzLCJleHAiOjE3NTg3MDU4ODAuODUyMTUzLCJuYmYiOjE3NTYxMTM4ODAuODUyMTU0LCJpc3MiOiJzZW5zZXNwYWNlIiwic3ViIjoiNUg5UUxrODE1U3ZMaDdFQlZrWVBQS05xVHY5RlpQcDhmM211bUVLUVhVcldVWHByIn0.lN36nrX8kgG6mJLIo49ViSnzOPs5CMF6_TdJaOrSQnYcALsSMmFP3LvMBSIc9cJyltP_eD0I2pTQzhFVjKxhBA" 
SEND_INITIALIZED="${SEND_INITIALIZED:-true}"

INIT_BODY='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"'"$PROTO_VER"'","capabilities":{},"clientInfo":{"name":"curl-client","version":"0.1.0"}}}'
NOTIFY_BODY='{"jsonrpc":"2.0","method":"notifications/initialized"}'
LIST_BODY='{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'

hdrs=(
  -H "Content-Type: application/json"
  -H "Accept: application/json, text/event-stream"
  -H "MCP-Protocol-Version: ${PROTO_VER}"
)
[[ -n "$TOKEN" ]] && hdrs+=(-H "Authorization: Bearer ${TOKEN}")

# -- Step 1: initialize --
echo "===== Sending initialize (headers + body) ====="
curl -v -X POST "$URL" "${hdrs[@]}" --data "$INIT_BODY" || true

# Extract session ID for subsequent calls
SESSION_ID=$(curl -sS -D - -o /dev/null -X POST "$URL" "${hdrs[@]}" --data "$INIT_BODY" \
  | awk -F': ' 'BEGIN{IGNORECASE=1} tolower($1)=="mcp-session-id" {gsub(/\r/,"",$2); print $2}' | tail -n1 || true)

if [[ -z "$SESSION_ID" ]]; then
  echo "✖ Failed to extract Mcp-Session-Id"
  exit 1
fi
echo "✓ Extracted Session ID: $SESSION_ID"
hdrs+=(-H "Mcp-Session-Id: ${SESSION_ID}")

# -- Step 2: notifications/initialized (optional) --
if [[ "$SEND_INITIALIZED" == "true" ]]; then
  echo -e "\n===== Sending notifications/initialized (headers + body) ====="
  curl -v -X POST "$URL" "${hdrs[@]}" --data "$NOTIFY_BODY" || true
fi

# -- Step 3: tools/list (complete dump) --
echo -e "\n===== Sending tools/list (complete request & response) ====="
curl -v -X POST "$URL" "${hdrs[@]}" --data "$LIST_BODY" || true
