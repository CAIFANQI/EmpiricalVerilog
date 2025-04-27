import os
import subprocess
import json
from time import sleep
from get_data import get_data
DEBUG = True
HOME = os.path.expanduser("~")
COMPILE_RES_DIR = os.path.join(HOME, "verilog_testing/scripts/compilation_results/")
COMPILE_RES_FILE = "compilation_info.csv"
DATA_DIR = os.path.join(HOME, "verilog_testing/scripts/data/revised_executables/")
SCRIPT_DIR = os.path.join(HOME, "verilog_testing/scripts/")
def LOG(msg):
    if DEBUG:
        print(msg)

progress = []

def compile_tb(year_path, repo_name, repo_abs_path, tb_abs_filepath, tb_dir, dependencies, data_dir):
    LOG("Compiling module: " + tb_abs_filepath)
    # sleep(1)
    compile_statement = ['iverilog']
    if tb_abs_filepath.split(".")[1] == "sv":
        compile_statement.append("-g2012")
    """Compile the module"""
    output = os.path.join(data_dir, year_path.split(".")[0] + ".out")
    LOG("Output: " + output)
    compile_statement.append("-o")
    compile_statement.append(output)
    compile_statement.append(tb_abs_filepath)
    # LOG([dep.rel_path for dep in self.dependencies])
    compile_statement.extend([os.path.join(repo_abs_path, dep) for dep in dependencies])
    # make parent directory
    os.makedirs(os.path.dirname(output), exist_ok=True)
    os.chdir(tb_dir)
    # LOG(compile_statement)
    try:
        result = subprocess.run(
            compile_statement,
            capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired as e:
        result = subprocess.CompletedProcess(
            args=e.cmd,
            returncode=1,  # conventionally non-zero for failure
            stdout=e.stdout,
            stderr=e.stderr or f"Process timed out after {e.timeout} seconds."
        )
    return result

def compile_revised_testbenches(data, repo_path, year_path, data_dir):
    # Get list of newly generated testbench files
    testbench_files = []
    # Execute each testbench file along with its dependencies
    count = 0
    pass_count = 0
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if not (file.endswith(".v") or file.endswith(".sv")):
                raise Exception(f"File {file} is not a Verilog/SystemVerilog file")

            tb_file = os.path.join(root, file)
            tb_relpath = os.path.relpath(tb_file, repo_path)
            year_tb_path = os.path.join(year_path, tb_relpath)
            tb_abs_filepath = os.path.join(repo_path, tb_relpath)
            tb_name = os.path.basename(tb_file)
    
            if year_tb_path not in data:
                # print(f"Skipping {tb_file}: not in data")
                # LOG(f"Skipping {tb_file}: not in data")
                continue
            LOG(f"Compiling {tb_file}")
            count += 1
            res = compile_tb(year_tb_path, data[year_tb_path]["repo_name"], data[year_tb_path]["repo_abs_path"], tb_file, os.path.dirname(data[year_tb_path]["tb_abs_filepath"]), data[year_tb_path]["dependencies"], data_dir=data_dir)
            if res.returncode != 0:
                # raise(f"Compilation failed for {tb_file}: {res.stderr}")
                LOG(f"Compilation failed for {tb_file}: ")
                # LOG(f"{res.stderr}")
                LOG(f"Return code: {res.returncode}")
                continue
            else:
                LOG(f"Compilation PASSED for {tb_file}: ")
                pass_count +=1
                # print(f"Compilation succeeded for {tb_file}")
                progress.append(tb_file)
                # os.remove(tb_path)
    return count, pass_count
if __name__ == "__main__":
    data = get_data(COMPILE_RES_DIR)
    repo_dir =  "/home/yangjin/verilog_testing/scripts/data/revised_testbenches"
    count = 0
    pass_count = 0
    for year in os.listdir(repo_dir):
        if not os.path.isdir(os.path.join(repo_dir, year)):
            continue
        for month in os.listdir(os.path.join(repo_dir, year)):
            if not os.path.isdir(os.path.join(repo_dir, year, month)):
                continue
            month_path = os.path.join(repo_dir, year, month)
            for repo in os.listdir(month_path):
                year_path = os.path.join(year, month, repo)
                repo_path = os.path.join(repo_dir, year, month, repo)
                repo_count, repo_pass_count = compile_revised_testbenches(data, repo_path=repo_path,year_path=year_path, data_dir=DATA_DIR)
                count += repo_count
                pass_count += repo_pass_count
    LOG(f"Total number of testbenches: {count}")
    LOG(f"Total number of testbenches compiled successfully: {pass_count}")
    os.chdir(SCRIPT_DIR)