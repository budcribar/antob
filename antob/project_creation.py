# project_creation.py
import os
import subprocess
from utility import add_package_reference
import glob
import shutil


def create_blazor_project(dest_dir):
    project_name = os.path.basename(dest_dir)
    project_dir = os.path.dirname(dest_dir)

    os.makedirs(project_dir, exist_ok=True)
    # Define the command
    command = "dotnet new blazorwasm -o " + project_name

    # Call the command
    process = subprocess.Popen(command, shell=True, cwd=project_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for the command to complete
    stdout, stderr = process.communicate()

    # Check if the command was successful
    if process.returncode == 0:
        print(f"Command executed successfully. Output: {stdout.decode()}")
    else:
        print(f"Command failed. Error: {stderr.decode()}")
    
    pages_dir = os.path.join(dest_dir, "Pages")
    
    files = glob.glob(os.path.join(pages_dir, "*"))
    for file in files:
        os.remove(file)
    os.removedirs(pages_dir)
    
    add_package_reference(dest_dir,"System.Reactive.Linq","6.0.0")
    
    # TODO change the namespace in FormBuilder.cs
    target_path = os.path.join(dest_dir, "FormBuilder.cs")
    shutil.copy2("FormBuilder.cs", target_path)
    
