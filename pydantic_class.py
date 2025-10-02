from typing import List
from pydantic import BaseModel

class SOAPModel(BaseModel):
    Subjective: str = ""
    Objective: str = ""
    Assessment: str = ""
    Plan: list[str] = []

class ClinicianSummaryModel(BaseModel):
    Patient_Details: str = ""
    Chief_Complaint: str = ""
    History: str = ""
    Assessment: str = ""
    Plan: list[str] = []

class DosAndDontsModel(BaseModel):
    Dos: list[str] = []
    Donts: list[str] = []

class PatientSummaryModel(BaseModel):
    What_We_Did: list[str] = []
    What_To_Expect: list[str] = []
    Dos_and_Donts: DosAndDontsModel = DosAndDontsModel()
    When_To_Call: list[str] = []
    Next_Steps: list[str] = []

class LLMResponseModel(BaseModel):
    SOAP: SOAPModel = SOAPModel()
    Clinician_Summary: ClinicianSummaryModel = ClinicianSummaryModel()
    Patient_Summary: PatientSummaryModel = PatientSummaryModel()
    
