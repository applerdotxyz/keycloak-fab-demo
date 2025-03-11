import pytest
import time
from multiprocessing import Process
from seleniumbase import BaseCase
from app import app  # Import your FAB app instance
import json
import os
from dotenv import set_key, load_dotenv

load_dotenv()
user = os.getenv("USER")
password = os.getenv("PASSWORD")

def run_fab():
    """Run the Flask AppBuilder (FAB) application."""
    FAB_HOST=os.getenv("FAB_HOST_PORT")
    app.run(host=FAB_HOST, port=5000, debug=True, use_reloader=False)

class TestFABAuth(BaseCase):
    @classmethod
    def setup_class(cls):
        """Start the FAB app in a separate process."""
        cls.server_process = Process(target=run_fab, daemon=True)  # Keeps FAB running after tests
        cls.server_process.start()

        # Wait for FAB to start
        time.sleep(2)  # Increase if needed

    @classmethod
    def teardown_class(cls):
        """Stop the FAB app."""
        pass

    def test_fab_login(self):
        """Test login on FAB."""
        # Set Chrome-specific options for incognito mode and maximized window
        self.driver.capabilities["goog:chromeOptions"] = {
            "args": ["--incognito", "--start-maximized"]
        }
        FAB_URL = os.getenv("FAB_URL")
        self.open(FAB_URL)
        self.sleep(1)
        self.click('a[href="/login/"]')  # Adjust selector if needed
        self.sleep(1)
        self.click('a#btn-signin-keycloak')
        self.sleep(1)
        self.type('input#username', user)
        self.type('input#password', password)
        self.click('button#kc-login')

        self.sleep(2)

        # Extract JSON text from <pre> tag
        pre_text = self.execute_script("return document.querySelector('pre').textContent;")

        try:
            json_data = json.loads(pre_text)
            access_token = json_data["token_data"]["access_token"]
            print(f"Extracted Access Token: {access_token}")

            # Save token to .env file
            update_env_file("ACCESS_TOKEN", access_token)

        except json.JSONDecodeError:
            pytest.fail("Failed to parse JSON from <pre> tag!")

def update_env_file(key, value):
    """Update the .env file with the new access token"""
    env_path = ".env"

    try:
        if os.path.exists(env_path):
            with open(env_path, "r") as file:
                lines = file.readlines()
        else:
            lines = []

        with open(env_path, "w") as file:
            found = False
            for line in lines:
                if line.startswith(f"{key}="):
                    file.write(f"{key}={value}\n")
                    found = True
                else:
                    file.write(line)

            if not found:
                file.write(f"{key}={value}\n")

        print(f"Updated {key} in .env file")

    except Exception as e:
        print(f"Failed to update .env file: {e}")