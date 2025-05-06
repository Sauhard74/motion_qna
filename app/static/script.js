// Motion Q&A Frontend Script

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const questionForm = document.getElementById('question-form');
    const analyzeBtn = document.getElementById('analyze-btn');
    const generateHintsBtn = document.getElementById('generate-hints-btn');
    const generateSolutionBtn = document.getElementById('generate-solution-btn');
    const questionInput = document.getElementById('question-input');
    const questionTypeSelect = document.getElementById('question-type');
    const difficultySelect = document.getElementById('difficulty');
    const analysisResult = document.getElementById('analysis-result');
    const hintsResult = document.getElementById('hints-result');
    const solutionResult = document.getElementById('solution-result');
    const apiBaseUrl = '/api/v1';
    
    let currentQuestionId = null;
    
    // Event listeners
    if (questionForm) {
        questionForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await submitQuestion();
        });
    }
    
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            await analyzeQuestion();
        });
    }
    
    if (generateHintsBtn) {
        generateHintsBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            if (currentQuestionId) {
                await generateHints();
            } else {
                showError('Please submit or select a question first');
            }
        });
    }
    
    if (generateSolutionBtn) {
        generateSolutionBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            if (currentQuestionId) {
                await generateSolution();
            } else {
                showError('Please submit or select a question first');
            }
        });
    }

    // Functions
    async function submitQuestion() {
        // Clear previous results
        clearResults();
        
        try {
            const questionContent = questionInput.value.trim();
            if (!questionContent) {
                showError('Please enter a question');
                return;
            }
            
            const questionType = questionTypeSelect.value;
            const difficulty = difficultySelect.value;
            
            // Show loading state
            showLoading('Submitting question...');
            
            // Submit the question
            const response = await fetch(`${apiBaseUrl}/questions/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: questionContent,
                    type: questionType,
                    difficulty: difficulty
                }),
            });
            
            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }
            
            const data = await response.json();
            currentQuestionId = data.id;
            
            // Show success message
            showSuccess('Question submitted successfully!');
            
            // Enable hint and solution buttons
            enableActionButtons();
            
        } catch (error) {
            console.error('Error submitting question:', error);
            showError('Failed to submit question: ' + error.message);
        } finally {
            hideLoading();
        }
    }
    
    async function analyzeQuestion() {
        try {
            const questionContent = questionInput.value.trim();
            if (!questionContent) {
                showError('Please enter a question to analyze');
                return;
            }
            
            // Show loading state
            showLoading('Analyzing question...');
            
            // Send analysis request
            const response = await fetch(`${apiBaseUrl}/questions/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: questionContent,
                    type: questionTypeSelect.value !== 'other' ? questionTypeSelect.value : null,
                    difficulty: difficultySelect.value !== 'medium' ? difficultySelect.value : null
                }),
            });
            
            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Display analysis results
            displayAnalysis(data);
            
        } catch (error) {
            console.error('Error analyzing question:', error);
            showError('Failed to analyze question: ' + error.message);
        } finally {
            hideLoading();
        }
    }
    
    async function generateHints() {
        try {
            if (!currentQuestionId) {
                showError('No question selected');
                return;
            }
            
            // Show loading state
            showLoading('Generating hints...');
            
            // Send hint generation request
            const response = await fetch(`${apiBaseUrl}/questions/${currentQuestionId}/hints`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question_id: currentQuestionId,
                    num_hints: 3, // Default to 3 hints
                    max_level: 3  // Up to level 3 difficulty
                }),
            });
            
            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Display hints
            displayHints(data);
            
        } catch (error) {
            console.error('Error generating hints:', error);
            showError('Failed to generate hints: ' + error.message);
        } finally {
            hideLoading();
        }
    }
    
    async function generateSolution() {
        try {
            if (!currentQuestionId) {
                showError('No question selected');
                return;
            }
            
            // Show loading state
            showLoading('Generating solution...');
            
            // Send solution generation request
            const response = await fetch(`${apiBaseUrl}/questions/${currentQuestionId}/solution`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question_id: currentQuestionId,
                    step_by_step: true
                }),
            });
            
            if (!response.ok) {
                // If solution already exists, try to get it
                if (response.status === 400) {
                    await getSolution();
                    return;
                }
                throw new Error(`Error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Display solution
            displaySolution(data);
            
        } catch (error) {
            console.error('Error generating solution:', error);
            showError('Failed to generate solution: ' + error.message);
        } finally {
            hideLoading();
        }
    }
    
    async function getSolution() {
        try {
            // Get existing solution
            const response = await fetch(`${apiBaseUrl}/questions/${currentQuestionId}/solution`);
            
            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Display solution
            displaySolution(data);
            
        } catch (error) {
            console.error('Error getting solution:', error);
            showError('Failed to get solution: ' + error.message);
        }
    }
    
    // Display functions
    function displayAnalysis(analysis) {
        if (!analysisResult) return;
        
        analysisResult.innerHTML = `
            <div class="card">
                <h3 class="card-title">Question Analysis</h3>
                <div class="analysis-content">
                    <p><strong>Type:</strong> ${analysis.type}</p>
                    <p><strong>Difficulty Score:</strong> ${analysis.difficulty_score.toFixed(2)}</p>
                    <p><strong>Word Count:</strong> ${analysis.word_count}</p>
                    <p><strong>Sentence Count:</strong> ${analysis.sentence_count}</p>
                    <p><strong>Keywords:</strong> ${analysis.keywords.join(', ')}</p>
                </div>
            </div>
        `;
        
        // Update select boxes based on analysis
        if (questionTypeSelect && analysis.type) {
            questionTypeSelect.value = analysis.type;
        }
    }
    
    function displayHints(hints) {
        if (!hintsResult) return;
        
        if (!hints || hints.length === 0) {
            hintsResult.innerHTML = '<div class="card"><p>No hints available.</p></div>';
            return;
        }
        
        const hintsHtml = hints.map(hint => {
            return `
                <div class="hint">
                    <h4>Hint Level ${hint.level}</h4>
                    <p>${hint.content}</p>
                </div>
            `;
        }).join('');
        
        hintsResult.innerHTML = `
            <div class="card">
                <h3 class="card-title">Hints</h3>
                ${hintsHtml}
            </div>
        `;
    }
    
    function displaySolution(solution) {
        if (!solutionResult) return;
        
        let stepsHtml = '';
        if (solution.steps) {
            const steps = solution.steps.split('\n');
            stepsHtml = `
                <div class="steps">
                    <h4>Step-by-Step Solution</h4>
                    ${steps.map(step => `<div class="step">${step}</div>`).join('')}
                </div>
            `;
        }
        
        solutionResult.innerHTML = `
            <div class="card">
                <h3 class="card-title">Solution</h3>
                <div class="solution">
                    <p>${solution.content}</p>
                </div>
                ${stepsHtml}
            </div>
        `;
    }
    
    // Utility functions
    function clearResults() {
        if (analysisResult) analysisResult.innerHTML = '';
        if (hintsResult) hintsResult.innerHTML = '';
        if (solutionResult) solutionResult.innerHTML = '';
    }
    
    function showLoading(message = 'Loading...') {
        // Implementation depends on UI design
        const loadingMessage = document.getElementById('loading-message');
        if (loadingMessage) {
            loadingMessage.textContent = message;
            loadingMessage.style.display = 'block';
        }
    }
    
    function hideLoading() {
        const loadingMessage = document.getElementById('loading-message');
        if (loadingMessage) {
            loadingMessage.style.display = 'none';
        }
    }
    
    function showError(message) {
        const errorMessage = document.getElementById('error-message');
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 5000);
        }
    }
    
    function showSuccess(message) {
        const successMessage = document.getElementById('success-message');
        if (successMessage) {
            successMessage.textContent = message;
            successMessage.style.display = 'block';
            setTimeout(() => {
                successMessage.style.display = 'none';
            }, 3000);
        }
    }
    
    function enableActionButtons() {
        if (generateHintsBtn) generateHintsBtn.disabled = false;
        if (generateSolutionBtn) generateSolutionBtn.disabled = false;
    }
}); 