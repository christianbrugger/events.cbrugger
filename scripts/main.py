
import argparse

import model
import lib
import get_groups, get_events, get_times

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", "-d", default="events.db", type=str,
                        help="database file (default: events.db)")
    parser.add_argument("--headless", "-l", help="run chrome in headless mode", action="store_true")
    args = parser.parse_args()
    print("database file: {}".format(args.database))
    if args.headless:
        print("headless turned on")
    return args


def main():
    args = get_args()
    db = model.Database(args.database)
    driver = lib.create_driver(args.headless)
    try:
        lib.login_facebook(driver)
        get_groups.get_groups(driver)
        get_events.get_all_events(driver)
        get_times.get_all_times(driver)
    finally:
        driver.close()
    print("Done...", flush=True)


if __name__ == "__main__":
    main()
