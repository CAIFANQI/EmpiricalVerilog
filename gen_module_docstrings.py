from generate_docstring import generate_docstring, generate_module_from_docstring
import os
import json
import tiktoken

HOME = os.path.expanduser("~")
MODULE_INFO_FILE = os.path.join(HOME, "verilog_testing/scripts/data", "module_data.jsonl")

# Load the module information from the JSON file
count = 0
sum = 0
with open(MODULE_INFO_FILE, "r") as f:
    lines = f.readlines()
    for line in lines:
        # print(len(lines))
        module_info = json.loads(line)
        if module_info["project_name"] == "verilog-eval":
            print(module_info)
        # module_contents = module_info["module_contents"].replace("\\n", "\n")
        # # count tokens in module_contents
        # enc = tiktoken.get_encoding("cl100k_base")
        # tokens = len(enc.encode(module_contents))
        # print(f"Tokens in module contents: {tokens}")
        # if tokens < 1800:
        #     print("Generating docstring...")
        #     docstrings = generate_docstring(module_contents, max_tokens=1000, n=5)
        #     for d in docstrings:
        #         print("Docstring:")
        #         print(d)
            
        #     module = generate_module_from_docstring(docstring, max_tokens=2000)
        #     print("Module:")
        #     print(module)

# print(f"Average tokens in module contents: {avg}")
# print(f"Total modules with less than 1800 tokens: {count}")
        


# # Take the first module and print it
# # print(module_info.keys())
# # print(str(module_info["module_contents"]))

# replace \\n with \n 

