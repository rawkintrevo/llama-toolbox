
import requests
import json

from..base import BaseTool
from ..config import FunctionRegistry
import logging

logger = logging.getLogger(__name__)

@FunctionRegistry.register
class CommitFile(BaseTool):
    def __init__(self,
                 api_key=None,
                 name="commit_file",):
        super().__init__()
        self.api_key = api_key
        self.name = name
        self.API_SERVICE = 'github'

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Commit a file to a GitHub repository",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_url": {
                            "type": "string",
                            "description": "The URL of the repository, e.g. https://github.com/The-AI-Alliance//gofannon"
                        },
                        "file_path": {
                            "type": "string",
                            "description": "The path of the file in the repository, e.g. example.txt"
                        },
                        "file_contents": {
                            "type": "string",
                            "description": "The contents of the file as a string"
                        },
                        "commit_message": {
                            "type": "string",
                            "description": "The commit message, e.g. 'Added example.txt'"
                        }
                    },
                    "required": ["repo_url", "file_path", "file_contents", "commit_message"]
                }
            }
        }

    def fn(self, repo_url,
           file_path,
           file_contents,
           commit_message)-> str:
        logger.debug(f"Committing file {file_path} to {repo_url}")
        # Extracting the owner and repo name from the URL
        repo_parts = repo_url.rstrip('/').split('/')
        owner = repo_parts[-2]
        repo = repo_parts[-1]

        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        headers = {
            'Authorization': f'token {self.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            "message": commit_message,
            "content": file_contents
        }

        response = requests.put(api_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()

        return response.json()