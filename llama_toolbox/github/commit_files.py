# llama_toolbox/github/commit_files.py

import requests
import json
import git
from..base import BaseTool

class CommitFiles(BaseTool):
    def __init__(self,
                 api_key=None,
                 name="commit_files",):
        super().__init__()
        self.api_key = api_key
        self.name = name

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Commit multiple files to a GitHub repository",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_url": {
                            "type": "string",
                            "description": "The URL of the repository, e.g. https://github.com/rawkintrevo/llama-toolbox"
                        },
                        "branch": {
                            "type": "string",
                            "description": "The branch to commit to, e.g. 'main'"
                        },
                        "commit_msg": {
                            "type": "string",
                            "description": "The commit message, e.g. 'Added new files'"
                        },
                        "files_json": {
                            "type": "string",
                            "description": "A JSON string containing a list of files to commit, e.g. '{\"files\": [{\"path\": \"file1.py\", \"code\": \"import os\"}, {\"path\": \"file2.py\", \"code\": \"import sys\"}]}'"
                        }
                    },
                    "required": ["repo_url", "branch", "commit_msg", "files_json"]
                }
            }
        }

    def fn(self, repo_url, branch, commit_msg, files_json):
        # Extracting the owner and repo name from the URL
        repo_parts = repo_url.rstrip('/').split('/')
        owner = repo_parts[-2]
        repo = repo_parts[-1]

        # Clone the repository
        repo_dir = f"/tmp/{repo}"
        try:
            repo = git.Repo.clone_from(repo_url, repo_dir)
        except git.exc.GitCommandError:
            # If the repository already exists, pull the latest changes
            repo = git.Repo(repo_dir)
            repo.git.pull()

            # Check out the specified branch
        repo.git.checkout(branch)

        # Load the JSON string
        files = json.loads(files_json)['files']

        # Update or create the files
        for file in files:
            file_path = file['path']
            code = file['code']
            with open(f"{repo_dir}/{file_path}", 'w') as f:
                f.write(code)

                # Add the files to the commit
        repo.git.add('.')

        # Commit the files
        repo.git.commit('-m', commit_msg)

        # Push the commit
        repo.git.push('origin', branch)

        return "Files committed and pushed successfully"  