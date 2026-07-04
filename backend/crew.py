import json
from agents import ExtractionAgents, JobSearchAgents
from tasks import ExtractionTasks, JobSearchTasks
from models import ApplyPolicy
from crewai import Crew
import os

os.environ["OTEL_SDK_DISABLED"] = "true"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESUME_PATH = os.path.join(BASE_DIR, "resume.pdf")
QUEUE_PATH = os.path.join(BASE_DIR, "apply_queue.json")

# 1. Initialize
agents_factory = ExtractionAgents()
tasks_factory = ExtractionTasks()
search_agents_factory = JobSearchAgents()
search_tasks_factory = JobSearchTasks()

# 2. Define your "Apply Policy"
user_policy = ApplyPolicy(
    max_applications_per_day=20, 
    min_match_threshold=0.8,     
    preferred_locations=["Remote", "Bangalore", "Dhanbad"], 
    blocked_companies=["ScamCorp", "UnrelatedInc"] 
)

# 3. Instantiate Agents
researcher = agents_factory.researcher_agent()
validator = agents_factory.validator_agent()
assembler = agents_factory.artifact_assembler_agent()
analyst = search_agents_factory.job_analyst_agent()

# 4. Define Tasks
extract_task = tasks_factory.extraction_task(researcher, RESUME_PATH)
validate_task = tasks_factory.validation_task(validator, extract_task, RESUME_PATH)
assemble_task = tasks_factory.assembly_task(assembler, validate_task, user_policy)
rank_task = search_tasks_factory.ranking_task(analyst, assemble_task)

import time

# Rate limiting sleep configuration between sequential tasks
RATE_LIMIT_DELAY = int(os.getenv("RATE_LIMIT_DELAY_SECONDS", "65"))

def rate_limit_delay(task_output):
    if RATE_LIMIT_DELAY > 0:
        print(f"\n[Rate Limiter] Task completed. Sleeping {RATE_LIMIT_DELAY} seconds to reset TPM rate limits...")
        time.sleep(RATE_LIMIT_DELAY)

# 5. Assemble the Crew
artifact_crew = Crew(
    agents=[researcher, validator, assembler, analyst],
    tasks=[extract_task, validate_task, assemble_task, rank_task],
    verbose=True,
    task_callback=rate_limit_delay
)

# 6. Run the Pipeline (Standalone Mode)
if __name__ == "__main__":
    print("Starting Phase 2 Pipeline: Extraction & Ranking...")
    result = artifact_crew.kickoff()
    
    # 7. Output to JSON
    with open(QUEUE_PATH, 'w', encoding='utf-8') as f:
        f.write(result.raw)
    
    print(f"Success! Generated apply_queue.json.")