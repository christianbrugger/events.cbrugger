
import sys
import os
import time
import datetime

import dateutil.parser
import dateutil.tz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

try:
    from credentials import username
    from credentials import password
except ImportError:
    username = os.environ["FB_USERNAME"]
    password = os.environ["FB_PASSWORD"]


FILE_TAG = os.environ.get("FILE_TAG", None)

SCROLL_PAUSE_TIME = 3.0 # seconds

EXIT_FILE_MISSING = 66

TIMEZONE = "Europe/Berlin"

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


def create_driver(headless=False, profile_path=None, open_devtools=False, log_level=2):
    """
    log_level:
        3: only fatal
    """
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument('--no-sandbox')
    options.add_argument('log-level={}'.format(log_level))
    options.add_argument("--disable-notifications")
    options.add_experimental_option('prefs', {
        'credentials_enable_service': False,
        'profile': {
            'password_manager_enabled': False
        }
    })
    if profile_path:
        options.add_argument('user-data-dir={}'.format(profile_path))
    if open_devtools:
        options.add_argument("--auto-open-devtools-for-tabs")

    driver = webdriver.Chrome(options=options)

    print("Driver started", flush=True)

    return driver


def logged_in(driver):
    try:
        driver.find_element_by_xpath("//div[@aria-label='Account']")
        return True
    except NoSuchElementException:
        return False


def login_facebook(driver):
    
    while True:
        driver.get("http://www.facebook.org")

        if logged_in(driver):
            print("Already logged in")
            break

        # provide credentials
        print("Not logged in. Providing login...")
        assert "Facebook" in driver.title
        elem = driver.find_element_by_id("email")
        elem.send_keys(username)
        elem = driver.find_element_by_id("pass")
        elem.send_keys(password)
        elem.send_keys(Keys.RETURN)

        if logged_in(driver):
            break

        print("WARNING: Login was not successfull. Retry in 60 seconds.", flush=True)
        time.sleep(3)

    print("Login completed", flush=True)


def tagged_filename(folder, filename, default=""):
    tag = FILE_TAG or default
    filename = '{}_{}'.format(tag, filename)
    return os.path.join(folder, filename)

def split(a, n):
    """ splits list a in n parts """
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

def parse_time_string(from_to):
    """
    parses facebook time string and returns start time and time delta.

    start time is returned as localized datetime object
    time delta is returned as float, hours
    """
    tz = dateutil.tz.gettz(TIMEZONE)
    if " to " in from_to:
        from_str, to_str = from_to.split(" to ")
        dt_from = dateutil.parser.parse(from_str).astimezone(tz)
        dt_to = dateutil.parser.parse(to_str).astimezone(tz)

        dt_start = dt_from

        td = (dt_to - dt_from).total_seconds() / 3600.
    else:
        dt_start = dateutil.parser.parse(from_to).astimezone(tz)
        td = -1.
    
    return dt_start, td
