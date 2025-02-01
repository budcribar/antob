using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Xml.Linq;

public static class Utility
{
    /// <summary>
    /// Gets the latest version of a NuGet package by querying the NuGet API.
    /// </summary>
    /// <param name="packageName">The NuGet package name.</param>
    /// <returns>The latest version string.</returns>
    public static string GetLatestVersion(string packageName)
    {
        using (HttpClient client = new HttpClient())
        {
            string url = $"https://api.nuget.org/v3/registration5-gz-semver2/{packageName}/index.json";
            HttpResponseMessage response = client.GetAsync(url).GetAwaiter().GetResult();
            response.EnsureSuccessStatusCode();
            string jsonString = response.Content.ReadAsStringAsync().GetAwaiter().GetResult();

            using (JsonDocument doc = JsonDocument.Parse(jsonString))
            {
                if (doc.RootElement.TryGetProperty("items", out JsonElement items))
                {
                    if (items.GetArrayLength() > 0)
                    {
                        // Get the last item in the items array.
                        JsonElement lastItem = items[items.GetArrayLength() - 1];
                        if (lastItem.TryGetProperty("catalogEntry", out JsonElement catalogEntry))
                        {
                            if (catalogEntry.TryGetProperty("version", out JsonElement versionElement))
                            {
                                return versionElement.GetString();
                            }
                            else
                            {
                                throw new Exception($"No version information found for package {packageName}");
                            }
                        }
                        else
                        {
                            throw new Exception($"No catalog entry found for package {packageName}");
                        }
                    }
                    else
                    {
                        throw new Exception($"No versions found for package {packageName}");
                    }
                }
                else
                {
                    throw new Exception("Invalid JSON: missing 'items' property");
                }
            }
        }
    }

    /// <summary>
    /// Adds a package reference to the project's .csproj file.
    /// </summary>
    /// <param name="destDir">The destination directory containing the .csproj file.</param>
    /// <param name="packageName">The NuGet package name.</param>
    /// <param name="packageVersion">The package version to reference.</param>
    public static void AddPackageReference(string destDir, string packageName, string packageVersion)
    {
        // Construct the project file path (assumes the project file is named after the folder).
        string projFile = Path.GetFileName(destDir) + ".csproj";
        string csprojPath = Path.Combine(destDir, projFile);

        // Load the existing .csproj file as XML.
        XDocument doc = XDocument.Load(csprojPath);

        // Find the first ItemGroup element.
        XElement itemGroup = doc.Root.Element("ItemGroup");
        if (itemGroup == null)
        {
            // If not found, create a new ItemGroup element.
            itemGroup = new XElement("ItemGroup");
            doc.Root.Add(itemGroup);
        }

        // Create a new PackageReference element.
        XElement packageRef = new XElement("PackageReference");
        packageRef.SetAttributeValue("Include", packageName);
        packageRef.SetAttributeValue("Version", packageVersion);

        itemGroup.Add(packageRef);

        // Save the updated .csproj file with XML declaration and UTF-8 encoding.
        doc.Save(csprojPath);
    }

    /// <summary>
    /// Parses compiler error output and returns a dictionary mapping file names to a list of error messages.
    /// </summary>
    /// <param name="output">The output text from the compiler.</param>
    /// <returns>A dictionary where the key is the filename and the value is a list of error messages.</returns>
    public static Dictionary<string, List<string>> ParseErrors(string output)
    {
        var errorDict = new Dictionary<string, List<string>>();
        var lines = output.Split(new[] { '\n' }, StringSplitOptions.RemoveEmptyEntries);
        // Regular expression to match error lines.
        var errorRegex = new Regex(@"(.*\.cs)\((\d+,\d+)\): error (.+): (.+) \[.+\]");

        foreach (var line in lines)
        {
            var match = errorRegex.Match(line);
            if (match.Success)
            {
                string filePath = match.Groups[1].Value;
                string location = match.Groups[2].Value;
                string errorCode = match.Groups[3].Value;
                string errorMessage = match.Groups[4].Value;
                string errorText = $"{location} {errorCode}: {errorMessage}";

                if (!errorDict.ContainsKey(filePath))
                {
                    errorDict[filePath] = new List<string>();
                }
                if (!errorDict[filePath].Contains(errorText))
                {
                    errorDict[filePath].Add(errorText);
                }
            }
        }

        return errorDict;
    }

    /// <summary>
    /// Converts a filename to follow Blazor naming conventions.
    /// For example, "my-component" becomes "MyComponent".
    /// </summary>
    /// <param name="filename">The input filename.</param>
    /// <returns>The converted filename.</returns>
    public static string ConvertToBlazorName(string filename)
    {
        // Replace '/' with '\' for Windows file paths.
        filename = filename.Replace('/', '\\');
        // Split the filename on backslashes.
        string[] parts = filename.Split('\\');
        // Get the last part of the filename.
        string lastPart = parts[parts.Length - 1];
        // Split the last part on '-'.
        string[] segments = lastPart.Split('-');
        // Capitalize the first letter of each segment and join them.
        string blazorName = string.Concat(segments.Select(segment =>
            string.IsNullOrEmpty(segment) ? segment : char.ToUpper(segment[0]) + segment.Substring(1)));
        // Replace the last part with the new name.
        parts[parts.Length - 1] = blazorName;
        // Join the parts back together.
        string result = string.Join("\\", parts);
        result = result.Replace(".component", "Component");
        return result;
    }

    /// <summary>
    /// Returns the proper file extension based on Blazor conventions.
    /// </summary>
    /// <param name="extension">The original file extension.</param>
    /// <returns>The converted file extension.</returns>
    public static string GetBlazorExtension(string extension)
    {
        if (extension.Equals(".html", StringComparison.OrdinalIgnoreCase))
            return ".razor";
        else if (extension.Equals(".ts", StringComparison.OrdinalIgnoreCase))
            return ".razor.cs";
        return extension;
    }

    /// <summary>
    /// Extracts the C# code block from a string that contains code delimited by ```csharp and ``` tags.
    /// </summary>
    /// <param name="input">The input string containing the code.</param>
    /// <returns>The extracted C# code, or the original string if no delimiters are found.</returns>
    public static string GetCSharpCode(string input)
    {
        var match = Regex.Match(input, @"```csharp(.*?)```", RegexOptions.Singleline);
        if (match.Success)
        {
            return match.Groups[1].Value;
        }
        else
        {
            return input;
        }
    }

    /// <summary>
    /// Extracts the Razor code block from a string that contains code delimited by ```razor and ``` tags.
    /// </summary>
    /// <param name="input">The input string containing the code.</param>
    /// <returns>The extracted Razor code, or the original string if no delimiters are found.</returns>
    public static string GetRazorCode(string input)
    {
        var match = Regex.Match(input, @"```razor(.*?)```", RegexOptions.Singleline);
        if (match.Success)
        {
            return match.Groups[1].Value;
        }
        else
        {
            return input;
        }
    }
}
