
import os
import shutil

import common

def run_parse():
    # extract parameters
    input_file, id_, file_tag = common.extract_parameters()
    repo_name = "events.cbrugger.results"

    # copy previous result files
    common.clone(repo_name)
    result_dir = os.path.join(common.project_path(), repo_name, "inputs")
    for filename in os.listdir(result_dir):
        shutil.copy(os.path.join(result_dir, filename), common.project_path())

    # run script
    returncode = common.run_returncode([
        'python', 'scripts/parse_results.py', 
        '--chunks', str(common.N_TIMES_CHUNKS), 
        common.to_basename(input_file)])

    # check return code
    if returncode == common.EXIT_FILE_MISSING:
        print("INFO: file missing, exiting gracefully")
        return
    elif returncode != 0:
        raise RuntimeError("Error while calling script")

    # push results to next repository
    filenames = [path for path in os.listdir(common.project_path()) if path.endswith(".html")]
    
    common.upload_file(filenames, repo_name, id_, file_tag, do_clone=False)

    print("Parse done")

if __name__ == "__main__":
    run_parse()
