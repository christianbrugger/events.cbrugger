Facebook Events
===============

Collects all Facebook events of all groups a user is in a text and html file.

Result: https://christianbrugger.github.io/events.cbrugger/index.html

How to run:
-----------

First collect all events by running:

```
python get_all_events.py
```

This will generate the file `all_event_ids.txt` containing all event ids.

Then run

```
python get_event_times.py
```

This will collect all event times in `all_event_times.txt`.

Then run

```
python parse_events_from_file.py
```

This will generate the text and html file `events.txt` and `events_*.html`.

Also the `index.html` is updated.

Alternatively you can run

```
run_all.bat
```

This will run all the above commands in sequence.


Credentials:
------------

Copy the file ```credentials_template.py``` and name it ```credentials.py```.

Enter your Facebook username and password. 

If you want to use the facebook-sdk, first create a user access token on the 
following site ```https://developers.facebook.com/tools/explorer```.
Allowed all permissions for simplicity.


Dependencies:
-------------

It is best to use a virtual environment with all the dependencies. You can do this by:
```
python -m venv env
.\env\Scripts\activate
python -m pip install -r requirements.txt
```

### Python 3.5+

The main interpreter. Get the latest version.

*tested with version 3.7.3 64bit*

### Dateutil

Used to parse dates and times. Get the latest version

```
python -m pip install python-dateutil
```

*tested with version 2.8.0*

### Facebook SDK

Not used right now. If you want to use it, get the latest version

```
python -m pip install facebook-sdk
```

*tested with version 2019.6.16*

### Selenium for Python

Used to drive chrome from python.

```
python -m pip install selenium
```

*tested with version 3.141.0*

### Chrome ###

Latest Chrome browser. Used to retrieve most of the information.

*tested with 76.0.3809.87 (64-bit) on Windows 10*

### Chromedriver

Used to control chrome programatically.

A `chromedriver.exe` matching your Chrome version from
 
https://sites.google.com/a/chromium.org/chromedriver/

I put the `chromedriver.exe` in the same directory as the python files.

*tested with version 75.0.3770.140*
