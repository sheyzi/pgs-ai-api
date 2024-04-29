import base64
from PIL import Image
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from fastapi import File
import json
import ast

from .schema import LLMContent
from .extractors import GetTextFromPdf, OCRExtractor

ocr_helper = OCRExtractor()
pdf_extractor = GetTextFromPdf(OCRExtractor())


class LLMManager:

    def __init__(self):
        self.vision_model = ChatGoogleGenerativeAI(model="gemini-pro-vision")
        self.text_model = ChatGoogleGenerativeAI(model="gemini-pro")

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

                                1. Analyze the syllabus in provided.
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

        result = self.vision_model.invoke([message])

        return self._process_json(result)

    def get_topics_from_syllabus_pdf(self, pdf) -> list[str]:
        text = pdf_extractor.get_text(pdf)

        prompt = (
            """
                Instructions:
                        1. Analyze the syllabus in"""
            + f"'{text}'"
            + """
                provided.
                        2. Extract a structured list of topics and subtopics.
                        3. Output Formats:
                            - Success: Return a standard JSON Object formatted as follows

                            {"status": "success",topics: [{"name": "topic 1","subtopics": [{"name": "topic 1 child",subtopics: [{...}]}]},{"name": "topic 2",subtopics: [{"name": "topic 2 child","subtopics": [{...}]}]}]}
                            

                            - Error: Return a JSON object formatted exactly as follows:

                            
                            {"status": "error",message: "Reason for failure"}
                            

                        NOTE: Only return in the expected format and nothing else, no leading or trailing space should be added. 
            """
        )

        result = self.text_model.invoke(prompt)

        return self._process_json(result)

    def get_topic_lesson_content(self, topic_name: str) -> LLMContent:
        pass

    def explain_topic(self, selected_text, context):
        pass

    def _process_json(self, result: BaseMessage) -> list[str]:
        result_content = result.content.strip()

        if result_content[0] == "`":
            result_content = result_content[7:-3]

        result_content = json.loads(result_content)

        if result_content.get("status") == "error":
            raise Exception(result_content.message)

        return result_content.get("topics")


llm_manager = LLMManager()
