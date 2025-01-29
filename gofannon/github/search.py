from..base import BaseTool
import requests
from ..config import FunctionRegistry
import logging

logger = logging.getLogger(__name__)

@FunctionRegistry.register
class SearchRepos(BaseTool):
    def __init__(self,
                 api_key=None,
                 name="search_repos",):
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
                "description": "Search for GitHub repositories",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query, e.g. 'machine learning'"
                        },
                        "page": {
                            "type": "integer",
                            "description": "The page number to retrieve (default: 1)"
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "The number of results per page (default: 10)"
                        }
                    },
                    "required": ["query"]
                }
            }
        }

    def fn(self, query, page=1, per_page=10) -> str:
        logger.debug(f"Searching github.com for '{query}'")
        api_url = f"https://api.github.com/search/repositories"
        headers = {
            'Authorization': f'token {self.api_key}'
        }
        params = {
            "q": query,
            "page": page,
            "per_page": per_page
        }

        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()

        results = response.json()

        formatted_results = []
        for result in results['items']:
            formatted_results.append(f"**{result['name']}** by **{result['owner']['login']}** - {result['description']}")

        return "\n\n".join(formatted_results)  