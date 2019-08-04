
import os
import shutil
import json

import common

def run_events():
    # extrat parameters
    input_file, id_, file_tag = common.extract_parameters()

    # run script
    common.run(['python', 'scripts/merge_events.py', 
        '--input_chunks', 1, 
        '--output_chunks', common.N_MERGE_CHUNKS, 
        "{}_events".format(file_tag)])

    # push results to next repository
    for id_ in range(1):
        repo_name = "events.cbrugger.times{}".format(id_)
        filename = "{}_merged{}.txt".format(file_tag, id_)
        
        common.upload_file(filename, repo_name, id_, file_tag)

    print("Events done")

if __name__ == "__main__":
    run_events()
