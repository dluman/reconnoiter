import os
import re
import sys
import json
import subprocess
from pathlib import Path
from git import Repo

from arglite import parser as cliarg
from .agent import Agent
from .review import CodeReview

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

def run_grader(student, path, grader_file: str = "gatorgrade.yml") -> bool:
    # Execute the grader using uv
    result = subprocess.run(
        ["uv", "run", "--quiet", "gatorgrade",
         "--config", grader_file,
         "--report", "file", "json", 
         f"../feedback/grade_reports/{student}_grader.json"],
        stdout = subprocess.DEVNULL
    )
    if result.returncode > 0:
        return False
    return True

def read_grader(path: str = "") -> int:
    with open(path, "r") as fh:
        data = json.loads(fh.read())
    return (data["percentage_score"] / 100) * 2

def write_feedback(path, feedback, student) -> bool:
    assign = student or path
    student = str(assign).split("-")[-1]
    print(student)
    with open(f"feedback/{student}.md", "w") as fh:
        json.dump(feedback, fh)

def main():
    agent = Agent(os.getenv("RECONNOITER"))
    assign_name = cliarg.optional.assignment
    org_name = cliarg.required.org
    os.makedirs(
        "feedback/grade_reports", 
        exist_ok = True
    )
    for assign in os.listdir(os.getcwd()):
        # Clean the student's name
        student = re.sub(
            "[&\\-\\.]", 
            "", 
            assign.split(assign_name)[-1], 
            1
        )
        # Move on to parsing the data
        if not os.path.isdir(assign):
            continue
        if cliarg.optional.ignore in assign or assign == "feedback":
            continue
        grader_file = discover_grader(assign)
        status = "❌"
        path = Path(os.getcwd(), assign)
        if not pull_latest_changes(Path(os.getcwd(), assign)):
           print(f"[ERROR] Error pulling from {assign}")
        os.chdir(path)
        if run_grader(student, grader_file):
            status = "✅"
        print(f"{status} {assign}")
        os.chdir(UP)
        score = read_grader(f"feedback/grade_reports/{student}_grader.json")
        feedback = agent.evaluate(Path(path, "docs/summary.md"))
        feedback["programming"] = score
        code_review = CodeReview(f"{org_name}/{assign}", student).eval
        feedback["code_review"] = code_review
        write_feedback(path, feedback, student)

if __name__ == "__main__":
    main()
