export PATH=/usr/local/bin:/opt/homebrew/bin:$PATH

# Install curl via brew if available
if command -v brew &>/dev/null; then
  echo "Brew available, skipping curl install"
else
  echo "No brew, installing..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" 2>/dev/null
fi

# Try curl again
command -v curl 2>/dev/null && echo "curl found" && curl --version | head -1

# If no curl, use a simple node script
if ! command -v curl &>/dev/null; then
  echo "No curl, using node"
fi
