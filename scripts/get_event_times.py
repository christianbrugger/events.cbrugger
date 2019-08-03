import time
import re
import os
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

try:
    from credentials import username
    from credentials import password
except ImportError:
    username = os.environ["FB_USERNAME"]
    password = os.environ["FB_PASSWORD"]

IS_HEADLESS = len(sys.argv) >= 2 and sys.argv[1] == "--headless"
FILE_TAG = os.environ.get("FILE_TAG", "")


# read event ids


filename = '{}_all_event_ids.txt'.format(FILE_TAG)
filepath = os.path.join(os.path.dirname(__file__), "..", "results", filename)

event_ids = []
with open(filepath, encoding="utf-8") as file:
    lines = file.read().strip("\n").split("\n")
    for line in lines:
        event_ids.append(line.split("<")[0])

print("Imported {} events.".format(len(event_ids)))

# create driver

options = Options()
if IS_HEADLESS:
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

print("Driver started")

# login

driver.get("http://www.facebook.org")
assert "Facebook" in driver.title
elem = driver.find_element_by_id("email")
elem.send_keys(username)
elem = driver.find_element_by_id("pass")
elem.send_keys(password)
elem.send_keys(Keys.RETURN)

print("Login completed")



# get date

def parse_event_time(item):
    try:
        from_to = item.find_element_by_class_name("_2ycp").get_attribute("content")
    except NoSuchElementException:
        print("exception")
        from_to = ""
    return from_to

def get_event_time(eid):
    print(eid)
    driver.get("https://www.facebook.com/events/" + eid)

    # check for time slots
    slots = driver.find_elements_by_class_name("_3h4x")
    if slots:
        # open first 3 times
        links = []
        for link in slots[0].find_elements_by_tag_name("a"):
            href = link.get_attribute("href")
            if "event_time_id" in href:
                links.append(str(href))
        
        times = []
        for link in links:
            driver.get(link)
            times.append(parse_event_time(driver))
        
        return ("recurring",) + tuple(times)
    else:
        return (parse_event_time(driver),)


event_times = {}
for index, event_id in enumerate(event_ids, start=1):
    print("Fetching events {} of {}.".format(index, len(event_ids)), end=" ")
    event_times[event_id] = get_event_time(event_id)
    print(event_id, event_times[event_id])


# store results

print("Processed {} events.".format(len(event_ids)))


filename = '{}_all_event_times.txt'.format(FILE_TAG)
filepath = os.path.join(os.path.dirname(__file__), "..", "results", filename)

with open(filepath, 'w', encoding="utf-8") as file:
    for event_id, data in event_times.items():
        line = event_id + "<"+ "<".join(data) + "\n"
        file.write(line)


# exit chrome

driver.close()

print("Done...")
