#!/usr/bin/env python3
"""Find which file get_candidate_spots reads"""
import sys, inspect
sys.path.insert(0, r"D:\moto")
from app.services import candidate_spots as cs
src = inspect.getsource(cs.get_candidate_spots.__code__) if hasattr(cs, "get_candidate_spots") and hasattr(cs.get_candidate_spots, "__code__") else inspect.getsource(cs)
print(src)
