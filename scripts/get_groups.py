import re
import argparse
import json

import lib
import model

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


def get_groups(driver, ignored_group_ids=IGNORED_GROUP_IDS):
    print("\nScanning for new groups:")
    # get all event ids
    group_ids = fetch_groups(driver, ignored_group_ids)
    print("Found {} groups.".format(len(group_ids)), flush=True)

    # store groups
    for group_id in group_ids:
        model.Group.get_or_create(id=group_id)
