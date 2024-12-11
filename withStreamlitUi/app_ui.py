import streamlit as st
import os
import sys
import tempfile
import boto3
import requests
import numpy as np
import cv2
from tkinter import Tk, filedialog

# Import the necessary classes from the original application
#from main import MainApp, LocalStorage, S3Storage, OCRProcessor, AnalyzerEngine, PDFReporter
from modules import * 
from main import MainApp


class StreamlitUI:
    def __init__(self):
        """
        Initialize the Streamlit UI for the text detection application.
        """
        # Initialize dependencies
        self.analyzer = PIIAnalyzer()
        self.local_storage = MainApp()
        #self.s3_storage = AWSHandler()
        self.pdf_generator = PDFReportGenerator(filename="PII_Report.pdf")
        self.ocr = OCRProcessor()

    def run(self):
        """
        Run the Streamlit application interface.
        """
        st.title("EasyOCR Text Detection with Presidio Classification")
        
        # Sidebar for navigation
        menu = st.sidebar.radio("Select Data Source", 
                                ["Local Storage", "S3 Buckets"])
        
        if menu == "Local Storage":
            self.local_storage_ui()
        else:
            self.s3_storage_ui()

    def local_storage_ui(self):
        """
        UI for local storage file processing from a directory.
        """
        st.header("Local Storage Image Processing")
        
        
        # Process button for Directory
        if st.button("Select Directory to Scan"):
            root = Tk()
            root.withdraw()
            directory = filedialog.askdirectory(title="Select Directory to Scan")
            root.destroy()

            if not directory:
                st.error("Please enter a directory path.")
                return
            
            # Validate directory exists
            if not os.path.isdir(directory):
                st.error(f"The directory {directory} does not exist.")
                return
            
            # Find image files in the directory
            image_files = [
                os.path.join(directory, f) for f in os.listdir(directory) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
            ]
            
            if not image_files:
                st.error("No image files found in the selected directory.")
                return
            
            # Create a temporary directory to save processed files if needed
            with tempfile.TemporaryDirectory() as temp_dir:
                processed_data = []
                
                # Progress bar
                progress_bar = st.progress(0)
                
                # Process each image file
                for i, file_path in enumerate(image_files):
                    # Update progress bar
                    progress_bar.progress((i + 1) / len(image_files))
                    
                    # Get image filename
                    image_name = os.path.basename(file_path)
                    
                    # Perform OCR and entity detection
                    st.subheader(f"Processing: {image_name}")
                    
                    try:
                        # OCR Detection
                        detected_text = self.ocr.detect_text(file_path)
                        st.text("Detected Text:")
                        st.text(detected_text)
                        
                        # Entity Detection
                        entities = self.analyzer.classify_text(detected_text)
                        """st.text("Detected Entities:")
                        for entity in entities:
                            st.text(f" - Type: {entity.type}, Text: {entity.text}, Confidence: {entity.score:.2f}")"""
                        
                        # Store processed data for PDF generation
                        processed_data.append({
                            "image_name": image_name, 
                            "detected_text": detected_text, 
                            "entities": entities
                        })
                    
                    except Exception as e:
                        st.error(f"Error processing {image_name}: {e}")
                
                # Complete progress bar
                progress_bar.progress(100)
            

                if processed_data:
                    st.write("Generating PDF...")

                    try:
                        # Call the generate_report function
                        pdf_path = self.pdf_generator.generate_report(processed_data)
                        st.success(f"PDF successfully generated!")

                        # Preview the generated PDF in the UI (optional, depending on the Streamlit environment)
                        with open(pdf_path, "rb") as pdf_file:
                            pdf_data = pdf_file.read()
                        
                        st.download_button("Download PDF", pdf_data, "report.pdf", mime="application/pdf")
                        
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
                else:
                    st.warning("No processed data available for PDF generation.")


            

    def s3_storage_ui(self):
        """
        UI for S3 bucket image processing.
        """
        st.header("S3 Bucket Image Processing")
        
        # AWS Credentials Input
        with st.form("s3_credentials"):
            aws_access_key = st.text_input("AWS Access Key")
            aws_secret_access_key = st.text_input("AWS Secret Access Key", type="password")
            region_name = st.text_input("AWS Region Name")
            submitted = st.form_submit_button("Connect to S3")

        
        
        if submitted and aws_access_key and aws_secret_access_key and region_name:
            try:
                s3_storage = AWSHandler(aws_access_key, aws_secret_access_key, region_name)
                # Fetch object URLs
                all_buckets = s3_storage.list_all_buckets()
                
                processed_data = []
                
                # Process images from each bucket
                for bucket in all_buckets:
                    st.subheader(f"Processing Bucket: {bucket}")
                    urls = s3_storage.list_objects_in_bucket(bucket)
                    for url in urls:
                        try:
                            # Fetch image
                            response = requests.get(url)
                            if response.status_code == 200:
                                image_array = np.frombuffer(response.content, np.uint8)
                                img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                                
                                if img is not None:
                                    # OCR Detection
                                    detected_text = self.ocr.detect_text_s3(img)
                                    st.text(f"Image URL: {url}")
                                    st.text("Detected Text:")
                                    st.text(detected_text)
                                    
                                    # Entity Detection
                                    entities = self.analyzer.classify_text(detected_text)
                                    """st.text("Detected Entities:")
                                    for entity in entities:
                                        st.text(f" - Type: {entity.type}, Text: {entity.text}, Confidence: {entity.score:.2f}")"""
                                    
                                    # Store processed data
                                    processed_data.append({
                                        "image_name": url.split('/')[-1], 
                                        "detected_text": detected_text, 
                                        "entities": entities
                                    })
                                else:
                                    st.error(f"Failed to decode image: {url}")
                            else:
                                st.error(f"Failed to fetch image. HTTP Status Code: {response.status_code}")
                        
                        except Exception as e:
                            st.error(f"Error processing image {url}: {str(e)}")
                
                if processed_data:
                    st.write("Generating PDF...")

                    try:
                        # Call the generate_report function
                        pdf_path = self.pdf_generator.generate_report(processed_data)
                        st.success(f"PDF successfully generated!")

                        # Preview the generated PDF in the UI (optional, depending on the Streamlit environment)
                        with open(pdf_path, "rb") as pdf_file:
                            pdf_data = pdf_file.read()
                        
                        st.download_button("Download PDF", pdf_data, "report.pdf", mime="application/pdf")
                        
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
                else:
                    st.warning("No processed data available for PDF generation.")

            
            except Exception as e:
                st.error(f"Error connecting to S3: {str(e)}")



