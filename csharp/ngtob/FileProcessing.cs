using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

public static class FileProcessing
{
    public static void ProcessFiles(string src, string dest)
    {
        // Ensure the destination directory exists.
        Directory.CreateDirectory(dest);

        var skipFiles = new HashSet<string> { "angular.json", "package.json", "editorconfig", ".gitignore", "main.ts" };
        var convertFiles = new HashSet<string> { "cart.component.ts" };

        ProcessDirectory(src, src, dest, skipFiles, convertFiles);
    }

    private static void ProcessDirectory(
        string currentDir,
        string src,
        string dest,
        HashSet<string> skipFiles,
        HashSet<string> convertFiles)
    {
        // Determine the relative path and convert it to Blazor naming convention.
        string relativePath = Utility.ConvertToBlazorName(Path.GetRelativePath(src, currentDir));
        string destCurrentDir = Path.Combine(dest, relativePath);
        Directory.CreateDirectory(destCurrentDir);

        // Process subdirectories (skip any named "e2e").
        var directories = Directory.GetDirectories(currentDir)
                                   .Where(d => Path.GetFileName(d) != "e2e")
                                   .ToArray();
        foreach (var dir in directories)
        {
            string convertedDirName = Utility.ConvertToBlazorName(Path.GetFileName(dir));
            string destSubDir = Path.Combine(destCurrentDir, convertedDirName);
            Directory.CreateDirectory(destSubDir);
            ProcessDirectory(dir, src, dest, skipFiles, convertFiles);
        }

        // Process files in the current directory.
        var files = Directory.GetFiles(currentDir);
        foreach (var filePath in files)
        {
            string fileName = Path.GetFileName(filePath);

            if (skipFiles.Contains(fileName) ||
                (fileName.StartsWith("tsconfig") && fileName.EndsWith(".json", StringComparison.OrdinalIgnoreCase)))
            {
                continue;
            }

            string fileNameWithoutExt = Path.GetFileNameWithoutExtension(fileName);
            string fileExt = Path.GetExtension(fileName);
            // Convert file name to Blazor naming convention.
            string blazorName = Utility.ConvertToBlazorName(fileNameWithoutExt) + Utility.GetBlazorExtension(fileExt);

            string source = filePath;
            string destination = Path.Combine(destCurrentDir, blazorName);

            if (fileExt.Equals(".razor", StringComparison.OrdinalIgnoreCase))
            {
                continue;
            }

            if (string.Equals(fileName, "index.html", StringComparison.OrdinalIgnoreCase))
            {
                destination = Path.Combine(destCurrentDir, "index.html");
            }

            string fileContents = File.ReadAllText(source);

            if (destination.EndsWith(".cs", StringComparison.OrdinalIgnoreCase))
            {
                // Check for a corresponding HTML file.
                string htmlFilename = Path.Combine(currentDir, fileNameWithoutExt + ".html");
                if (File.Exists(htmlFilename))
                {
                    string htmlContents = File.ReadAllText(htmlFilename);
                    var message = Conversion.ConvertAngularComponent(source, fileContents, htmlContents);
                    if (message != null)
                    {
                        // Write the generated C# file.
                        File.WriteAllLines(destination, message.Item1.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None));

                        // Write the generated Razor file.
                        string htmlFileNameOnly = Path.GetFileNameWithoutExtension(htmlFilename);
                        string blazorHtmlName = Utility.ConvertToBlazorName(htmlFileNameOnly) +
                                                  Utility.GetBlazorExtension(Path.GetExtension(htmlFilename));
                        string razorDestination = Path.Combine(destCurrentDir, blazorHtmlName);
                        File.WriteAllLines(razorDestination, message.Item2.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None));
                    }
                }
                else
                {
                    // If there is no HTML file, convert TypeScript to C#.
                    destination = destination.Replace(".razor", "");
                    string message = Conversion.ConvertToCs(source, fileContents);
                    if (message != null)
                    {
                        File.WriteAllText(destination, message);
                    }
                }
                continue;
            }
            else if (destination.EndsWith(".html", StringComparison.OrdinalIgnoreCase))
            {
                string message = Conversion.ConvertToRazor(source, fileContents);
                if (message != null)
                {
                    File.WriteAllText(destination, message);
                }
            }
            else
            {
                // Otherwise, copy the file content as is.
                File.WriteAllText(destination, fileContents);
            }
        }
    }
}
