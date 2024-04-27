from fastapi import APIRouter, File, UploadFile

router = APIRouter(tags=["LLM"])


@router.post("/get-topic-from-syllabus-image")
def get_topics_from_syllabus_image(image: UploadFile):
    print(image.file.read())
    # To continue
