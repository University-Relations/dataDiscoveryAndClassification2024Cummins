
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import cv2
import numpy as np
import requests 

from modules.ocr_processor import OCRProcessor
from modules.pii_analyzer import PIIAnalyzer
from modules.pdf_report_generator import PDFReportGenerator
from modules.aws_handler import AWSHandler

app = Flask(__name__)
CORS(app)

ocr_processor = OCRProcessor()
pii_analyzer = PIIAnalyzer()
report_generator = PDFReportGenerator()

@app.route('/api/process-local-files', methods=['POST'])
def process_local_files():
    if 'files' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400
    
    files = request.files.getlist('files')
    report_data = []

    for file in files:
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                file.save(temp_file.name)
                app.logger.info(f"Saved file: {file.filename}")

            # Process file
            detected_text = ocr_processor.detect_text(temp_file.name)
            app.logger.info(f"Detected text: {detected_text}")

            entities = pii_analyzer.classify_text(detected_text)
            app.logger.info(f"Entities: {entities}")

            report_data.append({
                "image_name": file.filename, 
                "detected_text": detected_text, 
                "entities": entities
            })
        except Exception as e:
            app.logger.error(f"Error processing file {file.filename}: {str(e)}")
            return jsonify({"error": f"Error processing file {file.filename}: {str(e)}"}), 500
        finally:
            # Cleanup temporary file
            try:
                os.unlink(temp_file.name)  # Delete temporary file
            except Exception as e:
                app.logger.error(f"Error deleting temporary file {temp_file.name}: {str(e)}")

    # Generate report
    try:
        report_filename = "PII_Report.pdf"
        report_generator.filename = report_filename
        report_generator.generate_report(report_data)
    except Exception as e:
        app.logger.error(f"Error generating report: {str(e)}")
        return jsonify({"error": "Error generating report"}), 500

    return jsonify({
        "message": "Files processed successfully",
        "report": report_filename
    })



@app.route('/api/process-s3-files', methods=['POST'])
def process_s3_files():
    data = request.json
    aws_access_key = data.get('aws_access_key')
    aws_secret_access_key = data.get('aws_secret_access_key')
    region_name = data.get('region_name')

    try:
        aws_handler = AWSHandler(aws_access_key, aws_secret_access_key, region_name)
        buckets = aws_handler.list_all_buckets()
        
        report_data = []
        for bucket in buckets:
            urls = aws_handler.list_objects_in_bucket(bucket)
            for url in urls:
                response = requests.get(url)
                if response.status_code == 200:
                    image_array = np.frombuffer(response.content, np.uint8)
                    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                    if img is not None:
                        detected_text = ocr_processor.detect_text_s3(img)
                        entities = pii_analyzer.classify_text(detected_text)
                        report_data.append({
                            "image_name": url.split('/')[-1], 
                            "detected_text": detected_text, 
                            "entities": entities
                        })

        # Generate report
        report_filename = "S3_PII_Report.pdf"
        report_generator.filename = report_filename
        report_generator.generate_report(report_data)

        return jsonify({
            "message": "S3 files processed successfully",
            "report": report_filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

REPORTS_DIRECTORY = os.path.join(os.getcwd(), '')

@app.route('/download-report/<filename>')
def download_report(filename):
    # Construct the full file path
    file_path = os.path.join(REPORTS_DIRECTORY, filename)
    print(f"Looking for file at: {file_path}")  # Debugging

    try:
        # Serve the file from the reports directory
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        print(f"File not found: {file_path}")  # Debugging
        return jsonify({"error": "Report not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)