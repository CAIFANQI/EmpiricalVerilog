# A big aspect of Verilog testbenches is that many of them don't actually contain tests
# Tests here means that there exists a builtin check on the values of the signals against a ground truth
# Instead, a lot of is is just a simulation of the design with print statements 
# This file revises the testbenches to replace the print statements with error checks
from utils.remove_comments import remove_comments
def revise_tb(tb_path):
    # Remove comments from the file
    content = remove_comments(tb_path)
    if not check_for_error_handling(content):
        raise Exception(f"NO ERROR HANDLING in {tb_path}")

    count = 0
    updated_content = []
    line = content[0]
    for j in range(1,len(content)+1):
        # line is already $fatal 
        if re.search(r'\$fatal', line):
            updated_content.append(line)
            count += 1
            line = content[j]
            continue

        # multi-line cases
        elif (re.search(r'^[^/]*\$display\s*\(.*', line) or re.search(r'^[^/]*\$error\s*\(.*', line)) and not re.search(r'\)\s*;', line):
            line = line.rstrip() + ' ' + content[j] if j < len(content) else None
            continue
        elif re.search(r'^[^/`]*(?:^|\s)assert\s*\(.*', line) and not re.search(r'\)\s*;', line):
            line = line.rstrip() + ' ' + content[j] if j < len(content) else None
            continue

        # Replace uncommented assert else messages with $fatal outputs
        # Is this redundant?
        elif re.search(r'^[^/`]*assert\s*\(.*\).*else', line):
            count += 1
            line = re.sub(r'assert\s*\((.*)\).*else.*;.*', r'assert(\1) else $fatal;', line)
        # Replace uncommented assert then messages with $fatal outputs
        # Is this redundant?
        elif re.search(r'^[^/`]*(?:^|\s)assert\s*\(.*\).*', line):
            count += 1
            line = re.sub(r'assert\s*\((.*)\).*;', r'assert(\1) else $fatal;', line)
        # Replace uncommented $error messages with $fatal outputs
        elif re.search(r'^[^/]*\$error\s*\(.*\)\s*;', line):
            count += 1
            line = re.sub(r'\$error\s*\((.*)\)\s*;', r'\$fatal;', line)
        elif re.search(r'\$error', line):
            count += 1
            line = re.sub(r'\$error', r'\$fatal', line)
        # Replace uncommented $display messages containing 'error' or 'wrong' with $fatal outputs
        elif re.search(r'^[^/]*\$display\s*\(.*(error|wrong|bad|fail|fault|incorrect).*;', line, re.IGNORECASE):
            count += 1
            line = re.sub(r'\$display\s*\((.*)\)\s*;', r'\$fatal;', line)

        updated_content.append(line + '\n')
        line = content[j] if j < len(content) else None

    if count == 0:
        LOG(f"No changes made to {tb_path}")
        raise Exception(f"No changes made to {tb_path}")
    return updated_content

def create_revised_tb(tb_filepath: str, out_path: str):
    output = revise_tb(tb_filepath)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        for line in output:
            f.write(line)
    f.close()
    # LOG(f"Revised testbench written to {out_path}")