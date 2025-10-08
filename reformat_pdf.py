from PyPDF2 import PdfReader
import re

input_pdf = "/Users/rakesh_arrepu/Documents/Design patterns/PDF/Fluent Pattern in Selenium + Java + TestNG.pdf"
reader = PdfReader(input_pdf)

text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

with open("extracted.txt", "w", encoding="utf-8") as f:
    f.write(text)

from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Preformatted, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Create new PDF
output_pdf = "fluent_pattern_redesigned.pdf"
doc = SimpleDocTemplate(output_pdf, pagesize=LETTER, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)

# Styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Header', fontSize=16, leading=20, spaceAfter=12, textColor=colors.HexColor('#003366'), fontName='Helvetica-Bold'))
styles.add(ParagraphStyle(name='Body', fontSize=10.5, leading=14, spaceAfter=6))
styles.add(ParagraphStyle(name='CustomCode', fontName='Courier', fontSize=9, leading=12, backColor=colors.whitesmoke, borderPadding=5))

# Split content by major headers
pattern = r"(?:What is Fluent Pattern\?|Key Benefits|Basic Fluent Page Object Implementation|TestNG Test Implementation|Advanced Fluent Pattern with Conditional Actions|Traditional vs Fluent Pattern Comparison|🎯  Best Practices)"
sections = re.split(pattern, text)
headers = re.findall(pattern, text)

# Build content list
content = []
for i, section in enumerate(sections):
    if i == 0 and not headers:
        continue
    if i < len(headers):
        content.append(Paragraph(headers[i], styles['Header']))

    lines = section.strip().split("\n")
    buffer = []
    for line in lines:
        if (line.strip().startswith("public ") or line.strip().startswith("//") or 
            line.strip().startswith("@") or "{" in line or "}" in line):
            buffer.append(line)
        else:
            if buffer:
                content.append(Preformatted("\n".join(buffer), styles['CustomCode']))
                buffer = []
            if line.strip():
                content.append(Paragraph(line.strip(), styles['Body']))
    if buffer:
        content.append(Preformatted("\n".join(buffer), styles['CustomCode']))

    content.append(PageBreak())  # Force new page after each section

# Build PDF
doc.build(content)

print("✅ PDF created:", output_pdf)
