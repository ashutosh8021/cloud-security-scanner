import io
from PyPDF2 import PdfReader
import docx

def load_text_from_uploaded(uploaded_file) -> str:
    """
    Safely extract text from Streamlit UploadedFile (txt, pdf, docx).
    """
    name = getattr(uploaded_file, "name", "").lower()

    # Get raw bytes once
    data = uploaded_file.getvalue()

    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(data))
            chunks = []
            for page in reader.pages:
                txt = page.extract_text() or ""
                chunks.append(txt)
            return "\n".join(chunks)
        except Exception:
            return ""

    if name.endswith(".docx"):
        try:
            doc = docx.Document(io.BytesIO(data))
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception:
            return ""

    return ""
