import requests
from ..base import BaseTool
from ..config import FunctionRegistry
import logging

logger = logging.getLogger(__name__)

@FunctionRegistry.register
class GetRepoContents(BaseTool):

    def __init__(self,
                 api_key=None,
                 name="get_repo_contents",):
        super().__init__()
        self.api_key = api_key
        self.name = name
        self.API_SERVICE = 'github'
        self.eoi = {'js' : 'javascript',
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

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Get contents of repo on github",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_url": {
                            "type": "string",
                            "description":
                                "The URL of the Repo this is for reading an entire repo, not individual files., e.g. https://github.com/The-AI-Alliance//gofannon"
                        },
                        "directory_path": {
                            "type": "string",
                            "description": "Path from repository root of the directory of interest. Default '/'"
                        },
                        # "eoi": {
                        #     "type": "dictionary",
                        #     "description": "Extensions of interest. If not set, defaults to self.eoi (which contains common Python, Javascript, HTML, and Markdown extension). Example: `{'.js': 'javascript'}`",
                        # }
                    },
                    "required": ["repo_url"]
                }
            }
        }

    def fn(self, repo_url,
           directory_path = "/",
           eoi = None)-> str:
        logger.debug(f"Getting contents of repo {repo_url}")
        if eoi is None:
            eoi = self.eoi
        # Extracting the owner and repo name from the URL
        repo_parts = repo_url.rstrip('/').split('/')
        owner = repo_parts[-2]
        repo = repo_parts[-1]

        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{directory_path}"
        headers = {
            'Authorization': f'token {self.api_key}'
        }

        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        contents = response.json()

        result = []

        for item in contents:
            if item['type'] == 'file':
                file_response = requests.get(item['download_url'], headers=headers)
                extension = item['name'].split('.')[-1]
                if extension in eoi:
                    language = eoi[extension]
                else:
                    continue
                file_response.raise_for_status()
                file_content = file_response.text
                result.append(f"{item['path']}\n```{language}\n{file_content}\n```")
            elif item['type'] == 'dir':
                # Recursively go through subdirectories
                subdirectory_contents = self.fn(repo_url, item['path'], eoi)
                result.append(subdirectory_contents)

        return "\n\n".join(result)