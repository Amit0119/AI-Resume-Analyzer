/**
 * AI Resume Analyzer - Frontend Application
 * Professional resume analysis with AI-powered skill matching
 * Version: 2.0
 */

// ===== CONFIGURATION =====
const API_BASE_URL = 'http://localhost:8000/api';
const MAX_FILES = 10;  // Maximum 10 files allowed
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB
const MIN_JOB_DESC_LENGTH = 10;

// ===== STATE MANAGEMENT =====
let uploadedFilesArray = [];
let barChartInstance = null;
let radarChartInstance = null;
let currentAnalysisData = null;
let skillWeights = {};        // { "Python": 3.0, "React": 1.0 }
let isStrictMode = false;     // strict vs flexible matching

// ===== DOM ELEMENTS =====
const dropZoneElement = document.getElementById('dropZone');
const fileInputElement = document.getElementById('fileInput');
const analyzeButton = document.getElementById('analyzeBtn');
const jobDescriptionInput = document.getElementById('jobDescription');
const sensitivitySlider = document.getElementById('sensitivitySlider');
const sensitivityValueDisplay = document.getElementById('sensitivityValue');
const resultsSection = document.getElementById('resultsSection');
const loadingSpinner = document.getElementById('loadingSpinner');
const loadingText = document.getElementById('loadingText');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const fileStatusContainer = document.getElementById('fileStatusContainer');
const fileStatusText = document.getElementById('fileStatus');
const fileInfoText = document.getElementById('fileInfo');

// ===== EVENT LISTENERS =====

/**
 * Update sensitivity display value
 */
sensitivitySlider.addEventListener('input', function(event) {
    let currentValue = event.target.value;
    sensitivityValueDisplay.textContent = parseFloat(currentValue).toFixed(2);
});

/**
 * Open file picker when drop zone is clicked
 */
dropZoneElement.addEventListener('click', function() {
    fileInputElement.click();
});

/**
 * Handle drag and drop
 */
dropZoneElement.addEventListener('dragover', function(event) {
    event.preventDefault();
    dropZoneElement.classList.add('drag-active');
});

dropZoneElement.addEventListener('dragleave', function(event) {
    event.preventDefault();
    dropZoneElement.classList.remove('drag-active');
});

dropZoneElement.addEventListener('drop', function(event) {
    event.preventDefault();
    dropZoneElement.classList.remove('drag-active');
    
    const droppedFiles = event.dataTransfer.files;
    handleFileSelection(droppedFiles);
});

/**
 * Handle file input change
 */
fileInputElement.addEventListener('change', function(event) {
    handleFileSelection(event.target.files);
});

/**
 * Handle analyze button click
 */
analyzeButton.addEventListener('click', async function() {
    await performAnalysis();
});

/**
 * Enable/disable analyze button based on input validation
 */
jobDescriptionInput.addEventListener('input', validateInputs);
fileInputElement.addEventListener('change', validateInputs);

// ===== SETTINGS FUNCTIONS =====

/**
 * Update match mode (strict vs flexible) and help text
 */
function updateMatchMode(radio) {
    isStrictMode = radio.value === 'strict';
    const helpText = document.getElementById('matchModeHelpText');
    if (helpText) {
        helpText.textContent = isStrictMode
            ? 'Strict: only exact keyword matches count'
            : 'Flexible: finds related skills (e.g. Kotlin ≈ Java)';
    }
}

/**
 * Toggle API key visibility
 */
