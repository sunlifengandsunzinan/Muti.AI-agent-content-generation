export PATH=/usr/local/bin:$PATH
pkill -f oc_node 2>/dev/null
pkill -f 'openclaw.*node' 2>/dev/null
sleep 1
screen -wipe 2>/dev/null
screen -dmS oc_node bash -c 'export PATH=/usr/local/bin:$PATH; while true; do openclaw node run --host 192.168.0.112 --port 18789 --display-name sunlifeng-Mac; sleep 5; done'
echo NODE_STARTED
