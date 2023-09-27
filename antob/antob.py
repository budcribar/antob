
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

from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig

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


def process_files(src, dest,tokenizer,model):
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
                message = convert_to_cs(source,file_contents,tokenizer,model)
            elif destination.endswith('.razor'):
                message = convert_to_razor(source,file_contents)           
            else:
                message = file_contents

            with open(destination, 'w', encoding='utf-8') as f:
                f.write(message)



def convert_to_cs(path,file_contents,tokenizer,model):
    print("converting{path}") 
    
    prompt = "Convert the following angular typescript code into blazor c# using the following hints (1.Add appropriate using statements if needed. 2. Do not include @Component statements):" + file_contents

    _output = evaluate(prompt, tokenizer, model, input=None, temperature=0.01, top_p=0.9, top_k=40, num_beams=1, max_new_tokens=1024)

    final_output = _output[0].split("### Response:")[1].strip()
    return final_output

def convert_to_razor(path,file_contents,tokenizer,model):
    
    prompt = "Convert the following angular html code into razor:" + file_contents
    _output = evaluate(prompt, tokenizer, model, input=None, temperature=0.01, top_p=0.9, top_k=40, num_beams=1, max_new_tokens=1024)
    final_output = _output[0].split("### Response:")[1].strip()
    return final_output
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
    inputs = tokenizer(prompts, return_tensors="pt",max_length=512, truncation=True, padding=True)
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

def main():
    load_8bit: bool = False
    base_model: str = "C:/Users/Arti_BlizzardPV3/source/repos/text-generation-webui/models/TheBloke_WizardCoder-Python-13B-V1.0-GPTQ"
    input_data_path = "Input.jsonl"
    output_data_path = "Output.jsonl"
    #source = input("Enter source directory: ")
    #destination = input("Enter destination directory: ")
    src_dir = 'C:/Users/Arti_BlizzardPV3/source/repos/Example1'
    dest_dir = 'C:/Users/Arti_BlizzardPV3/source/repos/BlazorExample1'

   


    #copy_and_rename(src_dir, dest_dir)

    #openai.api_key = os.environ["OPENAI_API_KEY"]

    #create_project_file(dest_dir)
    tokenizer = AutoTokenizer.from_pretrained(base_model,max_seq_len=12800)
    
    print("start loading model...") 
    if device == "cuda":
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            load_in_8bit=load_8bit,
            torch_dtype=torch.float16,
            device_map="auto",
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

    process_files(src_dir,dest_dir,tokenizer,model)
   

    

if __name__ == '__main__':
    main()
