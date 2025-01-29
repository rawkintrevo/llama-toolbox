
from..base import BaseTool
import requests
from ..config import FunctionRegistry
import logging

logger = logging.getLogger(__name__)

@FunctionRegistry.register
class Search(BaseTool):
    def __init__(self, name="search"):
        super().__init__()
        self.name = name

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Search for articles on arXiv",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "start": {
                            "type": "integer",
                            "description": "The start index of the search results"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "The maximum number of search results to return"
                        },
                        "submittedDateFrom": {
                            "type": "string",
                            "description": "The start submission date in the format YYYYMMDD"
                        },
                        "submittedDateTo": {
                            "type": "string",
                            "description": "The end submission date in the format YYYYMMDD"
                        },
                        "ti": {
                            "type": "string",
                            "description": "Search in title"
                        },
                        "au": {
                            "type": "string",
                            "description": "Search in author"
                        },
                        "abs": {
                            "type": "string",
                            "description": "Search in abstract"
                        },
                        "co": {
                            "type": "string",
                            "description": "Search in comment"
                        },
                        "jr": {
                            "type": "string",
                            "description": "Search in journal reference"
                        },
                        "cat": {
                            "type": "string",
                            "description": "Search in subject category"
                        }
                    },
                    "required": ["query"]
                }
            }
        }

    def _format_date(self, date):
        if len(date) == 8:
            return f"{date}0000"
        return date

    def fn(self, query, start=0, max_results=10, submittedDateFrom=None, submittedDateTo=None, ti=None, au=None, abs=None, co=None, jr=None, cat=None):
        logger.debug("Querying ArXiv for '%s'", query)
        base_url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": query,
            "start": start,
            "max_results": max_results
        }

        if submittedDateFrom and submittedDateTo:
            params["search_query"] += f" AND submittedDate:[{self._format_date(submittedDateFrom)}0000 TO {self._format_date(submittedDateTo)}0000]"
        elif submittedDateFrom:
            params["search_query"] += f" AND submittedDate:[{self._format_date(submittedDateFrom)}0000 TO *]"
        elif submittedDateTo:
            params["search_query"] += f" AND submittedDate:[* TO {self._format_date(submittedDateTo)}0000]"

        if ti:
            params["search_query"] += f" AND ti:{ti}"

        if au:
            params["search_query"] += f" AND au:{au}"

        if abs:
            params["search_query"] += f" AND abs:{abs}"

        if co:
            params["search_query"] += f" AND co:{co}"

        if jr:
            params["search_query"] += f" AND jr:{jr}"

        if cat:
            params["search_query"] += f" AND cat:{cat}"

        response = requests.get(base_url, params=params)
        return response.text