# Get the results in the compilation csvs and consolidate them into a jsonl file usable for other ML tasks
import re
import os
import json
from get_data import get_data

HOME = os.path.expanduser("~")
OUTPUT_FILE = os.path.join(HOME, "verilog_testing/scripts/data/module_data.jsonl")
COMPILE_RES_DIR = os.path.join(HOME, "verilog_testing/scripts/compilation_results/")

def get_module_contents(module_name, file_path):
    """
    Extracts the contents of a specific Verilog module from a file.

    Args:
        module_name (str): The name of the Verilog module to extract.
        file_path (str): The path to the file containing the module.

    Returns:
        str: The contents of the specified module as a single string, or None if the module is not found.
    """
    try:
        with open(file_path, 'r', errors='replace') as file:
            content = file.read()

        # Regular expression to match the module and its contents
        module_pattern = re.compile(
            rf'module\s+{module_name}.*?endmodule',
            re.DOTALL
        )

        match = module_pattern.search(content)
        if match:
            # Replace actual newlines with the literal string '\n'
            return match.group(0)
        else:
            return None

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
def get_module_names(file_path):
    """Extracts the names of all Verilog modules from a file.
    Args:
        file_path (str): The path to the file containing the modules.
    Returns:
        list: A list of module names found in the file.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        # Regular expression to match module names
        module_pattern = re.compile(r'module\s+(\w+)')
        matches = module_pattern.findall(content)
        return matches

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []
    
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
    id = 0
    data = get_data(COMPILE_RES_DIR)
    for key, d in data.items():
        if len(d["main_dep_names"]) == 0:
            print(f"{key} has no main dependencies")
            tb_modules = get_module_names(d["tb_abs_filepath"])
            print(f"Modules in {key}: {tb_modules}")
        for module in d["main_dep_names"]:
            id += 1
            project_name = d["repo_name"]
            month = d["repo_abs_path"].split("/")[-2]
            year = d["repo_abs_path"].split("/")[-3]
            tb_file_name = d["tb_relpath"].split("/")[-1]
            entry = {
                "id": id,
                "year": year,
                "month": month,
                "project_name": project_name,
                "filepath": "",
                "file_name": "",
                "module_name": module,
                "module_contents": "",
                "testbench_path": d["tb_abs_filepath"],
                "testbench_file_name": tb_file_name,
            }
            for dep in d["main_deps"]:
                module_abs_path = os.path.join(d["repo_abs_path"], dep)
                content = get_module_contents(module, module_abs_path)
                if not content:
                    continue
                entry["filepath"] = module_abs_path
                entry["file_name"] = dep
                entry["module_contents"] = content
                res.append(entry)
                break
            if entry["filepath"] == "":
                raise Exception(f"Module not found, check get_module_contents")
    print(len(res))
    write_output(OUTPUT_FILE, res)
    
    