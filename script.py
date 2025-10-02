import openai
from dotenv import load_dotenv
import os
from docx import Document
import time
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

start_time = time.time()

# read transcript file
with open("transcript.txt", "r", encoding="utf-8") as f:
    data = f.read()

print(data)  

client=openai.Client(api_key=os.getenv("GEMINI_API_KEY"),base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

response = client.chat.completions.parse(
    model="gemini-2.5-flash",
    messages=[{"role": "system", "content": System_prompt},
        {
            "role": "user",
            "content": data
        }
    ],response_format=LLMResponseModel
)           

# print(response.choices[0].message.parsed)

# Creating instance of a word document
print(response.choices[0].message.parsed)

# Creating Patient_Resport Document file
create_patient_docx(response.choices[0].message.parsed, "Patient_Report1.docx")

end_time = time.time()
elapsed = end_time - start_time

print(f"Processing completed in {elapsed:.2f} seconds (constraint: <60s)")