from typing import Any, Optional, Type

from embedchain.models.data_type import DataType
from pydantic import BaseModel, Field

from ..rag.rag_tool import RagTool


class FixedJSONSearchToolSchema(BaseModel):
    """Input for JSONSearchTool."""

    search_query: str = Field(
        ...,
        description="Mandatory search query you want to use to search the JSON's content",
    )


class JSONSearchToolSchema(FixedJSONSearchToolSchema):
    """Input for JSONSearchTool."""

    json_path: str = Field(..., description="Mandatory json path you want to search")
    config_path: str = Field(..., description="embedchain configuration path to pass to Ragtool to pass to embedchain")


class JSONSearchTool(RagTool):
    name: str = "JSONSearchTool"
    description: str = (
        "A tool that can be used upload json data embeddings to a chroma database and to semantic search a query from a JSON's content."
    )
    args_schema: Type[BaseModel] = JSONSearchToolSchema

    def __init__(self, json_path: Optional[str] = None, config_path: Optional[str] = None, **kwargs):
        super().__init__(config_path = config_path, **kwargs)
        if json_path is not None:
            kwargs["data_type"] = DataType.JSON
            self.add(json_path)
            self.description = f"A tool that can be used to semantic search a query the {json_path} JSON's content."
            self.args_schema = FixedJSONSearchToolSchema
            self._generate_description()

    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().add(*args, **kwargs)

    def _before_run(
        self,
        query: str,
        **kwargs: Any,
    ) -> Any:
        if "json_path" in kwargs:
            self.add(kwargs["json_path"])

    def _run(
        self,
        search_query: str,
        **kwargs: Any,
    ) -> Any:
        return super()._run(query=search_query, **kwargs)
