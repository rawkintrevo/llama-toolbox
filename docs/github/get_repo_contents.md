## `GetRepoContents`

The `GetRepoContents` API allows you to retrieve the contents of a repository on GitHub. This can be useful for accessing files, directories, and other resources stored in a repository.

Parameters:
`repo_url` (str): The URL of the repository to retrieve contents from.
`path` (str): The path within the repository to retrieve contents from. Defaults to the root directory (`/`).
`eoi` (dict): Extensions of interest, files that do not match one of the keys in this dictionary will be ignored. Defualt:
```python
eoi = {'js' : 'javascript',
                 'jsx' : 'javascript',
                 'ts' : 'typescript',
                 'tsx' : 'typescript',
                 'py' : 'python',
                 'html' : 'html',
                 'css' : 'css',
                 'scss' : 'scss',
                 'sass' : 'sass',
                 'md' : 'markdown',
                 'json' : 'json'}
```