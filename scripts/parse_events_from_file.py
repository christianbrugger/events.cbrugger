import pprint
import time
import datetime
import os

import dateutil.parser
import dateutil.tz
import facebook

from credentials import access_token

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

# parse time

def parse_time(from_to, is_recurring=True):
    tzlocal = dateutil.tz.tzlocal()
    if " to " in from_to:
        from_str, to_str = from_to.split(" to ")
        dt_from = dateutil.parser.parse(from_str).astimezone(tzlocal)
        dt_to = dateutil.parser.parse(to_str).astimezone(tzlocal)

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
        dt_start = dateutil.parser.parse(from_to).astimezone(tzlocal)
        event_type = Unknown()
    
    return {"dt_start": dt_start, "event_type": event_type}




times = {}
with open("all_event_times.txt", encoding="utf-8") as file:
    lines = file.read().strip("\n").split("\n")
    for line in lines:
        id_, from_to, *recurring_times = line.split("<")
        is_recurring = from_to == "recurring"

        if is_recurring:
            times[id_] = list(map(parse_time, recurring_times))
        else:
            times[id_] = [parse_time(from_to, False)]
        

data = []
with open("all_event_ids.txt", encoding="utf-8") as file:
    lines = file.read().strip("\n").split("\n")
    for line in lines:
        id_, name, location, image = line.split("<")
        try:
            event_times = times[id_]
        except KeyError:
            print("Event without time information:", id_, name)
            continue
        else:
            for event_time in event_times:
                dt_start = event_time["dt_start"]
                event_type = event_time["event_type"]
                
                if dt_start.date() < datetime.datetime.now().date():
                    print("Skipping event, event is in the past:", id_, name)
                    continue

                data.append({"id": id_, "name": name, "location": location,
                    "image": image, "datetime": dt_start, "event_type": event_type})


sorted_data = sorted(data, key=lambda x: x['datetime'])

print("Imported {} events.".format(len(sorted_data)))

# get my event responses

"""
graph = facebook.GraphAPI(access_token, version='2.8')

all_rsvp_raw = list(graph.get_all_connections("me", "events", fields="id,rsvp_status"))
all_rsvp = {item['id']:item['rsvp_status'] for item in all_rsvp_raw}

print(all_rsvp)
print("got data")
"""
all_rsvp = {}


# simple text output

with open("events.txt", 'w', encoding="utf-8") as f:
    for info in sorted_data:
        f.write(#info["start_time"] + '\n' +
                info["name"] + '\n' +
                "https://www.facebook.com/events/" + info["id"] + '\n\n')



print("writen events.txt")


def html_output(filename, output_data):

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
          <body>
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
                       time=info["datetime"].strftime("%I:%M %p").strip('0'),
                       place=place_str,
                       rsvp=rsvp_str,
                       event_type=info["event_type"]))
        
        f.write("  </body>\n</html>\n")
    print("written", filename)


suffix = datetime.datetime.now().strftime("%Y_%m_%d")

# html all
html_output("events_{}.html".format(suffix), sorted_data)


# html berlin
berlin_workshops = [info for info in sorted_data if "berlin" in info["location"].lower()]
html_output("events_{}_berlin.html".format(suffix), berlin_workshops)

# html evening
evening_workshops = [info for info in sorted_data if 
                     isinstance(info["event_type"], (Session, Workshop)) and
                     "berlin" in info["location"].lower() and info["datetime"].hour > 17]
html_output("events_{}_evening.html".format(suffix), evening_workshops)


def update_index():
    with open("index.html", 'w', encoding="utf-8") as f:
        f.write("""
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <title>Events</title>
            <link rel="stylesheet" href="style.css">
          </head>
          <body>
        """)

        for filename in sorted(os.listdir(".")):
            if filename.startswith("events_"):
                f.write('<h1><a class="" href="{}">{}</a></h1>\n'.format(
                    filename, os.path.splitext(filename)[0]))
        
        f.write("  </body>\n</html>\n")
    print("written index.html")

update_index()

