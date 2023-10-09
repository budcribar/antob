
# TheBloke/WizardCoder-Python-34B-V1.0-GGUF
#wizardcoder-python-34b-v1.0.Q4_K_M.gguf

# command window
# cd C:\ProgramData\anaconda3\condabin
# pip install fire
# pip install jsonlines
# conda activate tg
# cd C:\Users\budcr\source\repos\text-generation-webui
# python server.py
# select model
# load model
# max seq len 12800 -> with new card and memory max_seq_len 9216
# max_new_tokens 4096
# temperature 0.01

# 9/27/2023 76 errors
# 9/27/2023 117 errors
# 9/27 43 errors
# 9/27 41 errors
# 9/28 17 errors


# Need to add <PackageReference Include="Newtonsoft.Json" Version="13.0.3" /> to csproj file
from msilib.schema import File
import sys
import os
import fire
import torch
import transformers
import json
import jsonlines
from msilib import Directory
import os
import shutil
import fnmatch
import re

from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig,pipeline

from inference_wizardcoder import evaluate

# https://www.youtube.com/watch?v=Ud_86SaCTrM   Install CodeLLama locally

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

try:
    if torch.backends.mps.is_available():
        device = "mps"
except:
    pass

def convert_to_blazor_name(filename):
    # Replace '/' with '\' for Windows file paths
    filename = filename.replace('/', '\\')
    # Split the filename on '\'
    parts = filename.split('\\')
    # Get the last part of the filename
    last_part = parts[-1]
    # Split the last part on '-'
    segments = last_part.split('-')
    # Capitalize the first letter of each segment and join them
    blazor_name = ''.join(segment.capitalize() for segment in segments)
    # Replace the last part of the filename with the new name
    parts[-1] = blazor_name
    # Join the parts back together
    result = '\\'.join(parts)
    result = result.replace(".component","Component")
    return result

# def convert_to_blazor_name(filename):
#     # Replace '-' with '_' and make the first letter of each segment uppercase
#     parts = filename.split('-')
#     blazor_name = ''.join(part.capitalize() for part in parts)
#     return blazor_name

def get_blazor_extension(extension):
    if extension == '.html':
        return '.razor'
    elif extension == '.ts':
        return '.razor.cs'
    return extension


def process_files(src, dest,tokenizer,model):
    # Ensure the destination directory exists
    os.makedirs(dest, exist_ok=True)

    skip_files = ['angular.json', 'package.json', 'editorconfig','.gitignore']
    convert_files = ['cart.component.ts']
    
    for root, dirs, files in os.walk(src):
        # Determine the relative path to the current directory
        relative_path = convert_to_blazor_name(os.path.relpath(root, src))

        if 'e2e' in dirs:
            # Remove 'e2edef' from the list of directories to prevent it from being copied
            dirs.remove('e2e')

        for d in dirs:
            d = convert_to_blazor_name(d)
            # Create the corresponding directory in the destination folder
            os.makedirs(os.path.join(dest, relative_path, d), exist_ok=True)

        for f in files:
            # Skip files in the skip_files list and any file starting with 'tsconfig' and ending with '.json'
            if f in skip_files or fnmatch.fnmatch(f, 'tsconfig*.json'):
                continue

            #if f not in convert_files:
            #    continue

          
            

            # Convert the file name to the Blazor naming convention
            file_name, file_ext = os.path.splitext(f)
            blazor_name = convert_to_blazor_name(file_name) + get_blazor_extension(file_ext)

            source = os.path.join(root, f)
            destination = os.path.join(dest, relative_path, blazor_name)
            
            if(file_ext == ".razor"):
                continue

            if(f=="index.html"):
                destination = os.path.join(dest, relative_path, "index.html")

            with open(source, 'r', encoding='utf-8') as f:
               file_contents = f.read()
               
            if destination.endswith('.cs'):
                html_filename = os.path.join(root, file_name + ".html")
                # Check if the file exists
                if os.path.exists(html_filename):
                    # If the file exists, open and read it
                    with open(html_filename, 'r', encoding='utf-8') as f:
                        html_contents = f.read()
                        message = convert_angular_component(source,file_contents,html_contents,tokenizer,model)
                        if(message != None):
                            # write the c# file
                            with open(destination, 'w', encoding='utf-8') as f:
                                f.write(message[0])
                            # write the razor file
                            file_name, file_ext = os.path.splitext(os.path.basename(html_filename))
                            blazor_name = convert_to_blazor_name(file_name) + get_blazor_extension(file_ext)   
                            destination = os.path.join(dest, relative_path, blazor_name)
                            with open(destination, 'w', encoding='utf-8') as f:
                                f.write(message[1])
                else:
                    # If the file does not exist, assign an empty string
                    html_contents = ""
                    message = convert_to_cs(source,file_contents,tokenizer,model)
                    if(message != None):
                        # write the c# file
                        with open(destination, 'w', encoding='utf-8') as f:
                            f.write(message)
                continue
            #elif destination.endswith('.razor'):
            #    message = convert_to_razor(source,file_contents,tokenizer,model)       
            elif destination.endswith('.html'):
                message = convert_to_razor(source,file_contents,tokenizer,model)      
            else:
                message = file_contents

            if(message != None):
                with open(destination, 'w', encoding='utf-8') as f:
                    f.write(message)

