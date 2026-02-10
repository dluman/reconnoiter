import os
import sys

class Python:

    def __init__(self, cwd: str = os.getcwd(), python: str = ""):
        environment = self.__find_venv(cwd = cwd)
        self.binary = f"{environment}/bin/python"
        self.grader = f"{environment}/bin/gatorgrade"
        if python:
            self.binary = python
            # TODO: allow custom grader

    def __find_venv(self, cwd: str = "") -> str:
        """
        Determine if the repository under examination is housed
        in a virtual environment
        
        :param self: Description
        :param cwd: Description
        :type cwd: str
        :return: Description
        :rtype: bool
        """
        for root, dirs, files in os.walk(cwd):
            print(root, dirs, files)
        return ""