from typing import List, Dict
import os
import subprocess
import re
import sys
import csv
import pandas as pd
from time import sleep
from utils.remove_comments import remove_comments

DEBUG = True
HOME = os.path.expanduser("~")
DATA_DIR = os.path.join(HOME, "verilog_testing/data")
REPO_DIR_1 = os.path.join(HOME, "verilog_testing/verilog-repos/saverepo")
# IF YOU CHANGE THE BOTTOM, ALSO CHANGE THE IF STATMENT IN MAIN
REPO_DIR_2 = os.path.join(HOME, "verilog_testing/verilog-repos2")
COMPILER = "iverilog"
COMPILE_RES_DIR = os.path.join(HOME, "verilog_testing/scripts/data/compilation_results_extended/")
COMPILE_RES_FILE = "compilation_info.csv"
returncodes = {}
def LOG(msg):
    if DEBUG:
        print(msg)

class Repository():
    def __init__(self, path: str, custom_path: str = None):
        self.abs_path = os.path.abspath(path)
        # LOG("Initializing repository: " + self.abs_path)
        self.name = path.split("/")[-1]
        self.rel_path = path.split("/")[-3] + "/" + path.split("/")[-2] + "/" + self.name
        if not os.path.exists(path):
            raise Exception("Path does not exist for repository: " + path)

        if custom_path:
            self.data_dir = os.path.abspath(custom_path)
            self.rel_path = self.name
        else:
            self.data_dir = os.path.join(DATA_DIR, self.rel_path)
            # year/month/repo_filename
            self.rel_path = path.split("/")[-3] + "/" + path.split("/")[-2] + "/" + self.name

        self.modules = []
        self.testbenches = []
        self.failed_revision_count = 0
        self.names_to_files = {}
        self.init_modules()
        for test in self.testbenches:
            try:
                test.check_for_dependencies()
            except Exception as e:
                LOG(f"Error in checking for dependencies: {e}")
                continue

    class ModuleFile():
        """Class representing a Verilog file containing one or more modules"""
        def __init__(self, repo, modules: List[str], filepath: str, is_testbench: bool = False):
            self.is_testbench = is_testbench # whether the file is a testbench
            self.valid = False
            self.repo = repo # repository object
            self.modules = modules 
            self.abs_filepath = os.path.join(repo.abs_path, filepath) # absolute path to the module
            if not os.path.exists(self.abs_filepath):
                # LOG("Path does not exist: " + self.abs_filepath)
                raise Exception("Path does not exist: " + self.abs_filepath)
            self.rel_path = filepath # relative to the repository
            self.sv = False if filepath.endswith(".v") else True
            self.docstrings = Dict[str, str] # module name to docstring
            self.dependencies = set()
            self.main_dependencies = set()
            self.main_dep_names = set()
            self.been_verified = False # whether the module and its dependencies have been verified
            self.passed_verify = False # whether the module passed verification

        def add_dependency(self, dependency):
            self.dependencies.add(dependency)
        
        def compile(self):
            # LOG("Compiling module: " + self.rel_path)
            # sleep(1)
            compile_statement = [COMPILER]
            if self.sv:
                compile_statement.append("-g2012")
            """Compile the module"""
            output = os.path.join(DATA_DIR, self.repo.rel_path, self.abs_filepath.split(".")[0].split("/")[-1] + ".out")
            LOG("Output: " + output)
            compile_statement.append("-o")
            compile_statement.append(output)
            compile_statement.append(self.abs_filepath)
            # LOG([dep.rel_path for dep in self.dependencies])
            compile_statement.extend([dep.abs_filepath for dep in self.dependencies])
            os.chdir(os.path.dirname(self.abs_filepath))
            # LOG(compile_statement)
            try:
                result = subprocess.run(
                    compile_statement,
                    capture_output=True, text=True, timeout=3)
            except subprocess.TimeoutExpired as e:
                result.k
                result = subprocess.CompletedProcess(
                    args=e.cmd,
                    returncode=1,  # conventionally non-zero for failure
                    stdout=e.stdout,
                    stderr=e.stderr or f"Process timed out after {e.timeout} seconds."
                )
            if result.returncode in returncodes:
                returncodes[result.returncode] += 1
            else:
                returncodes[result.returncode] = 1
            # LOG(f"{result.returncode} {returncodes[result.returncode]}" )
            # sleep(1)
            # if result.returncode == 255:
                # LOG("Compilation failed: " + result.stderr)
            return result

        def check_for_dependencies(self, make_executable: bool = False) -> List["Repository.ModuleFile"]:
            """Check for file dependencies in the given module

            Args:
                module (ModuleFile): The file to check for dependencies

            Raises:
                Exception: Module does not exist
                Exception: Module dependency does not exist
                Exception: Module dependency is not compilable
                Exception: Module is not compilable

            1. Check if the module exists
            2. Attempt to compile the module
            3. If compilation fails, collect missing modules
            4. recursively check missing modules for dependencies
            4. return the list of dependencies if all modules compile
            5. Otherwise, raise an exception
            
            Returns:
                set[Module]: A list of files that are dependencies of the module
            """
            # 1
            if not os.path.exists(self.abs_filepath):
                # LOG(self.abs_filepath)
                raise Exception("Module does not exist")
            elif self.been_verified and not self.passed_verify:
                raise Exception("Module has already failed verification")
            elif self.been_verified and self.passed_verify:
                return self.dependencies
            self.been_verified = True

            # 2
            compile_result = self.compile()
            if compile_result.returncode == 0:
                self.passed_verify = True
                return set()
            else:
                # 3
                missing_mods = find_missing_modules(compile_result.stderr)
                if len(missing_mods) == 0: # failure was not due to missing modules
                    self.been_verified = True
                    self.passed_verify = False
                    raise Exception("Module is not compilable")

                # check if the module is unique and exists
                for mod in missing_mods:
                    if mod not in self.repo.names_to_files:
                        raise Exception("Module dependency does not exist")
                    if len(self.repo.names_to_files[mod]) > 1:
                        # LOG("WARNING Module dependency is not unique: " + mod)
                        raise Exception("Module dependency is not unique")
                    # get the filepath of the module
                    for module_obj in self.repo.names_to_files[mod]:
                        self.main_dependencies.add(module_obj)
                        self.main_dep_names.add(mod)
                        try:
                            sub_dependencies = module_obj.check_for_dependencies(False)
                            self.dependencies.add(module_obj)
                            for dep in sub_dependencies:
                                self.dependencies.add(dep)
                            # LOG(f"Dependencies: {[dep.rel_path for dep in self.dependencies]}")
                        except Exception as e:
                            self.been_verified = True
                            self.passed_verify = False
                            # LOG("Error in checking for dependencies: ", e)
                            raise Exception("Module dependency is not compilable")

                # 4
                # compile the module again, with the dependencies
                # LOG(f"Compiling module with {len(self.dependencies)} dependencies")
                compile_result = self.compile()
                if compile_result.returncode != 0:
                    self.been_verified = True
                    self.passed_verify = False
                    # LOG("Error in compiling module: ", compile_result.stderr)
                    raise Exception("Module is not compilable")

                self.been_verified = True
                self.passed_verify = True
                return self.dependencies

        def check_for_err_handling(self):
            lines = remove_comments(self.abs_filepath)
            self.valid = check_for_error_handling(lines)
            return self.valid
                

    def add_testbench(self, testbench):
        self.testbenches.append(testbench)
    
    def add_module(self, module: ModuleFile):
        self.modules.append(module)

    def init_modules(self, mod_list = "module_list.csv", tb_list = "testbench_list.csv"):
        """Initialize the modules in the repository
        The module data file should be of the format:
        <relative_path>, <module_name_1>, <module_name_2>, ...
        The testbench data file should be of the format:
        <relative_path>, <module_name>
        """
        if not os.path.exists(os.path.join(self.data_dir, mod_list)):
            raise Exception("Module list does not exist: " + os.path.join(self.data_dir, mod_list))

        # Look for modules
        with open(os.path.join(self.data_dir, mod_list), "r") as f:
            lines = f.readlines()
            for line in lines:
                parse = line.strip().split(",")
                rel_filepath = parse[0]
                modules = parse[1:]
                for m in modules:
                    if not os.path.exists(os.path.join(self.abs_path, rel_filepath)):
                        # LOG("Path does not exist: " + rel_filepath)
                        continue
                    try:
                        new_module = Repository.ModuleFile(self, m, rel_filepath)
                    except Exception as e:
                        LOG("Error in creating module: ", e)
                        continue
                    if m in self.names_to_files:
                        self.names_to_files[m].append(new_module)
                    else:
                        self.names_to_files[m] = [new_module] 
                    self.add_module(new_module)

        # Look for testbenches
        tb_list_path = os.path.join(self.data_dir, tb_list)
        if not os.path.exists(tb_list_path):
            raise Exception("Testbench list does not exist: " + os.path.join(self.data_dir, tb_list))

        with open(tb_list_path) as f:
            lines = f.readlines()
            for line in lines:
                if len(line.strip().split(",")) < 2:
                    continue
                # get the filepath of the testbench
                filepath = line.strip().split(",")[0]
                module = line.strip().split(",")[1]
                if not os.path.exists(os.path.join(self.abs_path, filepath)):
                    LOG("TB Path does not exist: " + filepath)
                    continue
                if module in self.names_to_files:
                    for m in self.names_to_files[module]:
                        if m.rel_path == filepath and not os.path.isdir(m.abs_filepath):
                            m.is_testbench = True                            
                            m.check_for_err_handling()
                            if m.valid:
                                self.add_testbench(m)
                            break
                    
