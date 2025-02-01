using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ngtob
{
    using System;
    using System.Diagnostics;
    using System.IO;

    public static class ProjectCreation
    {
        public static void CreateBlazorProject(string destDir)
        {
            // Get the project name from the destination folder name
            string projectName = Path.GetFileName(destDir);
            string projectDir = Path.GetDirectoryName(destDir);

            // Ensure the parent directory exists
            if (!Directory.Exists(projectDir))
            {
                Directory.CreateDirectory(projectDir);
            }

            // Build the command (using dotnet CLI)
            string command = $"dotnet new blazorwasm -o {projectName}";

            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = "cmd.exe",
                Arguments = $"/c {command}",
                WorkingDirectory = projectDir,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            using (Process process = Process.Start(psi))
            {
                process.WaitForExit();
                string stdout = process.StandardOutput.ReadToEnd();
                string stderr = process.StandardError.ReadToEnd();
                if (process.ExitCode == 0)
                {
                    Console.WriteLine($"Command executed successfully. Output: {stdout}");
                }
                else
                {
                    Console.WriteLine($"Command failed. Error: {stderr}");
                }
            }

            // Remove the Pages folder and its files if it exists
            string pagesDir = Path.Combine(destDir, "Pages");
            if (Directory.Exists(pagesDir))
            {
                foreach (string file in Directory.GetFiles(pagesDir))
                {
                    File.Delete(file);
                }
                Directory.Delete(pagesDir, recursive: true);
            }

            // Call a helper to add a package reference (placeholder implementation)
            Utility.AddPackageReference(destDir, "System.Reactive.Linq", "6.0.0");

            // Copy the FormBuilder.cs file into the new project (assumes a source FormBuilder.cs exists)
            string targetPath = Path.Combine(destDir, "FormBuilder.cs");
            File.Copy("FormBuilder.cs", targetPath, overwrite: true);
        }
    }

}
