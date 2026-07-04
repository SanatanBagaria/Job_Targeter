/**
 * Dashboard Module - Renders job listings grid dynamically
 */

export function renderJobs(jobs, { jobsGridEl, emptyStateEl, totalBadgeEl }) {
    jobsGridEl.innerHTML = '';
    
    if (!jobs || jobs.length === 0) {
        emptyStateEl.classList.remove('hidden');
        totalBadgeEl.textContent = '0 Found';
        return;
    }

    emptyStateEl.classList.add('hidden');
    totalBadgeEl.textContent = `${jobs.length} Found`;

    jobs.forEach((job) => {
        const card = document.createElement('div');
        card.className = 'job-card';

        const logoLetter = job.company ? job.company.charAt(0).toUpperCase() : 'J';
        
        // Build missing skills tags
        let skillsHtml = '';
        if (job.missing_skills && job.missing_skills.length > 0) {
            skillsHtml = `
                <div class="skills-list-container">
                    <span>Missing Skills</span>
                    <div class="skills-tags">
                        ${job.missing_skills.map(s => `<span class="skill-tag">${escapeHtml(s)}</span>`).join('')}
                    </div>
                </div>
            `;
        } else {
            skillsHtml = `
                <div class="skills-list-container">
                    <span>Missing Skills</span>
                    <div class="skills-tags">
                        <span class="skill-tag-match">None (Perfect Fit)</span>
                    </div>
                </div>
            `;
        }

        card.innerHTML = `
            <div class="job-card-header">
                <div class="company-logo-styled">${escapeHtml(logoLetter)}</div>
                <div class="score-badge">${job.match_score}% Match</div>
            </div>
            <div class="job-title-group">
                <h4>${escapeHtml(job.title)}</h4>
                <div class="job-company">${escapeHtml(job.company)}</div>
            </div>
            <p class="job-reasoning">${escapeHtml(job.fit_reasoning)}</p>
            ${skillsHtml}
            <div class="apply-button-card">
                <a href="${job.apply_link}" target="_blank" class="btn-card-apply">
                    <span>Apply on Platform</span>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M18 13V19C18 19.5304 17.7893 20.0391 17.4142 20.4142C17.0391 20.7893 16.5304 21 16 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V8C3 7.46957 3.21071 6.96086 3.58579 6.58579C3.96086 6.21071 4.46957 6 5 6H11M21 3M21 3H15M21 3V9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </a>
            </div>
        `;
        jobsGridEl.appendChild(card);
    });
}

function escapeHtml(text) {
    if (!text) return '';
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
