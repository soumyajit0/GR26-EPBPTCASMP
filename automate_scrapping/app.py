import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pickle
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # Import Keys class for special keys like Enter
import time
from selenium.common.exceptions import NoAlertPresentException

# File to store the path of the driver (so it only installs once)
driver_path_file = 'driver_path.pkl'
EMAIL="8334999569"
PASSWORD="myfbaccount2024"


import socket
import json



def dismiss_alert_if_present(driver):
    try:
        alert = driver.switch_to.alert  # Switch to alert if present
        alert.dismiss()  # Dismiss the alert
    except NoAlertPresentException:
        pass

def get_driver_path():
    # If the driver path is already saved, load it
    if os.path.exists(driver_path_file):
        with open(driver_path_file, 'rb') as file:
            driver_path = pickle.load(file)
            if os.path.exists(driver_path):  # Make sure the path is valid
                return driver_path
    
    # If no saved driver, install it using ChromeDriverManager and save the path
    driver_path = ChromeDriverManager().install()
    with open(driver_path_file, 'wb') as file:
        pickle.dump(driver_path, file)
    return driver_path

def page_has_loaded(driver):
    page_state = driver.execute_script('return document.readyState;')
    return page_state == 'complete'

Logged_in=False

def login(driver,email,password):
    global Logged_in
    if Logged_in:
        return
    c=0
    while c<120:
        c+=1
        if page_has_loaded(driver):
            break
        time.sleep(0.5)
    
    email_input = driver.find_element(By.NAME, "email")
    email_input.send_keys(email)
    
    # Select the input field with name="pass" and enter the value
    pass_input = driver.find_element(By.NAME, "pass")
    pass_input.send_keys(password)
    
    # Send the Enter key to submit the form
    pass_input.send_keys(Keys.ENTER)

    # Close the browser after the operation
    time.sleep(3)  # Sleep for a bit to see the result

def get_user_name(driver):
    try:
        h1_element = driver.find_element(By.TAG_NAME, 'h1')
        NAME = h1_element.text  # Store the text of the first h1 in the NAME variable
        print(f"User's Name: {NAME}")
        return NAME
    except Exception as e:
        print("An error occurred while finding the h1 element:", e)
        return "NONE"

# Function to scroll through a user profile
def scroll_profile(profile_link):
    global NAME
    # Get or install the Chrome driver path
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "profile.default_content_setting_values.notifications": 2   # block notifications
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--disable-gpu")
    # Initialize the Chrome driver with the notification disabled
    # Load the extension
    # Load the extension from a directory
    extension_directory = r'D:\Final Year Project\Final-Year-Project-Shared\automate_scrapping\extension' 
    chrome_options.add_argument(f'--load-extension={extension_directory}')
    driver_path = get_driver_path()
    print(driver_path)
    driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
    # Open the profile link
    driver.get(profile_link)
    login(driver,EMAIL,PASSWORD)
    script = """
    Object.defineProperty(document, 'hidden', {value: false});
    Object.defineProperty(document, 'visibilityState', {value: 'visible'});
    setInterval(() => {document.dispatchEvent(new Event('visibilitychange'));}, 6000);
    """
    driver.execute_script(script)
    # Time to wait for the page to load completely
    time.sleep(3)
    NAME=get_user_name(driver)
    time.sleep(1)
    SCROLL_PAUSE_TIME = 1

    # Get scroll height
    last_height=0
    while last_height==0:
        dismiss_alert_if_present(driver)
        last_height = driver.execute_script("return document.body.scrollHeight")
    height=min(100,last_height)
    lim=500
    cur=0
    while cur<lim:
        cur+=1
        dismiss_alert_if_present(driver)
        # Scroll down to bottom
        print(f"window.scrollTo(0, {height});")
        driver.execute_script(f"window.scrollTo(0, {height});")
        height=min(height+400,last_height)
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        last_height = new_height
        
        # Close the browser after scrolling
    time.sleep(30)
    driver.quit()
   
   
# Function to scroll through a user profile
def start_scroll(driver,profile_link):
    # Open the profile link
    global Logged_in
    driver.get(profile_link)
    while True:
        try:
            login(driver,EMAIL,PASSWORD)
            Logged_in=True
            break
        except:
            print("Exception in login")
            continue
    script = """
    Object.defineProperty(document, 'hidden', {value: false});
    Object.defineProperty(document, 'visibilityState', {value: 'visible'});
    setInterval(() => {document.dispatchEvent(new Event('visibilitychange'));}, 6000);
    """
    driver.execute_script(script)
    # Time to wait for the page to load completely
    time.sleep(3)
    time.sleep(1)
    SCROLL_PAUSE_TIME = 1

    # Get scroll height
    last_height=0
    while last_height==0:
        dismiss_alert_if_present(driver)
        last_height = driver.execute_script("return document.body.scrollHeight")
    height=min(100,last_height)
    lim=500
    cur=0
    while cur<lim:
        cur+=1
        dismiss_alert_if_present(driver)
        # Scroll down to bottom
        print(f"window.scrollTo(0, {height});")
        driver.execute_script(f"window.scrollTo(0, {height});")
        height=min(height+400,last_height)
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        last_height = new_height
        
        # Close the browser after scrolling
    
    
import socket
import threading

import threading

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

def start_server(host='127.0.0.1', port=65432):
    """
    Starts a server that listens for incoming connections and receives data.

    :param host: IP address to bind the server to (default is localhost).
    :param port: Port to bind the server to.
    
    """
    global NAME
    # Get or install the Chrome driver path
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "profile.default_content_setting_values.notifications": 2   # block notifications
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--disable-gpu")
    # Initialize the Chrome driver with the notification disabled
    # Load the extension
    # Load the extension from a directory
    extension_directory = r'D:\Final Year Project\Final-Year-Project-Shared\automate_scrapping\extension' 
    chrome_options.add_argument(f'--load-extension={extension_directory}')
    driver_path = get_driver_path()
    print(driver_path)
    driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
    Thread=None
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Server listening on {host}:{port}...")
        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")
                data = conn.recv(1024)  # Receive up to 1024 bytes
                if not data:
                    break
                message = data.decode('utf-8')  # Decode received bytes
                print(f"Received: {message}")
                if message.strip().lower() == "final stop":
                    print("Stop message received. Shutting down the server.")
                    conn.sendall(b"Server stopping.")  # Send acknowledgment
                    break
                elif message.strip().lower() == "stop":
                    Thread.stop()
                else:
                    link=message.strip().lower()
                    Thread=StoppableThread(target=start_scroll,args=(driver,link))
                    Thread.start()
    


if __name__=='__main__':
    #profile=input("Enter Facebook profile link: ")
    profile='https://www.facebook.com/zuck'
    scroll_profile(profile)
