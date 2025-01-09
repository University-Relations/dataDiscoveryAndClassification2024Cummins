import easyocr
import cv2
import logging

class OCRProcessor:
    """Handles OCR detection using EasyOCR."""
    def __init__(self):
        logging.getLogger("easyocr").setLevel(logging.ERROR)
        self.reader = easyocr.Reader(['en', 'es'])

    def preprocess_image(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        morphed = cv2.dilate(binary, kernel, iterations=1)
        return morphed

    def detect_text(self, image_path):
        image = cv2.imread(image_path)
        morphed = self.preprocess_image(image)
        contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detected_text_parts = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 50 and h > 20:
                roi = image[y:y+h, x:x+w]
                text_data = self.reader.readtext(roi)
                detected_text_parts.extend([text for _, text, score in text_data if score > 0.25])
        return " ".join(detected_text_parts)
    

    def detect_text_s3(self, image):
        #image = cv2.imread(image_path)
        morphed = self.preprocess_image(image)
        contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detected_text_parts = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 50 and h > 20:
                roi = image[y:y+h, x:x+w]
                text_data = self.reader.readtext(roi)
                detected_text_parts.extend([text for _, text, score in text_data if score > 0.25])
        return " ".join(detected_text_parts)
