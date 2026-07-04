/**
 * Main module - Coordinates page startup, settings sync, and run flow orchestration
 */
import { initializeUpload } from './upload.js';
import { createProgressTracker } from './progress.js';
import { renderJobs } from './dashboard.js';
import { fetchQueue, runPipeline } from './api.js';

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements - Control Side
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileStatus = document.getElementById('file-status');
    const fileNameDisplay = document.getElementById('file-name');
    const removeFileBtn = document.getElementById('remove-file');
    const minMatchSlider = document.getElementById('min-match');
    const minMatchVal = document.getElementById('min-match-val');
    const locationsInput = document.getElementById('locations');
    const btnRun = document.getElementById('btn-run');
    const pipelineStatus = document.getElementById('pipeline-status');

    // DOM Elements - Dashboard Side
    const jobsGrid = document.getElementById('jobs-grid');
    const emptyState = document.getElementById('empty-state');
    const badgeTotalJobs = document.getElementById('badge-total-jobs');

    // DOM Elements - Loading overlay
    const loadingOverlay = document.getElementById('loading-overlay');
    const progressFill = document.getElementById('progress-fill');

    // Instantiations
    const progress = createProgressTracker({
        overlayEl: loadingOverlay,
        progressFillEl: progressFill,
        stepsIds: ['step-1', 'step-2', 'step-3', 'step-4', 'step-5']
    });

    const upload = initializeUpload({
        dropZoneEl: dropZone,
        fileInputEl: fileInput,
        fileStatusEl: fileStatus,
        fileNameDisplayEl: fileNameDisplay,
        removeFileEl: removeFileBtn,
        btnRunEl: btnRun,
        pipelineStatusEl: pipelineStatus,
        onUploadSuccess: () => {
            console.log('Resume PDF uploaded successfully.');
        },
        onReset: () => {
            console.log('Resume reset.');
        }
    });

    // Sync Slider Value
    minMatchSlider.addEventListener('input', (e) => {
        minMatchVal.textContent = `${e.target.value}%`;
    });

    // Fetch existing queue on load
    loadInitialData();

    async function loadInitialData() {
        try {
            const data = await fetchQueue();
            if (data && data.top_matches && data.top_matches.length > 0) {
                // Pre-enable run button if backend already has resume.pdf cache
                upload.setResumeSuccessState('resume.pdf');
                renderJobs(data.top_matches, {
                    jobsGridEl: jobsGrid,
                    emptyStateEl: emptyState,
                    totalBadgeEl: badgeTotalJobs
                });
            }
        } catch (err) {
            console.warn('Initial queue load skipped or failed:', err);
        }
    }

    // Run pipeline click handler
    btnRun.addEventListener('click', async () => {
        if (!upload.hasResume()) return;

        const minMatch = parseFloat(minMatchSlider.value) / 100.0;
        const locations = locationsInput.value;

        // Visual run triggers
        pipelineStatus.textContent = 'Processing';
        pipelineStatus.className = 'status-processing';
        
        // Starts the dynamic step simulation (rate limit config: default 0 seconds for Gemini)
        progress.show(0);

        try {
            const data = await runPipeline(minMatch, locations);
            if (data.status === 'success') {
                progress.complete();
                setTimeout(() => {
                    pipelineStatus.textContent = 'Ready';
                    pipelineStatus.className = 'status-online';
                    renderJobs(data.data.top_matches, {
                        jobsGridEl: jobsGrid,
                        emptyStateEl: emptyState,
                        totalBadgeEl: badgeTotalJobs
                    });
                }, 1500);
            } else {
                progress.hide();
                pipelineStatus.textContent = 'Ready';
                pipelineStatus.className = 'status-online';
                alert(`Analysis completed with errors: ${data.message || 'Check console logs.'}`);
                if (data.raw_output) {
                    console.log('Raw output from model:', data.raw_output);
                }
            }
        } catch (err) {
            progress.hide();
            pipelineStatus.textContent = 'Ready';
            pipelineStatus.className = 'status-online';
            console.error('Pipeline request failure:', err);
            alert('An error occurred during request execution.');
        }
    });
});
