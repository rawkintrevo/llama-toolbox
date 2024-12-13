import requests
from..base import BaseTool
import json

class ReviewPR(BaseTool):
    def __init__(self, name='pr_review'):
        super().__init__()
        self.name = name

    @property
    def definition(self):
        return {
            'type': 'function',
            'function': {
                'name': self.name,
                'description': 'Review a PR in a GitHub repository',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'repo_url': {
                            'type': 'string',
                            'description': 'The URL of the repository, e.g. https://github.com/rawkintrevo/llama-toolbox'
                        },
                        'pr_number': {
                            'type': 'integer',
                            'description': 'The number of the PR to review'
                        },
                        'review_body': {
                            'type': 'string',
                            'description': 'The body of the review'
                        }
                    },
                    'required': ['repo_url', 'pr_number', 'review_body']
                }
            }
        }

    def fn(self, repo_url, pr_number, review_body):
        # Extracting the owner and repo name from the URL
        repo_parts = repo_url.rstrip('/').split('/')
        owner = repo_parts[-2]
        repo = repo_parts[-1]

        review_url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews'

        headers = {
            'Authorization': f'token {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'body': review_body,
            'event': 'COMMENT'
        }

        response = requests.post(review_url, headers=headers, json=payload)
        response.raise_for_status()

        return json.dumps(response.json(), indent=4)
