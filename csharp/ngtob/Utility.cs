using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

public static class Utility
{
    public static void AddPackageReference(string destDir, string packageName, string version)
    {
        // This is a placeholder. In a real implementation you might edit the project’s .csproj file.
        Console.WriteLine($"Adding package reference {packageName} version {version} to project at {destDir}.");
    }

    public static string ConvertToBlazorName(string name)
    {
        // Placeholder: simply return the input name.
        return name;
    }

    public static string GetBlazorExtension(string fileExt)
    {
        // Map certain extensions to Blazor conventions.
        if (string.Equals(fileExt, ".ts", StringComparison.OrdinalIgnoreCase))
        {
            return ".cs";
        }
        if (string.Equals(fileExt, ".html", StringComparison.OrdinalIgnoreCase))
        {
            return ".razor";
        }
        return fileExt;
    }

    public static string GetCSharpCode(string code)
    {
        // Placeholder: in your output, you might extract the portion delimited by ```csharp.
        return code;
    }

    public static string GetRazorCode(string code)
    {
        // Placeholder: similarly, extract the Razor code from the response.
        return code;
    }

    public static Dictionary<string, List<string>> ParseErrors(string buildOutput)
    {
        // A simple (and very rough) parser for errors.
        var errors = new Dictionary<string, List<string>>();
        var lines = buildOutput.Split(new[] { '\n' }, StringSplitOptions.RemoveEmptyEntries);
        foreach (var line in lines)
        {
            if (line.IndexOf("error", StringComparison.OrdinalIgnoreCase) >= 0)
            {
                // In a real parser, use regex to extract file names and messages.
                string file = "UnknownFile";
                if (line.Contains(":"))
                {
                    file = line.Split(':')[0];
                }
                if (!errors.ContainsKey(file))
                {
                    errors[file] = new List<string>();
                }
                errors[file].Add(line);
            }
        }
        return errors;
    }
}
