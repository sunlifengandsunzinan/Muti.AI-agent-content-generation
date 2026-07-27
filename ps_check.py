import subprocess

sc = subprocess.Popen(
    ['ssh', '-o', 'StrictHostKeyChecking=no', '192.168.0.121', '-l', 'sunlifeng',
     "ps aux | grep -E '(brew|curl|cmake|make|cc|clang)' | grep -v grep | head -5"],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
)
out, err = sc.communicate(timeout=10)
if out:
    print("Running:", out[:500])
else:
    print("No active build processes")
