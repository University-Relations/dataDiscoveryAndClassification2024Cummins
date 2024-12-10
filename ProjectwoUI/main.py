from modules import OCRProcessor, PIIAnalyzer, PDFReportGenerator, AWSHandler
from tkinter import Tk, filedialog
import os
import sys
import cv2
import requests
import numpy as np

class MainApp:
    """Main application orchestrating the workflow."""
    def __init__(self):
        self.ocr_processor = OCRProcessor()
        self.pii_analyzer = PIIAnalyzer()
        self.report_generator = PDFReportGenerator()

    def select_directory(self):
        root = Tk()
        root.withdraw()
        directory = filedialog.askdirectory(title="Select Directory to Scan")
        root.destroy()
        return directory

    def process_local_files(self, directory):
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        image_files = [os.path.join(root, file)
                       for root, _, files in os.walk(directory)
                       for file in files if os.path.splitext(file)[1].lower() in image_extensions]

        report_data = []
        for image_path in image_files:
            detected_text = self.ocr_processor.detect_text(image_path)
            entities = self.pii_analyzer.classify_text(detected_text)
            report_data.append({"image_name": os.path.basename(image_path), "detected_text": detected_text, "entities": entities})
        self.report_generator.generate_report(report_data)

    def process_s3_files(self, aws_access_key, aws_secret_access_key, region_name):
        aws_handler = AWSHandler(aws_access_key, aws_secret_access_key, region_name)
        buckets = aws_handler.list_all_buckets()
        print(buckets)
        report_data = []
        for bucket in buckets:
            print(bucket)
            urls = aws_handler.list_objects_in_bucket(bucket)
            for url in urls:
                response = requests.get(url)
                if response.status_code == 200:
                    print(url)
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
        self.report_generator.generate_report(report_data)

    def displayMenu(self) : 
        print("1. Process Local Files")
        print("2. Process S3 Files")
        print("0. Exit Program")

        choice = input("Enter choice: ")
        return choice


    def run(self):
        
        choice = 4 # something  random for the loop 
        print("***Data Discovery and Classification in Images using EasyOCR and Microsoft Presidio***")
        while(choice != 0 ):
            choice = self.displayMenu()
        
            if choice == "1":
                print("press Alt+Tab to check for a dialog box ")
                directory = self.select_directory()
                self.process_local_files(directory)
            elif choice == "2":
                aws_access_key = input("Enter AWS Access Key: ")
                aws_secret_access_key = input("Enter AWS Secret Access Key: ")
                region_name = input("Enter AWS Region: ")
                self.process_s3_files(aws_access_key, aws_secret_access_key, region_name)

            elif choice == "0" :
                print("Exiting the program...")
                sys.exit(0) 

            else:
                print("Invalid choice.")

            choice = 4 # to continue the loop


if __name__ == "__main__":
    app = MainApp()
    app.run()
