import os
from fpdf import FPDF
import unicodedata
from datetime import datetime
from app.config import findings_template, risks_template, tests_template, UPLOAD_FOLDER, PROCESSED_FOLDER


class PDF(FPDF):
    def header(self):
        if os.path.exists("app/logo.png"):
            self.image("app/logo.png", 10, 10, 30)
        self.set_xy(45, 10)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 8, "THE SETV.G HOSPITAL", ln=True, align='L')
        self.set_xy(45, 18)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, "Accurate | Caring | Instant", ln=True, align='L')
        self.set_xy(135, 10)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, "Phone: 040-XXXXXXXXX / +91 XX XXX XXX", ln=True, align='R')
        self.cell(0, 8, "Email: setvgbhospital@gmail.com", ln=True, align='R')
        self.set_xy(10, 30)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, "SETV.ASRV LLP, Avishkaran, NIPER, Balanagar, Hyderabad, Telangana, 500037.", ln=True, align='C')
        self.set_fill_color(0, 121, 191)
        self.rect(10, 40, 190, 3, 'F')
        self.set_fill_color(228, 30, 37)
        self.rect(10, 43, 190, 3, 'F')
        self.ln(15)
        
    def footer(self):
        self.set_y(-15)
        self.set_fill_color(100, 149, 237)
        self.rect(0, self.get_y(), 210, 10, 'F')
        self.set_font('Arial', 'I', 8)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, f"Page {self.page_no()} || THE SETV.G HOSPITAL || EMERGENCY CONTACT - +91 XXXXXXXXXX", 0, 0, 'C')

def _to_latin1(text):
    if not isinstance(text, str): 
        return text
    return unicodedata.normalize('NFKD', text).encode('latin-1', 'ignore').decode('latin-1')

