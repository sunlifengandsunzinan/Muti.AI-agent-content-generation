#!/bin/bash
export PATH=/Users/sunlifeng/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin
echo "=== TESSERACT INSTALL ==="
brew install tesseract 2>&1
EC=$?
echo "EXITCODE=$EC"
echo ""
echo "=== VERSION ==="
/Users/sunlifeng/homebrew/bin/tesseract --version 2>&1 || echo "BINARY_MISSING"
echo "=== DONE ==="
exit $EC
