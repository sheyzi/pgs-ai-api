import base64
from PIL import Image
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from fastapi import File

from .schema import LLMContent


class LLMManager:

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro")

    def get_topics_from_syllabus_image(self, image: File) -> list[str]:
        """
        Extract topics from a provided image

        :param
            - image: Pillow Image

        :return
            - topics:list[str]
        """

    def get_topics_from_syllabus_pdf(self, pdf) -> list[str]:
        pass

    def get_topic_lesson_content(self, topic_name: str) -> LLMContent:
        pass

    def explain_topic(self, selected_text, context):
        pass
