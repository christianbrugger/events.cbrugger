import re
import argparse
import json

from selenium.common.exceptions import NoSuchElementException

import lib


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


def get_all_events(input_filename, id_="", headless=False):
    # load group ids
    with open(input_filename) as file:
        group_ids = json.load(file)

    print("Imported {} groups.".format(len(group_ids)), flush=True)

    # login facebook
    driver = lib.create_driver(headless)

    lib.login_facebook(driver)

    # get events

    all_group_events = {}

    for index, group_id in enumerate(group_ids, start=1):
        print("Fetching events {} of {} ({})".format(index, len(group_ids), group_id), flush=True)
        group_events = get_group_events(driver, group_id)
        all_group_events.update(group_events)
        print("Found {} events".format(len(group_events)), flush=True)

    print("\nFound {} events in total".format(len(all_group_events)))

    # store

    filename = lib.tagged_filename("events{}.txt".format(id_))

    with open(filename, 'w') as file:
        json.dump(all_group_events, file, indent=4, sort_keys=True)

    print("written", filename, flush=True)

    # exit chrome

    driver.close()

    print("Done...", flush=True)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, help="input file with group ids")
    parser.add_argument("--headless", help="run chrome in headless mode", action="store_true")
    parser.add_argument("--id", type=str, help="id appended to output filename", default="")
    args = parser.parse_args()
    print("input_file: {}".format(args.input_file))
    print("id: {}".format(args.id))
    if args.headless:
        print("headless turned on")
    return args


def main():
    args = get_args()
    get_all_events(args.input_file, args.id, args.headless)


if __name__ == "__main__":
    main()
