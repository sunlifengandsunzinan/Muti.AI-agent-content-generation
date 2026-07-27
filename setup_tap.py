import subprocess

# Fix: tap homebrew-core first, then install
script = r"""
export PATH=/Users/sunlifeng/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
echo "Setting up homebrew-core..."
brew tap homebrew/core 2>&1
echo "=== TAP DONE ==="
"""
proc = subprocess.Popen(
    ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ServerAliveInterval=15',
     '192.168.0.121', '-l', 'sunlifeng',
     'cat > /tmp/setup_tap.sh && bash /tmp/setup_tap.sh'],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
)
stdout, _ = proc.communicate(script.encode('utf-8'), timeout=600)
output = stdout.decode('utf-8', errors='replace')
print(output[-1500:])
print(f"=== Exit: {proc.returncode} ===")