def generate_pdf_report(patient_info, selected_images_info, output_path=None):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, _to_latin1("Patient Scan Report"), ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    date_str = datetime.now().strftime('%Y-%m-%d')
    time_str = datetime.now().strftime('%H:%M:%S')
    cw_left, cw_right = 110, 110
    
    pdf.cell(cw_left, 10, _to_latin1(f"Patient Name: {patient_info['Name']}"), align="L")
    pdf.cell(cw_right, 10, _to_latin1(f"Radiologist Name: {patient_info['Radiologist_Name']}"), ln=True)
    pdf.cell(cw_left, 10, _to_latin1(f"Patient ID: {patient_info['Patient_ID']}"), align="L")
    pdf.cell(cw_right, 10, _to_latin1(f"Radiologist ID: {patient_info['Radiologist_ID']}"), ln=True)
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(cw_left, 10, _to_latin1(f"Age: {patient_info['Age']}"), align="L")
    pdf.cell(cw_right, 10, _to_latin1(f"Date: {date_str}"), ln=True)
    pdf.cell(cw_left, 10, _to_latin1(f"Gender: {patient_info['Gender']}"), align="L")
    pdf.cell(cw_right, 10, _to_latin1(f"Time: {time_str}"), ln=True)
    pdf.ln(10)
    
    for idx, img_info in enumerate(selected_images_info):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, _to_latin1(f"Output Xray image {idx+1}:"), ln=True)
        
        # Center the image
        page_width = pdf.w
        image_width = 120  
        image_height = 90  
        x_offset = (page_width - image_width) / 2

        annotated_abs_path = os.path.join(PROCESSED_FOLDER, img_info['annotated_path'].replace('processed/', ''))
        if os.path.exists(annotated_abs_path):
            pdf.image(annotated_abs_path, x=x_offset, w=image_width, h=image_height)
            
        pdf.ln(10)  # Add more space after image
        
        # Add a separator line
        pdf.line(20, pdf.get_y(), page_width-20, pdf.get_y())
        pdf.ln(5)

        label = img_info['label']
        if label.startswith('knee osteoarthritis (') and label.endswith(')'):
            base_label = label[label.find('(')+1:label.find(')')].strip()
            findings = findings_template.get(base_label, "No findings available")
            risks = risks_template.get(base_label, "No risks available")
            tests = tests_template.get(base_label, "No tests available")
            
            # Section headers with consistent spacing
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, _to_latin1(f"Findings for Knee Osteoarthritis ({base_label.title()}):"), ln=True)
        else:
            findings = findings_template.get(label, "No findings available")
            risks = risks_template.get(label, "No risks available")
            tests = tests_template.get(label, "No tests available")
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, _to_latin1(f"Findings for {label.title()}:"), ln=True)

        # Add content with consistent margins and spacing
        pdf.set_left_margin(20)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 8, _to_latin1(findings))
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 12)
        if label.startswith('knee osteoarthritis ('):
            pdf.cell(0, 10, _to_latin1(f"Risks for Knee Osteoarthritis ({base_label.title()}):"), ln=True)
        else:
            pdf.cell(0, 10, _to_latin1(f"Risks for {label.title()}:"), ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 8, _to_latin1(risks))
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 12)
        if label.startswith('knee osteoarthritis ('):
            pdf.cell(0, 10, _to_latin1(f"Recommended Tests for Knee Osteoarthritis ({base_label.title()}):"), ln=True)
        else:
            pdf.cell(0, 10, _to_latin1(f"Recommended Tests for {label.title()}:"), ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 8, _to_latin1(tests))
        
        # Reset margin and add section separator
        pdf.set_left_margin(10)
        pdf.ln(10)
        pdf.line(20, pdf.get_y(), page_width-20, pdf.get_y())
        pdf.ln(10)

    # Add disclaimer and other content...
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, _to_latin1("Disclaimer:"), ln=True)
    pdf.set_font("Arial", "", 11)
    disclaimer_text = (
        "The scans show areas that could be fractures, dislocations, arthritis, "
        "or no acute issues at all. To be sure, your doctor will review your history, examine you, "
        "and may order additional tests or imaging. This summary is informational only and isn't "
        "a substitute for professional medical advice. Please see a healthcare professional "
        "for diagnosis and treatment."
    )
    pdf.multi_cell(0, 8, _to_latin1(disclaimer_text))
    
    # Disease Symptoms Table
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, _to_latin1("Disease Symptoms Table:"), ln=True)
    pdf.ln(2)
    
    # Center the table
    page_width = pdf.w
    table_width = 170  # Total table width
    x_offset = (page_width - table_width) / 2
    pdf.set_x(x_offset)

    symptoms_data = [
        ["Body Part", "Common Symptoms"],
        ["Knee", "Joint pain, Swelling, Limited flexion/extension, Instability"],
        ["Spine", "Back pain, Restricted movement, Radiculopathy, Postural changes"],
        ["Heel", "Heel pain, Difficulty walking, Morning stiffness, Swelling"],
        ["Wrist", "Wrist pain, Limited range of motion, Grip weakness, Swelling"]
    ]
    
    col_w = [40, 130]  # Adjusted column widths to match table_width
    line_height = 8
    pdf.set_font("Arial", "B", 10)
    
    # Header with background color
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(col_w[0], line_height, _to_latin1(symptoms_data[0][0]), border=1, fill=True)
    pdf.cell(col_w[1], line_height, _to_latin1(symptoms_data[0][1]), border=1, fill=True, ln=True)
    
    # Data rows
    pdf.set_font("Arial", "", 10)
    for row in symptoms_data[1:]:
        pdf.set_x(x_offset)  # Reset X position for each row
        pdf.cell(col_w[0], line_height, _to_latin1(row[0]), border=1)
        pdf.multi_cell(col_w[1], line_height, _to_latin1(row[1]), border=1)
    
    pdf.ln(10)
    
    # Doctor's signature section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, _to_latin1("Doctor's Comments:"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, _to_latin1(" "))
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, _to_latin1("Signature: ____________________"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, _to_latin1("Name of Doctor: "), ln=True)
    pdf.cell(0, 8, _to_latin1("Designation: "), ln=True)
    pdf.cell(0, 8, _to_latin1("Contact No: +91 XXXXXXXXXX"), ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, _to_latin1("*End of Report*"), ln=True, align="C")
    
    if output_path is None:
        os.makedirs(REPORTS_FOLDER, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pid = patient_info.get("Patient_ID", "unknown")
        output_path = os.path.join(REPORTS_FOLDER, f"{pid}_report_{timestamp}.pdf")
    
    try:
        pdf.output(output_path)
        return output_path
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None
