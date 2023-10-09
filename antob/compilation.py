# compilation.py
import os
import re
import subprocess
from utility import parse_errors
from conversion import fix_cs

# function to execute c# compiler

from subprocess import check_output, CalledProcessError
def compile_cs(path):    
    try:
        output = check_output(['csc', path])
        if not output.strip():
            return []
        else:
            return [line for line in output.decode().split('\n') if 'error' in line]
    except CalledProcessError as e:
        return ['Compilation failed with exit code {}'.format(e.returncode)]


def compile_project(dest_dir):
    # Define the command
    command = "dotnet build"

    # Call the command in the specified directory
    process = subprocess.Popen(command, shell=True, cwd=dest_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for the command to complete
    stdout, stderr = process.communicate()

    # Check if the command was successful
    if process.returncode == 0:
        print("Build succeeded.")
        return None
    else:
        print("Build failed. Errors:")
        errors = parse_errors(stdout.decode())
        for file, error_list in errors.items():
            print(f"{file}:")
            for error in error_list:
                print(f"  {error}")
        return errors

def fix_errors(errors, dest_dir,tokenizer,model):
    # ask model to fix errors
    for file, error_list in errors.items():
       if file.endswith(".razor.cs"):
          print(f"Fixing errors in {file}:")
          with open(file, 'r', encoding='utf-8') as f:
             csharp = f.read()
             error_string = '\n  '.join(error_list)
             fixed = fix_cs(dest_dir,csharp,error_string,tokenizer,model)
             with open(file, 'w', encoding='utf-8') as f:
                f.write(fixed)