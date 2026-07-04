/**
 * API Fetch Client for Job Targeter Backend API
 */

export async function uploadResume(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/upload-resume', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error(`Upload server responded with code ${response.status}`);
    }
    
    return await response.json();
}

export async function fetchQueue() {
    const response = await fetch('/queue');
    if (!response.ok) {
        throw new Error(`Queue fetch failed with code ${response.status}`);
    }
    return await response.json();
}

export async function runPipeline(minMatch, locations) {
    const response = await fetch(`/run-pipeline?min_match=${minMatch}&locations=${encodeURIComponent(locations)}`);
    if (!response.ok) {
        throw new Error(`Pipeline execution failed with code ${response.status}`);
    }
    return await response.json();
}
