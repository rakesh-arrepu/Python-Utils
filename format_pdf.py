import fitz  # PyMuPDF

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
                    # You may need to adjust this threshold based on your PDF
                    if font_size > 14 and text:  # Assume headers have font size > 14
                        # Save previous section
                        if current_header:
                            sections.append({
                                "header": current_header,
                                "content": " ".join(current_content).strip()
                            })
                        current_header = text
                        current_content = []
                    else:
                        if current_header:
                            current_content.append(text)
    # Add last section
    if current_header:
        sections.append({
            "header": current_header,
            "content": " ".join(current_content).strip()
        })
    return sections

# Usage
pdf_path = "fluent_pattern_fixed.pdf"
sections = extract_headers_and_content(pdf_path)

# Print or process sections
for section in sections:
    print(f"Header: {section['header']}")
    print(f"Content: {section['content']}\n")
