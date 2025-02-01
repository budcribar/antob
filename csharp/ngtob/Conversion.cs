using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;

public static class Conversion
{
    // Change this URL to point to your Ollama server endpoint.
    private static readonly string OllamaUrl = "http://localhost:11434/complete";

    // Classes for serializing the request and deserializing the response.
    private class OllamaRequest
    {
        public string prompt { get; set; }
        public double temperature { get; set; }
        public double top_p { get; set; }
        public int top_k { get; set; }
        public int num_beams { get; set; }
        public int max_new_tokens { get; set; }
    }

    private class OllamaResponse
    {
        public string completion { get; set; }
    }

    /// <summary>
    /// Sends a prompt to the Ollama server and returns the generated completion.
    /// </summary>
    /// <param name="prompt">The prompt to send.</param>
    /// <param name="temperature">Sampling temperature.</param>
    /// <param name="topP">Top-p value.</param>
    /// <param name="topK">Top-k value.</param>
    /// <param name="numBeams">Beam count.</param>
    /// <param name="maxNewTokens">Maximum new tokens to generate.</param>
    /// <returns>A list containing the response string (typically one element).</returns>
    public static List<string> Evaluate(string prompt, double temperature, double topP, int topK, int numBeams, int maxNewTokens)
    {
        using (HttpClient client = new HttpClient())
        {
            var requestObj = new OllamaRequest
            {
                prompt = prompt,
                temperature = temperature,
                top_p = topP,
                top_k = topK,
                num_beams = numBeams,
                max_new_tokens = maxNewTokens
            };

            string jsonRequest = JsonSerializer.Serialize(requestObj);
            var content = new StringContent(jsonRequest, Encoding.UTF8, "application/json");

            HttpResponseMessage response = client.PostAsync(OllamaUrl, content).GetAwaiter().GetResult();
            response.EnsureSuccessStatusCode();
            string jsonResponse = response.Content.ReadAsStringAsync().GetAwaiter().GetResult();

            var ollamaResponse = JsonSerializer.Deserialize<OllamaResponse>(jsonResponse);
            return new List<string> { ollamaResponse.completion };
        }
    }

    /// <summary>
    /// Fixes C# code by sending it (with error messages) to the Ollama server.
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

        var output = Evaluate(prompt, temperature: 0.01, topP: 0.9, topK: 40, numBeams: 1, maxNewTokens: 1024);
        string finalOutput = ParseResponse(output.FirstOrDefault());
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

        var output = Evaluate(prompt, temperature: 0.01, topP: 0.9, topK: 40, numBeams: 1, maxNewTokens: 1024);
        string finalOutput = ParseResponse(output.FirstOrDefault());
        return Utility.GetCSharpCode(finalOutput);
    }

    /// <summary>
    /// Converts an Angular component (TypeScript and HTML) into a Blazor component (C# and Razor).
    /// </summary>
    public static Tuple<string, string> ConvertAngularComponent(string path, string typescript, string html)
    {
        Console.WriteLine("Converting Angular component for " + path);
        string prompt =
            $"You are an expert in Typescript, Angular, C#, and Blazor. Your task is to convert an Angular component consisting of an HTML file and a TypeScript file to an equivalent Blazor Razor file and Blazor C# file. " +
            "\nThe Angular component to be converted will be delimited as in this example:\n" +
            "```typescript\n" +
            "import {{ Component, Input, Output, EventEmitter }} from '@angular/core';\n" +
            "import {{ Product }} from '../products';\n" +
            "\n" +
            "@Component({{\n" +
            "    selector: 'app-product-alerts',\n" +
            "    templateUrl: './product-alerts.component.html',\n" +
            "    styleUrls: ['./product-alerts.component.css']\n" +
            "}})\n" +
            "export class ProductAlertsComponent {{\n" +
            "    @Input() product: Product | undefined;\n" +
            "    @Output() notify = new EventEmitter();\n" +
            "}}\n" +
            "```\n" +
            "```html\n" +
            "<p *ngIf=\"product && product.price > 700\">\n" +
            "    <button type=\"button\" (click)=\"notify.emit()\">Notify Me</button>\n" +
            "</p>\n" +
            "```\n" +
            "The example TypeScript will be converted to C# and delimited in the output as follows:\n" +
            "```csharp\n" +
            "using Microsoft.JSInterop;\n" +
            "using System.Threading.Tasks;\n" +
            "using Microsoft.AspNetCore.Components;\n" +
            "\n" +
            "namespace BlazorApp\n" +
            "{{\n" +
            "  public partial class ProductAlertsComponent : ComponentBase\n" +
            "  {{\n" +
            "    [Inject]\n" +
            "    public IJSRuntime JSRuntime {{ get; set; }}\n" +
            "\n" +
            "    [Parameter]\n" +
            "    public Product Product {{ get; set; }}\n" +
            "\n" +
            "    [Parameter]\n" +
            "    public EventCallback<Product> Notify {{ get; set; }}\n" +
            "  }}\n" +
            "}}\n" +
            "```\n" +
            "The converted Razor from the example should look like:\n" +
            "```razor\n" +
            "<p @if(Product != null && Product.price > 700)>\n" +
            "    <button type=\"button\" @onclick=\"NotifyMe\">Notify Me</button>\n" +
            "</p>\n" +
            "```\n" +
            "Use the following hints during the conversion process:\n" +
            "[Hint: Add the using statements such as Microsoft.JSInterop, System.Linq, System.Collections.Generic, System.Threading.Tasks, System, System.Net.Http, System.Reactive.Linq, Microsoft.AspNetCore.Components, System.Net.Http.Json where appropriate]\n" +
            "[Hint: No statements starting with @ should be in the generated C# code]\n" +
            "[Hint: Make sure to add the # comment character to any lines that are meant as directions or examples and are not part of the converted component]\n" +
            "[Hint: Use the same namespace in all of the generated files]\n" +
            "[Hint: Classes should be defined at the namespace level and not the Component level if they need to be used in the Razor file]\n" +
            "Here is the TypeScript for you to convert to C#:\n" +
            "[Hint: Angular statements starting with * should be converted to Razor statements starting with @]\n" +
            "```typescript\n" + typescript + "\n```\n" +
            "And here is the HTML to convert to Razor:\n" +
            "```html\n" + html + "\n```\n";

        var output = Evaluate(prompt, temperature: 0.001, topP: 0.9, topK: 40, numBeams: 1, maxNewTokens: 1024);
        string response = ParseResponse(output.FirstOrDefault());
        string csharpCode = Utility.GetCSharpCode(response);
        string razorCode = Utility.GetRazorCode(response);
        return Tuple.Create(csharpCode, razorCode);
    }

    /// <summary>
    /// Converts Angular HTML code into a Blazor Razor file.
    /// </summary>
    public static string ConvertToRazor(string path, string fileContents)
    {
        Console.WriteLine("Converting HTML to Razor for " + path);
        string prompt = "Convert the following Angular HTML code into a Blazor Razor file using the following hints:\n" +
                        "[Hint: The input code is Angular HTML code and the output is Blazor HTML code using Razor syntax]\n" +
                        "[Hint: ngIf converts to @if]\n" +
                        "[Hint: The output should not include any @code sections]\n" +
                        fileContents;
        var output = Evaluate(prompt, temperature: 0.001, topP: 0.9, topK: 40, numBeams: 1, maxNewTokens: 1024);
        string finalOutput = ParseResponse(output.FirstOrDefault());
        return Utility.GetRazorCode(finalOutput);
    }

    /// <summary>
    /// Parses the response by looking for a delimiter ("### Response:") and returns the trimmed result.
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