def find_missing_modules(error_string) -> List[str]:
    if "These modules were missing" in error_string:
        missing_modules = re.findall(r'\b(\w+)\s+referenced', error_string)
        # LOG(f"MISSING MODULES: {missing_modules}")
        return missing_modules
    return []


class Database():
    def __init__(self):
        """Initializes the Database object and repositories."""
        self.failed_revision_count = 0
        self.repositories = {}

    def add_repository(self, repo):
        self.repositories[repo.name] = repo

    def init_repositories(self, base_path: str):
        """
        Initialize the repositories in the base path.

        Args:
            base_path (str): The path to the base directory.
        """
        # directory is in the format ./year/month/repo_name
        # walk through and get all repo names 
        for repo in os.listdir(base_path):
            repo_path = os.path.join(base_path, repo)
            if not os.path.isdir(repo_path):
                continue
            repo = Repository(repo_path)
            self.failed_revision_count += repo.failed_revision_count
            self.add_repository(repo)
            LOG(f"Testbench count: {len(repo.testbenches)}")
        # LOG(f"Initialized repositories from {base_path}")

def check_for_error_handling(lines) -> bool:
    for line in lines:
        # check for asserts that are uncommented
        if "assert" in line:
            return True
        elif "$error" in line:
            return True
        elif "$fatal" in line:
            return True
        elif "$display" in line:
            display_content = re.search(r'\$display\s*\((.*)\)', line)
            if display_content:
                content = display_content.group(1).lower()
                if "wrong" in content:
                    return True
                if "error" in content:
                    return True
                if "incorrect" in content:
                    return True
                if "fail" in content:
                    return True
                if "fault" in content:
                    return True
                if "bad" in content:
                    return True
        else:
            continue
    return False


