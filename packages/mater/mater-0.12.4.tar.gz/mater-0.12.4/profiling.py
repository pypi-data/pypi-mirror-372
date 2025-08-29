"""This module is called to profile the MATER model with kernprof -lvr profiling.py"""

from mater import Mater

model = Mater()

model.run_from_excel("run_profiling", "mater_example.xlsx", 1901, 2100, "YS")
