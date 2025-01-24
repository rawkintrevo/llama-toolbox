from requests import get
from json import dumps

from ..base import BaseTool
from ..config import FunctionRegistry
import logging

logger = logging.getLogger(__name__)

@FunctionRegistry.register
class ComplaintsByVehicle(BaseTool):
    def __init__(self,
                 api_key=None,
                 name="complaints_by_vehicle",):
        super().__init__()
        self.api_key = api_key
        self.name = name
        self.API_SERVICE = 'nhtsa'

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Get complaints by vehicle make, model, and year",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "make": {
                            "type": "string",
                            "description": "The make of the vehicle, e.g. Acura"
                        },
                        "model": {
                            "type": "string",
                            "description": "The model of the vehicle, e.g. ILX"
                        },
                        "modelYear": {
                            "type": "string",
                            "description": "The year of the vehicle, e.g. 2022"
                        }
                    },
                    "required": ["make", "model", "modelYear"]
                }
            }
        }

    def fn(self, make,
                 model,
                 modelYear)-> str:
        logger.debug(f"Searching for complaints related to {modelYear} {make} {model}")
        base_url = "https://api.nhtsa.gov/complaints/complaintsByVehicle"
        payload = {
            "make": make,
            "model": model,
            "modelYear": modelYear
        }
        r = get(base_url, params=payload)
        return dumps(r.json())
