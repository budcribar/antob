using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;

public static class Conversion
{
    // Endpoint URL for the Ollama server.
    private static readonly string OllamaUrl = "http://localhost:11434/api/generate";

    // Represents the expected response from the Ollama server.
    private class OllamaResponse
    {
        public string completion { get; set; }
    }

    /// <summary>
    /// Sends a prompt to the Ollama server using a JSON body with "model", "prompt", and "stream" fields.
    /// </summary>
    /// <param name="prompt">The prompt text to send.</param>
    /// <returns>A list containing the response completion.</returns>
    public static string Evaluate(string prompt)
    {
        using (HttpClient client = new HttpClient { Timeout = TimeSpan.FromMinutes(3) })
        {
            // Build the JSON body as in your PowerShell script.
            var requestObj = new
            {
                model = "deepseek-r1:14b",  // Default model – change if needed.
                prompt = prompt,
                stream = false
            };

            string jsonRequest = JsonSerializer.Serialize(requestObj);
            var content = new StringContent(jsonRequest, Encoding.UTF8, "application/json");

            // Send the POST request.
            HttpResponseMessage response = client.PostAsync(OllamaUrl, content).GetAwaiter().GetResult();
            response.EnsureSuccessStatusCode();

            string jsonResponse = response.Content.ReadAsStringAsync().GetAwaiter().GetResult();
            return jsonResponse;
        }
    }

    /// <summary>
    /// Fixes C# code based on provided error messages by sending a prompt to Ollama.
    /// </summary>
    public static string FixCs(string path, string csharp, string errorString)
    {
        Console.WriteLine("Fixing errors in " + path);
        string prompt =
            $"You are an expert in C# and Blazor. Your task is to fix the compiler errors and output corrected code in its entirety " +
            "Use the following hints during the conversion process " +
            "[Hint: Add the using statements such as Microsoft.JSInterop, System.Linq, System.Collections.Generic, System.Threading.Tasks, System, System.Net.Http, System.Reactive.Linq, Microsoft.AspNetCore.Components, System.Net.Http.Json where appropriate]\n" +
            $"Here is the C# code used in a Blazor application:\n" +
            "```csharp\n" + csharp + "\n```\n" +
            $"Here are the compiler errors:\n{errorString}\n" +
            "Please fix as many compiler errors as you can and delimit the output C# with the following tag:\n" +
            "```csharp\n```\n";

        var finalOutput = Evaluate(prompt);
        return Utility.GetCSharpCode(finalOutput);
    }

    /// <summary>
    /// Converts an Angular TypeScript file to an equivalent Blazor C# file.
    /// </summary>
    public static string ConvertToCs(string path, string typescript)
    {
        Console.WriteLine("Converting TypeScript to C# for " + path);
        string prompt =
            $"You are an expert in Typescript, Angular, C#, and Blazor. Your task is to convert an Angular TypeScript file to an equivalent Blazor C# file. " +
            "Please delimit the output C# with the following tag:\n" +
            "```csharp\n```\n" +
            "Use the following hints during the conversion process:\n" +
            "[Hint: Add the using statements such as Microsoft.JSInterop, System.Linq, System.Collections.Generic, System.Threading.Tasks, System, System.Net.Http, System.Reactive.Linq, Microsoft.AspNetCore.Components, System.Net.Http.Json, Microsoft.AspNetCore.Components.WebAssembly.Hosting where appropriate]\n" +
            "[Hint: Make sure to add the # comment character to any lines that are meant as directions, examples or notes and are not part of the converted component]\n" +
            "[Hint: Use the same namespace in all of the generated files]\n" +
            "Here is the TypeScript for you to convert to C#:\n" +
            "```typescript\n" + typescript + "\n```\n";

        var finalOutput = Evaluate(prompt);
        return Utility.GetCSharpCode(finalOutput);
    }

