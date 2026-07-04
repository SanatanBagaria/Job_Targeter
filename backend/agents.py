from tools import JobSearchTool, ResumeParserTool
from crewai import Agent, LLM
import os
from dotenv import load_dotenv
import litellm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)
litellm.num_retries = 5

# Select LLM model based on environment config (default to gemini/gemini-flash-latest)
default_model = "gemini/gemini-flash-latest"
model_name = os.getenv("LLM_MODEL", default_model)

# Assign correct api key based on provider prefix
if model_name.startswith("groq/"):
    api_key = os.getenv("GROQ_API_KEY")
else:
    api_key = os.getenv("GEMINI_API_KEY")

print(f"[LLM Config] Initializing agent model: {model_name}")

llm = LLM(
    model=model_name, 
    api_key=api_key,
    temperature=0.0,
    verbose=True
)

resume_tool = ResumeParserTool()

class ExtractionAgents:
    def researcher_agent(self):
        return Agent(
            role="Lead Fact-Extractor",
            goal="Identify and extract education, skills, and projects exactly as written.",
            backstory="Expert at parsing technical resumes for IIT (ISM) Dhanbad students.",
            tools=[resume_tool],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )

    def validator_agent(self):
        return Agent(
            role="Safety Auditor",
            goal="Cross-check extracted JSON against the original text to prevent hallucinations.",
            backstory="You are a strict recruiter who penalizes any fabricated experience or 'fluff'.",
            llm=llm,
            tools=[resume_tool],
            verbose=True
        )
    
    def artifact_assembler_agent(self):
        return Agent(
            role="Artifact Assembly Specialist",
            goal="Combine verified student data and user-defined policies into a final, deployable Artifact Pack.",
            backstory="""You are a meticulous project manager. You take verified facts from the Safety Auditor 
            and the operational constraints from the Apply Policy to ensure the final application 
            profile is consistent, truthful, and follows all student-defined rules.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        
class JobSearchAgents:
    def job_analyst_agent(self):
        return Agent(
            role="Targeted Job Analyst",
            goal="Filter and rank the top 5 most relevant jobs from the search results based on the student's Artifact Pack.",
            backstory="""You are a strict, data-driven recruiter. You do not make assumptions. 
            You only recommend jobs where the student's verified skills and projects 
            directly align with the job requirements. Every job recommended must have a valid apply link.""",
            llm=llm, 
            verbose=True,
            allow_delegation=False,
            tools=[JobSearchTool()]
        )