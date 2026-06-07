rm -rf ~/.openclaw
mkdir -p ~/.openclaw
cat > ~/.openclaw/openclaw.json << 'EOF'
{"gateway":{"auth":{"mode":"token","token":"749fdc…cd45"}}}
EOF
echo CONFIG_SET
