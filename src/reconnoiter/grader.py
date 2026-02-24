import os
import json
import subprocess

from .env import Python

UP = ".."

class GraderFile:

    @staticmethod
    def discover(
            grader_files: list = [],
            folder: str = ""
    ) -> str:
        # Parameter should _supplement_ the defaults
        defaults = ["gatorgrade.yml", ".gatorgrade.yml"]
        # TODO: Use os.walk to discover sub-graders
        for file in os.listdir(folder):
            if file in defaults + grader_files:
                return os.path.join(folder, file)

    @staticmethod
    def run(student, path, grader_file: str = "gatorgrade.yml") -> bool:
        interpreter = Python(cwd = path)
        os.chdir(path)
        result = subprocess.run(
            interpreter.grader + ["--config", grader_file,
            "--report", "file", "json",
            f"../feedback/grade_reports/{student}_grader.json"],
            stdout = subprocess.DEVNULL
        )
        os.chdir(UP)
        if result.returncode > 0:
            return False
        return True
    
    @staticmethod
    def result(path: str = "") -> int:
        with open(path, "r") as fh:
            data = json.loads(fh.read())
        # This is a default points value; TODO: make it flexible
        return (data["percentage_score"] / 100) * 2