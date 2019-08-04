import pprint
import time
import datetime
import os
import argparse
import json
import sys

import dateutil.parser
import dateutil.tz
#import facebook

import lib
#from credentials import access_token

TIMEZONE = "Europe/Berlin"


class EventType:
    def __init__(self, label, recurring=False):
        self.label = label
        if recurring:
            self.label += ", recurring"
    def __str__(self):
        return self.label
    
class Session(EventType):
    def __init__(self, recurring):
        super().__init__("Short Event", recurring)
    
class Workshop(EventType):
    def __init__(self, hours, recurring):
        super().__init__("{}-hour Workshop".format(hours), recurring)
    
class Retreat(EventType):
    def __init__(self, days, recurring):
        super().__init__("{}-day Retreat".format(days), recurring)
    
class Unknown(EventType):
    def __init__(self):
        super().__init__("")


def parse_time(from_to, is_recurring=True):
    tz = dateutil.tz.gettz(TIMEZONE)
    if " to " in from_to:
        from_str, to_str = from_to.split(" to ")
        dt_from = dateutil.parser.parse(from_str).astimezone(tz)
        dt_to = dateutil.parser.parse(to_str).astimezone(tz)

        dt_start = dt_from

        td = dt_to - dt_from
        days, hours, seconds = td.days, td.seconds//3600, (td.seconds//60)%60
        if days > 0:
            event_type = Retreat(days + 1, is_recurring)
        elif hours > 5:
            event_type = Workshop(hours, is_recurring)
        else:
            event_type = Session(is_recurring)
    else:
        dt_start = dateutil.parser.parse(from_to).astimezone(tz)
        event_type = Unknown()
    
    return dt_start, event_type


def write_html_output(filename, output_data, all_rsvp={}):
    # html output
    with open(filename, 'w', encoding="utf-8") as f:
        f.write("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>Events</title>
            <link rel="stylesheet" href="style.css">
        </head>
        <body>\n
        """)
        
        last_day = None
        for info in output_data:
            day = info["datetime"].date()
            if day != last_day:
                last_day = day
                f.write("<h2>" + day.strftime("%A, %B %d, %Y") + "</h2>\n")

            place_str = info["location"]

            rsvp_str = ""
            if info["id"] in all_rsvp:
                rsvp_str = all_rsvp[info["id"]]

            # table with entries
            f.write("""
                <ul>
                <li>
                <table class="{rsvp}">
                    <tr>
                    <td>
                        <div class="time">{time}</div>
                    </td>
                    <td>
                        <div><img src="{img_url}"></div>
                    </td>
                    <td>
                        <div><a class="{rsvp}" href="{event_url}">{event_name}</a></div>
                        <div>{place}</div>
                        <div class="rsvp">{rsvp}</div>
                        <div>{event_type}</div>
                    </td>
                    <tr>
                </table>
                </li>
                </ul>
            """.format(img_url=info["image"],
                    event_url='https://www.facebook.com/events/' + info["id"],
                    event_name=info["name"],
                    time=info["datetime"].strftime("%H:%M").lstrip('0'), #%I:%M %p
                    place=place_str,
                    rsvp=rsvp_str,
                    event_type=info["event_type"]))
        
        f.write("  </body>\n</html>\n")

    print("written", filename, flush=True)


def write_index(filepath):
    with open(filepath, 'w', encoding="utf-8") as f:
        f.write("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>Events</title>
            <link rel="stylesheet" href="style.css">
        </head>
        <body>\n
        """)

        for filename in sorted(os.listdir(".")):
            if filename.endswith(".html") and filename != filepath:
                f.write('<h1><a class="" href="{}">{}</a></h1>\n'.format(
                    filename, os.path.splitext(filename)[0]))
        
        f.write("  </body>\n</html>\n")
    
    print("written", filepath, flush=True)


def get_rsvp():

    # get my event responses
    graph = facebook.GraphAPI(access_token, version='2.8')

    all_rsvp_raw = list(graph.get_all_connections("me", "events", fields="id,rsvp_status"))
    all_rsvp = {item['id']:item['rsvp_status'] for item in all_rsvp_raw}

    print("Fetched data")
    return all_rsvp


def parse_results(basename, input_chunks):

    # import event data

    data = []
    try:
        for i in range(input_chunks):
            filename = "{}{}.txt".format(basename, i)
            print("Opening file", filename)

            with open(filename) as file:
                new_data = json.load(file)

            for id_ in new_data:
                event_times = new_data[id_]["times"]
                recurring = new_data[id_]["recurring"]

                for from_to in event_times:
                    dt_start, event_type = parse_time(from_to, recurring)
                    
                    if dt_start.date() < datetime.datetime.now().date():
                        print("Skipping event, event is in the past:", id_, new_data[id_]["name"])
                        continue

                    data_copy = new_data[id_].copy()
                    data_copy.update({"id": id_, "datetime": dt_start, "event_type": event_type})
                    data.append(data_copy)

    except FileNotFoundError:
        print("INFO: One or more files not available. Quitting")
        sys.exit(lib.EXIT_FILE_MISSING)

    # sort data

    sorted_data = sorted(data, key=lambda x: x['datetime'])

    print("Imported {} events.".format(len(sorted_data)), flush=True)


    # write html files

    default_tag = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M")
    T = lambda name: lib.tagged_filename(name, default_tag)

    # all
    write_html_output(T("events.html"), sorted_data)

    # berlin
    berlin_workshops = [info for info in sorted_data if "berlin" in info["location"].lower()]
    write_html_output(T("events_berlin.html"), berlin_workshops)

    # eveing
    evening_workshops = [info for info in sorted_data if 
                        isinstance(info["event_type"], (Session, Workshop)) and
                        "berlin" in info["location"].lower() and info["datetime"].hour > 17]
    write_html_output(T("events_evenings.html"), evening_workshops)

    # index
    write_index("index.html")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("basename", type=str, help="beginning of filename with time data, excluding id and extension")
    parser.add_argument("--chunks", type=int, help="number of input files", default=1)
    args = parser.parse_args()
    print("basename: {}".format(args.basename))
    print("chunks: {}".format(args.chunks))
    return args


def main():
    args = get_args()
    parse_results(args.basename, args.chunks)


if __name__ == "__main__":
    main()
