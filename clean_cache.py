import subprocess

# Clean all incomplete and locks, then check what's cached
script = r"""
rm -rf /Users/sunlifeng/Library/Caches/Homebrew/downloads/*.incomplete
rm -f /Users/sunlifeng/Library/Caches/Homebrew/*.lock
echo "Cleaned"
# Check what's in Cache
ls /Users/sunlifeng/Library/Caches/Homebrew/downloads/ 2>/dev/null | wc -l
echo " cached files"
"""
proc = subprocess.Popen(
    ['ssh', '-o', 'StrictHostKeyChecking=no', '192.168.0.121', '-l', 'sunlifeng', script],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
)
out, err = proc.communicate(timeout=10)
print(out)
if err: print(err)
