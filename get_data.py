"""Collect data from all compilation result csvs and return as a list of dicts
"""
import os
def get_data(dirpath):
    res = {}
    count = 0
    for files in os.listdir(dirpath):
        filepath = os.path.join(dirpath, files)
        with open(filepath, 'r') as file:
            lines = file.readlines()
            for line in lines:
                cols = line.strip().split(",")
                if len(cols) < 5:
                    print(f"Skipping line in {files}: {line.strip()}")
                    continue
                abs_path = cols[0]

                    
                tb_relpath = cols[1]
                year_path = ""
                if "verilog-repos/saverepo" in abs_path:
                    year_path = "/".join(abs_path.split("/")[6:]) 
                else:
                    year_path = "/".join(abs_path.split("/")[5:])
                year_path = os.path.join(year_path, tb_relpath)
                tb_abs_filepath = os.path.join(abs_path, tb_relpath)
                tb_name = tb_relpath.split("/")[-1]
                if tb_abs_filepath in res:
                    # print(f"Skipping line in {files}: {line.strip()}")
                    count += 1
                    continue
                main_dep_names = cols[2].split(";")
                if len(main_dep_names) == 1 and main_dep_names[0] == "":
                    main_dep_names = []
                main_deps = cols[3].split(";")
                if len(main_deps) == 1 and main_deps[0] == "":
                    main_deps = []
                dependencies = cols[4].split(";")
                if len(dependencies) == 1 and dependencies[0] == "":
                    dependencies = []
                res[year_path] = {
                    "tb_year_path": year_path,
                    "repo_abs_path": abs_path,
                    "tb_relpath": tb_relpath,
                    "tb_abs_filepath": tb_abs_filepath,
                    "main_dep_names": main_dep_names,
                    "main_deps": main_deps,
                    "dependencies": dependencies,
                    "repo_name": abs_path.split("/")[-1],
                }
    print(f"Total skipped lines: {count}")
    return res