import os
import re
import json
from pathlib import Path
from git import Repo

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
        # Pull latest student's work
        assign.remote().pull()
    except:
        print(f"[ERROR] Error interacting with remote: {repo}.")
        return False
    return True

def write_feedback(path, feedback, student) -> None:
    assign = student or str(path).split("-")[-1]
    # TODO: Make this Mustache or Handlebars
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
    # TODO: This driver is a mess

    # Look at this illerate mess of a driver function, ibid.
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
        if cliarg.optional.ignore in assign or assign == "feedback" or assign == "changes":
            continue

        # Read relevant files and start to assess
        path = Path(os.getcwd(), assign)
        if not pull_latest_changes(Path(os.getcwd(), assign)):
           print(f"[ERROR] Error pulling from {assign}")
        # TODO: Need to discover _all_ grader files and early exit if only
        #       running the grader (see activities repos)
        grader_file = GraderFile.discover(folder = assign)
        os.chdir(path)
        if GraderFile.run(student, grader_file):
            status = "✅"
        print(f"{status} {assign}")
        os.chdir(UP)

        # Output grader run to read later
        programming_score = GraderFile.result(
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
            "score": round(float(code_review.eval),2),
            "feedback": code_review_review['eval']
        }
        # Write an assessment of the code review


        # Write final report out
        write_feedback(path, feedback, student)

if __name__ == "__main__":
    main()
