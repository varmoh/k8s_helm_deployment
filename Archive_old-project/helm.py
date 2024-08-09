import subprocess
import json
import os
import logging
import time
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_kubernetes_connection():
    """Check if the Kubernetes cluster is accessible."""
    try:
        result = subprocess.run(
            ["kubectl", "config", "current-context"],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info(f"Connected to Kubernetes context: {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        logging.error("Failed to connect to Kubernetes cluster. Ensure that your kubeconfig is correctly set.")
        sys.exit(1)

def helm_release_exists(release_name, namespace):
    """Check if a Helm release exists in the given namespace."""
    logging.info(f"Checking if release {release_name} exists in namespace {namespace}...")
    result = subprocess.run(
        ["helm", "list", "-n", namespace, "-q", release_name],
        capture_output=True,
        text=True
    )
    exists = release_name in result.stdout
    logging.info(f"Release {release_name} exists: {exists}")
    return exists

def helm_install_or_upgrade(release_name, namespace, chart_path):
    """Install or upgrade a Helm release."""
    logging.info(f"Preparing to install or upgrade release {release_name} in namespace {namespace} using chart {chart_path}...")

    # Check if the chart directory exists
    if not os.path.isdir(chart_path):
        logging.error(f"Chart directory {chart_path} does not exist.")
        raise FileNotFoundError(f"Chart directory {chart_path} does not exist.")
    
    if helm_release_exists(release_name, namespace):
        logging.info(f"Upgrading release {release_name} in namespace {namespace}...")
        cmd = ["helm", "upgrade", release_name, chart_path, "-n", namespace]
    else:
        logging.info(f"Installing release {release_name} in namespace {namespace}...")
        cmd = ["helm", "install", release_name, chart_path, "-n", namespace]
    
    logging.info(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def deploy_helm_charts(config_file, specific_release=None):
    """Deploy multiple Helm releases based on the config file."""
    logging.info(f"Loading configuration from {config_file}...")
    with open(config_file, 'r') as file:
        config = json.load(file)
    logging.info("Configuration loaded successfully.")

    namespace = config["namespace"]
    logging.info(f"Target namespace: {namespace}")

    releases = config["releases"]
    logging.info(f"Found {len(releases)} releases in the configuration.")

    for release in releases:
        release_name = release["name"]
        chart_path = release["chart"]
        
        if specific_release and release_name != specific_release:
            logging.info(f"Skipping release {release_name} as it does not match the specified release {specific_release}.")
            continue
        
        logging.info(f"Deploying release {release_name}...")
        helm_install_or_upgrade(release_name, namespace, chart_path)

        # Add delay after database deployments
        if "databases" in release_name:
            logging.info(f"Waiting for 2 minutes after deploying {release_name}...")
            time.sleep(120)  # Sleep 

if __name__ == "__main__":
    # Ensure the script is executed with the config file path and optional release name as arguments
    if len(sys.argv) < 2:
        logging.error("Usage: python helm.py <config_file> [release_name]")
        sys.exit(1)
    
    config_file = sys.argv[1]
    release_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Check Kubernetes connection
    check_kubernetes_connection()
    
    logging.info(f"Starting deployment with config file {config_file} and release {release_name}...")
    deploy_helm_charts(config_file, release_name)
    logging.info("Deployment process completed.")
