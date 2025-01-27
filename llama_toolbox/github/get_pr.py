import requests
from..base import BaseTool
import json

class GetPR(BaseTool):
    def __init__(self, name='get_pr'):
        super().__init__()
        self.name = name

    @property
    def definition(self):
        return {
            'type': 'function',
            'function': {
                'name': self.name,
                'description': 'Get a PR and its comments from a GitHub repository',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'repo_url': {
                            'type': 'string',
                            'description': 'The URL of the repository, e.g. https://github.com/rawkintrevo/llama-toolbox'
                        },
                        'pr_number': {
                            'type': 'integer',
                            'description': 'The number of the PR to get'
                        }
                    },
                    'required': ['repo_url', 'pr_number']
                }
            }
        }

    def fn(self, repo_url, pr_number):
        # Extracting the owner and repo name from the URL
        repo_parts = repo_url.rstrip('/').split('/')
        owner = repo_parts[-2]
        repo = repo_parts[-1]

        pr_url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}'
        comments_url = f'https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments'

        headers = {
            'Authorization': f'token {self.api_key}'
        }

        pr_response = requests.get(pr_url, headers=headers)
        pr_response.raise_for_status()

        comments_response = requests.get(comments_url, headers=headers)
        comments_response.raise_for_status()

        pr_data = pr_response.json()
        comments_data = comments_response.json()

        result = {
            'pr': pr_data,
            'comments': comments_data
        }

        return json.dumps(result, indent=4)
