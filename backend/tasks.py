from crewai import Task
from models import RankedJobQueue, StudentProfile

class ExtractionTasks:
    def extraction_task(self, agent, pdf_path):
        return Task(
            description=f"""
            MANDATORY STEP: Use the 'Resume Parser Tool' exactly once.
            The input for the tool must be EXACTLY this string: '{pdf_path}'
            
            1. Extract name, college (IIT (ISM) Dhanbad), and degree.
            2. Identify all projects (MERN, Python) and experiences.
            3. Fill out the Answer Library and identify GitHub links.
            
            CRITICAL: Return ONLY a valid JSON object matching the StudentProfile schema.
            """,
            expected_output="""
                A strictly formatted JSON object containing the extracted student profile data. 
                Example structure: {"name": "...", "college": "...", "skills": {...}, ...}
            """,
            agent=agent,
            output_pydantic=StudentProfile # Keep this to ensure structure
        )

    def validation_task(self, agent, context_task, pdf_path):
        return Task(
            description=f"""
                1. Analyze the StudentProfile from the previous task.
                2. Compare every 'Bullet Bank' entry against the raw resume text by calling 'Resume Parser Tool' exactly once on '{pdf_path}'.
                3. CRITICAL: If the Researcher added skills like 'AWS' or 'Docker' that are NOT in the PDF, remove them immediately.
                4. Ensure the 'Answer Library' accurately reflects the student's status (e.g., IIT (ISM) Dhanbad student, authorized for India).
                5. Verify that 'Proof Pack' links are correctly mapped to their respective projects.
            """,
            expected_output="""
                A 100% grounded StudentProfile object. Any 'fluff' or unverified 
                technical claims must be purged to ensure absolute truthfulness.
            """,
            agent=agent,
            context=[context_task],
            output_pydantic=StudentProfile
    )
    def assembly_task(self, agent, validation_context, policy):
        return Task(
            description=f"""
                1. Take the verified StudentProfile from the Safety Auditor[cite: 19].
                2. Integrate the following Apply Policy constraints: {policy}[cite: 61].
                3. Finalize the 'Bullet Bank' by ensuring every achievement is tied to a 'Proof Pack' link[cite: 22, 25].
                4. Construct the final Answer Library for common application questions[cite: 23].
                5. Ensure the entire Artifact Pack is consistent and ready for high-volume, autonomous submission[cite: 12].
            """,
            expected_output="""
                A comprehensive, merged StudentProfile object (Artifact Pack) that includes 
                both verified professional facts and operational apply-constraints.
            """,
            agent=agent,
            context=[validation_context],
            output_pydantic=StudentProfile
    )

# tasks.py
class JobSearchTasks:
    def ranking_task(self, agent, artifact_context):
        return Task(
            description="""
                1. Fetch available jobs from the Job Search Tool by querying it using relevant keywords from the profile and preferred locations from the policy.
                2. Cross-reference them with the Student Artifact Pack.
                3. Rank the top 5 roles that match the student's verified skills.
                4. REJECT any jobs from blocked companies or those requiring excessive experience.
                5. For each match, provide the job_id, title, company, a match_score (0-100), 
                   a 1-sentence reasoning, a list of missing skills, and the apply_link.
            """,
            expected_output="""
                A structured list of the top 5 most relevant jobs including apply links.
            """,
            agent=agent,
            context=[artifact_context],
            output_pydantic=RankedJobQueue # This handles the JSON formatting for you!
        )