function toggleApiKeyVisibility() {
    const input = document.getElementById('apiKeyInput');
    const icon = document.getElementById('eyeIcon');
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

/**
 * Render skill weight sliders whenever job description changes
 */
function renderWeightSliders() {
    const text = jobDescriptionInput.value.trim();
    const skills = text.split('\n').map(s => s.trim()).filter(s => s.length > 0);
    
    const container = document.getElementById('skillWeightSliders');
    const section = document.getElementById('weightingSection');
    
    if (!container || !section) return;
    
    if (skills.length === 0) {
        section.style.display = 'none';
        skillWeights = {};
        return;
    }
    
    section.style.display = 'block';
    
    // Keep existing weights; add defaults for new skills
    const newWeights = {};
    skills.forEach(skill => {
        newWeights[skill] = skillWeights[skill] || 1.0;
    });
    skillWeights = newWeights;
    
    container.innerHTML = skills.map(skill => `
        <div class="weight-row">
            <span class="weight-skill-name" title="${skill}">${skill}</span>
            <input 
                type="range" 
                min="1" max="5" step="0.5" 
                value="${skillWeights[skill] || 1.0}"
                oninput="updateWeight('${skill.replace(/'/g, "\\'")}', this.value)"
            >
            <span class="weight-value-badge" id="wb_${skill.replace(/\s+/g,'_')}">${parseFloat(skillWeights[skill] || 1.0).toFixed(1)}x</span>
        </div>
    `).join('');
}

/**
 * Update weight for a specific skill
 */
function updateWeight(skill, value) {
    skillWeights[skill] = parseFloat(value);
    const badge = document.getElementById('wb_' + skill.replace(/\s+/g, '_'));
    if (badge) badge.textContent = parseFloat(value).toFixed(1) + 'x';
}

// ===== FILE HANDLING =====

/**
 * Process selected files
 */
function handleFileSelection(files) {
    console.log(`Processing ${files.length} file(s)...`);
    
    uploadedFilesArray = [];
    const invalidFiles = [];
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Validate file type
        if (file.type !== 'application/pdf') {
            invalidFiles.push({
                name: file.name,
                reason: 'Invalid format (PDF required)'
            });
            continue;
        }
        
        // Validate file size
        if (file.size > MAX_FILE_SIZE) {
            invalidFiles.push({
                name: file.name,
                reason: `File too large (${(file.size / 1024 / 1024).toFixed(1)}MB > 10MB)`
            });
            continue;
        }
        
        // File is valid
        uploadedFilesArray.push(file);
    }
    
    // Update UI
    updateFileStatusDisplay();
    
    // Show errors if any
    if (invalidFiles.length > 0) {
        const errorMsg = invalidFiles
            .map(f => `• ${f.name}: ${f.reason}`)
            .join('\n');
        showErrorMessage(`Some files were rejected:\n${errorMsg}`);
    }
    
    // Validate and enable/disable button
    validateInputs();
}

/**
 * Update file status display
 */
function updateFileStatusDisplay() {
    if (uploadedFilesArray.length > 0) {
        fileStatusContainer.style.display = 'block';
        
        const totalSize = uploadedFilesArray.reduce((sum, f) => sum + f.size, 0);
        const sizeMB = (totalSize / 1024 / 1024).toFixed(2);
        
        fileStatusText.textContent = `✅ ${uploadedFilesArray.length} resume(s) selected`;
        fileInfoText.textContent = `Total size: ${sizeMB}MB`;
        
        console.log(`Files selected: ${uploadedFilesArray.length}, Size: ${sizeMB}MB`);
    } else {
        fileStatusContainer.style.display = 'none';
    }
}

// ===== VALIDATION =====

/**
 * Validate all inputs
 */
function validateInputs() {
    const hasFiles = uploadedFilesArray.length > 0;
    const hasJobDescription = jobDescriptionInput.value.trim().length >= MIN_JOB_DESC_LENGTH;
    
    analyzeButton.disabled = !(hasFiles && hasJobDescription);
}

/**
 * Validate analysis parameters before submission
 */
