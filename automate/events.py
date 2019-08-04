
import common

def run_events():
    # extract parameters
    input_file, id_, file_tag = common.extract_parameters()

    # run script
    common.run(['python', 'scripts/get_events.py', '--headless', '--id', str(id_), input_file])

    # push results to next repository
    repo_name = "events.cbrugger.merge"
    filename = "{}_events{}.txt".format(file_tag, id_)
    
    common.upload_file(filename, repo_name, id_, file_tag)

    print("Events done")

if __name__ == "__main__":
    run_events()
