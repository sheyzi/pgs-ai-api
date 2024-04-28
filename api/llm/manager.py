import base64
from PIL import Image
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from fastapi import File
import json

from .schema import LLMContent


class LLMManager:

    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-pro-vision",
        )

    def get_topics_from_syllabus_image(self, image_str: str) -> list[str]:
        """
        Extract topics from a provided image

        :param
            - image_str: str

        uses ocr or pdf text extractor to get text
        construct a prompt with the text

        :return
            - topics:list[str]
        """

        encoded_str = base64.b64encode(image_str).decode("utf-8")
        base64_str = f"data:image/png;base64,{encoded_str}"

        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": """
Instructions:

1. Analyze the syllabus image provided.
2. Extract a structured list of topics and subtopics.
3. Output Formats:
    - Success: Return a JSON Object formatted exactly as follows

    {status: "success",topics: [{name: "topic 1",subtopics: [{name: "topic 1 child",subtopics: [{...}]}]},{name: "topic 2",subtopics: [{name: "topic 2 child",subtopics: [{...}]}]}]}
    

    - Error: Return a JSON object formatted exactly as follows:

    
    {status: "error",message: "Reason for failure"}
    

NOTE: Only return in the expected format and nothing else, no leading or trailing space should be added. 

                """,
                },
                {
                    "type": "image_url",
                    "image_url": base64_str,
                },
            ]
        )

        result = self.model.invoke([message])

        result_content = result.content.strip()

        if result_content[0] == "`":
            result_content = result_content[7:-3]

        print(result_content)

        result_content = json.loads(result_content)

        if result_content.get("status") == "error":
            raise Exception(result_content.message)

        return result_content.get("topics")

    def get_topics_from_syllabus_pdf(self, pdf) -> list[str]:
        pass

    def get_topic_lesson_content(self, topic_name: str) -> LLMContent:
        pass

    def explain_topic(self, selected_text, context):
        pass


llm_manager = LLMManager()
