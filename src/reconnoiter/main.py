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

def write_feedback(path, feedback, student) -> None:
    assign = student or str(path).split("-")[-1]
    with open(f"feedback/{assign}.md", "w") as fh:
        fh.write("# Assignment Feedback\n\n")
        fh.write("|Category | Score |\n")
        fh.write("|:--------|:------|\n")
        fh.write(f"|Programming|{feedback['programming']}|\n")
        fh.write(f"|Writing|{feedback['writing']['score']}|\n")
        fh.write(f"|Code Review|{feedback['review']['score']}|\n\n")
        fh.write("## Writing Feedback\n\n")
        fh.write(f"{feedback['writing']['eval']}\n\n")
        fh.write("## Code Review Feedback\n\n")
        fh.write(f"{feedback['review']['feedback']}")

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
        status = "❌"
        student = re.sub(
            "[&\\-\\.]", 
            "", 
            assign.split(assign_name)[-1], 
            1
        )

        # Move on to parsing the data and fence out the bad stuff
        if not os.path.isdir(assign):
            continue
        if cliarg.optional.ignore in assign or assign == "feedback":
            continue
        
        # Read relevant files and start to assess
        path = Path(os.getcwd(), assign)
        if not pull_latest_changes(Path(os.getcwd(), assign)):
           print(f"[ERROR] Error pulling from {assign}")
       
        grader_file = discover_grader(assign)
        os.chdir(path)
        if run_grader(student, grader_file):
            status = "✅"
        print(f"{status} {assign}")
        os.chdir(UP)

        # Output grader run to read later
        programming_score = read_grader(
            f"feedback/grade_reports/{student}_grader.json"
        )
        # Send the summary to the agent to evaluate
        feedback = {}
        feedback["writing"] = agent.evaluate_writing(Path(path, "docs/summary.md"))
        # Rly? Have to int(float())? Makes sense to round it from decimal,
        # else, everyone gets a 0!
        pct_write_score = float(feedback["writing"]["score"])
        feedback["writing"]["score"] = 1 if pct_write_score >= .5 else 0
        # Integrate programming into feedback scores
        feedback["programming"] = round(float(programming_score), 1)
        # Integrate code review into feedback scores
        code_review = CodeReview(f"{org_name}/{assign}", student)
        code_review_review = agent.evaluate_review(code_review.text)
        feedback["review"] = {
            "score": float(code_review.eval),
            "feedback": code_review_review['eval']
        }
        # Write an assessment of the code review


        # Write final report out
        write_feedback(path, feedback, student)

if __name__ == "__main__":
    main()
