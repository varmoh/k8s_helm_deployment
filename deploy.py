import subprocess
import yaml
import sys
import os

def run_helm_command(command):
    """Run a Helm command and handle errors."""
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Helm: {e}")
        sys.exit(1)

def deploy(deployment):
    """Deploy using Helm based on the deployment configuration."""
    name = deployment['name']
    chart_path = deployment['chart_path']
    namespace = deployment['namespace']

    command = [
        'helm', 'upgrade', '--install', name, chart_path,
        '--namespace', namespace
    ]

    # Check if 'values_file' is provided and add it to the command if present
    if 'values_file' in deployment:
        values_file = deployment['values_file']
        command.extend(['-f', values_file])

    print(f"Deploying {name} to {namespace} namespace...")
    run_helm_command(command)
    print(f"Deployment {name} completed successfully.\n")

def load_config(config_file):
    """Load deployments configuration from a YAML file."""
    if not os.path.exists(config_file):
        print(f"Config file {config_file} does not exist.")
        sys.exit(1)

    with open(config_file, 'r') as file:
        try:
            config = yaml.safe_load(file)
            return config.get('deployments', [])
        except yaml.YAMLError as e:
            print(f"Error parsing the config file: {e}")
            sys.exit(1)

def process_file(file_name, filters=None):
    """Process deployments from a given file with optional filters."""
    deployments = load_config(file_name)
    for deployment in deployments:
        if filters is None or deployment['name'] in filters:
            deploy(deployment)

def main():
    if len(sys.argv) < 2:
        print("Usage: python deploy.py <file1.yaml> [<file2.yaml> ...] [deployment_name]")
        sys.exit(1)

    # Collect all file arguments (excluding the script name)
    files = sys.argv[1:]
    target_deployment = None

    # Check if the last argument is a deployment name (filter)
    if len(files) > 1 and (files[-1].startswith('component-') or files[-1].startswith('module-')):
        target_deployment = files.pop()

    for file_name in files:
        process_file(file_name, filters=[target_deployment] if target_deployment else None)

if __name__ == "__main__":
    main()
