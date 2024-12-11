import os
import requests
import cv2
import numpy as np
from modules import OCRProcessor, PIIAnalyzer, PDFReportGenerator, AWSHandler

class MainApp:
    def __init__(self):
        """
        Initialize the main application with necessary components.
        """
        self.ocr_processor = OCRProcessor()
        self.pii_analyzer = PIIAnalyzer()
        self.pdf_reporter = PDFReportGenerator()
        #self.aws_handler = AWSHandler()

    def process_local_directory(self, directory_path):
        """
        Process images in a local directory.
        """
        if not os.path.isdir(directory_path):
            raise FileNotFoundError(f"The directory {directory_path} does not exist.")

        image_files = [
            os.path.join(directory_path, f) for f in os.listdir(directory_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
        ]

        if not image_files:
            raise ValueError("No image files found in the selected directory.")

        processed_data = []
        for file_path in image_files:
            # Perform OCR and entity analysis
            detected_text = self.ocr_processor.detect_text(file_path)
            entities = self.pii_analyzer.classify_text(detected_text)
            processed_data.append({
                "image_name": os.path.basename(file_path),
                "detected_text": detected_text,
                "entities": entities
            })

        return processed_data

    def process_s3_bucket(self, aws_access_key, aws_secret_access_key, region_name):
        """
        Process images in S3 buckets.

        """
        #self.aws_handler = AWSHandler()
        aws_handler = AWSHandler(aws_access_key, aws_secret_access_key, region_name)
        """s3_client = aws_handler.initialize_s3_client(
            aws_access_key, aws_secret_access_key, region_name
        )
"""
        all_buckets = aws_handler.list_all_buckets()

        report_data = []
        for bucket in all_buckets:
            urls = aws_handler.list_objects_in_bucket(bucket)
            for url in urls:
                response = requests.get(url)
                if response.status_code == 200:
                    image_array = np.frombuffer(response.content, np.uint8)
                    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                    if img is not None : 
                        detected_text = self.ocr_processor.detect_text_s3(img)
                        entities = self.pii_analyzer.classify_text(detected_text)
                        report_data.append({"image_name": url.split('/')[-1], "detected_text": detected_text, "entities": entities})
                    else : 
                        print("failed to decode the image")
                else : 
                    print("Failed to fetch the image. HTTP Status Code : {response.status_code}")

                """# Fetch image and process
                image = aws_handler.fetch_image_from_url(url)
                detected_text = self.ocr_processor.easyocr_ocr_s3(image)
                entities = self.pii_analyzer.analyze(detected_text, language="en")
                processed_data.append({
                    "image_name": url.split('/')[-1],
                    "detected_text": detected_text,
                    "entities": entities
                })"""

        return report_data

    def generate_pdf_report(self, processed_data):
        """
        Generate a PDF report based on processed data.
        """
        print("helllo main2.py")
        return self.pdf_reporter.generate_report(processed_data)

def main():
    """
    Main entry point to initialize the Streamlit UI.
    """
    from app_ui import StreamlitUI  # Import the Streamlit UI class

    ui = StreamlitUI()
    ui.run()

main()
