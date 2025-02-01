using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

public static class FileProcessing
{
    public static void ProcessFiles(string src, string dest, Tokenizer tokenizer, Model model)
    {
        // Ensure destination directory exists
        Directory.CreateDirectory(dest);

        var skipFiles = new HashSet<string> { "angular.json", "package.json", "editorconfig", ".gitignore", "main.ts" };
        var convertFiles = new HashSet<string> { "cart.component.ts" };

        ProcessDirectory(src, src, dest, tokenizer, model, skipFiles, convertFiles);
    }

    private static void ProcessDirectory(
        string currentDir,
        string src,
        string dest,
        Tokenizer tokenizer,
        Model model,
        HashSet<string> skipFiles,
        HashSet<string> convertFiles)
    {
        // Compute the relative path (and convert the name to Blazor style)
        string relativePath = Utility.ConvertToBlazorName(Path.GetRelativePath(src, currentDir));
        string destCurrentDir = Path.Combine(dest, relativePath);
        Directory.CreateDirectory(destCurrentDir);

        // Process subdirectories (skip any named "e2e")
        var directories = Directory.GetDirectories(currentDir)
                                   .Where(d => Path.GetFileName(d) != "e2e")
                                   .ToArray();
        foreach (var dir in directories)
        {
            string convertedDirName = Utility.ConvertToBlazorName(Path.GetFileName(dir));
            string destSubDir = Path.Combine(destCurrentDir, convertedDirName);
            Directory.CreateDirectory(destSubDir);
            ProcessDirectory(dir, src, dest, tokenizer, model, skipFiles, convertFiles);
        }

        // Process files in this directory
        var files = Directory.GetFiles(currentDir);
        foreach (var filePath in files)
        {
            string fileName = Path.GetFileName(filePath);

            // Skip unwanted files (and files matching tsconfig*.json)
            if (skipFiles.Contains(fileName) ||
                (fileName.StartsWith("tsconfig") && fileName.EndsWith(".json", StringComparison.OrdinalIgnoreCase)))
            {
                continue;
            }

            string fileNameWithoutExt = Path.GetFileNameWithoutExtension(fileName);
            string fileExt = Path.GetExtension(fileName);
            // Convert file name to Blazor naming convention and extension (utility functions)
            string blazorName = Utility.ConvertToBlazorName(fileNameWithoutExt) + Utility.GetBlazorExtension(fileExt);

            string source = filePath;
            string destination = Path.Combine(destCurrentDir, blazorName);

            // If the file is a Razor file, skip it
            if (string.Equals(fileExt, ".razor", StringComparison.OrdinalIgnoreCase))
            {
                continue;
            }

            // For index.html, use a fixed destination name
            if (string.Equals(fileName, "index.html", StringComparison.OrdinalIgnoreCase))
            {
                destination = Path.Combine(destCurrentDir, "index.html");
            }

            string fileContents = File.ReadAllText(source);

            if (destination.EndsWith(".cs", StringComparison.OrdinalIgnoreCase))
            {
                // Look for an HTML file with the same base name
                string htmlFilename = Path.Combine(currentDir, fileNameWithoutExt + ".html");
                if (File.Exists(htmlFilename))
                {
                    string htmlContents = File.ReadAllText(htmlFilename);
                    // Convert Angular component (returns a tuple: (csharp, razor))
                    var message = Conversion.ConvertAngularComponent(source, fileContents, htmlContents, tokenizer, model);
                    if (message != null)
                    {
                        // Write the generated C# file
                        File.WriteAllText(destination, message.Item1);
                        // Write the generated Razor file
                        string htmlFileNameOnly = Path.GetFileNameWithoutExtension(htmlFilename);
                        string blazorHtmlName = Utility.ConvertToBlazorName(htmlFileNameOnly) +
                                                  Utility.GetBlazorExtension(Path.GetExtension(htmlFilename));
                        string razorDestination = Path.Combine(destCurrentDir, blazorHtmlName);
                        File.WriteAllText(razorDestination, message.Item2);
                    }
                }
                else
                {
                    // If no HTML exists, call the conversion to C#
                    destination = destination.Replace(".razor", "");
                    string message = Conversion.ConvertToCs(source, fileContents, tokenizer, model);
                    if (message != null)
                    {
                        File.WriteAllText(destination, message);
                    }
                }
                continue;
            }
            else if (destination.EndsWith(".html", StringComparison.OrdinalIgnoreCase))
            {
                // Convert HTML to Razor syntax
                string message = Conversion.ConvertToRazor(source, fileContents, tokenizer, model);
                if (message != null)
                {
                    File.WriteAllText(destination, message);
                }
            }
            else
            {
                // Otherwise, copy the file contents as is
                File.WriteAllText(destination, fileContents);
            }
        }
    }
}
