#!/bin/bash
export PATH="/usr/local/bin:$PATH"
while true; do
  openclaw node run --host 192.168.0.112 --port 18789 --display-name "sunlifeng-Mac"
  sleep 3
done
