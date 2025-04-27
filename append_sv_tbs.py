import os
import csv
import re
import shutil

def find_sv_testbenches(directory, output_file):
    # Search for .sv files in the directory and subdirectories
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".sv"):
                tb_filepath = os.path.join(root, file)
                testbenches = parse_sv_file_for_testbenches(tb_filepath)
                if len(testbenches) > 0:
                    write_to_csv(output_file, tb_filepath, ",".join(testbenches))

def parse_sv_file_for_testbenches(tb_filepath):
    testbenches = []
    try:
        with open(tb_filepath, 'r') as file:
            for line in file:
                # Match module definitions with "test" or "tb" in the name
                match = re.match(r"^\s*module\s+(\w*(test|tb)\w*)", line, re.IGNORECASE)
                if match:
                    testbenches.append(match.group(1))
    except Exception as e:
        print(f"ERROR: Unable to parse file {tb_filepath}: {str(e)}")
    return testbenches

def write_to_csv(output_file, tb_filepath, tb_name):
    revised_output_file = output_file.replace("testbench_list.csv", "testbench_list_revised.csv")
    
    # Copy the original file to the revised file if it hasn't been copied yet
    if not os.path.exists(revised_output_file) and os.path.exists(output_file):
        shutil.copy(output_file, revised_output_file)
    
    # Ensure the revised CSV file exists
    if not os.path.exists(revised_output_file):
        with open(revised_output_file, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(["testbench_filepath", "testbench_name"])
    
    # Append the testbench filepath and name to the revised file
    with open(revised_output_file, 'a') as file:
        writer = csv.writer(file)
        writer.writerow([tb_filepath, tb_name])

def main(flag=0, custom_directory=None):
    HOME = os.path.expanduser("~")
    if flag == 0:
        base_repo_path = os.path.join(HOME, "verilog_testing/verilog-repos/saverepo")
    else:
        base_repo_path = os.path.join(HOME, "verilog_testing/verilog-repos2")

    if not os.path.exists(base_repo_path):
        print(f"Error: Base repository path {base_repo_path} does not exist.")
        return

    for year in os.listdir(base_repo_path):
        year_path = os.path.join(base_repo_path, year)
        if not os.path.isdir(year_path):
            continue

        for month in os.listdir(year_path):
            month_path = os.path.join(year_path, month)
            if not os.path.isdir(month_path):
                continue

            for repo_name in os.listdir(month_path):
                repo_path = os.path.join(month_path, repo_name)
                if not os.path.isdir(repo_path):
                    continue

                output_file = os.path.join(HOME, f"verilog_testing/data/{year}/{month}/{repo_name}/testbench_list.csv")
                find_sv_testbenches(repo_path, output_file)
                print(f"SystemVerilog testbenches added for {repo_name}")

if __name__ == "__main__":
    import sys
    flag = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    custom_directory = sys.argv[2] if len(sys.argv) > 2 else None
    main(flag, custom_directory)
