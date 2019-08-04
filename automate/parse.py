
import os

import common

def run_parse():
    # extract parameters
    input_file, id_, file_tag = common.extract_parameters()

    # run script
    common.run(['python', 'scripts/parse_results.py', 
        '--chunks', str(common.N_TIMES_CHUNKS), 
        common.to_basename(input_file)])

    # push results to next repository
    repo_name = "events.cbrugger.times{}".format(id_)
    filenames = [path for path in os.listdir(common.project_path()) if path.endswith(".html")]
    
    common.upload_file(filenames, repo_name, id_, file_tag)

    print("Parse done")

if __name__ == "__main__":
    run_parse()
