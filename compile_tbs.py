# Compiles the testbenches that passed the get_valid_tbs.py 
# This is meant as a sanity check to make sure that all get_valid_tb results compile 
import os
import subprocess
from get_data import get_data
HOME = os.path.expanduser("~")
COMPILE_RES_DIR = os.path.join(HOME, "verilog_testing/scripts/compilation_results/")
DATA_DIR = os.path.join(HOME, "verilog_testing/scripts/data/executables/")
COMPILER = "iverilog"

def LOG(msg):
    print(msg)

def compile_tb(year_path, repo_abs_path, tb_abs_filepath, dependencies, data_dir):
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
    os.chdir(os.path.dirname(tb_abs_filepath))
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

if __name__ == "__main__":
    data = get_data(COMPILE_RES_DIR)
    repo_dir =  "/home/yangjin/verilog_testing/scripts/data/revised_testbenches"
    pass_count = 0
    total = 0
    for d in data:
        res = compile_tb(
            data[d]["tb_year_path"],
            data[d]["repo_abs_path"],
            data[d]["tb_abs_filepath"],
            data[d]["dependencies"],
            DATA_DIR
        )
        print(f"testbench: {data[d]['tb_relpath']}")
        print(f"return code: {res.returncode}")
        if res.returncode == 0:
            print("Compilation successful")
            pass_count += 1
        else:
            print("Compilation failed")
        total += 1


        
        
        
    count = 0
    
    LOG(f"Total number of testbenches: {count}")
    LOG(f"Total number of testbenches compiled successfully: {pass_count}")