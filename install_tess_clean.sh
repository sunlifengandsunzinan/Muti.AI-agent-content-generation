#!/bin/bash
export PATH=/Users/sunlifeng/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin
echo "=== CLEANING ==="
rm -rf /Users/sunlifeng/Library/Caches/Homebrew/downloads/*.incomplete
rm -f /Users/sunlifeng/Library/Caches/Homebrew/*.lock
echo "=== INSTALL ==="
brew install tesseract 2>&1
EC=$?
echo "EXITCODE=$EC"
echo "=== VERSION ==="
/Users/sunlifeng/homebrew/bin/tesseract --version 2>&1 || /Users/sunlifeng/homebrew/bin/tesseract --version 2>&1 || echo "BINARY_MISSING"
echo "=== DONE ==="
exit $EC
