from pydantic import BaseModel


class LLMContent(BaseModel):
    note: str
    resources: list[str]
