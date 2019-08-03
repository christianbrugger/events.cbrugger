#!/bin/sh

set -e

export FILE_TAG=`TZ="Europe/Berlin" date +"%Y_%m_%d__%H_%M"`

echo generating $FILE_TAG

python scripts/get_all_events.py --headless

python scripts/get_event_times.py --headless

python scripts/parse_events_from_file.py