function validateAnalysisParameters() {
    // Check files
    if (uploadedFilesArray.length === 0) {
        return {
            valid: false,
            error: 'Please upload at least one PDF resume'
        };
    }
    
    if (uploadedFilesArray.length > MAX_FILES) {
        return {
            valid: false,
            error: `Maximum ${MAX_FILES} files allowed`
        };
    }
    
    // Check job description
    const jobDesc = jobDescriptionInput.value.trim();
    if (jobDesc.length === 0) {
        return {
            valid: false,
            error: 'Please enter required skills/job description'
        };
    }
    
    if (jobDesc.length < MIN_JOB_DESC_LENGTH) {
        return {
            valid: false,
            error: 'Job description must be at least 10 characters long'
        };
    }
    
    // Check sensitivity
    const sensitivity = parseFloat(sensitivitySlider.value);
    if (isNaN(sensitivity) || sensitivity < 0.3 || sensitivity > 0.9) {
        return {
            valid: false,
            error: 'Invalid sensitivity value'
        };
    }
    
    return { valid: true };
}

// ===== ANALYSIS EXECUTION =====

/**
 * Perform resume analysis
 */
async function performAnalysis() {
    console.log('Starting analysis...');
    
    // Validate inputs
    const validation = validateAnalysisParameters();
    if (!validation.valid) {
        showErrorMessage(validation.error);
        return;
    }
    
    // Hide previous results and clear messages
    resultsSection.style.display = 'none';
    errorMessage.style.display = 'none';
    
    // Show loading state
    loadingSpinner.style.display = 'block';
    loadingText.textContent = `Analyzing ${uploadedFilesArray.length} resume(s)...`;
    analyzeButton.disabled = true;
    
    try {
        // Prepare form data
        const formData = new FormData();
        
        // Add files
        for (let i = 0; i < uploadedFilesArray.length; i++) {
            formData.append('files', uploadedFilesArray[i]);
        }
        
        // Add job description and sensitivity
        formData.append('job_description', jobDescriptionInput.value.trim());
        formData.append('sensitivity', sensitivitySlider.value);
        
        // Add new settings
        formData.append('skill_weights', JSON.stringify(skillWeights));
        formData.append('strict_mode', isStrictMode ? 'true' : 'false');
        
        const apiKey = document.getElementById('apiKeyInput')?.value?.trim() || '';
        if (apiKey) formData.append('groq_api_key', apiKey);
        
        console.log('Sending request to API...');
        
        // Send to backend
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        });
        
        // Handle response
        const responseData = await response.json();
        
        if (!response.ok) {
            const errorMsg = responseData.detail || 'Analysis failed. Please try again.';
            throw new Error(errorMsg);
        }
        
        console.log('Analysis successful!', responseData);
        
        // Display results
        currentAnalysisData = responseData;
        displayResultsOnDashboard(responseData);
        
    } catch (error) {
        console.error('Error during analysis:', error);
        
        // Determine error message
        let errorMsg = 'Analysis failed. ';
        if (error.message.includes('Failed to fetch')) {
            errorMsg += 'Could not connect to server. Make sure the backend is running on localhost:8000';
        } else if (error.message) {
            errorMsg += error.message;
        } else {
            errorMsg += 'An unexpected error occurred.';
        }
        
        showErrorMessage(errorMsg);
        
    } finally {
        loadingSpinner.style.display = 'none';
        analyzeButton.disabled = false;
    }
}

// ===== RESULTS DISPLAY =====

/**
 * Display analysis results on dashboard
 */
