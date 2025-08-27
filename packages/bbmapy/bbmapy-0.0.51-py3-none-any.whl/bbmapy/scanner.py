import os
import glob
import re
from .base import find_bbtools_path

def extract_help_message(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
        usage_match = re.search(r'usage\(\)\s*{\s*echo\s*"(.*?)"', content, re.DOTALL)
        if usage_match:
            help_message = usage_match.group(1).strip()
            help_message = help_message.replace('in=', 'in_file=')
            return help_message
    return "No help message found."

def scan_bbtools():
    bbtools_path = find_bbtools_path()
    sh_files = glob.glob(os.path.join(bbtools_path, "*.sh"))
    valid_tools = []

    for sh_file in sh_files:
        with open(sh_file, 'r') as f:
            content = f.read()
            if "bbmap" in content.lower() or "brian" in content.lower():
                tool_name = os.path.basename(sh_file)[:-3]  # Remove .sh extension
                help_message = extract_help_message(sh_file)
                valid_tools.append((tool_name, help_message))

    generate_commands_file(valid_tools)

def generate_commands_file(tools):
    output_path = os.path.join(os.path.dirname(__file__), "commands.py")
    if os.path.exists(output_path):
        os.remove(output_path)
    
    with open(output_path, "w") as f:
        f.write("from typing import Union, Tuple\n")
        f.write("from bbmapy.base import _pack_args, _run_command\n\n")
        
        for tool, help_message in tools:
            method_name = tool.replace('-', '_')
            f.write(f"""
def {method_name}(capture_output: bool = False, **kwargs) -> Union[None, Tuple[str, str]]:
    \"\"\"
    Wrapper for {tool}.sh

    Help message:
    {help_message}

    Args:
        capture_output (bool): If True, capture and return the output instead of printing it.
        in_file (str): Input file (replaces 'in=' parameter)
        **kwargs: Other arguments for {tool}.sh

    Returns:
        Union[None, Tuple[str, str]]: If capture_output is True, returns (stdout, stderr), else None.
    \"\"\"
    args = _pack_args(kwargs)
    return _run_command("{tool}.sh", args, capture_output)
""")

def main():
    print("Scanning BBTools and generating command wrappers...")
    scan_bbtools()
    print("Command wrappers generated successfully.")

if __name__ == "__main__":
    main()
    
#     # test:
#     from bbmapy import * 
# # #     bbtools = BBTools()
#     bbtools.bbduk()
    

#     stdout, stderr = bbtools.bbduk(
#     capture_output=True,
#     in_file="input.fastq",
#     out="output2.fastq",
#     ktrim="r",
#     k="23",
#     mink="11",
#     hdist="1",
#     tbo=True,
#     tpe=True,
#     minlen="45",
#     ref="adapters",
#     ftm="5",
#     maq="6",
#     maxns="1",
#     ordered=True,
#     memory="6g",
#     threads="4",
#     overwrite="t",
#     stats="stats2.txt"
# )
