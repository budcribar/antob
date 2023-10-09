# conversion.py

from utility import get_csharp_code, get_razor_code
import torch
from transformers import AutoModelForCausalLM, GenerationConfig
device = ""
def load_model(base_model):
    global device
    if torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    try:
        if torch.backends.mps.is_available():
            device = "mps"
    except:
        pass
    load_8bit: bool = False
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
    return model

def generate_prompt(instruction, input=None):
    return f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:"""

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
def fix_cs(path,csharp,error_string,tokenizer,model):
    print("converting",path) 
    
    prompt = f"""You are an expert in C# and Blazor. Your task is to fix the compiler errors and output corrected code in its entirety \
    Use the following hints during the conversion process \
    [Hint: Add the using statements such as Microsoft.JSInterop,System.Linq,Systems.Collections.Generic,System.Threading.Tasks,System,System.Net.Http,System.Reactive.Linq, Microsoft.AspNetCore.Components,System.Net.Http.Json where appropriate]\
  
     Here is the C# code used in a Blazor application\
     ```csharp \
    {csharp} \
    ``` \
    
    Here are the compiler errors \
    {error_string}
    
    Please fix as many compiler errors as you can and delimit the output C# with the following tag \
     ```csharp \
     ``` \
    """
    
    _output = evaluate(prompt, tokenizer, model, input=None, temperature=0.01, top_p=0.9, top_k=40, num_beams=1, max_new_tokens=1024)

    final_output = _output[0].split("### Response:")[1].strip()
    return get_csharp_code(final_output)



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

