/**
 * Upload Module - Handles Drag & Drop PDF upload UI interactions and API submission
 */
import { uploadResume } from './api.js';

export function initializeUpload({
    dropZoneEl,
    fileInputEl,
    fileStatusEl,
    fileNameDisplayEl,
    removeFileEl,
    btnRunEl,
    pipelineStatusEl,
    onUploadSuccess,
    onReset
}) {
    let hasUploadedResume = false;

    // Drag and Drop highlighting
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZoneEl.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZoneEl.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZoneEl.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZoneEl.classList.remove('dragover');
        }, false);
    });

    // File Drop & Selection
    dropZoneEl.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    dropZoneEl.addEventListener('click', () => {
        fileInputEl.click();
    });

    fileInputEl.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    removeFileEl.addEventListener('click', (e) => {
        e.stopPropagation();
        resetUpload();
    });

    async function handleFileUpload(file) {
        if (file.type !== 'application/pdf') {
            alert('Please upload a valid PDF resume file.');
            return;
        }

        // Show uploading visual state
        fileNameDisplayEl.textContent = 'Uploading...';
        fileStatusEl.classList.remove('hidden');

        try {
            const data = await uploadResume(file);
            if (data.status === 'success') {
                hasUploadedResume = true;
                fileNameDisplayEl.textContent = file.name;
                btnRunEl.disabled = false;
                pipelineStatusEl.textContent = 'Ready';
                pipelineStatusEl.className = 'status-online';
                if (onUploadSuccess) onUploadSuccess();
            } else {
                alert(`Upload failed: ${data.message}`);
                resetUpload();
            }
        } catch (err) {
            console.error('File Upload Error:', err);
            alert('Network error uploading file.');
            resetUpload();
        }
    }

    function resetUpload() {
        hasUploadedResume = false;
        fileInputEl.value = '';
        fileStatusEl.classList.add('hidden');
        btnRunEl.disabled = true;
        pipelineStatusEl.textContent = 'Offline';
        pipelineStatusEl.className = 'status-offline';
        if (onReset) onReset();
    }

    return {
        hasResume: () => hasUploadedResume,
        setResumeSuccessState: (name) => {
            hasUploadedResume = true;
            fileNameDisplayEl.textContent = name;
            btnRunEl.disabled = false;
            pipelineStatusEl.textContent = 'Ready';
            pipelineStatusEl.className = 'status-online';
            fileStatusEl.classList.remove('hidden');
        },
        reset: resetUpload
    };
}
