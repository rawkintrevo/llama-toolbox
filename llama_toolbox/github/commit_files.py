# llama_toolbox/github/commit_files.py
import os

import requests
import json
import git
from..base import BaseTool

class CommitFiles(BaseTool):
    def __init__(self,
                 api_key=None,
                 name="commit_files",
                 git_user_name=None,
                 git_user_email=None):
        super().__init__()
        self.api_key = api_key
        self.name = name
        self.git_user_name = git_user_name
        self.git_user_email = git_user_email


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
                            "description": "The branch to commit to, e.g. 'main' or 'new-branch'. If the branch does not exist, set create_new_branch to True"
                        },
                        "commit_msg": {
                            "type": "string",
                            "description": "The commit message, e.g. 'Added new files'"
                        },
                        "files_json": {
                            "type": "string",
                            "description": "A JSON string containing a list of files to commit, e.g. '{\"files\": [{\"path\": \"file1.py\", \"code\": \"import os\"}, {\"path\": \"file2.py\", \"code\": \"import sys\"}]}'"
                        },
                        "create_new_branch": {
                            "type": "boolean",
                            "description": "Optional. If True, create a new branch with the specified name if it does not exist. Default: False"
                        },
                        "base_branch": {
                            "type": "string",
                            "description": "Optional. The base branch to create the new branch from. Default: 'main'"
                        }
                    },
                    "required": ["repo_url", "branch", "commit_msg", "files_json"]
                }
            }
        }

    def fn(self, repo_url, branch, commit_msg, files_json, create_new_branch=False, base_branch='main'):
        # Extracting the owner and repo name from the URL
        repo_parts = repo_url.rstrip('/').split('/')
        owner = repo_parts[-2]
        repo = repo_parts[-1]

        # Clone the repository
        repo_dir = f"/tmp/{repo}"


        if os.path.exists(repo_dir):
            repo = git.Repo(repo_dir)
        else:
            repo = git.Repo.clone_from(repo_url, repo_dir)
        # repo.config_writer().set_value("user", "name", self.git_user_name).release()
        # repo.config_writer().set_value("user", "email", self.git_user_email).release()

        os.system(f"git config --global user.name \"{self.git_user_name}\"")
        os.system(f"git config --global user.email \"{self.git_user_email}\"")

        # Check if the branch has an upstream set
        if branch in repo.heads:
            if repo.heads[branch].tracking_branch() is None:
                # If not, skip the pull
                pass
            else:
                pass
        else:
            # If it does, pull the latest changes
            repo.index.pull()

            # If create_new_branch is True, create a new branch
        if create_new_branch:
            # Checkout the base branch
            try:
                repo.index.checkout(base_branch)
            except git.exc.GitCommandError:
                # If the base branch does not exist, raise an error
                raise ValueError(f"Base branch '{base_branch}' does not exist.")

                # Create a new branch
            repo.index.checkout('-b', branch)

        else:
            try:
                repo.index.checkout(branch)
            except git.exc.GitCommandError:
                # If the branch does not exist, raise an error
                raise ValueError(f"Branch '{branch}' does not exist. Set create_new_branch to True to create it.")


        # Load the JSON string
        files = json.loads(files_json)['files']
        # Update or create the files
        for file in files:
            file_path = file['path']
            code = file['code']
            with open(f"{repo_dir}/{file_path}", 'w') as f:
                f.write(code)

                # Add the files to the commit
        repo.index.add('.')


        # Commit the files
        repo.index.commit('-m', commit_msg)

        # Push the commit
        if create_new_branch:
            repo.index.push('origin', branch, '--set-upstream')
        else:
            repo.index.push('origin', branch)

        return "Files committed and pushed successfully"