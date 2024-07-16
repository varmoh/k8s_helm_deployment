import unittest
from unittest.mock import patch, call
from helm import deploy_helm_charts
import json

class TestHelmDeployment(unittest.TestCase):

    @patch('helm.time.sleep')  # Mock time.sleep in the helm module
    @patch('subprocess.run')
    @patch('helm.helm_release_exists')
    def test_deploy_helm_charts_install(self, mock_helm_release_exists, mock_run, mock_sleep):
        config_file = 'config_test.json'
        mock_helm_release_exists.return_value = False
        
        # Run the function with the test configuration
        deploy_helm_charts(config_file)
        
        with open(config_file) as f:
            config = json.load(f)
        
        namespace = config["namespace"]
        releases = config["releases"]
        
        expected_calls = []
        for release in releases:
            release_name = release["name"]
            chart_path = release["chart"]
            expected_calls.append(
                call(["helm", "install", release_name, chart_path, "-n", namespace], check=True)
            )
        
        mock_run.assert_has_calls(expected_calls, any_order=True)
        
        # Verify that sleep was called for "databases" release
        if any("databases" in release["name"] for release in releases):
            mock_sleep.assert_called_with(120)  # Check the call to sleep
        else:
            mock_sleep.assert_not_called()  # Ensure sleep is not called when not needed

    @patch('helm.time.sleep')  # Mock time.sleep in the helm module
    @patch('subprocess.run')
    @patch('helm.helm_release_exists')
    def test_deploy_helm_charts_upgrade(self, mock_helm_release_exists, mock_run, mock_sleep):
        config_file = 'config_test.json'
        mock_helm_release_exists.return_value = True
        
        # Run the function with the test configuration
        deploy_helm_charts(config_file)
        
        with open(config_file) as f:
            config = json.load(f)
        
        namespace = config["namespace"]
        releases = config["releases"]
        
        expected_calls = []
        for release in releases:
            release_name = release["name"]
            chart_path = release["chart"]
            expected_calls.append(
                call(["helm", "upgrade", release_name, chart_path, "-n", namespace], check=True)
            )
        
        mock_run.assert_has_calls(expected_calls, any_order=True)
        
        # Verify that sleep was called for "databases" release
        if any("databases" in release["name"] for release in releases):
            mock_sleep.assert_called_with(120)  # Check the call to sleep
        else:
            mock_sleep.assert_not_called()  # Ensure sleep is not called when not needed

if __name__ == '__main__':
    unittest.main()