def process_module_info(module: Repository.ModuleFile):
    """
    Processes a ModuleFile object and returns relevant information if conditions are met.

    Args:
        module (Repository.ModuleFile): The module to process.

    Returns:
        List[str]: A list containing the testbench absolute path, relative path, 
                   and a list of dependency absolute paths.

    Raises:
        Exception: If the module has not been verified.
    """
    # Check if the module is a testbench
    if not module.is_testbench:
        return None

    # Check if the testbench is valid
    if not module.valid:
        return None

    # Raise an error if the module has not been verified
    if not module.been_verified:
        raise Exception("Module has not been verified")

    # Return nothing if the module did not pass verification
    if not module.passed_verify:
        return None

    LOG("FOUND TRUE TESTBENCH: " + module.abs_filepath)
    # sleep(1)
    # Gather and return the required information
    return [
        module.abs_filepath,  # Testbench absolute path
        module.rel_path,      # Testbench relative path
        [name for name in module.main_dep_names],  # Dependency names
        [dep.rel_path for dep in module.main_dependencies],  # Dependency relative paths
        [dep.rel_path for dep in module.dependencies]  # Dependency absolute paths
    ]

def collect_testbench_info(repo: Repository) -> List[Dict[str, List[str]]]:
    """
    Collects all testbench information from a Repository object.

    Args:
        repo (Repository): The repository to process.

    Returns:
        List[Dict[str, List[str]]]: A list of dictionaries containing testbench information.
    """
    testbench_info = []
    for testbench in repo.testbenches:
        try:
            info = process_module_info(testbench)
            if info:
                testbench_info.append({
                    "abs_path": repo.abs_path,
                    "rel_path": info[1],
                    "main_modules": info[2],
                    "main_dependencies": info[3],
                    "dependencies": info[4]
                })
        except Exception as e:
            LOG(f"Error processing testbench {testbench.rel_path}: {e}")
    return testbench_info

