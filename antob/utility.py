# utility.py
import re
import requests
import xml.etree.ElementTree as ET
import os

def get_latest_version(package_name):
    url = f"https://api.nuget.org/v3/registration5-gz-semver2/{package_name}/index.json"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()
    items = data.get('items', [])
    if items:
        catalog_entry = items[-1].get('catalogEntry', {})
        version = catalog_entry.get('version')
        if version:
            return version
        else:
            raise Exception(f"No version information found for package {package_name}")
    else:
        raise Exception(f"No versions found for package {package_name}")

def add_package_reference(dest_dir, package_name,package_version):
    #package_version = get_latest_version(package_name)
    
    proj_file = os.path.basename(dest_dir) + ".csproj"
    csproj_path = os.path.join(dest_dir, proj_file)
    # Parse the existing .csproj file
    tree = ET.parse(csproj_path)
    root = tree.getroot()

    # Find the ItemGroup element
    item_group = root.find('./ItemGroup')

    if item_group is None:
        # If not found, create a new ItemGroup element
        item_group = ET.SubElement(root, 'ItemGroup')

    # Create a new PackageReference element
    package_ref = ET.SubElement(item_group, 'PackageReference')
    package_ref.set('Include', package_name)
    package_ref.set('Version', package_version)

    # Write the updated .csproj file back to disk
    tree.write(csproj_path, encoding='utf-8', xml_declaration=True)

def parse_errors(output):
    # Dictionary to hold filename: [list of errors]
    error_dict = {}

    # Split the output into lines
    lines = output.split('\n')

    # Regular expression to match error lines
    error_regex = re.compile(r'(.*\.cs)\((\d+,\d+)\): error (.+): (.+) \[.+\]')

    for line in lines:
        match = error_regex.match(line)
        if match:
            # Extract relevant information from the regex match groups
            file_path, location, error_code, error_message = match.groups()
            # Append error message to list of errors for this file, creating a new list if necessary
            error_dict.setdefault(file_path, []).append(f"{location} {error_code}: {error_message}")

    # Remove duplicates from each list in the dictionary
    for file_path, errors in error_dict.items():
        error_dict[file_path] = list(set(errors))

    return error_dict

def convert_to_blazor_name(filename):
    # Replace '/' with '\' for Windows file paths
    filename = filename.replace('/', '\\')
    # Split the filename on '\'
    parts = filename.split('\\')
    # Get the last part of the filename
    last_part = parts[-1]
    # Split the last part on '-'
    segments = last_part.split('-')
    # Capitalize the first letter of each segment and join them
    blazor_name = ''.join(segment.capitalize() for segment in segments)
    # Replace the last part of the filename with the new name
    parts[-1] = blazor_name
    # Join the parts back together
    result = '\\'.join(parts)
    result = result.replace(".component","Component")
    return result

def get_blazor_extension(extension):
    if extension == '.html':
        return '.razor'
    elif extension == '.ts':
        return '.razor.cs'
    return extension




def get_csharp_code(string):
  """Extracts the C# code between ```csharp` and ``` tags.

  Args:
    string: The string to extract the C# code from.

  Returns:
    A string containing the C# code, or None if no C# code is found.
  """

  match = re.search(r"```csharp(.*?)```", string, re.DOTALL)
  if match:
    return match.group(1)
  else:
    return string

def get_razor_code(string):
  """Extracts the C# code between ```razor` and ````` tags.

  Args:
    string: The string to extract the Razor code from.

  Returns:
    A string containing the Razorcode, or None if no Razor code is found.
  """

  match = re.search(r"```razor(.*?)```", string, re.DOTALL)
  if match:
    return match.group(1)
  else:
    return string

