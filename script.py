import openai
from dotenv import load_dotenv
import os
from docx import Document
import time

load_dotenv()

start_time = time.time()
# read whole file
with open("transcript.txt", "r", encoding="utf-8") as f:
    data = f.read()

print(data)  # full text

client=openai.Client(api_key=os.getenv("GEMINI_API_KEY"),base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[{"role": "system", "content": "You are a helpful assistant that helps people find information."},
        {
            "role": "user",
            "content": data
        }
    ]
)           

print(response.choices[0].message.content)

document = Document()

document.add_heading('Transcript', 0)
document.add_paragraph(response.choices[0].message.content)

document.save('transcript.docx')

end_time = time.time()
elapsed = end_time - start_time

print(f"Processing completed in {elapsed:.2f} seconds (constraint: <60s)")