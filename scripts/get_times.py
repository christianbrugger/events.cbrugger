
import argparse
import json

from selenium.common.exceptions import NoSuchElementException

import lib



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


def get_all_times(input_filename, id_="", headless=False):
    # read event ids
    with open(input_filename) as file:
        event_ids = json.load(file)

    print("Imported {} events.".format(len(event_ids)), flush=True)

    # login facebook
    driver = lib.create_driver(headless)

    lib.login_facebook(driver)

    # get times

    event_times = {}
    for index, event_id in enumerate(event_ids, start=1):
        print("Fetching events {} of {} ({})".format(index, len(event_ids), event_id), flush=True)
        event_times[event_id] = get_event_time(driver, event_id)
        print(event_id, event_times[event_id], flush=True)

    print("Processed {} events.".format(len(event_ids)), flush=True)

    # store results

    filename = lib.tagged_filename("times{}.txt".format(id_))

    with open(filename, 'w') as file:
        json.dump(event_times, file, indent=4, sort_keys=True)

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
    get_all_times(args.input_file, args.id, args.headless)


if __name__ == "__main__":
    main()
