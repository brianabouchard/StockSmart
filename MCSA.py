import os
import sys
import time
import smtplib
from termcolor import colored
from dotenv import load_dotenv
from selenium import webdriver
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Dictionary of product name to URL
PRODUCTS = {
    "Astral 5090 OC": "https://www.microcenter.com/product/690032/asus-nvidia-geforce-rtx-5090-rog-astral-overclocked-triple-fan-32gb-gddr7-pcie-50-graphics-card",
    "Astral 5090": "https://www.microcenter.com/product/690036/asus-nvidia-geforce-rtx-5090-rog-astral-triple-fan-32gb-gddr7-pcie-50-graphics-card",
    "TUF 5090 OC": "https://www.microcenter.com/product/690033/asus-nvidia-geforce-rtx-5090-tuf-gaming-overclocked-triple-fan-32gb-gddr7-pcie-50-graphics-card",
    "TUF 5090": "https://www.microcenter.com/product/690037/asus-nvidia-geforce-rtx-5090-tuf-gaming-triple-fan-32gb-gddr7-pcie-50-graphics-card"
}

def set_store_cookie(driver, url):
    # Get the main store page URL so you don't overload the product webpage. Selenium limitation
    driver.get("https://www.microcenter.com")

    # Wait for the page to load, adjust as needed (seconds)
    time.sleep(0)

    # Set the storeSelected cookie. Default: 131 (Dallas store)
    driver.add_cookie({
        'name': 'storeSelected',
        'value': '131',
        'domain': '.microcenter.com',
        'path': '/',
        'secure': True,
        'httpOnly': False
    })
    # Get the product page URL
    driver.get(url)

    # Wait for the page to load, adjust as needed (seconds)
    time.sleep(0)

def prompt():
    # Prompts the user for email and password securely
    print("Security Disclaimer:\n"
          "Your personal information can only be accessed by a system administrator while the program is running.\n"
          "This information cannot be accessed by outside users and is immediately deleted upon the end of program runtime.\n"
          "This means that you will have to re-enter your information every time the program is ran.\n"
          "Alternatively, you may bypass this step by hitting return twice on your keyboard.\n"
          "\n"
          "Email Information Instructions:\n"
          "Go to myaccount.google.com, search 'App Passwords', and click the respective option.\n"
          "In the 'App name' field enter any title specific to this program.\n"
          "Copy and paste the newly generated password into the appropriate field below:")

    # Set the environment variables
    os.environ["email"] = input("Enter your email: ")
    os.environ["password"] = input("Enter your password: ")

def test_email():
    # Send the test email
    try:
        # Get the environment variables
        email_user = os.getenv("email")
        email_password = os.getenv("password")

        # Confirm whether email credentials were entered
        if not email_user or not email_password:
            raise Exception("Test email credentials not found")

        # Set up the email
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_user
        msg['Subject'] = 'Test Email Successful'
        msg.attach(MIMEText('This is a test email to confirm that your email login is correctly working alongside SMTP within the Microcenter Stock Python Application.\n\n'
                            'You may now let the application run in the background while it actively checks stock of your selected Microcenter product.','plain'))

        # Connect to the email server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_user, email_password)
            server.sendmail(email_user, email_user, msg.as_string())

        print("Test email sent successfully!")

    # Test email exception
    except Exception as e:
        print(f"Failed to send test email: {e}")
        print("Application will continue without user email")

def send_email(product_name, product_url):
    try:
        # Get the environment variables
        email_user = os.getenv("email")
        email_password = os.getenv("password")

        # Confirm whether email credentials were entered
        if not email_user or not email_password:
            raise Exception("Email credentials not found")

        # Set up the email
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_user
        msg['Subject'] = f'{product_name} is in Stock at Microcenter!'
        msg.attach(MIMEText(f'Your product "{product_name}" is in stock!\n\n{product_url}', 'plain'))

        # Connect to the email server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_user, email_password)
            server.sendmail(email_user, email_user, msg.as_string())

        print("Email sent successfully!")

    # Test email exception
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_stock(driver, product_name, url):
    # Set the store cookie to Dallas (storeSelected: 131)
    set_store_cookie(driver, url)

    # Get the page source (HTML)
    page_source = driver.page_source

    # Search for 'inStock': 'False' in the page source
    if "'inStock':'True'" in page_source:
        print(colored(f"{product_name}: IN STOCK!", 'green', attrs=['reverse', 'blink']))
        send_email(product_name, url)
        driver.quit()  # Close the browser
        return True
    else:
        print(colored(f"{product_name}: Out of Stock", 'red'))
        return False

def main():
    # Enter email and password
    prompt()

    # Specify the config.env path
    config_path = ".venv/config.env"

    # Load email credentials from the config.env file
    load_dotenv(config_path)

    # Test email
    test_email()

    while True:
        # Set up Chrome options to enable headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Enable headless mode
        chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
        chrome_options.add_argument("--no-sandbox")  # Fix potential environment issues

        # Set up the WebDriver with the specified options
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            for name, url in PRODUCTS.items():
                check_stock(driver, name, url)
        finally:
            driver.quit()

        print("Waiting for next check...\n")

        time.sleep(300) # Change the number to check stock sooner/faster (seconds). Default: checks stock every ~5 minutes

main()