"""
1. Get the total number of working testbenches from get_valid_tbs.py
2. Verify that get_data.py returns the same number of entries as (1)
3. Get the total number of revised testbenches compiled
"""
import os
from get_data import get_data
HOME = os.path.expanduser("~")
COMPILE_RES_DIR = os.path.join(HOME, "verilog_testing/scripts/compilation_results/")
REVISED_TB_DIR = os.path.join(HOME, "verilog_testing/scripts/data/revised_testbenches/")
count = 0
for file in os.listdir(COMPILE_RES_DIR):
    if file.endswith(".csv"):
        file_path = os.path.join(COMPILE_RES_DIR, file)
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                count +=1 
print(f"Total number of lines: {count}")

data = get_data(COMPILE_RES_DIR)
print(f"Total number of lines in data: {len(data)}")

count = 0
for root, dirs, files in os.walk(REVISED_TB_DIR):
    for file in files:
        count += 1
print(f"Total number of revised testbenches: {count}")