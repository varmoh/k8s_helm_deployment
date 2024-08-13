import yaml
import sys
import os
import glob

def replace_text_in_file(file_path, replacements):
    """Replace old_text with new_text in the YAML file based on replacements list."""
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return 0

    # Read the existing YAML file
    with open(file_path, 'r') as file:
        try:
            content = file.read()
        except Exception as e:
            print(f"Error reading the file {file_path}: {e}")
            return 0

    changes_made = 0
    # Apply replacements
    for replacement in replacements:
        old_text = replacement['old_text']
        new_text = replacement['new_text']
        if old_text in content:
            content = content.replace(old_text, new_text)
            changes_made += content.count(new_text)  # Count the occurrences of new_text

    # Write the updated content back to the file
    if changes_made > 0:
        with open(file_path, 'w') as file:
            try:
                file.write(content)
                print(f"Applied changes to {file_path}. Changes made: {changes_made}")
                return changes_made
            except Exception as e:
                print(f"Error writing the file {file_path}: {e}")
                return 0
    return 0

def find_files(scan_directory, file_pattern):
    """Find files in the scan_directory that match the file_pattern."""
    search_pattern = os.path.join(scan_directory, '**', file_pattern)
    return glob.glob(search_pattern, recursive=True)

def load_changes(config_file):
    """Load scan directory and replacements configuration from a YAML file."""
    if not os.path.exists(config_file):
        print(f"Config file {config_file} does not exist.")
        sys.exit(1)

    with open(config_file, 'r') as file:
        try:
            config = yaml.safe_load(file)
            return config
        except yaml.YAMLError as e:
            print(f"Error reading the config file: {e}")
            sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python update_text.py <changes_file>")
        sys.exit(1)

    changes_file = sys.argv[1]
    config = load_changes(changes_file)
    
    scan_directory = config.get('scan_directory', '.')
    file_pattern = config.get('files', [{}])[0].get('file_pattern', 'values.yaml')
    replacements = config.get('files', [{}])[0].get('replacements', [])

    total_changes = 0

    # Find and process all matching files
    files = find_files(scan_directory, file_pattern)
    
    for file_path in files:
        changes_made = replace_text_in_file(file_path, replacements)
        total_changes += changes_made

    print(f"Total changes made: {total_changes}")

if __name__ == "__main__":
    main()