    /// <summary>
    /// Converts an Angular component (with TypeScript and HTML) into Blazor C# and Razor files.
    /// </summary>
    public static Tuple<string, string> ConvertAngularComponent(string path, string typescript, string html)
    {
        Console.WriteLine("Converting Angular component for " + path);
        string prompt =
            """
            
            You are an expert in Typescript, Angular, C#, and Blazor. Your task is to convert an Angular component consisting of an HTML file and a TypeScript file to an equivalent Blazor Razor file and Blazor C# file. 
            The Angular component to be converted will be delimited as in this example:
            
            ```typescript
            import { Component, Input, Output, EventEmitter } from '@angular/core';
            import { Product } from '../products';
           
            @Component({
                selector: 'app-product-alerts',
                templateUrl: './product-alerts.component.html',
                styleUrls: ['./product-alerts.component.css']
            })
            export class ProductAlertsComponent {
                @Input() product: Product | undefined;
                @Output() notify = new EventEmitter();
            } 
            ```
            ```html
            <p *ngIf=\"product && product.price > 700\">
                <button type=\"button\" (click)=\"notify.emit()\">Notify Me</button>
            </p>
            ```
            The example TypeScript will be converted to C# and delimited in the output as follows:
            ```csharp
            using Microsoft.JSInterop;
            using System.Threading.Tasks;
            using Microsoft.AspNetCore.Components;
            
            namespace BlazorApp
            {
              public partial class ProductAlertsComponent : ComponentBase
              {
                [Inject]
                public IJSRuntime JSRuntime { get; set; }
          
                [Parameter]
                public Product Product { get; set; }
           
                [Parameter]
                public EventCallback<Product> Notify { get; set; }
              }
            }
            ```
            The converted Razor from the example should look like:
            ```razor
            <p @if(Product != null && Product.price > 700)>
                <button type=\"button\" @onclick=\"NotifyMe\">Notify Me</button>
            </p>
            ```
            Use the following hints during the conversion process:
            [Hint: Add the using statements such as Microsoft.JSInterop, System.Linq, System.Collections.Generic, System.Threading.Tasks, System, System.Net.Http, System.Reactive.Linq, Microsoft.AspNetCore.Components, System.Net.Http.Json where appropriate]
            [Hint: No statements starting with @ should be in the generated C# code]
            [Hint: Make sure to add the # comment character to any lines that are meant as directions or examples and are not part of the converted component]
            [Hint: Use the same namespace in all of the generated files]
            [Hint: Classes should be defined at the namespace level and not the Component level if they need to be used in the Razor file]
            Here is the TypeScript for you to convert to C#:
            [Hint: Angular statements starting with * should be converted to Razor statements starting with @]
            ```typescript
            
            """ + typescript + """
            ```
            """ + """
            
            And here is the HTML to convert to Razor:
            ```html
            
            """ 
            + html 
            + """```""";

        var response = Evaluate(prompt);
       
        string csharpCode = Utility.GetCSharpCode(response);
        string razorCode = Utility.GetRazorCode(response);
        return Tuple.Create(csharpCode, razorCode);
    }

    /// <summary>
    /// Converts Angular HTML code to a Blazor Razor file.
    /// </summary>
    public static string ConvertToRazor(string path, string fileContents)
    {
        Console.WriteLine("Converting HTML to Razor for " + path);
        string prompt = "Convert the following Angular HTML code into a Blazor Razor file using the following hints:\n" +
                        "[Hint: The input code is Angular HTML code and the output is Blazor HTML code using Razor syntax]\n" +
                        "[Hint: ngIf converts to @if]\n" +
                        "[Hint: The output should not include any @code sections]\n" +
                        fileContents;
        var finalOutput = Evaluate(prompt);
        return Utility.GetRazorCode(finalOutput);
    }

    /// <summary>
    /// Parses the response to extract the generated code.
    /// </summary>
    private static string ParseResponse(string response)
    {
        if (string.IsNullOrEmpty(response))
        {
            return "";
        }
        string[] parts = response.Split(new string[] { "### Response:" }, StringSplitOptions.None);
        if (parts.Length > 1)
        {
            return parts[1].Trim();
        }
        return response.Trim();
    }
}
