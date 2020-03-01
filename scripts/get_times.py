
import argparse
import json
import datetime

from peewee import DoesNotExist
from selenium.common.exceptions import NoSuchElementException

import lib
from model import Database, Event, EventTime



def parse_event_time(item):
    try:
        from_to = item.find_element_by_class_name("_2ycp").get_attribute("content")
    except NoSuchElementException:
        print("exception")
        from_to = ""
    return from_to


def get_event_time(driver, eid):
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
        
        return {"recurring": True, "times": times}
    else:
        return {"recurring": False, "times": [parse_event_time(driver)]}


def get_all_times(driver, debug=False):
    print("\nScanning for event times:")
    
    while True:
        event_count = Event.select().where(Event.fetched_times == False).count()
        if event_count == 0:
            break

        event = Event.get(Event.fetched_times == False)
        print("Processing {} events. Fetching times.".format(event_count), flush=True)

        result = get_event_time(driver, event.id)
        for time_str in result["times"]:
            t_from, t_delta = lib.parse_time_string(time_str)

            event_time = EventTime(event=event, time_str=time_str,
                    time_from=t_from.astimezone(datetime.timezone.utc).replace(tzinfo=None),
                    time_delta=t_delta)
            try:
                event_time.id = EventTime.get(event=event, time_str=time_str).id
            except DoesNotExist:
                pass
            event_time.save()
            
        event.recurring = int(result["recurring"])
        event.fetched_times = True
        event.last_fetched = datetime.datetime.utcnow()
        event.save()
        print("Found {} times".format(len(result["times"])), flush=True)

        if debug:
            break
