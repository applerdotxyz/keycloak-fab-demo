import pytest
import requests
import os
import json
import time
from multiprocessing import Process
from dotenv import load_dotenv
from datetime import datetime  # Import datetime module
from app import app  # Import your FAB app instance

# Load environment variables
load_dotenv()
FAB_URL = os.getenv("FAB_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
FAB_URLS = f"{FAB_URL}/admin"

# Define different token scenarios
TOKEN_SCENARIOS = {
    "no_token": None,
    "invalid_token": "invalid_token",
    "expired_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJleHBpcmVkIiwiaWF0IjoxNjMwMDAwMDAwLCJleHAiOjE2MzAwMDAwMDB9.qYfI5H0MRNmf0u0r3MQl7LThzK51hrG0NAT9VJqyo8g",
    "correct_token": ACCESS_TOKEN,
}

# Open log file
log_file = "test_results.log"
with open(log_file, "w"):
    pass

def run_fab():
    """Run the Flask AppBuilder (FAB) application."""
    host_port=os.getenv("FAB_HOST_PORT")
    app.run(host=host_port, port=5000, debug=True, use_reloader=False)

@pytest.fixture(scope="session", autouse=True)
def start_fab_app():
    """Fixture to start the FAB app in a separate process."""
    # Start the FAB app in a separate process
    fab_process = Process(target=run_fab, daemon=True)
    fab_process.start()

    # Wait for the app to start
    time.sleep(2)  # Adjust the sleep time if needed

    yield  # Wait until all tests are done

    # Terminate the FAB app process after tests
    fab_process.terminate()

@pytest.mark.parametrize("scenario, token", TOKEN_SCENARIOS.items())
def test_admin_access(scenario, token):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(FAB_URLS, headers=headers)

    # Get current date and time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Prepare log entry
    log_entry = {
        "timestamp": current_time,  # Add timestamp
        "scenario": scenario,
        "status_code": response.status_code,
        "response_body": response.json() if response.headers.get("Content-Type") == "application/json" else response.text,
    }

    # Write to log file
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry, indent=4) + "\n\n")

    # No assertions, just logging the responses