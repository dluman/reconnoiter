import os
import re
import json

from git import Repo
from pathlib import Path
from difflib import SequenceMatcher
from arglite import parser as cliarg

from .agent import Agent
from .grader import GraderFile
from .review import CodeReview

UP = ".."

def pull_latest_changes(repo: str = "") -> bool:
    assign = Repo.init(Path(repo))
    try:
        # Discard local changes in favor of student's work
        assign.git.reset('--hard')
        # Pull latest work from student's repository
        assign.remote().pull()
    except:
        print(f"[ERROR] Error interacting with remote: {repo}.")
        return False
    return True

def get_assignment_root_name(cwd: str = "") -> str:
    substrings = {}
    files = [
        file for file in os.listdir(cwd)
        if os.path.isdir(file) and file != "feedback"
    ]
    base_file = files[0]
    for i in range(1, len(files)):
        current_file = files[i]
        match = SequenceMatcher(
            None, base_file, current_file
        ).find_longest_match(
            alo = 0, ahi = len(base_file), blo = 0, bhi = len(current_file)
        )
        base_file = files[i]
        substring = current_file[match.a:match.a + match.size]
        if substring not in substrings:
            substrings[substring] = 1
        else:
            substrings[substring] += 1
    return max(substrings)

def main():
    # Grab the org CLI flag for issues
    org_name = cliarg.required.org
    # Make the directory for gatorgrader reports
    os.makedirs(
        "feedback/grade_reports",
        exist_ok = True
    )
    # Get the assignment name from cloned repos
    assign_name = get_assignment_root_name(
        os.getcwd()
    )
    # Initialize agent and run grading workflow
    agent = Agent(os.getenv("RECONNOITER"))
    for assign in os.listdir(os.getcwd()):
        student = assign.split(assign_name, 1)[-1]
        if not os.path.isdir(assign) or student == "feedback":
            continue
        path = Path(os.getcwd(), assign)
        pull_latest_changes(path)

        # Generate programming score
        os.chdir(path)
        GraderFile.run(student = student, path = path)
        os.chdir(UP)

        # Fetch Code Review issue
        review = CodeReview(repo = f"{org_name}/{assign}", user = student)



if __name__ == "__main__":
    main()
