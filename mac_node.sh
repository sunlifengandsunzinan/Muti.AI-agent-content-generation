#!/bin/bash
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
while true; do
  /usr/local/bin/node /usr/local/lib/node_modules/openclaw/openclaw.mjs node run \
    --host 192.168.0.112 \
    --port 18789 \
    --display-name "sunlifeng-Mac"
  sleep 3
done
