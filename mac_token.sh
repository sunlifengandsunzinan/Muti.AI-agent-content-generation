rm -rf ~/.openclaw
mkdir -p ~/.openclaw
cat > ~/.openclaw/openclaw.json << 'EOF'
{"gateway":{"auth":{"mode":"token","token":"749fdc49ae959deb392819b81e93477bf01e12b9b83bcd45"}}}
EOF
cat ~/.openclaw/openclaw.json
