
from..base import BaseTool
import requests
import json
from ..config import FunctionRegistry
import logging

logger = logging.getLogger(__name__)

@FunctionRegistry.register
class ReadIssue(BaseTool):
    def __init__(self, api_key=None, name="read_issue"):
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
                "description": "Read an issue and its comments from a GitHub repository",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_url": {
                            "type": "string",
                            "description": "The URL of the repository, e.g. https://github.com/The-AI-Alliance//gofannon"
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "The number of the issue to read"
                        }
                    },
                    "required": ["repo_url", "issue_number"]
                }
            }
        }

    def fn(self, repo_url, issue_number):
        logger.debug(f"Reading issue number {issue_number} from repo {repo_url}")
        # Extracting the owner and repo name from the URL
        repo_parts = repo_url.rstrip('/').split('/')
        owner = repo_parts[-2]
        repo = repo_parts[-1]

        issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
        comment_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"

        headers = {
            'Authorization': f'token {self.api_key}'
        }

        issue_response = requests.get(issue_url, headers=headers)
        issue_response.raise_for_status()

        comment_response = requests.get(comment_url, headers=headers)
        comment_response.raise_for_status()

        issue_data = issue_response.json()
        comment_data = comment_response.json()

        result = {
            "issue": issue_data,
            "comments": comment_data
        }

        return json.dumps(result, indent=4)  