import fitz  # PyMuPDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def extract_headers_and_content(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []
    current_header = None
    current_content = []

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    font_size = span["size"]
                    # Adjust font size threshold as needed for your PDF
                    if font_size > 14 and text:
                        if current_header:
                            sections.append((current_header, " ".join(current_content).strip()))
                        current_header = text
                        current_content = []
                    else:
                        if current_header:
                            current_content.append(text)
    if current_header:
        sections.append((current_header, " ".join(current_content).strip()))
    return sections

def write_sections_to_pdf(sections, output_pdf):
    doc = SimpleDocTemplate(output_pdf, pagesize=A4)
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=10,
        spaceBefore=20,
        textColor='darkblue'
    )
    content_style = ParagraphStyle(
        'Content',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=15
    )
    story = []
    for header, content in sections:
        story.append(Paragraph(header, header_style))
        story.append(Paragraph(content, content_style))
        story.append(Spacer(1, 12))
    doc.build(story)

if __name__ == "__main__":
    pdf_path = "fluent_pattern_fixed.pdf"
    output_pdf = "formatted_output.pdf"
    sections = extract_headers_and_content(pdf_path)
    write_sections_to_pdf(sections, output_pdf)
    print(f"Formatted PDF written to {output_pdf}")