import json
from anthropic import Anthropic

from pathlib import Path

class Agent:

    def __init__(self, key: str = None):
        self.client = Anthropic(api_key = key)
        self.prompt = self.__prompt()

    def __prompt(self) -> str:
        try:
            with open(".rubric", "r") as fh:
                return fh.read()
        except FileNotFoundError:
            print("[ERROR] Cannot file rubric file; won't process writing.")

    def __message(self, report_file: str = ""):
        response = self.client.messages.create(
            model = "claude-sonnet-4-5-20250929",
            max_tokens = 1024,
            system = self.__prompt(),
            messages = [
                {"role": "user",
                 "content": report_file
                }
            ],
            output_config = {
                "format" : {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "writing": {"type": "string"},
                            "eval": {"type" : "string"}
                        },
                        "required": ["score", "eval"],
                        "additionalProperties": False
                    }
                }
            }
        )
        return json.loads(response.content[-1].text)
    
    def __writing(self, report_file: str = None) -> str:
        if not report_file:
            return
        with open(report_file, "r") as fh:
            return fh.read()
    
    def evaluate(self, report_file: str = None) -> dict:
        writing = self.__writing(report_file)
        response = self.__message(writing)
        return response