def get_csharp_code(string):
  """Extracts the C# code between ```csharp` and ````` tags.

  Args:
    string: The string to extract the C# code from.

  Returns:
    A string containing the C# code, or None if no C# code is found.
  """

  match = re.search(r"`csharp\n(.*?)\n`", string, re.DOTALL)
  if match:
    return match.group(1)
  else:
    return string

def get_razor_code(string):
  """Extracts the C# code between ```razor` and ````` tags.

  Args:
    string: The string to extract the Razor code from.

  Returns:
    A string containing the Razorcode, or None if no Razor code is found.
  """

  match = re.search(r"`razor\n(.*?)\n`", string, re.DOTALL)
  if match:
    return match.group(1)
  else:
    return string

def convert_to_cs(path,typescript,tokenizer,model):
    print("converting",path) 
    
    prompt = f"""You are an expert in Typescript,Angular,C#, and Blazor. Your task is to convert an Angular  typescript file to an equilivelent Blazor C# file. \
    Use the following hints during the conversion process \
    [Hint: Add the using statements such as Microsoft.JSInterop,System.Linq,Systems.Collections.Generic,System.Threading.Tasks,System,System.Net.Http,System.Reactive.Linq, Microsoft.AspNetCore.Components,System.Net.Http.Json,Microsoft.AspNetCore.Components.WebAssembly.Hosting where appropriate]\
    [Hint: Make sure to add the # comment character to any lines that are meant as directions or examples and are not part of the converted component] \
    [Hint: Use the same namespace in all of the generated files] \
     Here is the typescript for you to convert to C# \
     ```typescript \
    {typescript} \
    ``` \
    
    Please delimit the output C# with the following tag \
     ```csharp \
     ``` \
    """
    
    _output = evaluate(prompt, tokenizer, model, input=None, temperature=0.01, top_p=0.9, top_k=40, num_beams=1, max_new_tokens=1024)

    final_output = _output[0].split("### Response:")[1].strip()
    return get_csharp_code(final_output)
   
  

