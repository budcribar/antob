# garage-bAInd/Platypus-30B
# TheBloke/WizardCoder-Python-34B-V1.0-GGUF
#wizardcoder-python-34b-v1.0.Q4_K_M.gguf
# MMLU benchmark is the best to evaluate coding
# command window
# cd C:\ProgramData\anaconda3\condabin
# pip install fire
# pip install jsonlines
# conda activate tg
# cd C:\Users\budcr\source\repos\text-generation-webui
# python server.py
# select model
# load model
# max seq len 12800 -> with new card and memory max_seq_len 9300
# max_new_tokens 4096
# temperature 0.01

import sys
import os
import torch
from conversion import load_model

from file_processing import process_files
from compilation import compile_project, fix_errors
from transformers import AutoTokenizer, AutoModelForCausalLM
from project_creation import create_blazor_project

from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig

from inference_wizardcoder import evaluate
from project_creation import create_blazor_project
from utility import get_csharp_code

# https://www.youtube.com/watch?v=Ud_86SaCTrM   Install CodeLLama locally










def main():
    
    base_model: str = "C:/Users/budcr/source/repos/text-generation-webui/models/TheBloke_WizardCoder-Python-13B-V1.0-GPTQ"
    
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
    
    model = load_model(base_model)
    
    model.config.pad_token_id = tokenizer.pad_token_id
    
    model.eval()
    if torch.__version__ >= "2" and sys.platform != "win32":
        model = torch.compile(model)

    process_files(src_dir,dest_dir,tokenizer,model)
   
    errors = compile_project(dest_dir)
    if errors is not None:
        fix_errors (errors, dest_dir,tokenizer,model)
        errors = compile_project(dest_dir)
    

if __name__ == '__main__':
    main()
