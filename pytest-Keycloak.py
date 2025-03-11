import pytest
import subprocess
import time
import os
import pyperclip
import platform
from seleniumbase import BaseCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from dotenv import load_dotenv


# Global Variables (Modify as needed)
load_dotenv()
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
KEYCLOAK_URL = os.getenv("KEYCLOAK_BASE_URL")
FAB_URL = os.getenv("FAB_URL")
REDIRECT_URL = f"{FAB_URL}/oauth-authorized/keycloak"
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_CLIENT = os.getenv("KEYCLOAK_CLIENT_ID")

# Start Docker Compose (Keycloak & Flask)
@pytest.fixture(scope="session", autouse=True)
def start_docker():
    if platform.system() == "Windows":
        subprocess.Popen(["powershell", "docker compose up --build"], shell=True)
    else:
        subprocess.Popen(["/bin/bash", "-c", "docker compose up --build"], shell=False)
    assert os.system("docker ps | grep keycloak"), "Keycloak container not running!"
    time.sleep(30)  # Wait for containers to start


@pytest.fixture(scope="module")
def browser():
    """Setup and teardown for the browser"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


def test_login_keycloak(browser):
    """Login to Keycloak"""
    browser.get(KEYCLOAK_URL)
    wait = WebDriverWait(browser, 20)

    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("admin")
    browser.find_element(By.ID, "password").send_keys("admin")
    browser.find_element(By.ID, "kc-login").click()


def test_create_realm(browser):
    """Create Keycloak Realm"""
    wait = WebDriverWait(browser, 20)

    # Open Realm selector
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='realmSelector']"))).click()

    # Click "Create Realm"
    for _ in range(3):
        try:
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-testid="add-realm"]')))
            element.click()
            break
        except StaleElementReferenceException:
            print("Stale element, retrying...")

    # Enter realm details
    wait.until(EC.presence_of_element_located((By.ID, "realm"))).send_keys(KEYCLOAK_REALM)
    browser.find_element(By.XPATH, "//button[text()='Create']").click()

    # Validate realm creation
    time.sleep(2)
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='realmSelector']"))).click()
        assert wait.until(EC.presence_of_element_located(
            (By.XPATH, "//button[@role='menuitem']//div[text()='{}']".format(KEYCLOAK_REALM))
        )), "Realm was not created successfully!"
        print("Realm created successfully.")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='realmSelector']"))).click()
    except Exception as e:
        pytest.fail(f"ERROR: Realm not created properly. Details: {e}")


def test_create_client(browser):
    """Create Keycloak Client"""
    wait = WebDriverWait(browser, 20)

    # Navigate to Clients
    wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Clients']"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Create client')]"))).click()
    
    # Enter client details
    wait.until(EC.presence_of_element_located((By.ID, "clientId"))).send_keys(KEYCLOAK_CLIENT)
    browser.find_element(By.XPATH, "//button[text()='Next']").click()

    # Enable Client Authentication
    time.sleep(1)
    #--FIXME--
    wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'pf-v5-c-switch__toggle')]"))).click()
    wait.until(EC.element_to_be_clickable((By.ID, "kc-flow-service-account"))).click()
    wait.until(EC.element_to_be_clickable((By.ID, "kc-oauth-device-authorization-grant"))).click()
    browser.find_element(By.XPATH, "//button[text()='Next']").click()
    time.sleep(1)
    
    # Set Redirect URL
    redirect_uri_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[data-testid="redirectUris0"]')))
    redirect_uri_input.send_keys(REDIRECT_URL)

    # Save
    save_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-ouia-component-id="OUIA-Generated-Button-primary-2"]')))
    save_button.click()
    
    time.sleep(1)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Keys"]'))).click()
    time.sleep(1)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'label[for="attributes.use🍺jwks🍺url"] span.pf-v5-c-switch__toggle'))).click()

    time.sleep(1)
    jwks_url = f"{os.getenv('KEYCLOAK_BASE_URL')}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"

    input_element = wait.until(EC.presence_of_element_located((By.ID, "attributes.jwks🍺url")))
    input_element.clear()  # Clear existing value if needed
    input_element.send_keys(jwks_url)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="saveKeys"]'))).click()
    time.sleep(1)


def test_get_client_secret(browser):
    """Retrieve Client Secret"""
    wait = WebDriverWait(browser, 20)

    # Navigate to "Credentials" tab
    credentials_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@role='tab' and contains(@id, 'credentials')][span[text()='Credentials']]")))
    credentials_tab.click()
    time.sleep(1)

    # Copy Client Secret
    client_secret = browser.find_element(By.ID, "kc-client-secret").get_attribute("value")
    #import pdb; pdb.set_trace()
    #assert client_secret, "Client Secret not found!"        


    # Update `.env` file
    env_path = r".\.env"
    with open(env_path, "r") as file:
        lines = file.readlines()
    with open(env_path, "w") as file:
        for line in lines:
            if line.startswith("KEYCLOAK_CLIENT_SECERT="):
                file.write(f"KEYCLOAK_CLIENT_SECERT={client_secret}\n")
            else:
                file.write(line)
    #import pdb; pdb.set_trace()

def test_create_user(browser):
    """Create Keycloak User"""
    wait = WebDriverWait(browser, 20)

    # Navigate to Users
    wait.until(EC.element_to_be_clickable((By.ID, "nav-item-users"))).click()

    # Click "Add user"
    for _ in range(3):
        try:
            button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='no-users-found-empty-action']")))
            button.click()
            break
        except StaleElementReferenceException:
            print("Stale element, retrying...")

    # Enter user details
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USER)
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys("testuser@gmail.com")
    wait.until(EC.presence_of_element_located((By.ID, "firstName"))).send_keys("Test")
    wait.until(EC.presence_of_element_located((By.ID, "lastName"))).send_keys("User")
    time.sleep(1)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='user-creation-save']"))).click()


def test_set_user_password(browser):
    """Set Password for the Created User"""
    wait = WebDriverWait(browser, 20)

    wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-testid='credentials']/span[text()='Credentials']"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='no-credentials-empty-action']"))).click()

    pwd_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
    pwd_field.send_keys(PASSWORD)
    browser.find_element(By.ID, "passwordConfirmation").send_keys(PASSWORD)

    wait.until(EC.element_to_be_clickable((By.XPATH, "//label[@for='temporaryPassword']"))).click()
    wait.until(EC.element_to_be_clickable((By.ID, "modal-confirm"))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='confirm']"))).click()
    #time.sleep(1)
'''
    # Start Flask after Keycloak setup is complete
    start_flask()

def start_flask():
    """Start Flask App after Keycloak setup is complete"""
    print("Starting Flask application...")

    if platform.system() == "Windows":
        subprocess.Popen(["powershell", "flask run --host=0.0.0.0 --port=5000"], shell=True)
    else:
        subprocess.Popen(["/bin/bash", "-c", "flask run --host=0.0.0.0 --port=5000"], shell=False)

    print("✅ Flask app started successfully.")
    time.sleep(5)  # Give Flask time to initialize


def test_fab_login(browser):
    """Test FAB Login"""
    browser.get(FAB_URL)
    wait = WebDriverWait(browser, 20)

    wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/login/']"))).click()
    time.sleep(1)  # Wait for the login page to load
    wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@id='btn-signin-keycloak']"))).click()
    time.sleep(2)
    # Login with Keycloak
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("testuser")
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD)
    wait.until(EC.element_to_be_clickable((By.ID, "kc-login"))).click()
    time.sleep(20)  # Wait for login to complete

'''