def convert_angular_component(path,typescript,html,tokenizer,model):
    print("converting",path) 
    
    prompt = f"""You are an expert in Typescript,Angular,C#, and Blazor. Your task is to convert an Angular component consisting of an html file and a typescript file to an equilivelent Blazor Razor file and Blazor C# file. \
    \
    The Angular component to be converted will be delimited as in this example: \
    ```typescript \
    import {{ Component, Input, Output, EventEmitter }} from '@angular/core'; \
    import {{ Product }} from '../products'; \
    \
    @Component({{ \
        selector: 'app-product-alerts', \
        templateUrl: './product-alerts.component.html',\
        styleUrls: ['./product-alerts.component.css']\
    }})\
    export class ProductAlertsComponent {{\
        @Input() product: Product | undefined;\
        @Output() notify = new EventEmitter();\
    }}\
    ``` \
    ```html \
    <p *ngIf="product && product.price > 700"> \
        <button type="button" (click)="notify.emit()">Notify Me</button> \
    </p> \
    ```
    
    the example typescript will be converted to c# and delimited in the output as follows: \
    ```csharp \
    using Microsoft.JSInterop; \
    using System.Threading.Tasks; \
    using Microsoft.AspNetCore.Components; \

    namespace BlazorApp \
    {{ \
      public partial class ProductAlertsComponent : ComponentBase \
      {{ \
        [Inject] \
        public IJSRuntime JSRuntime {{ get; set; }} \

        [Parameter] \
        public Product Product {{ get; set; }} \

        [Parameter] \
        public EventCallback<Product> Notify {{ get; set; }} \
      }} \
    }} \
    ``` \
    
    the converted razor from the example should look like: \
    ```razor
    <p @if(Product != null && Product.price > 700)> \
        <button type="button" @onclick="NotifyMe">Notify Me</button> \
    </p> \
    ```
    
    Use the following hints during the conversion process \ 
    [Hint: Add the using statements such as Microsoft.JSInterop,System.Linq,Systems.Collections.Generic,System.Threading.Tasks,System,System.Net.Http,System.Reactive.Linq, Microsoft.AspNetCore.Components,System.Net.Http.Json where appropriate]\
    [Hint: No statements starting with @ should be in the generated csharp code] \
    [Hint: Make sure to add the # comment character to any lines that are meant as directions or examples and are not part of the converted component] \
    [Hint: Use the same namespace in all of the generated files] \
    [Hint: Classes should be defined at the namespace level and not the Component level if they need to be used in the razor file]
    
    Here is the typescript for you to convert to C# \
    [Hint: Angular statements starting with * should be converted to Razor statements starting with @] \
     ```typescript \
    {typescript} \
    ```
    
    and here is the html to convert to razor \
    ```html \
    {html} \
    ``` \
    """
    _output = evaluate(prompt, tokenizer, model, input=None, temperature=0.001, top_p=0.9, top_k=40, num_beams=1, max_new_tokens=1024)

    final_output = _output[0].split("### Response:")[1].strip()
    return get_csharp_code(final_output), get_razor_code(final_output)
   

def convert_to_razor(path,file_contents,tokenizer,model):
    print("converting",path) 
    prompt = "Convert the following Angular HTML code into a Blazor Razor file using the following hints:\n" + \
    "[Hint: The input code is Angular HTML code and the output is Blazor html code using Razor syntax]\n" + \
    "[Hint: ngIf converts to @if]\n"+\
    "[Hint: The output should not include any @code sections]\n" + \
    file_contents
    _output = evaluate(prompt, tokenizer, model, input=None, temperature=0.001, top_p=0.9, top_k=40, num_beams=1, max_new_tokens=1024)
    final_output = _output[0].split("### Response:")[1].strip()
    return get_razor_code(final_output)


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
    

def evaluate(
        batch_data,
        tokenizer,
        model,
        input=None,
        temperature=1,
        top_p=0.9,
        top_k=40,
        num_beams=1,
        max_new_tokens=2048,
        **kwargs,
):
    prompts = generate_prompt(batch_data, input)
    #inputs = tokenizer(prompts, return_tensors="pt", /*max_length=512,*/ truncation=True, padding=True)
    #inputs = tokenizer(prompts, return_tensors="pt",max_length=512, truncation=True, padding=True)
    inputs = tokenizer(prompts, return_tensors="pt")
    input_ids = inputs["input_ids"].to(device)
    generation_config = GenerationConfig(
        do_sample=True,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        num_beams=num_beams,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
        **kwargs,
    )
    with torch.no_grad():
        generation_output = model.generate(
            input_ids=input_ids,
            generation_config=generation_config,
            return_dict_in_generate=True,
            output_scores=True,
            max_new_tokens=max_new_tokens,
        )
    s = generation_output.sequences
    output = tokenizer.batch_decode(s, skip_special_tokens=True)
    return output

