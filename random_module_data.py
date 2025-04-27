# Get the results in the compilation csvs and consolidate them into a jsonl file usable for other ML tasks
import re
import os
import json
import pickle
import random
from consolidate_module_data import get_module_contents

HOME = os.path.expanduser("~")
DATA_DIR = os.path.join(HOME, "verilog_testing/data")
OUTPUT_FILE = os.path.join(HOME, "verilog_testing/scripts/data/module_random_data_2500.jsonl")
PICKLE_DIR = os.path.join(HOME, "verilog_testing/scripts/data")
REPO_DIR_1 = os.path.join(HOME, "verilog_testing/verilog-repos/saverepo")
REPO_DIR_2 = os.path.join(HOME, "verilog_testing/verilog-repos2")

def get_modules(data_dir, repo_dir, mod_list = "module_list.csv"):
    """Initialize the modules in the repository The module data file should be of the format:
    <relative_path>, <module_name_1>, <module_name_2>, ...
    The testbench data file should be of the format:
    <relative_path>, <module_name>
    """
    res = []
    if not os.path.exists(os.path.join(data_dir, mod_list)):
        raise Exception("Module list does not exist: " + os.path.join(data_dir, mod_list))

    # Look for modules
    with open(os.path.join(data_dir, mod_list), "r") as f:
        lines = f.readlines()
        for line in lines:
            parse = line.strip().split(",")
            rel_filepath = parse[0]
            file_path = os.path.join(repo_dir, rel_filepath)
            modules = parse[1:]
            for module_name in modules:
                file_name = os.path.basename(file_path)
                if not os.path.exists(os.path.join(repo_dir, rel_filepath)):
                    # LOG("Path does not exist: " + rel_filepath)
                    continue
                entry = {
                    "filepath": file_path,
                    "file_name": file_name,
                    "module_name": module_name,
                }   
                res.append(entry)
    return res
                
            

                


if __name__ == "__main__":
    count = 1
    total_db_path = os.path.join(HOME, "verilog_testing/data")
    modules = []
    for year in os.listdir(total_db_path):
        # check for pickle file
        if os.path.exists(os.path.join(PICKLE_DIR, "module_data.pkl")):
            with open(os.path.join(PICKLE_DIR, "module_data.pkl"), "rb") as f:
                modules = pickle.load(f)
            print("Loaded modules from pickle file")
            break
        year_path = os.path.join(total_db_path, year)
        month_path = ""
        year_repo_path = os.path.join(REPO_DIR_1, year)
        if not os.path.isdir(year_path):
            year_repo_path = os.path.join(REPO_DIR_2, year)
            if not os.path.isdir(year_repo_path):
                raise Exception("Path does not exist for year: " + year_path)

        for month in os.listdir(year_path):
            month_path = os.path.join(year_path, month)
            month_repo_path = os.path.join(year_repo_path, month)
            if not os.path.isdir(month_path):
                raise Exception("Path does not exist for month: " + month_path)
            for repo in os.listdir(month_path):
                repo_data_path = os.path.join(month_path, repo)
                repo_path = os.path.join(month_repo_path, repo)
                if not os.path.isdir(repo_data_path):
                    raise Exception("Path does not exist for repo: " + repo_data_path)
                print("Processing repo: " + str(count))
                count += 1
                entry = {
                    "year": year,
                    "month": month,
                    "project_name": repo,
                    "filepath": "",
                    "file_name": "",
                    "module_name": "",
                }
                mods = get_modules(repo_data_path, repo_path)
                for m in mods:
                    entry["filepath"] = m["filepath"]
                    entry["file_name"] = m["file_name"]
                    entry["module_name"] = m["module_name"]
                    modules.append(entry)
    # pickle the modules
    if not os.path.exists(PICKLE_DIR):
        with open(os.path.join(PICKLE_DIR, "module_data.pkl"), "wb") as f:
            pickle.dump(modules, f)
                    
    # total modules
    print(f"Total modules: {len(modules)}")
    # Get 10000 random modules
    random_modules = random.sample(modules, 2500)
    # Get module contents
    rand_mods = []
    count = 1
    for module in random_modules:
        print(f"Processing module: {count}")
        count += 1
        module_name = module["module_name"]
        file_path = module["filepath"]
        content = get_module_contents(module_name, file_path)
        if not content:
            print(f"Module not found: {module_name} in {file_path}")
            continue
        module["module_contents"] = content
        if module["module_contents"] == "":
            print(f"Module contents empty: {module_name} in {file_path}")
            continue
        rand_mods.append(module)
    
    # Save the randmods to a JSONL file
    with open(OUTPUT_FILE, "w") as f:
        for module in rand_mods:
            f.write(json.dumps(module) + "\n")
    print(f"Module data saved to {OUTPUT_FILE}")
    
    
                    
