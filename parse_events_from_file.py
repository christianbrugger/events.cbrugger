import pprint
import time
import datetime

import facebook

from credentials import access_token

event_ids = []
with open("all_event_ids.txt") as file:
    event_ids = file.read().strip("\n").split("\n")


graph = facebook.GraphAPI(access_token, version='2.8')


limit = 50
all_group_info = {}
while event_ids:
    chunk = event_ids[:limit]
    del event_ids[:limit]
    
    group_info = graph.get_objects(
            ids=chunk, fields="start_time, name, picture.type(normal), place")

    for result_dict in group_info.values():
        result_dict["py_start_time"] = datetime.datetime.strptime(
                result_dict["start_time"], '%Y-%m-%dT%H:%M:%S%z')
    all_group_info.update(group_info)


sorted_info = sorted(all_group_info.values(),
                     key=lambda x: x['py_start_time'])


# get my event responses
all_rsvp_raw = list(graph.get_all_connections("me", "events", fields="id,rsvp_status"))
all_rsvp = {item['id']:item['rsvp_status'] for item in all_rsvp_raw}

print("got data")

# simple text output
with open("events.txt", 'w', encoding="utf-8") as f:
    for info in sorted_info:
        f.write(info["start_time"] + '\n' +
                info["name"] + '\n' +
                "https://www.facebook.com/events/" + info["id"] + '\n\n')



print("writen text output")


# html output
with open("events.html", 'w', encoding="utf-8") as f:
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
    for info in sorted_info:
        day = info["py_start_time"].date()
        if day != last_day:
            last_day = day
            f.write("<h2>" + day.strftime("%A, %B %d, %Y") + "</h2>\n")

        place_str = ""
        if "place" in info:
            if "name" in info:
                place_str = info["place"]["name"]

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
      </td>
    <tr>
  </table>
</li>
</ul>
        """.format(img_url=info["picture"]["data"]["url"],
                   event_url='https://www.facebook.com/events/' + info["id"],
                   event_name=info["name"],
                   time=info["py_start_time"].time().strftime("%I:%M %p").strip('0'),
                   place=place_str,
                   rsvp=rsvp_str))
        
        #f.write("<h3>" + info["name"] + "</h3>\n")
        #f.write('<p>https://www.facebook.com/events/' + info["id"] + '</p>\n')
        
    
    f.write("  </body>\n</html>\n")
        
    

