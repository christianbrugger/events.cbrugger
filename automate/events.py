
import os
import shutil
import json

import common

def run_events():
    # extract parameters from commit log
    message = common.run_output("git log -1 --pretty=%B", common.to_abs("..")).strip()
    data = json.loads(message)

    input_file = common.to_abs("..", "inputs", data["input"])
    id_ = data["id"]
    file_tag = data["tag"]
    os.environ["FILE_TAG"] = file_tag

    # run script
    common.run(['python', 'scripts/get_events.py', '--headless', '--id', str(id_), input_file])

    # push results to next repository
    for id_ in range(1):
        repo_name = "events.cbrugger.merge{}".format(id_)
        filename = "{}_events{}.txt".format(file_tag, id_)
        
        common.upload_file(filename, repo_name, id_, file_tag)

    print("Events done")

if __name__ == "__main__":
    run_events()
