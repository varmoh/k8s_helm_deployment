import subprocess
import yaml
import sys
import os
import re

def run_helm_command(command):
    """Run a Helm command and handle errors."""
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Helm: {e}")
        sys.exit(1)

def check_and_create_namespace(namespace):
    """Check if a Kubernetes namespace exists, and create it if it doesn't."""
    try:
        result = subprocess.run(
            ['kubectl', 'get', 'namespace', namespace],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode != 0:
            print(f"Namespace '{namespace}' does not exist. Creating it...")
            subprocess.run(['kubectl', 'create', 'namespace', namespace], check=True)
            print(f"Namespace '{namespace}' created successfully.")
        else:
            print(f"Namespace '{namespace}' already exists.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while checking or creating the namespace: {e}")
        sys.exit(1)

def deploy(deployment):
    """Deploy using Helm based on the deployment configuration."""
    name = deployment.get('name')
    chart_path = deployment.get('chart_path')
    namespace = deployment.get('namespace')

    if not all([name, chart_path, namespace]):
        print(f"Skipping deployment due to missing parameters: {deployment}")
        return

    check_and_create_namespace(namespace)

    command = ['helm', 'upgrade', '--install', name, chart_path, '--namespace', namespace]
    values_file = deployment.get('values_file')
    if values_file:
        command.extend(['-f', values_file])

    print(f"Deploying {name} to {namespace} namespace...")
    run_helm_command(command)
    print(f"Deployment {name} completed successfully.\n")

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

def collect_values_yaml_files(directory, target_deployment=None):
    """Collect 'values.yaml' files for the specified deployment or all files in the directory."""
    values_yaml_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file == 'values.yaml':
                file_path = os.path.join(root, file)
                if target_deployment:
                    # Check if this values.yaml file belongs to the target deployment
                    if target_deployment in file_path:
                        values_yaml_files.append(file_path)
                else:
                    values_yaml_files.append(file_path)
    return values_yaml_files

def check_placeholders_in_files(values_files):
    """Check all 'values.yaml' files for unresolved placeholders."""
    unresolved_files = []

    for file_name in values_files:
        try:
            with open(file_name, 'r') as vf:
                content = vf.read()

            placeholders = re.findall(r'\{\{\s*(.*?)\s*\}\}', content)
            if placeholders:
                unresolved_files.append((file_name, placeholders))
        except Exception as e:
            print(f"Error checking placeholders in {file_name}: {e}")
            unresolved_files.append((file_name, str(e)))
    
    return unresolved_files

def process_file(file_name, filters=None):
    """Process deployments from a given file with optional filters."""
    deployments_data = load_yaml(file_name)
    if isinstance(deployments_data, dict):
        deployments = deployments_data.get('deployments', [])
    elif isinstance(deployments_data, list):
        deployments = deployments_data
    else:
        print(f"Unexpected data structure in {file_name}")
        return

    for deployment in deployments:
        if filters is None or deployment.get('name') in filters:
            deploy(deployment)

def main():
    if len(sys.argv) < 2:
        print("Usage: python deploy.py <config_file> [deployment_name]")
        sys.exit(1)

    config_file = sys.argv[1]
    target_deployment = sys.argv[2] if len(sys.argv) == 3 else None

    # Collect all 'values.yaml' files
    values_files = collect_values_yaml_files('./Components', target_deployment)

    # Check for unresolved placeholders
    unresolved_files = check_placeholders_in_files(values_files)

    if unresolved_files:
        print("Deployment aborted due to unresolved placeholders in the following files:")
        for file_name, placeholders in unresolved_files:
            print(f"- {file_name}: Missing values for placeholders {', '.join(placeholders)}")
        sys.exit(1)  # Exit with error code if any files have unresolved placeholders

    # Proceed with deployment if no unresolved placeholders
    if target_deployment:
        # Process only the specified deployment
        process_file(config_file, filters=[target_deployment])
    else:
        # Process all deployments in the config file
        process_file(config_file)

    # Dad joke about computers
    print("Why do programmers prefer dark mode? Because light attracts bugs!")

if __name__ == "__main__":
    main()
