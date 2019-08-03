import re
import argparse
import json

import lib

IGNORED_GROUP_IDS = [
    'liveinberlin',
    'EventsinBerlin',
]


def fetch_groups(driver, ignored_group_ids):
    driver.get("https://www.facebook.com/bookmarks/groups/")

    group_ids = set([])
    for elem in driver.find_elements_by_tag_name("a"):
        url = elem.get_property("href")
        if url.startswith("https://www.facebook.com/groups/"):
            match = re.match("https://www.facebook.com/groups/([0-9a-zA-Z.]+)/", url)
            if match:
                group_id = match.group(1)
                if group_id in ignored_group_ids:
                    print("INFO: ignoring", group_id)
                else:
                    group_ids.add(group_id)
            else:
                print("WARNING: unable to parse", url)

    return sorted(group_ids)


def get_groups(n_chunks=4, ignored_group_ids=tuple(), headless=False):
    # login facebook
    driver = lib.create_driver(headless)

    lib.login_facebook(driver)

    # get all event ids

    group_ids = fetch_groups(driver, ignored_group_ids)

    print("Found {} groups.".format(len(group_ids)), flush=True)

    assert len(group_ids) >= n_chunks

    # store groups

    for i, chunk in enumerate(lib.split(group_ids, n_chunks)):
        filepath = lib.tagged_filename("groups{}.txt".format(i))

        with open(filepath, 'w') as file:
            json.dump(chunk, file, indent=4)

        print("written", filepath, flush=True)

    # exit chrome

    driver.close()

    print("Done...", flush=True)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", help="run chrome in headless mode", action="store_true")
    parser.add_argument("--chunks", type=int, help="store output in n files", default=1)
    args = parser.parse_args()
    if args.headless:
        print("headless turned on")
    print("chunks: {}".format(args.chunks))
    return args


def main():
    args = get_args()
    get_groups(args.chunks, IGNORED_GROUP_IDS, args.headless)


if __name__ == "__main__":
    main()

