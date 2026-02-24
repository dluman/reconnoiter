import os
import sys

class Python:

    def __init__(self, cwd: str = os.getcwd(), python: str = ""):
        environment = self.__find_venv(cwd = cwd)
        if self.__is_uv():
            self.binary = ["uv", "run", "--directory", str(cwd), "python"]
            self.grader = ["uv", "run", "--directory", str(cwd), "gatorgrade"]
        else:
            self.binary = [f"{environment}/bin/python"]
            self.grader = [f"{environment}/bin/gatorgrade"]
        if python:
            self.binary = [python]
    
    def __is_uv(self) -> bool:
        """
        Docstring for __is_uv

        :param self: Description
        :return: Description
        :rtype: bool
        """
        if os.path.isfile(os.path.join(os.getcwd(), "uv.lock")):
            return True
        return False

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
        for root, dirs, _ in os.walk(cwd):
            if "bin" in dirs:
                return root
        return ""