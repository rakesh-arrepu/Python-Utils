import fitz  # PyMuPDF

def copy_pdf(input_pdf, output_pdf):
    src = fitz.open(input_pdf)
    dst = fitz.open()
    for page_num in range(len(src)):
        dst.insert_pdf(src, from_page=page_num, to_page=page_num)
    dst.save(output_pdf)
    dst.close()
    src.close()

if __name__ == "__main__":
    input_pdf = "fluent_pattern_fixed.pdf"
    output_pdf = "formatted_output_with_graphics.pdf"
    copy_pdf(input_pdf, output_pdf)
    print(f"PDF copied with all graphics to {output_pdf}")