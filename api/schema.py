from pydantic import BaseModel
from typing import Any, List


class Topic(BaseModel):
    name: str
    subtopics: list[Any]


class NoteSummaryForm(BaseModel):
    topic: str
    note: str


class GenerateQuiz(BaseModel):
    text: str
    topic: str


class Resource(BaseModel):
    url: str
    content: str = None


class LessonContent(BaseModel):
    note: str
    resources: list[Resource]
