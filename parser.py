from fastapi import UploadFile, HTTPException
from docx import Document
import csv
import io
from PyPDF2 import PdfReader

async def parse_file(file: UploadFile) -> str:
    filename = file.filename.lower()

    if filename.endswith(".txt"):
        transcript_text = (await file.read()).decode("utf-8")

    elif filename.endswith(".pdf"):
        pdf_reader = PdfReader(io.BytesIO(await file.read()))
        transcript_text = "\n".join([page.extract_text() or "" for page in pdf_reader.pages])

    elif filename.endswith(".csv"):
        content = (await file.read()).decode("utf-8")
        reader = csv.reader(io.StringIO(content))
        rows = [" ".join(row) for row in reader]
        transcript_text = "\n".join(rows)

    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(await file.read()))
        transcript_text = "\n".join([para.text for para in doc.paragraphs])

    else:
        raise HTTPException(status_code=400, detail="Only .txt, .pdf, .csv, .docx files are supported")

    return transcript_text
