from pydantic import BaseModel, ConfigDict


class AssistantFile(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = ""
    filename: str = ""
    description: str = ""
    status: str = ""
    content_type: str = ""


__all__ = ["AssistantFile"]
