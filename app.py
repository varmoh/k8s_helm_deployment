from flask import Flask, request, render_template, jsonify, Response
import subprocess
import json
import os
import logging
import time
import tempfile
from threading import Thread

app = Flask(__name__)

# Configure logging to a file
log_file_path = 'deployment.log'
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Deployment failed: {e}")
        raise

def deploy_helm_charts(config_file, specific_releases=None):
    """Deploy multiple Helm releases based on the config file."""
    try:
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
            
            if specific_releases and release_name not in specific_releases:
                logging.info(f"Skipping release {release_name} as it is not in the selected releases.")
                continue
            
            logging.info(f"Deploying release {release_name}...")
            helm_install_or_upgrade(release_name, namespace, chart_path)

            # Add delay after database deployments
            if "databases" in release_name:
                logging.info(f"Waiting for 2 minutes after deploying {release_name}...")
                time.sleep(120)  # Sleep 
    except Exception as e:
        logging.error(f"Deployment process encountered an error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/load_config', methods=['POST'])
def load_config():
    if 'configFile' not in request.files:
        return jsonify({"status": "error", "message": "No config file part in the request"}), 400

    file = request.files['configFile']
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

    if file:
        try:
            config = json.load(file)
            releases = [release["name"] for release in config["releases"]]
            return jsonify({"status": "success", "releases": releases})
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/deploy', methods=['POST'])
def deploy():
    if 'configFile' not in request.files:
        return jsonify({"status": "error", "message": "No config file part in the request"}), 400

    file = request.files['configFile']
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

    if file:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp:
                temp.write(file.read())
                temp.flush()
                config_file_path = temp.name
                selected_releases = request.form.getlist('selectedReleases')

                # Set KUBECONFIG environment variable
                os.environ['KUBECONFIG'] = '/path/to/your/kubeconfig'  # Change this to the correct path

                thread = Thread(target=deploy_helm_charts, args=(config_file_path, selected_releases if 'deployAll' not in request.form else None))
                thread.start()
                return jsonify({"status": "success", "message": "Deployment started."})
        except Exception as e:
            logging.error(f"Deployment failed: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/logs')
def logs():
    def log_stream():
        with open(log_file_path, 'r') as log_file:
            log_file.seek(0, os.SEEK_END)  # Go to the end of the file
            while True:
                line = log_file.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                yield f"data: {line}\n\n"
    return Response(log_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
