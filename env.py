import os
import re
import sys

class Python:

    def __init__(self, cwd: str = os.getcwd(), interp: str = ""):
        environment = self.__find_bin(cwd = cwd)
        self.binary = self.__find_python(environment)
        if interp:
            self.binary = interp
            # TODO: allow custom grader
        self.grader = self.__find_grader()
        print(self.grader)

    def __find_bin(self, cwd: str = "") -> os.path:
        """
        Determine if the repository under examination is housed
        in a virtual environment
        
        :param self: Description
        :param cwd: Description
        :type cwd: str
        :return: Description
        :rtype: os.path
        """
        for root, dirs, _ in os.walk(cwd):
            if "bin" in dirs:
                idx = dirs.index("bin")
                path = os.path.join(root, dirs[idx])
                break
        return path

    def __find_python(self, env: os.path = "") -> os.path:
        for binary in os.listdir(env):
            if re.match("python", binary, re.I):
                return os.path.join(env, binary)
    
    def __find_grader(self) -> os.path:
        parent = os.path.dirname(self.binary)
        if os.path.isfile(os.path.join(parent, "gatorgrade")):
            return os.path.join(parent, "gatorgrade")

if __name__ == "__main__":
    p = Python()