rm -f /tmp/openclaw-node2.log
export PATH=/usr/local/bin:$PATH
pkill -f openclaw 2>/dev/null
sleep 2
export NODE_OPTIONS=""
openclaw node run --host 192.168.0.112 --port 18789 --display-name sunlifeng-Mac > /tmp/openclaw-node2.log 2>&1
