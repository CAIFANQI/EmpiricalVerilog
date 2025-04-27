import subprocess
import threading
import os
import json
from get_data import get_data

MODULE_DATA_FILE = os.path.join(os.path.expanduser("~"), "verilog_testing/scripts/data/module_data.jsonl")
EXECUTABLES_DIR = os.path.join(os.path.expanduser("~"), "verilog_testing/scripts/data/executables/")
OUTPUT_FILE = os.path.join(os.path.expanduser("~"), "verilog_testing/scripts/data/executed_module_data.jsonl")

def run_vpp_sim(executable_path):
    proc = subprocess.Popen(
        ["vvp", executable_path],  # replace with your actual VPP command
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    error_seen = False

    def read_output():
        nonlocal error_seen
        err_keywords = ["wrong", "error", "fatal", "incorrect", "bad", "fail", "failed", "exception"]
        for line in proc.stdout:
            if "FATAL" in line or "ERROR" in line:
                print(line)
                error_seen = True
            if any(keyword in line.lower() for keyword in err_keywords):
                print(line)

        for line in proc.stderr:
            if "FATAL" in line or "ERROR" in line:
                print(line)
                error_seen = True

    reader = threading.Thread(target=read_output)
    reader.start()

    try:
        proc.wait(timeout=1)
    except subprocess.TimeoutExpired:
        proc.kill()

    reader.join()
    return(1 if error_seen else 2)

def get_executable(executable_dir, year, month, repo, tb_abs_path):
    # split the path starting from the year with the rest of the path
    year_path = tb_abs_path.split(year + "/" + month + "/" + repo + "/")[1].split(".")[0] + ".out"
    executable_path = os.path.join(executable_dir, year)
    executable_path = os.path.join(executable_path, month)
    executable_path = os.path.join(executable_path, repo)
    executable_path = os.path.join(executable_path, year_path)
    return executable_path

def write_output(output, data):
    """
    Writes the given data to the OUTPUT_FILE in JSONL format.

    Args:
        data (list): A list of dictionaries containing module information.
    """
    try:
        with open(output, 'w') as file:
            for entry in data:
                file.write(json.dumps(entry) + '\n')
        print(f"Output written to {output}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    res = []
    module_data = []
    with open(MODULE_DATA_FILE, 'r') as file:
        for line in file:
            module_data.append(json.loads(line.strip()))
        file.close()
    executed_tbs = set()
    successfully_executed = set()

    for m in module_data:
        executable_path = get_executable(EXECUTABLES_DIR, m["year"], m["month"], m["project_name"], m["testbench_path"])
        if executable_path in successfully_executed:
            res.append(m)
            print(f"Executable {executable_path} already executed successfully. Skipping.")
            continue
        if executable_path in executed_tbs:
            print(f"Executable {executable_path} already executed. Skipping.")
            continue

        exec_res = run_vpp_sim(executable_path)
        executed_tbs.add(executable_path)
        if exec_res == 2:
            successfully_executed.add(executable_path)
            res.append(m)
            print(f"Executable {executable_path} executed successfully.")
    
    print(f"Total number of successfully executed testbenches: {len(successfully_executed)}")
    print(f"Total number of modules in successfully executed testbenches: {len(res)}")
    write_output(OUTPUT_FILE, res)

