from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from crew import artifact_crew 
import json
import uvicorn
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "../frontend"))
RESUME_PATH = os.path.join(BASE_DIR, "resume.pdf")
QUEUE_PATH = os.path.join(BASE_DIR, "apply_queue.json")

app = FastAPI(title="Job Targeting API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_json(raw_str):
    """Helper to find JSON block even if the model adds chatty text around it."""
    # Find the first { and last }
    match = re.search(r'(\{.*\})', raw_str, re.DOTALL)
    return match.group(1) if match else raw_str

@app.get("/")
async def get_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/css/{file_path:path}")
async def get_css(file_path: str):
    full_path = os.path.join(FRONTEND_DIR, "css", file_path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return FileResponse(full_path)
    return {"error": "CSS file not found"}

@app.get("/js/{file_path:path}")
async def get_js(file_path: str):
    full_path = os.path.join(FRONTEND_DIR, "js", file_path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return FileResponse(full_path, media_type="application/javascript")
    return {"error": "JavaScript file not found"}

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        content = await file.read()
        with open(RESUME_PATH, "wb") as f:
            f.write(content)
        return {"status": "success", "filename": file.filename}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/queue")
async def get_queue():
    try:
        if os.path.exists(QUEUE_PATH):
            with open(QUEUE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"top_matches": []}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/run-pipeline")
def run_pipeline(
    min_match: float = 0.8,
    locations: str = "Remote, Bangalore"
):
    """
    Triggers the agents. Parameters 'min_match' and 'locations' 
    can now be seen in Swagger UI.
    """
    try:
        print(f"Starting Analysis (Min Match: {min_match}, Locs: {locations})")
        from crew import user_policy
        user_policy.min_match_threshold = min_match
        user_policy.preferred_locations = [loc.strip() for loc in locations.split(",")]
        
        result = artifact_crew.kickoff()
        
        # Use the helper to extract only the JSON part
        clean_json = extract_json(result.raw)
        
        # Parse the JSON
        parsed_data = json.loads(clean_json)
        
        # Save output to apply_queue.json
        with open(QUEUE_PATH, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=2)
            
        return {
            "status": "success",
            "data": parsed_data
        }
    except Exception as e:
        print(f"Parsing Error: {str(e)}")
        # Fallback: Return raw text if JSON parsing fails
        return {
            "status": "partial_success",
            "message": f"Error running pipeline: {str(e)}",
            "raw_output": getattr(result, "raw", "") if 'result' in locals() else ""
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)