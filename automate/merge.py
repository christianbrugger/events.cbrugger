
import common

def run_merge():
    # extract parameters
    input_file, id_, file_tag = common.extract_parameters()

    # run script
    returncode = common.run_returncode([
        'python', 'scripts/merge_events.py', 
        '--input_chunks', str(common.N_GROUP_CHUNKS), 
        '--output_chunks', str(common.N_EVENT_CHUNKS), 
        common.to_basename(input_file)])

    # check return code
    if returncode == common.EXIT_FILE_MISSING:
        print("INFO: file missing, exiting gracefully")
        return
    elif returncode != 0:
        raise RuntimeError("Error while calling script")

    # push results to next repository
    for id_ in range(common.N_EVENT_CHUNKS):
        repo_name = "events.cbrugger.times{}".format(id_)
        filename = "{}_merged{}.txt".format(file_tag, id_)
        
        common.upload_file(filename, repo_name, id_, file_tag)

    print("Merge done")

if __name__ == "__main__":
    run_merge()