def collect_testbench_info_from_database(db: Database) -> List[Dict[str, List[str]]]:
    """
    Collects all testbench information from a Database object.

    Args:
        db (Database): The database to process.

    Returns:
        List[Dict[str, List[str]]]: A list of dictionaries containing testbench information from all repositories.
    """
    all_testbench_info = []
    for repo_name, repo in db.repositories.items():
        # LOG(f"Processing repository: {repo_name}")
        testbench_info = collect_testbench_info(repo)
        all_testbench_info.extend(testbench_info)
    return all_testbench_info

def write_compilation_info_to_csv(testbench_info: List[Dict[str, List[str]]], output_file: str):
    """
    Writes testbench information to a CSV file using Pandas.

    Args:
        testbench_info (List[Dict[str, List[str]]]): List of dictionaries containing testbench information.
        output_file (str): The name of the output CSV file.
    """
    # if os.path.exists(output_file):
    #     return
    # Convert the testbench information into a DataFrame
    df = pd.DataFrame([
        {
            "Repository Path": info["abs_path"],
            "Testbench Relative Path": info["rel_path"],
            "Main Modules": ";".join(info["main_modules"]),
            "Main Dependencies": ";".join(info["main_dependencies"]),
            "Dependencies": ";".join(info["dependencies"])
        }
        for info in testbench_info
    ])
    # Write the DataFrame to a CSV file
    
    df.to_csv(output_file, index=False, header=False)
    LOG(f"Testbench information written to {output_file}")
    LOG(f"Total rows in CSV: {len(df)}")

def main():
    """Create a database object for each month/year combination
    """
    if len(sys.argv) < 2:
        print("Usage: python get_valid_tbs.py <database_option> [custom_path]")
        return

    database_option = int(sys.argv[1])
    if database_option <= 2:
        total_db_path = (REPO_DIR_1)
    elif database_option > 2:
        total_db_path = (REPO_DIR_2)
    # custom_path = sys.argv[2] if len(sys.argv) > 2 else None
    LOG("Compilation info written to compilation_info.csv")
    failed_revisions = 0
    for year in os.listdir(total_db_path):
        year_path = os.path.join(total_db_path, year)
        month_path = ""
        for month in os.listdir(year_path):
            if not os.path.isdir(os.path.join(year_path, month)):
                continue
            if int(month.split("_")[0]) not in [1, 2, 3] and database_option == 1:
                continue
            if int(month.split("_")[0]) not in [4, 5, 6] and database_option == 2:
                continue
            if int(month.split("_")[0]) not in [1, 2, 3] and database_option == 3:
                continue
            if int(month.split("_")[0]) not in [4, 5, 6] and database_option == 4:
                continue
            if int(month.split("_")[0]) not in [7, 8, 9] and database_option == 5:
                continue
            if int(month.split("_")[0]) not in [10, 11, 12] and database_option == 6:
                continue
            month_path = os.path.join(year_path, month)
            if not os.path.isdir(month_path):
                raise Exception("Path does not exist for month: " + month_path)
            new_db = Database()
            new_db.init_repositories(month_path)
            all_testbench_info = collect_testbench_info_from_database(new_db)
            base_output_path = os.path.join(COMPILE_RES_DIR, "_".join(month_path.split("/")[-2:]) + "_results.csv")
            write_compilation_info_to_csv(all_testbench_info, base_output_path)
            failed_revisions += new_db.failed_revision_count
            # LOG(f"Initialized repositories from {month_path}")
            # LOG(f"Failed Revisions: {new_db.failed_revision_count}")
    LOG(f"Total Failed Revisions: {failed_revisions}")
    
if __name__ == "__main__":
    main()