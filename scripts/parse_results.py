import pprint
import time
import datetime
import os
import argparse
import json
import sys
import collections

import dateutil.parser
import dateutil.tz

import lib
from model import Database, Group, Event, EventTime

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


def get_event_type(time_delta, is_recurring=True):
    """ time_delta in hours """
    if time_delta >= 0:
        days, hours = time_delta // 24, time_delta
        if days > 0:
            event_type = Retreat(days + 1, is_recurring)
        elif hours > 5:
            event_type = Workshop(hours, is_recurring)
        else:
            event_type = Session(is_recurring)
    else:
        event_type = Unknown()
    
    return event_type


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
            day = info.start_time.date()
            if day != last_day:
                last_day = day
                f.write("<h2>" + day.strftime("%A, %B %d, %Y") + "</h2>\n")

            place_str = info.location

            rsvp_str = ""
            if info.event_id in all_rsvp:
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
            """.format(img_url=info.image,
                    event_url='https://www.facebook.com/events/' + info.event_id,
                    event_name=info.name,
                    time=info.start_time.strftime("%H:%M").lstrip('0'), #%I:%M %p
                    place=place_str,
                    rsvp=rsvp_str,
                    event_type=info.event_type))
        
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

        for filename in sorted(os.listdir("."), reverse=True):
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


ParsedEvent = collections.namedtuple("ParseEvent",
        ["event_id", "name", "location", "image", "recurring", "start_time", "event_type"])

def parse_results():
    tz = dateutil.tz.gettz(TIMEZONE)
    
    # import event data
    parsed_events = []
    for event_time in EventTime.select():
        event = event_time.event

        event_type = get_event_type(event_time.time_delta, event.recurring)
        start_time = event_time.time_from.replace(tzinfo=datetime.timezone.utc).astimezone(tz)

        parsed_event = ParsedEvent(event.id, event.name, event.location, event.image, 
                event.recurring, event_time.time_from.astimezone(tz), event_type)
        
        if start_time.date() < datetime.datetime.now().date():
            print("Skipping event, event is in the past:", parsed_event.name)
        else:
            parsed_events.append(parsed_event)

    # sort data
    sorted_data = sorted(parsed_events, key=lambda x: x.start_time)
    print("Imported {} events.".format(len(sorted_data)), flush=True)

    # write html files    
    default_tag = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M")
    T = lambda name: lib.tagged_filename(name, default_tag)

    # all
    write_html_output(T("events.html"), sorted_data)

    # berlin
    berlin_workshops = [info for info in sorted_data if 
                        "berlin" in info.location.lower() and 
                        "yoga" not in info.name.lower() and
                        "acro" not in info.name.lower() and
                        "vinyasa" not in info.name.lower()]
    write_html_output(T("events_berlin.html"), berlin_workshops)

    # eveing
    evening_workshops = [info for info in sorted_data if 
                        isinstance(info.event_type, (Session, Workshop)) and
                        "berlin" in info.location.lower() and info.start_time.hour > 17 and
                        "yoga" not in info.name.lower() and
                        "acro" not in info.name.lower() and
                        "vinyasa" not in info.name.lower()]
    write_html_output(T("events_evenings.html"), evening_workshops)

    # index
    write_index("index.html")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", "-d", default="events.db", type=str,
                        help="database file (default: events.db)")
    args = parser.parse_args()
    print("database file: {}".format(args.database))
    return args


def main():
    args = get_args()
    db = Database(args.database)
    parse_results()


if __name__ == "__main__":
    main()
