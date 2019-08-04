#!/bin/sh

set -e

export FILE_TAG=`TZ="Europe/Berlin" date +"%Y_%m_%d__%H_%M"`

echo generating $FILE_TAG

python scripts/get_groups.py --headless --chunks 50

python scripts/get_events.py --headless --id 0 ${FILE_TAG}_groups0.txt

python scripts/merge_events.py --input_chunks 1 --output_chunks 1 ${FILE_TAG}_events

python scripts/get_times.py --headless --id 0 ${FILE_TAG}_merged0.txt

python scripts/parse_results.py --chunks 1 ${FILE_TAG}_times
