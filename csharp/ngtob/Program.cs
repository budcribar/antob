namespace ngtob
{
    internal class Program
    {
        static void Main(string[] args)
        {
            // source = input("Enter source directory: ")
            // destination = input("Enter destination directory: ")
            var src_dir = @"C:/Users/budcr/source/repos/Example1";
            var dest_dir = @"C:/Users/budcr/source/repos/BlazorExample2";

            if (Directory.Exists(dest_dir))
            {
                Console.WriteLine("Destination directory exists.");
            }
            else
            {
                ProjectCreation.CreateBlazorProject(dest_dir);
            }

        }
    }
}
