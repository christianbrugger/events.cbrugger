import time
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

from credentials import username
from credentials import password


# read event ids

event_ids = []
with open("all_event_ids.txt", encoding="utf-8") as file:
    lines = file.read().strip("\n").split("\n")
    for line in lines:
        event_ids.append(line.split("<")[0])

print("Imported {} events.".format(len(event_ids)))

# create driver

options = Options()
options.add_argument("--disable-notifications");
options.add_experimental_option('prefs', {
    'credentials_enable_service': False,
    'profile': {
        'password_manager_enabled': False
    }
})

driver = webdriver.Chrome(options=options)

# login

driver.get("http://www.facebook.org")
assert "Facebook" in driver.title
elem = driver.find_element_by_id("email")
elem.send_keys(username)
elem = driver.find_element_by_id("pass")
elem.send_keys(password)
elem.send_keys(Keys.RETURN)



# get date

def parse_event_time(item):
    try:
        from_to = driver.find_element_by_class_name("_2ycp").get_attribute("content")
    except NoSuchElementException:
        from_to = ""
    return from_to

def get_event_time(eid):
    print(eid)
    driver.get("https://www.facebook.com/events/" + eid)

    # check for time slots
    slots = driver.find_elements_by_class_name("_3h4x")
    if slots:
        # open first event
        href = slots[0].find_element_by_tag_name("a").get_attribute("href")
        driver.get(href)
        return parse_event_time(driver), "recurring"
    else:
        return parse_event_time(driver), ""


event_times = {}
for index, event_id in enumerate(event_ids, start=1):
    print("Fetching events {} of {}.".format(index, len(event_ids)), end=" ")
    event_times[event_id] = get_event_time(event_id)
    print(event_id, event_times[event_id])


# store results

print("Processed {} events.".format(len(event_ids)))

with open('all_event_times.txt', 'w', encoding="utf-8") as file:
    for event_id, data in event_times.items():
        line = event_id + "<"+ "<".join(data) + "\n"
        file.write(line)


# exit chrome

driver.close()

print("Done...")
