from pydantic import BaseModel
from typing import Any, List


class Topic(BaseModel):
    name: str
    subtopics: list[Any]


class NoteSummaryForm(BaseModel):
    topic: str
    note: str
