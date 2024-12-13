# CommitFile

The `CommitFile` API allows you to commit a file to a GitHub repository.

## Parameters

* `repo_url`: The URL of the repository, e.g. https://github.com/rawkintrevo/llama-toolbox
* `branch`: The branch to commit to, e.g. 'main' or 'new-branch'
* `commit_msg`: The commit message, e.g. 'Added new files'
* `files_json`: A JSON string containing a list of files to commit, e.g. '{\"files\": [{\"path\": \"file1.py\", \"code\": \"import os\"}, {\"path\": \"file2.py\", \"code\": \"import sys\"}]}'
* `base_branch`: Optional. The base branch to create the new branch from. Default: 'main'

When building the instance, you must pass the api_key, git_user_email, and git_user_name as parameters. For example:

```python
cf = CommitFiles(api_key=userdata.get('github-token'), git_user_email='trevor.d.grant@gmail.com', git_user_name='bottrevo')
```
