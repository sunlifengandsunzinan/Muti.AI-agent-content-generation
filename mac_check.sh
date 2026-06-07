export PATH=/usr/local/bin:$PATH
openclaw --version 2>&1
echo "SEPARATOR"
openclaw status 2>&1 | head -5
