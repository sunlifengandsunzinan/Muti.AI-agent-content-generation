rm -f /tmp/openclaw-node2.log
export PATH=/usr/local/bin:$PATH
pkill -f openclaw 2>/dev/null
sleep 3
screen -wipe 2>/dev/null
screen -dmS oc_node bash -c 'export PATH=/usr/local/bin:$PATH; while true; do openclaw node run --host 192.168.0.112 --port 18789 --display-name sunlifeng-Mac; sleep 10; done'
echo SCREEN_STARTED
