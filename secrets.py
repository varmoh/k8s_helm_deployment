import yaml
import sys
import os
import re

def is_valid_password(password):
    """Check if the password meets the requirements."""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):  # Check for at least one capital letter
        return False
    if not re.search(r"\d", password):  # Check for at least one number
        return False
    return True

def replace_placeholders(values_content, replacements):
    """Replace placeholders in the YAML content with actual values from replacements."""
    changes_made = False
    for placeholder, actual_value in replacements.items():
        # Validate password if the placeholder contains '.password'
        if '.password' in placeholder and not is_valid_password(actual_value):
            print(f"Error: The password for '{placeholder}' does not meet the complexity requirements.")
            sys.exit(1)

        # Convert actual_value to string if it's not already
        if not isinstance(actual_value, str):
            actual_value = yaml.dump(actual_value).strip()

        new_content = values_content.replace(f"{{{{ {placeholder} }}}}", actual_value)
        if new_content != values_content:
            changes_made = True
            values_content = new_content

    return values_content, changes_made

def load_yaml(file_path):
    """Load a YAML file and return its content."""
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        sys.exit(1)

    with open(file_path, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(f"Error reading the file {file_path}: {e}")
            sys.exit(1)

def find_values_files(base_dir):
    """Find all values.yaml files under the base directory."""
    values_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file == "values.yaml":
                values_files.append(os.path.join(root, file))
    return values_files

def main():
    if len(sys.argv) != 2:
        print("Usage: python secrets.py <passwords_file>")
        sys.exit(1)

    passwords_file = sys.argv[1]
    passwords = load_yaml(passwords_file)

    # Look for values.yaml files under the Components directory
    values_files = find_values_files("./Components")

    any_changes = False

    for values_file in values_files:
        print(f"Processing {values_file}...")

        # Load the values.yaml file
        with open(values_file, 'r') as vf:
            values_content = vf.read()

        # Replace placeholders with actual passwords
        updated_content, changes_made = replace_placeholders(values_content, passwords)

        if changes_made:
            with open(values_file, 'w') as vf:
                vf.write(updated_content)
            print(f"Updated {values_file} with values from {passwords_file}\n")
            any_changes = True
        else:
            print(f"No changes needed for {values_file}, skipping...\n")

    if not any_changes:
        print("No changes were made in any of the values.yaml files.")

if __name__ == "__main__":
    main()
