import base64
import json
import ast
from PIL import Image
from fastapi import File

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import YouTubeSearchTool
from langchain.agents import AgentExecutor, create_tool_calling_agent

from api.schema import LessonContent, Resource
from .extractors import GetTextFromPdf, OCRExtractor

ocr_helper = OCRExtractor()
pdf_extractor = GetTextFromPdf(OCRExtractor())


class LLMManager:

    def __init__(self):
        self.vision_model = ChatGoogleGenerativeAI(model="gemini-pro-vision")
        self.text_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
        self.tavily_search = TavilySearchResults()
        self.youtube_search = YouTubeSearchTool()
        self.agent_tools = [self.tavily_search, self.youtube_search]

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

        return self._process_json(result).get("topics")

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

        return self._process_json(result).get("topics")

    def generate_topic_content(self, topic_name: str) -> LessonContent:
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": """
                    You are a teacher and you will be provided a topic name to generate a very comprehensive
                    topic note for the student. You are to generate just the note alone and nothing else.

                    Instructions: 
                    - Write a long and very comprehensive lesson note about the provided topic.
                    - Output formats:
                            - Success: Return a text with the note

                        NOTE: Only return in the expected format and nothing else, no leading or trailing space should be added. 
                    """,
                },
                {
                    "type": "text",
                    "text": topic_name,
                },
            ]
        )
        result = self.text_model.invoke([message])

        note = result.content

        web_resources = self.tavily_search.invoke(f"Resources to learn {topic_name}")
        youtube_resources = self.youtube_search.invoke(f"{topic_name}, 2")

        resources = []

        for resource in web_resources[:3]:
            resources.append(
                Resource(url=resource.get("url"), content=resource.get("content"))
            )

        youtube_resources = youtube_resources.removeprefix("[")
        youtube_resources = youtube_resources.removesuffix("]")
        for resource in youtube_resources.split(","):
            resource = resource.removeprefix("'")
            resource = resource.removesuffix("'")
            resources.append(Resource(url=resource))

        lesson_content = LessonContent(note=note, resources=resources)

        return lesson_content

    def explain_topic(self, selected_text, context):
        pass

    def summarize_topic(self, text, topic):
        prompt = f"""
            summarize and highlight crucial point from this text {text} on the topic {topic}
            
            Output Formats:
                - Success: Return a JSON Object formatted exactly as follows
                {json.dumps({
                    "status":  "success",
                    "data": {
                        "summary":  "generated summary",
                        "highlights":  ["list of generated crucial point and area of concentration"]
                    }
                })}

                - Error: Return a JSON object formatted exactly as follows:
                                
                    {json.dumps({
                        "status": "error",
                        "message": "Reason for failure"
                    })}
                

                NOTE: Only return in the expected format and nothing else, no leading or trailing space should be added. 
        """

        result = self.text_model.invoke(prompt)

        return self._process_json(result)

    def generate_quiz(self, text, topic):
        prompt = f"""
            As a teacher take critically analyze the {text} on the topic {topic}

            Now i want you to generate a list of quizzes together with options (from a - d with one of the options as the correct answer), hint, brief answer explanation, and the answer following this format below
            
            Output Formats:
                - Success: Return a JSON Object formatted exactly as follows
                {json.dumps({
                    "status":  "success",
                    "quizzes": [
                        {
                            "question":  "add the question here",
                            "options": {
                                "a":  "option A here",
                                "b": "option B here",
                                "c": "option C here",
                                "d": "option D here"
                            },
                            "answer": "the correct option here",
                            "hint": "a very short and vague hint",
                            "answer-explanation": "a very brief explanation"
                        }
                    ]
                })}

                - Error: Return a JSON object formatted exactly as follows:
                                
                    {json.dumps({
                        "status": "error",
                        "message": "Reason for failure"
                    })}
                

                NOTE: Only return in the expected format and nothing else, no leading or trailing space should be added. 
        """

        result = self.text_model.invoke(prompt)

        return self._process_json(result)

    def _process_json(self, result: BaseMessage) -> list[str]:
        result_content = result.content.strip()

        if result_content[0] == "`":
            result_content = result_content[7:-3]

        result_content = json.loads(result_content)

        if result_content.get("status") == "error":
            raise Exception(result_content.get("message"))

        return result_content


llm_manager = LLMManager()
