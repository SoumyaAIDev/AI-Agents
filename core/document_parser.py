import fitz, docx, pptx, pandas as pd

def parse_pdf(file_path):
    doc = fitz.open(file_path)
    return [page.get_text() for page in doc]

def parse_docx(file_path):
    doc = docx.Document(file_path)
    return [para.text for para in doc.paragraphs]

def parse_pptx(file_path):
    pres = pptx.Presentation(file_path)
    return [shape.text for slide in pres.slides for shape in slide.shapes if hasattr(shape, "text")]

def parse_csv(file_path):
    df = pd.read_csv(file_path)
    return [row.to_json() for _, row in df.iterrows()]

def parse_txt(file_path):
    with open(file_path, "r") as f:
        return f.readlines()

def parse_file(file_path):
    if file_path.endswith(".pdf"):
        return parse_pdf(file_path)
    elif file_path.endswith(".docx"):
        return parse_docx(file_path)
    elif file_path.endswith(".pptx"):
        return parse_pptx(file_path)
    elif file_path.endswith(".csv"):
        return parse_csv(file_path)
    else:
        return parse_txt(file_path)
