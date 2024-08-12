import json
import subprocess
import sys

def install_packages_from_json(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {filename} does not exist.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: The JSON file is not valid.")
        sys.exit(1)

    packages = data.get('libraries', [])
    
    if not packages:
        print("No packages to install.")
        return
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}")

if __name__ == "__main__":
    install_packages_from_json('requirements.json')