def generate_prompt(instruction, input=None):
    return f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:"""

import xml.etree.ElementTree as ET
import requests

def get_latest_version(package_name):
    url = f"https://api.nuget.org/v3/registration5-gz-semver2/{package_name}/index.json"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()
    items = data.get('items', [])
    if items:
        catalog_entry = items[-1].get('catalogEntry', {})
        version = catalog_entry.get('version')
        if version:
            return version
        else:
            raise Exception(f"No version information found for package {package_name}")
    else:
        raise Exception(f"No versions found for package {package_name}")
    
def add_package_reference(dest_dir, package_name,package_version):
    #package_version = get_latest_version(package_name)
    
    proj_file = os.path.basename(dest_dir) + ".csproj"
    csproj_path = os.path.join(dest_dir, proj_file)
    # Parse the existing .csproj file
    tree = ET.parse(csproj_path)
    root = tree.getroot()

    # Find the ItemGroup element
    item_group = root.find('./ItemGroup')

    if item_group is None:
        # If not found, create a new ItemGroup element
        item_group = ET.SubElement(root, 'ItemGroup')

    # Create a new PackageReference element
    package_ref = ET.SubElement(item_group, 'PackageReference')
    package_ref.set('Include', package_name)
    package_ref.set('Version', package_version)

    # Write the updated .csproj file back to disk
    tree.write(csproj_path, encoding='utf-8', xml_declaration=True)

# Example usage:
# csproj_path = 'path_to_your_project_file.csproj'
# package_name = 'System.Reactive.Linq'
# add_package_reference(csproj_path, package_name)


import subprocess
import glob
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
    
import re

def parse_errors(output):
    # Dictionary to hold filename: [list of errors]
    error_dict = {}

    # Split the output into lines
    lines = output.split('\n')

    # Regular expression to match error lines
    error_regex = re.compile(r'(.*\.cs)\((\d+,\d+)\): error (.+): (.+) \[.+\]')

    for line in lines:
        match = error_regex.match(line)
        if match:
            # Extract relevant information from the regex match groups
            file_path, location, error_code, error_message = match.groups()
            # Append error message to list of errors for this file, creating a new list if necessary
            error_dict.setdefault(file_path, []).append(f"{location} {error_code}: {error_message}")

    return error_dict

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

def fix_cs(path,csharp,error_string,tokenizer,model):
    print("converting",path) 
    
    prompt = f"""You are an expert in C# and Blazor. Your task is to fix the compile errors and output corrected code in its entirety \
  
     Here is the C# code\
     ```csharp \
    {csharp} \
    ``` \
    
    Here are the compiler errors \
    {error_string}
    
    Please delimit the output C# with the following tag \
     ```csharp \
     ``` \
    """
    
    _output = evaluate(prompt, tokenizer, model, input=None, temperature=0.01, top_p=0.9, top_k=40, num_beams=1, max_new_tokens=1024)

    final_output = _output[0].split("### Response:")[1].strip()
    return get_csharp_code(final_output)

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

def main():
    load_8bit: bool = False
    base_model: str = "C:/Users/budcr/source/repos/text-generation-webui/models/TheBloke_WizardCoder-Python-13B-V1.0-GPTQ"
    input_data_path = "Input.jsonl"
    output_data_path = "Output.jsonl"
    #source = input("Enter source directory: ")
    #destination = input("Enter destination directory: ")
    src_dir = 'C:/Users/budcr/source/repos/Example1'
    dest_dir = 'C:/Users/budcr/source/repos/BlazorExample2'

    if os.path.isdir(dest_dir):
        print(dest_dir, " exists.")
    else:
        create_blazor_project(dest_dir)
        


    #copy_and_rename(src_dir, dest_dir)

    #openai.api_key = os.environ["OPENAI_API_KEY"]

    #create_project_file(dest_dir)
    #tokenizer = AutoTokenizer.from_pretrained(base_model,max_seq_len=12800)
    tokenizer = AutoTokenizer.from_pretrained(base_model,max_seq_len=12800,use_fast=True)
    
    print("start loading model...") 
    if device == "cuda":
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.float16,
            device_map="auto",
            revision="main",
            load_in_8bit=load_8bit, 
        )
    elif device == "mps":
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            device_map={"": device},
            torch_dtype=torch.float16,
        )

    print("end loading model...") 
    model.config.pad_token_id = tokenizer.pad_token_id
    
    model.eval()
    if torch.__version__ >= "2" and sys.platform != "win32":
        model = torch.compile(model)

    #process_files(src_dir,dest_dir,tokenizer,model)
   
    errors = compile_project(dest_dir)
    if errors is not None:
        fix_errors (errors, dest_dir,tokenizer,model)
        errors = compile_project(dest_dir)
    

if __name__ == '__main__':
    main()
