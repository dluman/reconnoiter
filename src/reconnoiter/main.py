import os
import sys
import subprocess
from pathlib import Path
from git import Repo

from arglite import parser as cliarg

UP = ".."

def pull_latest_changes(repo: str = "") -> bool:
    assign = Repo.init(Path(repo))
    try:
        assign.remote().pull()
    except Exception as e:
        print(f"[ERROR] Error pulling from the remote {repo}.")
        return False
    return True

def discover_grader(folder: str = "") -> str:
    grader_file = cliarg.optional.grader or "gatorgrade.yml"
    for file in os.listdir(folder):
        if file == grader_file:
            return os.path.join(os.getcwd(), file)

def run_grader(folder: Path, grader_file) -> bool:
    os.chdir(folder)
    # Execute the grader using uv
    result = subprocess.run(
        ["uv", "run", "--quiet", "gatorgrade"], 
        stdout = subprocess.DEVNULL
    )
    # Execute the agent for writing evaluation

    # Retrieve the Code Review Github issue for eval
    os.chdir(UP)
    if result.returncode > 0:
        return False
    return True

def main():
    for assign in os.listdir(os.getcwd()):
        if cliarg.optional.ignore in assign:
            continue
        grader_file = discover_grader(assign)
        status = "❌"
        path = Path(os.getcwd(), assign)
        if not pull_latest_changes(Path(os.getcwd(), assign)):
           print(f"[ERROR] Error pulling from {assign}")
        if run_grader(path, grader_file):
            status = "✅"
        print(f"{status} {assign}")
        

if __name__ == "__main__":
    main()
