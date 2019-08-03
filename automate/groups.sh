#!/bin/sh

set -e
. automate/helpers.sh

export FILE_TAG=`TZ="Europe/Berlin" date +"%Y_%m_%d__%H_%M"`

# install requirements
python -m pip -r requirements.txt

# run script
python scripts/get_groups.py --headless --chunks=50

# push results to next repository
export FILENAME=${FILE_TAG}_groups0.txt
git clone https://github.com/christianbrugger/events.cbrugger.events0.git
cd events.cbrugger.events0
mv ../${FILENAME} inputs
git add inputs/${FILENAME}
git commit --message "${FILENAME}"

setup_git
upload_files