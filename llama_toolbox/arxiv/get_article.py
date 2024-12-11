# llama_toolbox/arxiv/get_article.py
from..base import BaseTool
import requests

class GetArticle(BaseTool):
    def __init__(self, name="get_article"):
        super().__init__()
        self.name = name

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Get a specific article from arXiv",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "The ID of the article"
                        }
                    },
                    "required": ["id"]
                }
            }
        }

    def fn(self, id):
        base_url = "http://export.arxiv.org/api/query"
        params = {
            "id_list": id
        }
        response = requests.get(base_url, params=params)
        return response.text  