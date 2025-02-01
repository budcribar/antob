using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;

public static class Compilation
{
    public static List<string> CompileCs(string path)
    {
        List<string> errors = new List<string>();
        try
        {
            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = "csc",
                Arguments = path,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            using (Process process = Process.Start(psi))
            {
                process.WaitForExit();
                string output = process.StandardOutput.ReadToEnd();
                string errorOutput = process.StandardError.ReadToEnd();
                string combinedOutput = output + "\n" + errorOutput;
                if (!string.IsNullOrWhiteSpace(output))
                {
                    errors = combinedOutput.Split(new[] { '\n' }, StringSplitOptions.RemoveEmptyEntries)
                                           .Where(line => line.IndexOf("error", StringComparison.OrdinalIgnoreCase) >= 0)
                                           .ToList();
                }
            }
        }
        catch (Exception ex)
        {
            errors.Add("Compilation failed with exception: " + ex.Message);
        }
        return errors;
    }

    public static Dictionary<string, List<string>> CompileProject(string destDir)
    {
        string command = "dotnet build";

        ProcessStartInfo psi = new ProcessStartInfo
        {
            FileName = "cmd.exe",
            Arguments = $"/c {command}",
            WorkingDirectory = destDir,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        Dictionary<string, List<string>> errors = new Dictionary<string, List<string>>();
        using (Process process = Process.Start(psi))
        {
            process.WaitForExit();
            string stdout = process.StandardOutput.ReadToEnd();
            string stderr = process.StandardError.ReadToEnd();
            if (process.ExitCode == 0)
            {
                Console.WriteLine("Build succeeded.");
                return null;
            }
            else
            {
                Console.WriteLine("Build failed. Errors:");
                errors = Utility.ParseErrors(stdout);
                foreach (var kvp in errors)
                {
                    Console.WriteLine($"{kvp.Key}:");
                    foreach (var error in kvp.Value)
                    {
                        Console.WriteLine($"  {error}");
                    }
                }
            }
        }
        return errors;
    }

    public static void FixErrors(Dictionary<string, List<string>> errors, string destDir)
    {
        // For each file with errors, call FixCs to get a fixed version.
        foreach (var kvp in errors)
        {
            string file = kvp.Key;
            if (file.EndsWith(".razor.cs", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine("Fixing errors in " + file);
                string csharp = File.ReadAllText(file);
                string errorString = string.Join("\n  ", kvp.Value);
                string fixedCode = Conversion.FixCs(destDir, csharp, errorString);
                File.WriteAllText(file, fixedCode);
            }
        }
    }
}
