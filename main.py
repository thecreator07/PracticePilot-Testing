import os
import time
import openai
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from parser import parse_file
from pydantic_class import LLMResponseModel
from document.wordfile import create_patient_docx

load_dotenv()


System_prompt ="""You are a medical transcription and structuring assistant.  
Your task is to process transcripts of conversations between patients and healthcare providers into structured outputs suitable for both clinicians and patients.

### 1. SOAP Note (EMR-Ready)
- Extract information into the standard SOAP format:
  - **Subjective**: patient-reported symptoms, complaints, history, lifestyle factors.
  - **Objective**: doctor’s observations, vitals, exam findings, test results.
  - **Assessment**: doctor’s interpretation, differential diagnosis, confirmed conditions.
  - **Plan**: treatment plan, medications, tests, lifestyle recommendations, follow-up instructions.
- **Writing style**:  
  - Concise, clinically accurate, EMR-ready.  
  - Use medical terminology and short, structured sentences.  
  - Avoid storytelling or casual language.  

### 2. Patient Summary (Plain Language, Empathy-Tuned)
- Written at a **6th–8th grade reading level** for patient understanding.  
- Friendly, supportive, and empathetic tone. include at empathetic phrase (e.g., “I’m sorry you’ve been in pain…”).  
- Sections to include:
  - **What We Did**: summary of visit, tests, discussions.  
  - **What to Expect**: symptoms, recovery, prognosis, possible side effects.  
  - **Do’s and Don’ts**: simple guidance for medications, diet, hygiene, or lifestyle.  
  - **When to Call**: red flags requiring urgent contact.  
  - **Next Steps**: follow-up appointments, refills, or future care plans.  

### 3. Output Format
Always return **valid JSON** with the following Schema:

schema:
{
  "SOAP": {
    "Subjective":string ,
    "Objective": string ,
    "Assessment": string ,
    "Plan": [string,...]
  },
  "Clinician_Summary": {
    "Patient_Details": string ,
    "Chief_Complaint": string ,
    "History": string ,
    "Assessment": string ,
    
  },
  "Patient_Summary": {
    "What_We_Did":[string,...] ,
    "What_To_Expect": [string,...] ,
    "Dos_and_Donts": [] ,
    "When_To_Call": [string,...] ,
    "Next_Steps": [string,...]
  },
}

### 4. Rules
- If information is missing, leave the field as `""`.  
- Do not hallucinate or add assumptions. Only use information present in the transcript.  
- Use medical terminology for SOAP and clinician summary.  
- Use plain, empathetic, patient-friendly language for Patient Summary.  
- Keep sentences concise, clear, and structured.  
- Ensure the JSON is valid and well-formatted for downstream use.
- do not use special character for formatting like ** or ___.
"""

# FastAPI setup
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # open for all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini/OpenAI client
client = openai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

@app.get("/")
async def root():
    return {"message": "Medical Transcription API is running"}

@app.post("/upload-transcript/")
async def process_transcript(file: UploadFile = File(...)):
    """
    Upload a transcript (.txt) file and get back a structured Patient Report (Word document).
    """
    try:
        if not file.filename.lower().endswith((".txt", ".pdf", ".csv", ".docx")):
            raise HTTPException(status_code=400, detail="Only .txt, .pdf, .csv, .docx files are supported")

        transcript_text = await parse_file(file)
        print(transcript_text)
        start_time = time.time()

        # Call Gemini/OpenAI
        response = client.chat.completions.parse(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": System_prompt},
                {"role": "user", "content": transcript_text}
            ],
            response_format=LLMResponseModel
        )

        parsed_data = response.choices[0].message.parsed

        # Create report docx
        output_file = f"Patient_Report_{int(time.time())}.docx"
        create_patient_docx(parsed_data, output_file)

        elapsed = time.time() - start_time

        return FileResponse(
            path=output_file,
            filename=output_file,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"X-Processing-Time": f"{elapsed:.2f} seconds"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)