import fitz  # PyMuPDF

def extract_headers_and_content(pdf_path, output_path):
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

    # Write to output file
    with open(output_path, "w", encoding="utf-8") as f:
        for header, content in sections:
            f.write(f"{header}\n")
            f.write(f"{content}\n\n")

if __name__ == "__main__":
    pdf_path = "fluent_pattern_fixed.pdf"
    output_path = "formatted_output.txt"
    extract_headers_and_content(pdf_path, output_path)
    print(f"Formatted text written to {output_path}")