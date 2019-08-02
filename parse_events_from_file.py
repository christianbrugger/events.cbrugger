import pprint
import time
import datetime

import dateutil.parser
import dateutil.tz
import facebook

from credentials import access_token

TYPE_EVENING = "Evening"
TYPE_WORKSHOP = "Workshop"
TYPE_RETREAT = "Retreat"
TYPE_RECURRING = "Recurring"
TYPE_UNKNOWN = ""

times = {}
with open("all_event_times.txt", encoding="utf-8") as file:
    lines = file.read().strip("\n").split("\n")
    for line in lines:
        id_, time_str, from_to, recurring_time = line.split("<")

        # date
        if not time_str:
            continue
        dt_date = datetime.datetime.strptime(time_str, "%A, %B %d, %Y")

        # time
        if " to " in from_to:
            from_str, to_str = from_to.split(" to ")
            tzlocal = dateutil.tz.tzlocal()
            dt_from = dateutil.parser.parse(from_str).astimezone(tzlocal)
            dt_to = dateutil.parser.parse(to_str).astimezone(tzlocal)

            if recurring_time:
                dt_time = datetime.datetime.strptime(recurring_time, '%I:%M %p')
                event_type = TYPE_RECURRING
            else:
                dt_time = dt_from

                td = dt_to - dt_from
                days, hours, seconds = td.days, td.seconds//3600, (td.seconds//60)%60
                if days > 0:
                    event_type = TYPE_RETREAT
                elif hours > 5:
                    event_type = TYPE_WORKSHOP
                else:
                    event_type = TYPE_EVENING
        else:
            dt_time = dateutil.parser.parse(from_str).astimezone(tzlocal)
            event_type = TYPE_UNKNOWN

        # add time
        dt_start = dt_date.replace(hour=dt_time.hour, minute=dt_time.minute)
        

        times[id_] = {"dt_start": dt_start, "event_type": event_type}

data = []
with open("all_event_ids.txt", encoding="utf-8") as file:
    lines = file.read().strip("\n").split("\n")
    for line in lines:
        id_, name, location, image = line.split("<")
        try:
            dt_start = times[id_]["dt_start"]
            event_type = times[id_]["event_type"]
        except KeyError:
            print("Event without time information:", id_, name)
        data.append({"id": id_, "name": name, "location": location, "image": image,
                     "datetime": dt_start, "event_type": event_type})


sorted_data = sorted(data, key=lambda x: x['datetime'])


graph = facebook.GraphAPI(access_token, version='2.8')

"""
limit = 50
all_group_info = {}
while event_ids:
    chunk = event_ids[:limit]
    del event_ids[:limit]

    print(chunk)
    import sys
    sys.exit()
    
    group_info = graph.get_objects(
            ids=chunk, fields="start_time, name, picture.type(normal), place")

    for result_dict in group_info.values():
        result_dict["py_start_time"] = datetime.datetime.strptime(
                result_dict["start_time"], '%Y-%m-%dT%H:%M:%S%z')
    all_group_info.update(group_info)


sorted_info = sorted(all_group_info.values(),
                     key=lambda x: x['py_start_time'])

"""

# get my event responses
all_rsvp_raw = list(graph.get_all_connections("me", "events", fields="id,rsvp_status"))
all_rsvp = {item['id']:item['rsvp_status'] for item in all_rsvp_raw}
print(all_rsvp)
print("got data")



# simple text output
with open("events.txt", 'w', encoding="utf-8") as f:
    for info in sorted_data:
        f.write(#info["start_time"] + '\n' +
                info["name"] + '\n' +
                "https://www.facebook.com/events/" + info["id"] + '\n\n')



print("writen text output")


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

html_output("events.html", sorted_data)

evening_workshops = [info for info in sorted_data if info["event_type"] in [TYPE_RECURRING, TYPE_EVENING, TYPE_WORKSHOP] and
                     "berlin" in info["location"].lower() and info["datetime"].hour > 17]


html_output("events_evening.html", evening_workshops)

print("done")
