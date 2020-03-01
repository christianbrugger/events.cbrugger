
import argparse

import model
import lib
import get_groups, get_events, get_times, parse_results

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", "-d", default="events.db", type=str,
                        help="database file (default: events.db)")
    parser.add_argument("--no_headless", help="run chrome not in headless mode", action="store_true")
    parser.add_argument("--folder", "-f", default="results", type=str,
                        help="folder where results are stored (default: results)")
    parser.add_argument("--results_only", "-r", action="store_true", help="only update results")
    parser.add_argument("--debug", action="store_true", help="fetch only one event and event time")
    args = parser.parse_args()
    print("database file: {}".format(args.database))
    print("result folder: {}".format(args.folder))
    if args.no_headless:
        print("headless turned off")
    if args.debug:
        print("debugging turned on")
    return args


def main():
    args = get_args()
    db = model.Database(args.database)

    if not args.results_only:
        print("\nFacebook login:")
        driver = lib.create_driver(not args.no_headless)
        try:
            lib.login_facebook(driver)
            get_groups.get_groups(driver)
            get_events.get_all_events(driver, args.debug)
            get_times.get_all_times(driver, args.debug)
        finally:
            driver.close()

    parse_results.parse_results(args.folder)
    print("\nDone...", flush=True)


if __name__ == "__main__":
    main()
