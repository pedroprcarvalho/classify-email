import re
import pdfplumber



def extract_text(file):
    text = ""
    if file.filename.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    else:
        text = file.read().decode("utf-8")
    return text

def clean_email_content(text: str) -> str:
    text = re.sub(r'Atenciosamente.*', '', text,
                  flags=re.IGNORECASE | re.DOTALL)

    text = re.sub(r'\s+', ' ', text)

    text = re.sub(r'From:.*\n', '', text)
    return text.strip()