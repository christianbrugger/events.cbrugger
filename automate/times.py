
import common

def run_times():
    # extract parameters
    input_file, id_, file_tag = common.extract_parameters()

    # run script
    common.run(['python', 'scripts/get_times.py', '--headless', '--id', str(id_), input_file])

    # push results to next repository
    repo_name = "events.cbrugger.parse"
    filename = "{}_times{}.txt".format(file_tag, id_)
    
    common.upload_file(filename, repo_name, id_, file_tag)

    print("Times done")

if __name__ == "__main__":
    run_times()
