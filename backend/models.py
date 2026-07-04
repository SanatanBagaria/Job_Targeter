from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Project(BaseModel):
    title: str = Field(..., description="The name of the project")
    tech_stack: List[str] = Field(..., description="Key technologies used (e.g., MERN, LangChain)")
    # The 'Bullet Bank' requirement: tied to specific experiences [cite: 22]
    bullets: List[str] = Field(..., description="Normalized achievement bullets from the resume")
    links: List[str] = Field(default_factory=list, description="GitHub or Demo links for the Proof Pack")

class AnswerLibrary(BaseModel):
    # Change 'str' to 'Optional[str]' to allow 'None' values
    work_authorization: Optional[str] = Field(default="Not Found", description="Current work auth status")
    relocation: bool = Field(default=True, description="Willingness to relocate")
    salary_expectation: Optional[str] = None
    notice_period: str = Field(default="Immediate", description="Earliest start date")

class StudentProfile(BaseModel):
    name: str
    college: str 
    degree: str
    # Major must be optional because models often miss it in PDF headers
    major: Optional[str] = Field(default="Not Specified") 
    skills: Dict[str, List[str]] = Field(..., description="Categorized skills")
    projects: List[Project]
    experience: List[dict] 
    answer_library: AnswerLibrary 
    global_proof_links: List[str] = Field(default_factory=list)

class ApplyPolicy(BaseModel):
    # Maximum applications per day [cite: 62]
    max_applications_per_day: int = Field(default=15, ge=1, le=50)
    
    # Minimum match threshold to apply (0.0 to 1.0) [cite: 63]
    min_match_threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    
    # Required constraints [cite: 66]
    preferred_locations: List[str] = Field(default_factory=list, description="e.g., ['Bangalore', 'Remote']")
    visa_required: bool = Field(default=False)
    
    # "Stop now" kill switch [cite: 67]
    is_active: bool = Field(default=True)
    
    # Blocked companies or role types [cite: 64]
    blocked_companies: List[str] = Field(default_factory=list)
    blocked_roles: List[str] = Field(default_factory=list)

# models.py
class RankedJob(BaseModel):
    job_id: str = Field(..., description="The unique ID from the sandbox or API.")
    title: str = Field(..., description="The job title.")
    company: str = Field(..., description="The company name.")
    match_score: int = Field(..., ge=0, le=100, description="Score based on verified skill overlap.")
    fit_reasoning: str = Field(..., description="1-sentence explanation of why this fits.")
    missing_skills: List[str] = Field(..., description="Required skills NOT found in the resume.")
    apply_link: str = Field(..., description="Direct link to apply for the job.")

class RankedJobQueue(BaseModel):
    top_matches: List[RankedJob] = Field(..., max_items=10)