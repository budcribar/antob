namespace ngtob
{
    internal class Program
    {
        static void Main(string[] args)
        {
            // source = input("Enter source directory: ")
            // destination = input("Enter destination directory: ")
            var srcDir = @"C:/Users/budcr/source/repos/Example1";
            var destDir = @"C:/Users/budcr/source/repos/BlazorExample";

            if (Directory.Exists(destDir))
            {
                Console.WriteLine("Destination directory exists.");
                Directory.Delete(destDir, recursive: true);
            }
           
            ProjectCreation.CreateBlazorProject(destDir);

            FileProcessing.ProcessFiles(srcDir, destDir);

            // Compile the project using dotnet build and then attempt to fix errors.
            var errors = Compilation.CompileProject(destDir);
            if (errors != null)
            {
                Compilation.FixErrors(errors, destDir);
            }

        }
    }
}
