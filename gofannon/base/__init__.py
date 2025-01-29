import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any
import json
import logging
from pathlib import Path
from ..config import ToolConfig

from typing import Any, Dict


try:
    from smolagents.tools import Tool as SmolTool
    from smolagents.tools import tool as smol_tool_decorator
    _HAS_SMOLAGENTS = True
except ImportError:
    _HAS_SMOLAGENTS = False

try:
    from langchain.tools import BaseTool as LangchainBaseTool
    from langchain.pydantic_v1 import BaseModel, Field
    from typing import Type, Optional
    _HAS_LANGCHAIN = True
except ImportError:
    _HAS_LANGCHAIN = False

@dataclass
class ToolResult:
    success: bool
    output: Any
    error: str = None
    retryable: bool = False

class WorkflowContext:
    def __init__(self, firebase_config=None):
        self.data = {}
        self.execution_log = []
        self.firebase_config = firebase_config
        self.local_storage = Path.home() / ".llama" / "checkpoints"
        self.local_storage.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self, name="checkpoint"):
        if self.firebase_config:
            self._save_to_firebase(name)
        else:
            self._save_local(name)

    def _save_local(self, name):
        path = self.local_storage / f"{name}.json"
        with open(path, 'w') as f:
            json.dump({
                'data': self.data,
                'execution_log': self.execution_log
            }, f)

    def _save_to_firebase(self, name):
        from firebase_admin import firestore
        db = firestore.client()
        doc_ref = db.collection('checkpoints').document(name)
        doc_ref.set({
            'data': self.data,
            'execution_log': self.execution_log,
            'timestamp': firestore.SERVER_TIMESTAMP
        })

    def log_execution(self, tool_name, duration, input_data, output_data):
        entry = {
            'tool': tool_name,
            'duration': duration,
            'input': input_data,
            'output': output_data
        }
        self.execution_log.append(entry)

class BaseTool(ABC):
    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self._load_config()
        self._configure(**kwargs)
        self.logger.debug("Initialized %s tool", self.__class__.__name__)

    def _configure(self, **kwargs):
        """Set instance-specific configurations"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def _load_config(self):
        """Auto-load config based on tool type"""
        if hasattr(self, 'API_SERVICE'):
            self.api_key = ToolConfig.get(f"{self.API_SERVICE}_api_key")

    @property
    @abstractmethod
    def definition(self):
        pass

    @property
    def output_schema(self):
        return self.definition.get('function', {}).get('parameters', {})

    @abstractmethod
    def fn(self, *args, **kwargs):
        pass

    def execute(self, context: WorkflowContext, **kwargs) -> ToolResult:
        try:
            start_time = time.time()
            result = self.fn(**kwargs)
            duration = time.time() - start_time

            context.log_execution(
                tool_name=self.__class__.__name__,
                duration=duration,
                input_data=kwargs,
                output_data=result
            )

            return ToolResult(success=True, output=result)
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                retryable=True
            )

    def import_from_smolagents(self, smol_tool: "SmolTool"):
        """
        Takes a smolagents Tool instance and adapts it into this BaseTool.
        You might copy relevant attributes like name, description, inputs, etc.
        And adjust self.fn to call the smolagents Tool forward method.
        """
        if not _HAS_SMOLAGENTS:
            raise RuntimeError(
                "smolagents is not installed or could not be imported. "
                "Install it or check your environment."
            )

            # Example adaptation – adjust to suit your actual logic:
        self.name = smol_tool.name
        self.description = smol_tool.description

        # Optionally, if your 'definition' is dynamic, store some fields:
        # e.g.:
        # self.my_inputs = smol_tool.inputs
        # self.my_output_type = smol_tool.output_type

        def adapted_fn(*args, **kwargs):
            # This calls the smol_tool with the same signature
            return smol_tool.forward(*args, **kwargs)

            # Overwrite this tool's .fn with a new function that calls the smol_tool
        self.fn = adapted_fn

    def export_to_smolagents(self) -> "SmolTool":
        """
        Export this BaseTool as a smolagents Tool instance.
        This sets up a smolagents-style forward method that calls self.fn.
        """
        if not _HAS_SMOLAGENTS:
            raise RuntimeError(
                "smolagents is not installed or could not be imported. "
                "Install it or check your environment."
            )

            # Provide a standard forward function that calls self.fn
        def smol_forward(*args, **kwargs):
            return self.fn(*args, **kwargs)

            # Optionally define inputs / output_type if desired. E.g.:
        inputs_definition = {
            "example_arg": {
                "type": "string",
                "description": "Example argument recognized by this tool"
            }
        }
        output_type = "string"

        # Construct a new smolagents Tool with the minimal fields
        exported_tool = SmolTool()
        exported_tool.name = getattr(self, "name", "exported_base_tool")
        exported_tool.description = getattr(self, "description", "Exported from BaseTool")
        exported_tool.inputs = inputs_definition
        exported_tool.output_type = output_type
        exported_tool.forward = smol_forward
        exported_tool.is_initialized = True

        return exported_tool

    def import_from_langchain(self, langchain_tool: "LangchainBaseTool"):
        """
        Adapt a LangChain tool to work with this BaseTool implementation.

        Args:
            langchain_tool: Instance of a Langchain BaseTool to adapt
        """
        if not _HAS_LANGCHAIN:
            raise RuntimeError(
                "langchain is not installed. Install with `pip install langchain-core`"
            )

            # Copy core metadata
        self.name = langchain_tool.name
        self.description = langchain_tool.description

        # Create definition from LangChain args schema
        args_schema = langchain_tool.args_schema.schema() if langchain_tool.args_schema else {}

        self.definition = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": args_schema.get("properties", {}),
                "required": args_schema.get("required", [])
            }
        }

        # Wrap the LangChain execution method
        def adapted_fn(*args, **kwargs):
            return langchain_tool._run(*args, **kwargs)

        self.fn = adapted_fn

    def export_to_langchain(self) -> "LangchainBaseTool":
        """
        Export this tool as a LangChain compatible BaseTool instance.

        Returns:
            LangchainBaseTool: Instance of a Langchain tool
        """
        if not _HAS_LANGCHAIN:
            raise RuntimeError(
                "langchain is not installed. Install with `pip install langchain-core`"
            )

            # Create args schema from definition
        class ArgsSchema(BaseModel):
            __annotations__ = {
                k: (type(v.get("type", str)), Field(..., description=v.get("description", "")))
                for k, v in self.definition.get("function", {}).get("parameters", {}).items()
            }

            # Create tool subclass with our functionality
        class ExportedTool(LangchainBaseTool):
            name = self.definition.get("function", {}).get("name", "")
            description = self.definition.get("function", {}).get("description", "")
            args_schema: Type[BaseModel] = ArgsSchema

            def _run(self, *args, **kwargs):
                return self.fn(*args, **kwargs)

                # Instantiate and return the tool
        tool = ExportedTool()
        tool.fn = self.fn  # Direct reference to our implementation
        return tool  