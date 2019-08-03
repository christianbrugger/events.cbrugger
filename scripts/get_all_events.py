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


ignored_group_ids = [
    'liveinberlin',
    'EventsinBerlin',
]


def scroll_to_bottom():
    SCROLL_PAUSE_TIME = 3.
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height





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

# login

driver.get("http://www.facebook.org")
assert "Facebook" in driver.title
elem = driver.find_element_by_id("email")
elem.send_keys(username)
elem = driver.find_element_by_id("pass")
elem.send_keys(password)
elem.send_keys(Keys.RETURN)


def get_groups():
    driver.get("https://www.facebook.com/bookmarks/groups/")

    group_ids = set([])
    for elem in driver.find_elements_by_tag_name("a"):
        url = elem.get_property("href")
        if url.startswith("https://www.facebook.com/groups/"):
            match = re.match("https://www.facebook.com/groups/([0-9a-zA-Z.]+)/", url)
            if match:
                group_id = match.group(1)
                if group_id in ignored_group_ids:
                    print("ignoring", group_id)
                else:
                    group_ids.add(group_id)

    return group_ids


# get all event ids

group_ids = get_groups()

print("Found {} groups.".format(len(group_ids)))

assert len(group_ids) > 0



def get_group_events(gid):
    print(gid)
    
    driver.get("https://www.facebook.com/groups/" + gid + "/events/")

    scroll_to_bottom()

    event_ids = {}
    for calendar_elem in driver.find_elements_by_class_name("fbCalendarItem"):
        url = calendar_elem.find_element_by_tag_name("a").get_property("href")
        id_ = re.findall("\d+", url)[0]
        img = calendar_elem.find_element_by_tag_name("img").get_property("src")
        name = calendar_elem.find_element_by_class_name("fsl").find_element_by_tag_name("a").text
        try:
            location = calendar_elem.find_element_by_class_name("_5inl").text
        except NoSuchElementException:
            location = ""
        try:
            location += " in " + calendar_elem.find_element_by_class_name("_5inm").text
        except NoSuchElementException:
            pass
        event_ids[id_] = name, location, img

    return event_ids


all_group_events = {}

for index, group_id in enumerate(group_ids, start=1):
    print("Fetching events {} of {}.".format(index, len(group_ids)),
          end=" ")
    group_events = get_group_events(group_id)
    all_group_events.update(group_events)
    print("Found {} events.".format(len(group_events)))

    if all_group_events:
        break

assert len(all_group_events) > 0

# store results

print("Found {} events.".format(len(all_group_events)))

filename = '{}_all_event_ids.txt'.format(FILE_TAG)
filepath = os.path.join(os.path.dirname(__file__), "..", "results", filename)

with open(filepath, 'w', encoding="utf-8") as file:
    for event_id, data in all_group_events.items():
        line = event_id + "<" + "<".join(data) + "\n"
        file.write(line)

print("written", filename)

# exit chrome

driver.close()

print("Done...")