function displayResultsOnDashboard(data) {
    try {
        const candidates = data.candidates || [];
        const statistics = data.statistics || {};
        
        // Sort candidates by matched count (descending)
        candidates.sort((a, b) => b.matched_count - a.matched_count);
        
        if (candidates.length === 0) {
            showErrorMessage('No candidates to display');
            return;
        }
        
        const bestCandidate = candidates[0];
        
        // Update stat cards
        document.getElementById('totalAnalyzed').textContent = candidates.length;
        document.getElementById('bestScore').textContent = `${bestCandidate.matched_count}/15`;
        document.getElementById('bestName').textContent = bestCandidate.name;
        
        const avgPercentage = Math.round((statistics.average_score || 0) * 100);
        document.getElementById('avgScore').textContent = `${avgPercentage}%`;
        
        document.getElementById('topSkill').textContent = statistics.most_matched_skill || 'N/A';
        
        // Update best candidate banner
        const bestMatchPercentage = Math.round(bestCandidate.match_percentage || 0);
        document.getElementById('bestCandidateTitle').textContent = 
            `🏆 ${bestCandidate.name}`;
        document.getElementById('bestCandidateSubtitle').textContent = 
            `${bestCandidate.matched_count}/15 skills matched | ${bestMatchPercentage}% match score`;
        
        // Create charts
        createBarChart(candidates);
        createRadarChart(candidates);
        createSkillsTable(candidates);
        
        // Show results section
        resultsSection.style.display = 'block';
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        
        console.log('Results displayed successfully');
        
    } catch (error) {
        console.error('Error displaying results:', error);
        showErrorMessage('Error displaying results: ' + error.message);
    }
}

/**
 * Create candidate comparison bar chart
 */
function createBarChart(candidates) {
    try {
        const ctx = document.getElementById('barChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (barChartInstance) {
            barChartInstance.destroy();
        }
        
        // Prepare data
        const names = candidates.map(c => c.name);
        const percentages = candidates.map(c => Math.round(c.match_percentage || 0));
        
        // Create chart
        barChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: names,
                datasets: [{
                    label: 'Match Percentage',
                    data: percentages,
                    backgroundColor: [
                        '#8b5cf6',
                        '#6366f1',
                        '#3b82f6',
                        '#06b6d4',
                        '#10b981',
                        '#f59e0b'
                    ],
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(155, 155, 155, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
        
        console.log('Bar chart created');
    } catch (error) {
        console.error('Error creating bar chart:', error);
    }
}

/**
 * Create skills radar chart
 */
function createRadarChart(candidates) {
    try {
        const ctx = document.getElementById('radarChart').getContext('2d');
        
        if (radarChartInstance) {
            radarChartInstance.destroy();
        }
        
        // Get all unique skills
        const allSkills = new Set();
        if (candidates.length > 0) {
            const firstCandidate = candidates[0];
            (firstCandidate.matched_skills || []).forEach(s => allSkills.add(s));
            (firstCandidate.missing_skills || []).forEach(s => allSkills.add(s));
        }
        
        const skillLabels = Array.from(allSkills);
        
        // Prepare datasets
        const colors = ['#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899'];
        const datasets = candidates.map((candidate, idx) => {
            const skillData = skillLabels.map(skill => 
                (candidate.matched_skills || []).includes(skill) ? 100 : 0
            );
            
            return {
                label: candidate.name,
                data: skillData,
                borderColor: colors[idx % colors.length],
                backgroundColor: `${colors[idx % colors.length]}25`,
                borderWidth: 2.5,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointBackgroundColor: colors[idx % colors.length],
                pointBorderWidth: 2,
                pointBorderColor: '#fff'
            };
        });
        
        radarChartInstance = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: skillLabels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                devicePixelRatio: 2,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            display: true,
                            color: '#9ca3af',
                            font: { size: 11 }
                        },
                        angleLines: {
                            color: 'rgba(155, 155, 155, 0.2)',
                            lineWidth: 1
                        },
                        grid: {
                            color: 'rgba(155, 155, 155, 0.2)',
                            lineWidth: 1
                        },
                        pointLabels: {
                            color: '#9ca3af',
                            font: { size: 12, weight: '500' },
                            padding: 15
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: { size: 12, weight: '500' }
                        }
                    },
                    filler: {
                        propagate: true
                    }
                }
            }
        });
        
        console.log('Radar chart created');
    } catch (error) {
        console.error('Error creating radar chart:', error);
    }
}

