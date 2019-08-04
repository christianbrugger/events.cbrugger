
import sys
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

try:
    from credentials import username
    from credentials import password
except ImportError:
    username = os.environ["FB_USERNAME"]
    password = os.environ["FB_PASSWORD"]


FILE_TAG = os.environ.get("FILE_TAG", None)

SCROLL_PAUSE_TIME = 3.0 # seconds

EXIT_FILE_MISSING = 66

def scroll_to_bottom(driver, scroll_pause_time=SCROLL_PAUSE_TIME):
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(scroll_pause_time)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height



def create_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument('--no-sandbox')
    options.add_argument("--disable-notifications")
    options.add_experimental_option('prefs', {
        'credentials_enable_service': False,
        'profile': {
            'password_manager_enabled': False
        }
    })

    driver = webdriver.Chrome(options=options)

    print("Driver started", flush=True)

    return driver

def login_facebook(driver):
    driver.get("http://www.facebook.org")
    assert "Facebook" in driver.title
    elem = driver.find_element_by_id("email")
    elem.send_keys(username)
    elem = driver.find_element_by_id("pass")
    elem.send_keys(password)
    elem.send_keys(Keys.RETURN)

    # verify login
    composer_text = driver.find_element_by_id("pagelet_composer").text
    assert "Create Post" in composer_text
    assert "What's on your mind" in composer_text

    print("Login completed", flush=True)


def tagged_filename(filename, default=""):
    tag = FILE_TAG or default
    filename = '{}_{}'.format(tag, filename)
    return filename

def split(a, n):
    """ splits list a in n parts """
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))
