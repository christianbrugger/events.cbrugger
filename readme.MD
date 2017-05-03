Facebook Events
===============

Collects all Facebook events of all groups a user is in a text and html file.

How to run:
-----------

First collect all events by running:

```
python get_all_events.py
```

This will generate the file ```all_event_ids.txt``` containing all event ids.

Then run

```
python parse_events_from_file.py
```

This will generate the text and html file ```events.txt``` and ```events.html```.

I then edit the index.html by hand.

Dependencies:
-------------

### Python 3.5+ ###

The main interpreter.

*tested with version 3.5.1 32bit*

### Facebook Python SDK ###

I downloaded it from

https://github.com/mobolic/facebook-sdk.git

and installed it with:

```
python setup.py install
```

*tested with version 3.0.0-alpha (ea4e43ce5d8f0f9663c6574308d6c712dc52e9ad)*


### Selenium for Python ###

```
pip install selenium
```

*tested with version 3.3.3*

### Chrome ###

Latest Chrome browser

*tested with 57.0.2987.133 (64-bit) on Windows 10*

### Chromedriver ###

Latest ```chromedriver.exe``` from https://sites.google.com/a/chromium.org/chromedriver/

I put the ```chromedriver.exe``` in the same directory of the python files. Otherwise it has to be in path. 

*tested with version 2.29.461591*
