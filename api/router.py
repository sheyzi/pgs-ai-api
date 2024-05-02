from fastapi import APIRouter, File, UploadFile
from fastapi_extras.errors import BadRequestError

from api.llm.manager import llm_manager
from .schema import Topic, NoteSummaryForm, LessonContent, GenerateQuiz

router = APIRouter(tags=["LLM"])


@router.post("/get-topic-from-syllabus-image")
def get_topics_from_syllabus_image(image: UploadFile):
    image_str = image.file.read()
    try:
        topics = llm_manager.get_topics_from_syllabus_image(image_str)
        return topics
    except Exception as e:
        print(e)
        raise BadRequestError("Something went wrong")


@router.post("/get-topic-from-syllabus-pdf")
def get_topics_from_syllabus_pdf(file: UploadFile):
    file_str = file.file.read()
    try:
        topics = llm_manager.get_topics_from_syllabus_pdf(file_str)
        return topics
    except Exception as e:
        print(e)
        raise BadRequestError("Something went wrong")


@router.get("/generate-topic-content", response_model=LessonContent)
def generate_topic_content(topic_name: str):
    try:
        result = llm_manager.generate_topic_content(topic_name)
        return result
    except Exception as e:
        print(e)
        raise BadRequestError("Something went wrong")


@router.post("/summarize")
def summarize_notes(form: NoteSummaryForm):
    try:
        topics = llm_manager.summarize_topic(form.note, form.topic)
        return topics
    except Exception as e:
        print(e)
        raise BadRequestError("Something went wrong")


@router.post("/generate-quiz")
def generate_quiz(form: GenerateQuiz):
    try:
        topics = llm_manager.generate_quiz(form.text, form.topic)
        return topics
    except Exception as e:
        print(e)
        raise BadRequestError("Something went wrong")
