from abc import ABC, abstractmethod
from typing import Any, Optional, Type

from pydantic import BaseModel, Field, model_validator

from crewai_tools.tools.base_tool import BaseTool


class Adapter(BaseModel, ABC):
    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    def query(self, question: str) -> str:
        """Query the knowledge base with a question and return the answer."""

    @abstractmethod
    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Add content to the knowledge base."""


class RagTool(BaseTool):
    config_path: Optional[str] = None
    class _AdapterPlaceholder(Adapter):
        def query(self, question: str) -> str:
            raise NotImplementedError

        def add(self, *args: Any, **kwargs: Any) -> None:
            raise NotImplementedError

    name: str = "Knowledge base"
    description: str = "A knowledge base that can be used to answer questions."
    summarize: bool = False
    adapter: Adapter = Field(default_factory=_AdapterPlaceholder)
    config: dict[str, Any] | None = None
    
    def __init__(self, config_path: Optional[str] = None, **kwargs): #  add config path for App.from_config to reference custom llm, embedding, and vector DB to pass to embedchain
        super().__init__(**kwargs)
        self.config_path = config_path
        print(f"config_path in RagTool.__init__ : {self.config_path}")
    @model_validator(mode="after")
    def _set_default_adapter(self):
        if isinstance(self.adapter, RagTool._AdapterPlaceholder):
            from embedchain import App

            from crewai_tools.adapters.embedchain_adapter import EmbedchainAdapter

            if self.config_path:
                app = App.from_config(config_path=self.config_path)
            else:
                # Handle the case where self.config_path is not provided
                # 1. Load a default configuration file
                default_config_path = "/home/dabe/python3123/research_assistants/embedchain_config.yml"  # Replace with the actual path
                print(default_config_path)
                app = App.from_config(config_path=default_config_path)
                
            self.adapter = EmbedchainAdapter(
                embedchain_app=app, summarize=self.summarize
            )

        return self

    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.adapter.add(*args, **kwargs)

    def _run(
        self,
        query: str,
        **kwargs: Any,
    ) -> Any:
        self._before_run(query, **kwargs)

        return f"Relevant Content:\n{self.adapter.query(query)}"

    def _before_run(self, query, **kwargs):
        pass
