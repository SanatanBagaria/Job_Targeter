/**
 * Progress Module - Manages step-by-step loading overlays and progress indicators
 */

export function createProgressTracker({
    overlayEl,
    progressFillEl,
    stepsIds = []
}) {
    let progressInterval = null;

    function resetSteps() {
        stepsIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.className = 'step';
        });
    }

    function show(rateLimitDelay = 0) {
        overlayEl.classList.remove('hidden');
        resetSteps();
        
        // Dynamic step configuration based on whether pacing is active
        const stepDuration = rateLimitDelay > 0 ? 68 : 5; // seconds
        const steps = [
            { id: 'step-1', duration: 3, maxPct: 20 },
            { id: 'step-2', duration: stepDuration, maxPct: 40 },
            { id: 'step-3', duration: stepDuration, maxPct: 60 },
            { id: 'step-4', duration: stepDuration + 4, maxPct: 85 }, // analyst has additional API time
            { id: 'step-5', duration: 4, maxPct: 95 }
        ];

        let currentPct = 5;
        let activeStepIdx = 0;

        // Activate step 1
        const step1 = document.getElementById(steps[0].id);
        if (step1) step1.classList.add('active');
        progressFillEl.style.width = `${currentPct}%`;

        let secondsElapsed = 0;
        const totalDuration = steps.reduce((sum, s) => sum + s.duration, 0);

        if (progressInterval) clearInterval(progressInterval);

        progressInterval = setInterval(() => {
            secondsElapsed++;

            // Detect current step
            let accumTime = 0;
            let targetStepIdx = 0;
            for (let i = 0; i < steps.length; i++) {
                accumTime += steps[i].duration;
                if (secondsElapsed <= accumTime) {
                    targetStepIdx = i;
                    break;
                }
                if (i === steps.length - 1) {
                    targetStepIdx = i;
                }
            }

            // Step transition
            if (targetStepIdx !== activeStepIdx) {
                // Complete preceding steps
                for (let i = 0; i < targetStepIdx; i++) {
                    const prevStep = document.getElementById(steps[i].id);
                    if (prevStep) prevStep.className = 'step completed';
                }
                
                // Activate current step
                activeStepIdx = targetStepIdx;
                const currStep = document.getElementById(steps[activeStepIdx].id);
                if (currStep) currStep.className = 'step active';
            }

            // Calculate percentage increment
            const stepConfig = steps[activeStepIdx];
            const prevMax = activeStepIdx > 0 ? steps[activeStepIdx - 1].maxPct : 5;
            const stepProgressFraction = (secondsElapsed - (accumTime - stepConfig.duration)) / stepConfig.duration;
            
            currentPct = prevMax + Math.min(stepProgressFraction, 0.99) * (stepConfig.maxPct - prevMax);
            progressFillEl.style.width = `${currentPct}%`;

        }, 1000);
    }

    function complete() {
        if (progressInterval) clearInterval(progressInterval);
        
        stepsIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.className = 'step completed';
        });
        
        progressFillEl.style.width = '100%';
        
        setTimeout(() => {
            overlayEl.classList.add('hidden');
        }, 1200);
    }

    function hide() {
        if (progressInterval) clearInterval(progressInterval);
        overlayEl.classList.add('hidden');
    }

    return {
        show,
        complete,
        hide
    };
}