/**
 * Create skills comparison table with expandable candidate details
 */
function createSkillsTable(candidates) {
    try {
        const tableHead = document.getElementById('tableHead');
        const tableBody = document.getElementById('tableBody');
        
        tableHead.innerHTML = '';
        tableBody.innerHTML = '';
        
        // Get all unique skills
        const allSkills = new Set();
        if (candidates.length > 0) {
            const firstCandidate = candidates[0];
            (firstCandidate.matched_skills || []).forEach(s => allSkills.add(s));
            (firstCandidate.missing_skills || []).forEach(s => allSkills.add(s));
        }
        
        const skillLabels = Array.from(allSkills);
        
        // Create header
        const headerRow = document.createElement('tr');
        const skillHeader = document.createElement('th');
        skillHeader.textContent = 'Skill';
        headerRow.appendChild(skillHeader);
        
        candidates.forEach(candidate => {
            const th = document.createElement('th');
            th.innerHTML = `<div style="cursor: pointer; display: flex; align-items: center; gap: 8px;"><span>${candidate.name}</span><i class="fas fa-chevron-down" style="font-size: 12px;"></i></div>`;
            headerRow.appendChild(th);
        });
        
        tableHead.appendChild(headerRow);
        
        // Create data rows
        skillLabels.forEach(skill => {
            const row = document.createElement('tr');
            
            const skillCell = document.createElement('td');
            skillCell.textContent = skill;
            skillCell.className = 'skill-name';
            row.appendChild(skillCell);
            
            candidates.forEach(candidate => {
                const cell = document.createElement('td');
                
                if ((candidate.matched_skills || []).includes(skill)) {
                    cell.innerHTML = '<span class="skill-matched"><i class="fas fa-check"></i> Matched</span>';
                } else {
                    cell.innerHTML = '<span class="skill-missing"><i class="fas fa-times"></i> Missing</span>';
                }
                
                row.appendChild(cell);
            });
            
            tableBody.appendChild(row);
        });
        
        // Add expandable candidate detail rows
        candidates.forEach((candidate, idx) => {
            const detailRow = document.createElement('tr');
            detailRow.className = 'candidate-detail-row';
            detailRow.style.display = 'none';
            
            const detailCell = document.createElement('td');
            detailCell.colSpan = candidates.length + 1;
            detailCell.className = 'candidate-detail-cell';
            
            const detailContent = document.createElement('div');
            detailContent.className = 'candidate-detail-content';
            detailContent.innerHTML = `
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px;">
                    <div>
                        <h4 style="color: #8b5cf6; margin-bottom: 15px; font-size: 16px;">📊 ${candidate.name} - Details</h4>
                        <div style="background: rgba(139, 92, 246, 0.1); padding: 15px; border-radius: 8px;">
                            <p style="margin: 8px 0;"><strong>Match Score:</strong> ${candidate.match_percentage.toFixed(1)}%</p>
                            <p style="margin: 8px 0;"><strong>Skills Matched:</strong> ${candidate.matched_count}/15</p>
                            <p style="margin: 8px 0;"><strong>Skills Missing:</strong> ${candidate.missing_count}/15</p>
                            ${candidate.weighted_score != null ? `<p style="margin: 8px 0;"><strong>Weighted Score:</strong> <span class="weighted-badge">⚖️ ${candidate.weighted_score.toFixed(1)}%</span></p>` : ''}
                        </div>
                        
                        <h4 style="color: #10b981; margin-top: 15px; margin-bottom: 10px; font-size: 14px;">✅ Matched Skills (${candidate.matched_skills.length})</h4>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px;">
                            ${candidate.matched_skills.map(s => `<span style="background: rgba(16, 185, 129, 0.2); color: #10b981; padding: 4px 10px; border-radius: 4px; font-size: 12px;">🔑 ${s}</span>`).join('')}
                        </div>
                        
                        <h4 style="color: #ef4444; margin-bottom: 10px; font-size: 14px;">❌ Missing Skills (${candidate.missing_skills.length})</h4>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                            ${candidate.missing_skills.map(s => `<span style="background: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 4px 10px; border-radius: 4px; font-size: 12px;">✗ ${s}</span>`).join('')}
                        </div>
                    </div>
                    
                    <div>
                        <h4 style="color: #8b5cf6; margin-bottom: 15px; font-size: 16px;">💡 Recommendations</h4>
                        ${candidate.suggestions && candidate.suggestions.length > 0 ? `
                            <div style="display: flex; flex-direction: column; gap: 10px;">
                                ${candidate.suggestions.slice(0, 5).map((s, i) => `
                                    <div style="background: rgba(139, 92, 246, 0.1); padding: 10px; border-radius: 6px; border-left: 3px solid #8b5cf6;">
                                        <p style="margin: 0; font-size: 13px; color: #fafafa;">${i + 1}. ${s}</p>
                                    </div>
                                `).join('')}
                            </div>
                        ` : '<p style="color: #9ca3af;">No specific recommendations at this time.</p>'}
                    </div>
                </div>
            `;
            
            detailCell.appendChild(detailContent);
            detailRow.appendChild(detailCell);
            tableBody.appendChild(detailRow);
            
            // Add click handler to candidate header
            const candidateHeader = headerRow.querySelectorAll('th')[idx + 1];
            candidateHeader.style.cursor = 'pointer';
            candidateHeader.addEventListener('click', function() {
                const isVisible = detailRow.style.display !== 'none';
                detailRow.style.display = isVisible ? 'none' : 'table-row';
                
                // Toggle chevron icon
                const icon = this.querySelector('i');
                if (icon) {
                    icon.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(180deg)';
                    icon.style.transition = 'transform 0.3s ease';
                }
            });
        });
        
        console.log('Skills table with dropdowns created');
    } catch (error) {
        console.error('Error creating table:', error);
    }
}

