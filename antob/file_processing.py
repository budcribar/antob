# file_processing.py
import os
import shutil
import fnmatch
from conversion import convert_angular_component, convert_to_cs, convert_to_razor
from utility import convert_to_blazor_name, get_blazor_extension

def process_files(src, dest,tokenizer,model):
    # Ensure the destination directory exists
    os.makedirs(dest, exist_ok=True)

    skip_files = ['angular.json', 'package.json', 'editorconfig','.gitignore', 'main.ts']
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