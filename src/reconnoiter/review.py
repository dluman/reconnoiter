import os
import requests

from github import Auth
from github import Github
from github import UnknownObjectException

class IssueEvaluation:

    def __init__(self, text: str = ""):
        if text:
            fulfilled = text.count("- [x]")
            unfulfilled = text.count("- [ ]")
            self.eval = fulfilled / (unfulfilled + fulfilled) * 2

class CodeReview:
    
    def __init__(self, repo: str = None, user: str = None):
        if repo and user:
            auth = Auth.Token(os.getenv('GITHUB'))
            self.g = Github(auth = auth)
            self.repo = self.g.get_repo(repo)
            self.__get_issue(user)
    
    def __get_issue(self, user: str = ""):
        try:
            issues = self.repo.get_issues()
        except UnknownObjectException:
            print("[ERROR] No code review for {user}")
        for issue in issues:
            if issue.title == "Code Review":
                self.eval = IssueEvaluation(issue._body.value).eval
                