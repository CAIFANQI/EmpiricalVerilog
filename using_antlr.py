from antlr4_verilog import InputStream, CommonTokenStream, ParseTreeWalker
from antlr4_verilog.verilog import VerilogLexer, VerilogParser, VerilogParserListener
from generate_docstring import generate_docstring, generate_module_from_docstring
import os
import json
import tiktoken
from time import sleep

HOME = os.path.expanduser("~")
MODULE_INFO_FILE = os.path.join(HOME, "verilog_testing/scripts/data", "module_data.jsonl")

class ModuleIdentifierListener(VerilogParserListener):
    def __init__(self):
        super().__init__()
        self.identifier = []
    def exitModule_declaration(self, ctx):
        self.identifier.append(ctx.module_identifier().getText())

# Load the module information from the JSON file
with open(MODULE_INFO_FILE, "r") as f:
    lines = f.readlines()
    for line in lines:
        # print(len(lines))
        module_info = json.loads(line)
        if module_info["project_name"] == "verilog-eval":
            print(module_info)
        module_contents = module_info["module_contents"].replace("\\n", "\n")
        # count tokens in module_contents
        enc = tiktoken.get_encoding("cl100k_base")
        tokens = len(enc.encode(module_contents))
        if tokens < 1800:
            print(f"Tokens in module contents: {tokens}")
            print(module_contents)
            design = module_contents
            lexer = VerilogLexer(InputStream(design))
            stream = CommonTokenStream(lexer)
            parser = VerilogParser(stream)

            tree = parser.source_text()
            listener = ModuleIdentifierListener()
            walker = ParseTreeWalker()
            walker.walk(listener, tree)
            print(listener.identifier)
            sleep(1)
            # print("Generating docstring...")
            # docstrings = generate_docstring(module_contents, max_tokens=1000, n=5)
            # for d in docstrings:
            #     print("Docstring:")
            #     print(d)
            
            # module = generate_module_from_docstring(docstring, max_tokens=2000)
            # print("Module:")
            # print(module)