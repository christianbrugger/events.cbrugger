
import datetime
import os

import dateutil.tz

import common

TZ = dateutil.tz.gettz("Europe/Berlin")

def run_groups():
    # define tag
    utc_now = datetime.datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    now = utc_now.astimezone(TZ)
    file_tag = now.strftime("%Y.%m.%d_%H-%M")
    os.environ["FILE_TAG"] = file_tag

    # run script
    common.run("python scripts/get_groups.py --headless --chunks {}"
        .format(common.N_GROUP_CHUNKS))

    # push results to next repository
    for id_ in range(common.N_GROUP_CHUNKS):
        repo_name = "events.cbrugger.events{}".format(id_)
        filename = "{}_groups{}.txt".format(file_tag, id_)
        
        common.upload_file(filename, repo_name, id_, file_tag)

    print("Groups done")

if __name__ == "__main__":
    run_groups()