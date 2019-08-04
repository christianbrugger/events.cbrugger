
import subprocess
import shlex
import os
import time
import shutil
import json

N_GROUP_CHUNKS = 50
N_MERGE_CHUNKS = 1

def project_path():
    return os.path.join(os.path.dirname(__file__), os.path.pardir)
def to_abs(*paths):
    return os.path.join(project_path(), *paths)

def to_uri(repo_name):
    return "https://github.com/christianbrugger/{}.git".format(repo_name)

def run_secured(command, wd=project_path()):
    """ calls process and hides all outputs, usefull when operating on sensitive information """
    if isinstance(command, str):
        command = shlex.split(command)
    # do not use check=True, as it leaks secret information in tracebacks
    process = subprocess.run(command, cwd=wd, 
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if process.returncode != 0:
        raise RuntimeError("command failed")

def run(command, wd=project_path()):
    if isinstance(command, str):
        command = shlex.split(command)
    subprocess.run(command, check=True, cwd=wd)

def run_output(command, wd=project_path()):
    if isinstance(command, str):
        command = shlex.split(command)
    process = subprocess.run(command, check=True, cwd=wd,
        universal_newlines=True, stdout=subprocess.PIPE)
    return process.stdout


def setup_git(wd=project_path()):
    run('git config --global user.email "travis@travis-ci.org"', wd)
    run('git config --global user.name "Travis CI"', wd)

def push(repo_name, wd=project_path()):
    token = os.environ['GH_TOKEN']
    secure_uri = 'https://{}@github.com/christianbrugger/{}.git'.format(token, repo_name)

    run_secured('git remote add origin-push {}'.format(secure_uri), wd)

    while True:
        run_secured("git pull --rebase", wd)
        try:
            run_secured('git push --quiet --set-upstream origin-push master', wd)
        except RuntimeError:
            print("Error while pushing changes. Trying again in a few seconds.")
            time.sleep(3)
        else:
            break
    
    print("Uploaded files successfully.")


def extract_parameters():
    """ extract parameters from commit log """
    message = run_output("git log -1 --pretty=%B", to_abs("..")).strip()
    data = json.loads(message)

    input_file = to_abs("..", "inputs", data["input"])
    id_ = data["id"]
    file_tag = data["tag"]
    os.environ["FILE_TAG"] = file_tag

    return input_file, id_, file_tag

def upload_file(filename, repo_name, id_, file_tag):
    run("git clone {}".format(to_uri(repo_name)))

    shutil.move(to_abs(filename), to_abs(repo_name, "inputs", filename))
    message = json.dumps({"input": filename, "id": id_, "tag": file_tag})

    wd = to_abs(repo_name)
    setup_git(wd)
    run(['git', 'add', 'inputs/' + filename], wd)
    run(['git', 'commit', '--message', message], wd)

    push(repo_name, wd)
