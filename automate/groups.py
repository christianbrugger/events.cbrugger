
import datetime
import os
import shutil

import dateutil.tz

import common

TZ = dateutil.tz.gettz("Europe/Berlin")

def run_groups():
    # set tag
    utc_now = datetime.datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    now = utc_now.astimezone(TZ)
    file_tag = now.strftime("%Y.%m.%d_%H-%M")
    os.environ["FILE_TAG"] = file_tag

    # install dependencies
    common.run("python -m pip install -r requirements.txt")

    # run script
    common.run("python scripts/get_groups.py --headless --chunks {}"
        .format(common.N_GROUP_CHUNKS))

    # push results to next repository
    for id_ in range(1):
        repo_name = "events.cbrugger.events{}".format(id_)
        filename = "{}_groups{}.txt".format(file_tag, id_)
        
        common.run("git clone {}".format(common.to_uri(repo_name)))
        shutil.move(common.to_abs(filename), common.to_abs(repo_name, "inputs", filename))

        wd = common.to_abs(repo_name)
        common.setup_git(wd)
        common.run("git add inputs/{}".format(filename), wd)
        common.run('git commit --message "{}"'.format(filename), wd)

        common.upload_files(repo_name, wd)

    print("Groups done")

if __name__ == "__main__":
    run_groups()