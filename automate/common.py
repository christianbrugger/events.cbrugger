
import subprocess
import shlex
import os
import time

N_GROUP_CHUNKS = 50

def project_path():
    return os.path.join(os.path.dirname(__file__), os.path.pardir)
def to_abs(*paths):
    return os.path.join(project_path(), *paths)

def to_uri(repo_name):
    return "https://github.com/christianbrugger/{}.git".format(repo_name)

def run_secured(command, wd=project_path()):
    """ calls process and hides all outputs, usefull when operating on sensitive information """
    # do not use check=True, as it leaks secret information in tracebacks
    process = subprocess.run(shlex.split(command), cwd=wd, 
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if process.returncode != 0:
        raise RuntimeError("command failed")

def run(command, wd=project_path()):
    subprocess.run(shlex.split(command), check=True, cwd=wd)


def setup_git(wd=project_path()):
    run('git config --global user.email "travis@travis-ci.org"', wd)
    run('git config --global user.name "Travis CI"', wd)

def upload_files(repo_name, wd=project_path()):
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


