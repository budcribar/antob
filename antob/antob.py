# pip install selenium  


from msilib import Directory
import os
import shutil
import fnmatch
#import openai

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

# https://www.youtube.com/watch?v=Ud_86SaCTrM   Install CodeLLama locally

def convert_to_blazor_name(filename):
    # Replace '-' with '_' and make the first letter of each segment uppercase
    parts = filename.split('-')
    blazor_name = ''.join(part.capitalize() for part in parts)
    return blazor_name

def get_blazor_extension(extension):
    if extension == '.html':
        return '.razor'
    elif extension == '.ts':
        return '.razor.cs'
    return extension


def process_files(src, dest):
    # Ensure the destination directory exists
    os.makedirs(dest, exist_ok=True)

    skip_files = ['angular.json', 'package.json', 'editorconfig']
    convert_files = ['cart.component.ts']
    
    for root, dirs, files in os.walk(src):
        # Determine the relative path to the current directory
        relative_path = os.path.relpath(root, src)

        if 'e2e' in dirs:
            # Remove 'e2edef' from the list of directories to prevent it from being copied
            dirs.remove('e2e')

        for d in dirs:
            # Create the corresponding directory in the destination folder
            os.makedirs(os.path.join(dest, relative_path, d), exist_ok=True)

        for f in files:
            # Skip files in the skip_files list and any file starting with 'tsconfig' and ending with '.json'
            if f in skip_files or fnmatch.fnmatch(f, 'tsconfig*.json'):
                continue

            if f not in convert_files:
                continue

            # Convert the file name to the Blazor naming convention
            file_name, file_ext = os.path.splitext(f)
            blazor_name = convert_to_blazor_name(file_name) + get_blazor_extension(file_ext)

            source = os.path.join(root, f)
            destination = os.path.join(dest, relative_path, blazor_name)

            with open(source, 'r', encoding='utf-8') as f:
               file_contents = f.read()

            if destination.endswith('.cs'):
                message = convert_to_cs(source,file_contents)
            elif destination.endswith('.razor'):
                message = convert_to_razor(source,file_contents)           
            else:
                message = file_contents

            with open(destination, 'w', encoding='utf-8') as f:
                f.write(message)



def convert_to_cs(path,file_contents):
    model = "text-davinci-002"
    prompt = "Convert the following angular typescript code into blazor c# using the following hints (1.Add appropriate using statements if needed. 2. Do not include @Component statements):"

    completions = openai.Completion.create(
                engine=model,
                prompt=prompt + file_contents,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.5,
            )
    message = completions.choices[0].text
    return message

# command window
# cd D:\anaconda3\condabin>

# conda.bat activate tg
# cd C:\Users\Arti_BlizzardPV3\source\repos\text-generation-webui
# python server.py
# select model
# load model
# max seq len 12800
# max_new_tokens 4096
# temperature 0.01

# function to execute c# compiler
import os
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

def convert_to_razor(path,file_contents):
    model = "text-davinci-002"
    prompt = "Convert the following angular html code into razor:"

    completions = openai.Completion.create(
                engine=model,
                prompt=prompt + file_contents,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.5,
            )
    message = completions.choices[0].text
    return message

def create_project_file(dest):
    model = "text-davinci-002"
    prompt = [
        "create a blazor webassembly .csproj file",
        "use net7 for <TargetFramework>",
        "use version '7.0.0' for any packages starting with 'Microsoft.AspNetCore.Components'",
        "Make sure the following packages are included 'Microsoft.AspNetCore.Components' and 'Microsoft.AspNetCore.Components.Web' and 'Microsoft.AspNetCore.Components.WebAssembly'",
        "Do not include any xml statements or any project references",
        "also format the result with appropriate line endings"
    ]

    prompt_text = "\n".join(prompt)

    destination = os.path.join(dest, os.path.basename(dest) + ".csproj" )
    completions = openai.Completion.create(
                engine=model,
                prompt=prompt_text,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.5,
            )
    message = completions.choices[0].text
    with open(destination, 'w', encoding='utf-8') as f:
        f.write(message)
    




def main():
    #source = input("Enter source directory: ")
    #destination = input("Enter destination directory: ")
    src_dir = 'C:/Users/Arti_BlizzardPV3/source/repos/Example1'
    dest_dir = 'C:/Users/Arti_BlizzardPV3/source/repos/BlazorExample1'
    #copy_and_rename(src_dir, dest_dir)

    #openai.api_key = os.environ["OPENAI_API_KEY"]

    #create_project_file(dest_dir)
    #process_files(src_dir,dest_dir)
    cwd = os.getcwd()

    try:
      driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
      driver.get("http://127.0.0.1:7860/")
      
      
    # Your code to navigate and interact with web pages
    except Exception as e:
      print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
