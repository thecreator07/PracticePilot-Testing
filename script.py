import openai
from dotenv import load_dotenv
import os
from docx import Document
import time

load_dotenv()

System_prompt ="""You are a medical transcription and structuring assistant.  
You will process transcripts of conversations between patients and healthcare providers into structured outputs.

### 1. SOAP Note
Extract information into the standard SOAP format:
- Subjective: patient-reported symptoms, complaints, lifestyle factors.
- Objective: doctor’s observations, vitals, exam findings, test results.
- Assessment: doctor’s interpretation, differential diagnosis, confirmed conditions.
- Plan: treatment plan, medications, tests, lifestyle recommendations, follow-up.

### 2. Patient Summary (Plain Language, Empathy-Tuned)
- Written at a 6th–8th grade reading level for patients/families.
- Use friendly and empathetic tone. Must include at least one empathetic phrase (e.g., “I’m sorry you’ve been in pain…”).
- Sections:
  - What we did (today’s visit, tests, discussion)
  - What to expect (symptoms, recovery, prognosis, possible side effects)
  - Do’s and Don’ts (simple guidance on lifestyle/meds)
  - When to call (red flags that require urgent contact)
  - Next steps (appointments, follow-ups, refills)

### 3. Output Format
Always output valid JSON with the following structure:
{
  "SOAP": {
    "Subjective": "",
    "Objective": "",
    "Assessment": "",
    "Plan": ""
  },
  "Clinician_Summary": {
    "Patient_Details": "",
    "Chief_Complaint": "",
    "History": "",
    "Assessment": "",
    "Plan": ""
  },
  "Patient_Summary": {
    "What_We_Did": "",
    "What_To_Expect": "",
    "Dos_and_Donts": "",
    "When_To_Call": "",
    "Next_Steps": ""
  },
  "Exports": {
    "Formats": ["JSON", "PDF", "FHIR_compatible_bundle"],
    "FHIR_Mapping": {
      "Condition": "",
      "MedicationRequest": "",
      "Observation": "",
      "CarePlan": ""
    }
  }
}

### 4. Rules
- If information is missing, leave the field as `""`.
- Do not hallucinate. Only use transcript data.
- Use medical terminology for SOAP and clinician summary.
- Use layman-friendly, empathetic, plain language for patient summary.
"""

start_time = time.time()

# read transcript file
with open("transcript.txt", "r", encoding="utf-8") as f:
    data = f.read()

print(data)  

client=openai.Client(api_key=os.getenv("GEMINI_API_KEY"),base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[{"role": "system", "content": System_prompt},
        {
            "role": "user",
            "content": data
        }
    ],
)           

print(response.choices[0].message.content)

# Creating instance of a word document
document = Document()

document.add_heading('Transcript', 0)
document.add_paragraph(response.choices[0].message.content)
# saving the transcript into docx file
document.save('transcript.docx')

end_time = time.time()
elapsed = end_time - start_time

print(f"Processing completed in {elapsed:.2f} seconds (constraint: <60s)")