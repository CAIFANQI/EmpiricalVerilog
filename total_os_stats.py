import os
import json
MODULE_DATA_FILE = os.path.join(os.path.expanduser("~"), "verilog_testing/scripts/data/module_data.jsonl")
EXECUTED_MODULE_DATA_FILE = os.path.join(os.path.expanduser("~"), "verilog_testing/scripts/data/executed_module_data.jsonl")
DATA_DIR = os.path.join(os.path.expanduser("~"), "verilog_testing/data")
OUTPUT_FILE = os.path.join(os.path.expanduser("~"), "verilog_testing/scripts/data/total_os_stats.json")
MOD_LIST = "module_list.csv"
TB_LIST = "testbench_list.csv"

module_data = []
executed_module_data = []
repos_by_year = {}
with open(MODULE_DATA_FILE, 'r') as file:
    for line in file:
        module_data.append(json.loads(line.strip()))
    file.close()

with open(EXECUTED_MODULE_DATA_FILE, 'r') as file:
    for line in file:
        executed_module_data.append(json.loads(line.strip()))
        
res = {
    "total": {
        "total_modules": 0,
        "total_modules_excluding primitives": 0,
        "total_tbs": 0,
        "total_modules_with_compilable_tbs": len(module_data),
        "total_modules_with_executable_tbs": len(executed_module_data),
        "total_repositories": 0,
        "total_repositories_with_tbs": 0,
        "total_repositories_with_compilable_tbs": 0,
        "total_repositories_with_executable_tbs": 0,
        "percent_of_modules_covered": 0
    }
}
for i in range(2008, 2026):
    res[str(i)] = {
        "total_modules": 0,
        "total_modules_excluding primitives": 0,
        "total_tbs": 0,
        "total_modules_with_compilable_tbs": 0,
        "total_modules_with_executable_tbs": 0,
        "total_repositories": 0,
        "total_repositories_with_tbs": 0,
        "total_repositories_with_compilable_tbs": 0,
        "total_repositories_with_executable_tbs": 0,
        "percent_of_modules_covered": 0
    }
for year in os.listdir(DATA_DIR):
    if not os.path.isdir(os.path.join(DATA_DIR, year)):
        continue
    year_path = os.path.join(DATA_DIR, year)
    for month in os.listdir(year_path):
        month_path = os.path.join(year_path, month)
        if not os.path.isdir(month_path):
            continue
        for repo in os.listdir(month_path):
            repo_path = os.path.join(month_path, repo)
            if not os.path.isdir(repo_path):
                continue
            res["total"]["total_repositories"] += 1
            res[str(year)]["total_repositories"] += 1

            mod_list = os.path.join(repo_path, MOD_LIST)
            tb_list = os.path.join(repo_path, TB_LIST)

            with open(mod_list) as f:
                lines = f.readlines()
                for line in lines:
                    parse = line.strip().split(",")
                    rel_filepath = parse[0]
                    modules = parse[1:]
                    res["total"]["total_modules"] += len(modules)
                    res[str(year)]["total_modules"] += len(modules)
                    if len(modules) <= 5:
                        res["total"]["total_modules_excluding primitives"] += len(modules)
                        res[str(year)]["total_modules_excluding primitives"] += len(modules)
            f.close()
            
            with open(tb_list) as f:
                lines = f.readlines()
                has_tbs = False
                for line in lines:
                    if len(line.strip().split(",")) < 2:
                        continue
                    has_tbs = True
                    # get the filepath of the testbench
                    parse = line.strip().split(",")
                    rel_filepath = parse[0]
                    tb = parse[1]
                    res["total"]["total_tbs"] += 1
                    res[str(year)]["total_tbs"] += 1
                    res["total"]["total_modules"] -= 1
                    res[str(year)]["total_modules"] -= 1
                    res["total"]["total_modules_excluding primitives"] -= 1
                    res[str(year)]["total_modules_excluding primitives"] -= 1
                if has_tbs:
                    res["total"]["total_repositories_with_tbs"] += 1
                    res[str(year)]["total_repositories_with_tbs"] += 1
            f.close()

repos_by_year = {}
for mod_data in module_data:
    res[mod_data["year"]]["total_modules_with_compilable_tbs"] += 1
    if mod_data["year"] not in repos_by_year:
        repos_by_year[mod_data["year"]] = set()

    if mod_data["project_name"] not in repos_by_year[mod_data["year"]]:
        repos_by_year[mod_data["year"]].add(mod_data["project_name"])
        res["total"]["total_repositories_with_compilable_tbs"] += 1
        res[mod_data["year"]]["total_repositories_with_compilable_tbs"] += 1

repos_by_year = {}
for mod_data in executed_module_data:
    if mod_data["year"] not in repos_by_year:
        repos_by_year[mod_data["year"]] = set()

    res[mod_data["year"]]["total_modules_with_executable_tbs"] += 1
    if mod_data["project_name"] not in repos_by_year[mod_data["year"]]:
        repos_by_year[mod_data["year"]].add(mod_data["project_name"])
        res["total"]["total_repositories_with_executable_tbs"] += 1
        res[mod_data["year"]]["total_repositories_with_executable_tbs"] += 1

# calculate the percentage of modules covered
for year in res.keys():
    if res[year]["total_modules"] > 0:
        res[year]["percent_of_modules_covered"] = (res[year]["total_modules_with_executable_tbs"] / res[year]["total_modules"]) * 100
        if year == '2011':
            print(res[year]["total_modules_with_executable_tbs"])
            print(res[year]["total_modules"])
            print(res[year]["total_modules_with_executable_tbs"] / res[year]["total_modules"])

    else:
        res[year]["percent_of_modules_covered"] = 0
# send results to output file
with open(OUTPUT_FILE, 'w') as file:
    json.dump(res, file, indent=4)
    print(f"Output written to {OUTPUT_FILE}")