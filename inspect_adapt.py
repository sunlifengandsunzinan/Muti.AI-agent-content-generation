#!/usr/bin/env python3
"""Check candidate pipeline"""
import sys, inspect
sys.path.insert(0, r"D:\moto")
from scripts.adapt_openclaw_candidates import adapt_openclaw_candidate
src = inspect.getsource(adapt_openclaw_candidate)
print(src[:1200])
