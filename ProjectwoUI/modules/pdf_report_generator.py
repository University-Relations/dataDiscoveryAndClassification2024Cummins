from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
import random
from reportlab.lib import colors 

class PDFReportGenerator:
    """Generates a PDF report summarizing PII analysis."""
    def __init__(self, filename="PII_Report.pdf"):
        self.filename = filename
        

    def generate_summary(self, data):
        total_images = len(data)
        pii_detected_count = sum(1 for row in data if row["entities"])
        pii_types = {}
        for row in data:
            for entity in row["entities"]:
                entity_type = entity["entity"]
                pii_types[entity_type] = pii_types.get(entity_type, 0) + 1
        return {
            "total_images": total_images,
            "pii_detected_count": pii_detected_count,
            "pii_percentage": (pii_detected_count / total_images) * 100 if total_images > 0 else 0,
            "pii_types": pii_types
        }

    def generate_report(self, data): 
        file_extension = ".pdf"
        counter = 1
        
        while os.path.exists(self.filename):
            self.filename = "PII_Report"+str(counter)+file_extension
            counter += 1

        doc = SimpleDocTemplate(
            self.filename,
            pagesize=letter,
            leftMargin=30,
            rightMargin=30,
            topMargin=40,
            bottomMargin=40,
        )
        elements = []
        styles = getSampleStyleSheet()

        # Title
        elements.append(Paragraph("PII Detection Report", styles["Title"]))
        elements.append(Spacer(1, 20))

        # Summary Section
        summary = self.generate_summary(data)
        elements.append(Paragraph("Overall Summary", styles["Heading2"]))
        summary_table_data = [
            ["Metric", "Value"],
            ["Total Images Scanned", summary["total_images"]],
            ["Images Containing PII", f"{summary['pii_detected_count']} ({summary['pii_percentage']:.2f}%)"],
            ["Most Common PII Types", Paragraph(", ".join(f"{k} ({v})" for k, v in summary["pii_types"].items()) or "None", styles["BodyText"])]
        ]
        summary_table = Table(
            summary_table_data,
            colWidths=[150, 350],  # Dynamically adjust column width
            hAlign="LEFT"
        )
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 24))

        # Detailed Results Section (Truncated for brevity)
        # Detailed Results Section
        elements.append(Paragraph("Detailed Results", styles["Heading2"]))
        table_data = [["Image Name", "PII Detected", "Detected Entities"]]
        for row in data:
            pii_detected = "Yes" if row["entities"] else "No"
            entities = "\n".join([f"{e['entity']} (Score: {e['score']:.2f})" for e in row["entities"]]) or "None"
            table_data.append([row["image_name"], pii_detected, entities])

        # Create a table without fixed column widths
        detailed_table = Table(table_data)
        detailed_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('WORDWRAP', (0, 0), (-1, -1), 'LTR')
        ]))
        elements.append(detailed_table)
        doc.build(elements)
        print(f"PDF report saved as {self.filename}")
        
        return self.filename
    