// ===== ERROR HANDLING =====

/**
 * Show error message
 */
function showErrorMessage(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'block';
    console.error('Error:', message);
    
    // Auto-hide after 8 seconds
    setTimeout(() => {
        if (errorMessage.style.display !== 'none') {
            closeError();
        }
    }, 8000);
}

/**
 * Close error message
 */
function closeError() {
    errorMessage.style.display = 'none';
}

// ===== INITIALIZATION =====

console.log('AI Resume Analyzer v2.0 loaded');
validateInputs();

// ===== EXPORT FUNCTIONS =====

/**
 * Export analysis results as CSV
 */
function exportCSV() {
    if (!currentAnalysisData) return;
    
    const candidates = currentAnalysisData.candidates || [];
    const rows = [
        ['Name', 'Match %', 'Weighted Score %', 'Matched Count', 'Missing Count', 'Matched Skills', 'Missing Skills']
    ];
    
    candidates.forEach(c => {
        rows.push([
            c.name,
            c.match_percentage.toFixed(2),
            c.weighted_score != null ? c.weighted_score.toFixed(2) : 'N/A',
            c.matched_count,
            c.missing_count,
            (c.matched_skills || []).join(' | '),
            (c.missing_skills || []).join(' | ')
        ]);
    });
    
    const csvContent = rows.map(row =>
        row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')
    ).join('\r\n');
    
    downloadFile('resume-analysis.csv', csvContent, 'text/csv');
}

/**
 * Export analysis results as JSON
 */
function exportJSON() {
    if (!currentAnalysisData) return;
    const json = JSON.stringify(currentAnalysisData, null, 2);
    downloadFile('resume-analysis.json', json, 'application/json');
}

/**
 * Print / Save as PDF via browser dialog
 */
function exportPDF() {
    window.print();
}

/**
 * Helper: trigger file download
 */
function downloadFile(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
        URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }, 100);
}
