import re
import argparse
import json
import datetime

from selenium.common.exceptions import NoSuchElementException

import lib
from model import Database, Group, Event


def get_group_events(driver, gid):
    driver.get("https://www.facebook.com/groups/" + gid + "/events/")

    lib.scroll_to_bottom(driver)

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
        event_ids[id_] = {"name": name, "location": location, "image": img}

    return event_ids


def get_all_events(driver):
    while True:
        group_count = Group.select().where(Group.fetched_events == False).count()
        if group_count == 0:
            break
        
        group = Group.get(Group.fetched_events == False)
        print("Processing {} groups. Fetching events.".format(group_count), flush=True)

        group_events = get_group_events(driver, group.id)
        for event_id, data in group_events.items():
            event = Event.get_or_create(id=event_id)[0]
            event.name = data["name"]
            event.location = data["location"]
            event.image = data["image"]
            event.save()
        print("Found {} events".format(len(group_events)), flush=True)
                
        group.fetched_events = True
        group.last_fetched = datetime.datetime.utcnow()
        group.save()
            
        if len(group_events) > 0:
            break
