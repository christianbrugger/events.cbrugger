#!/bin/sh

set -e

. automate/helpers.sh

export FILE_TAG=`TZ="Europe/Berlin" date +"%Y_%m_%d__%H_%M"`

python scripts/get_groups.py --headless --chunks=50

cat ${FILE_TAG}_groups0.txt
