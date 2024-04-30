from fastapi import APIRouter, File, UploadFile
from fastapi_extras.errors import BadRequestError

from api.llm.manager import llm_manager
from .schema import Topic, NoteSummaryForm

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
def get_topics_from_syllabus_image(file: UploadFile):
    file_str = file.file.read()
    try:
        topics = llm_manager.get_topics_from_syllabus_pdf(file_str)
        return topics
    except Exception as e:
        print(e)
        raise BadRequestError("Something went wrong")


@router.post("/gen-notes")
def generate_notes():
    pass


@router.post("/summarize")
def summarize_notes(form: NoteSummaryForm):
    try:
        topics = llm_manager.summarize_topic(form.note, form.topic)
        return topics
    except Exception as e:
        print(e)
        raise BadRequestError("Something went wrong")
