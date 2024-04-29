from abc import ABC, abstractmethod

import numpy as np

import cv2

import pytesseract

import fitz


class ExtractionStrategy(ABC):

    @abstractmethod
    def get_text(self, blob: bytes) -> str:
        """extract text from raw image"""


class OCRExtractor(ExtractionStrategy):

    # get grayscale image
    def get_grayscale(self, image):

        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # noise removal

    def remove_noise(self, image):

        return cv2.medianBlur(image, 5)

    # thresholding

    def thresholding(self, image):

        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # dilation

    def dilate(self, image):

        kernel = np.ones((5, 5), np.uint8)

        return cv2.dilate(image, kernel, iterations=1)

    # erosion

    def erode(self, image):

        kernel = np.ones((5, 5), np.uint8)

        return cv2.erode(image, kernel, iterations=1)

    # opening - erosion followed by dilation

    def opening(self, image):

        kernel = np.ones((5, 5), np.uint8)

        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    # canny edge detection

    def canny(self, image):

        return cv2.Canny(image, 100, 200)

    # skew correction

    def deskew(self, image):

        coords = np.column_stack(np.where(image > 0))

        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:

            angle = -(90 + angle)

        else:

            angle = -angle

        (h, w) = image.shape[:2]

        center = (w // 2, h // 2)

        M = cv2.getRotationMatrix2D(center, angle, 1.0)

        rotated = cv2.warpAffine(
            image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )

        return rotated

    # template matching

    def match_template(self, image, template):

        return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

    def get_text(self, img_str: str) -> str:
        """use tesseract to extract image text"""

        extracted_text = ""

        try:

            nparr = np.frombuffer(img_str, np.uint8)

            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # img_np  =cv2.imread('/home/routebirds/Documents/work_folder/pgs-ai-api/api/llm/img.jpg')

            gray = self.get_grayscale(img_np)

            custom_config = r"--oem 3 --psm 6"

            extracted_text += pytesseract.image_to_string(
                self.thresholding(gray), config=custom_config
            )

        finally:

            return extracted_text


class GetTextFromPdf(ExtractionStrategy):

    def __init__(self, ocr_handler: ExtractionStrategy) -> None:
        self.ocr_handler = ocr_handler

    def _is_image_pdf(self, page, *args, **kwargs):
        return len(page.get_text().strip()) == 0

    def get_text(self, f_input: bytes):
        text = ""
        try:
            doc = fitz.open("pdf", f_input)

            for page in doc:
                if self._is_image_pdf(page):
                    pix = page.get_pixmap()
                    image_data = pix.tobytes()
                    text += self.ocr_handler.get_text(image_data)
                else:
                    text += page.get_text()
        finally:
            return text
