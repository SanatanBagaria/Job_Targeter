import json
from crewai.tools import BaseTool
import PyPDF2
from typing import Type
from pydantic import BaseModel, Field

class FileInputSchema(BaseModel):
    """Input schema for ResumeParserTool."""
    pdf_path: str = Field(..., description="The full path to the PDF resume file.")

class ResumeParserTool(BaseTool):
    name: str = "Resume Parser Tool"
    description: str = "Reads a PDF resume file from a path string and returns the raw text."

    def _run(self, pdf_path: str) -> str:
        # Clean up path in case the LLM wrapped it in quotes or braces
        pdf_path = pdf_path.strip().strip("'\"{}[]")
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                # Hackathon Requirement: Ingest student's input (Resume PDF)
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        text += content
            return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
        
import os
import requests
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

class JobSearchInput(BaseModel):
    """Input schema for JobSearchTool."""
    query: str = Field(..., description="Search query containing keywords and/or locations (e.g. 'React developer Bangalore').")

class JobSearchTool(BaseTool):
    name: str = "Job Search Tool"
    description: str = "Searches live job listings using a search query string containing keywords and locations."

    def _run(self, query: str) -> str:
        api_key = os.getenv("RAPIDAPI_KEY")
        if not api_key:
            # Fallback to local sandbox
            try:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                sandbox_path = os.path.join(base_dir, "jobs_sandbox.json")
                with open(sandbox_path, 'r') as f:
                    jobs = json.load(f)
                # Add mock apply links
                for job in jobs:
                    if 'apply_link' not in job:
                        job['apply_link'] = f"https://example.com/apply/{job.get('job_id', 'unknown')}"
                return json.dumps(jobs)
            except FileNotFoundError:
                return "Error: jobs_sandbox.json not found."

        url = "https://jsearch.p.rapidapi.com/search-v2"
        querystring = {"query": query, "num_pages": "1", "page": "1"}
        
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "jsearch.p.rapidapi.com"
        }
        
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "OK":
                    data_field = data.get("data", {})
                    if isinstance(data_field, dict):
                        raw_jobs = data_field.get("jobs", [])
                    else:
                        raw_jobs = data_field if isinstance(data_field, list) else []
                    normalized_jobs = []
                    for job in raw_jobs:
                        normalized_jobs.append({
                            "job_id": job.get("job_id", ""),
                            "title": job.get("job_title", ""),
                            "company": job.get("employer_name", ""),
                            "location": f"{job.get('job_city', '')}, {job.get('job_country', '')}",
                            "description": job.get("job_description", ""),
                            "requirements": [job.get("job_title", "")] + (job.get("job_required_skills", []) or []),
                            "min_experience_years": job.get("job_required_experience", {}).get("required_experience_in_months", 0) // 12 if job.get("job_required_experience") else 0,
                            "apply_link": job.get("job_apply_link", "https://example.com/apply")
                        })
                    return json.dumps(normalized_jobs)
                else:
                    return f"API Error: {data.get('message', 'Unknown error')}"
            else:
                return f"HTTP Error: {response.status_code}"
        except Exception as e:
            return f"Error connecting to Job API: {str(e)}"