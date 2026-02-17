// frontend/static/js/training.js
if (!checkAuth()) {
    throw new Error('Not authenticated');
}

let questions = [];
let currentQuestionIndex = 0;
let correctAnswers = 0;
let totalPointsEarned = 0;

async function loadQuestions(difficulty) {
    try {
        const response = await API.get(`/training/questions?difficulty=${difficulty}&count=5`);
        questions = response.questions;
        
        if (questions.length === 0) {
            alert('No questions available for this difficulty');
            return;
        }
        
        currentQuestionIndex = 0;
        correctAnswers = 0;
        totalPointsEarned = 0;
        
        document.querySelector('.difficulty-selector').style.display = 'none';
        document.getElementById('questionContainer').style.display = 'block';
        document.getElementById('totalQuestions').textContent = questions.length;
        
        displayQuestion();
    } catch (error) {
        alert('Error loading questions: ' + error.message);
    }
}

function displayQuestion() {
    const question = questions[currentQuestionIndex];
    
    document.getElementById('currentQuestion').textContent = currentQuestionIndex + 1;
    document.getElementById('questionText').textContent = question.question_text;
    
    const optionsContainer = document.getElementById('optionsContainer');
    const feedback = document.getElementById('feedback');
    feedback.innerHTML = '';
    
    if (question.question_type === 'mcq') {
        optionsContainer.innerHTML = `
            <button class="option-btn" onclick="selectAnswer('A')">${question.option_a}</button>
            <button class="option-btn" onclick="selectAnswer('B')">${question.option_b}</button>
            <button class="option-btn" onclick="selectAnswer('C')">${question.option_c}</button>
            <button class="option-btn" onclick="selectAnswer('D')">${question.option_d}</button>
        `;
    } else {
        optionsContainer.innerHTML = `
            <textarea id="speakingAnswer" placeholder="Type your answer here..." rows="5"></textarea>
            <button class="btn btn-primary" onclick="submitSpeakingAnswer()">Submit Answer</button>
        `;
    }
    
    updateProgress();
}

function updateProgress() {
    const progress = ((currentQuestionIndex) / questions.length) * 100;
    document.getElementById('progressFill').style.width = progress + '%';
}

async function selectAnswer(answer) {
    const question = questions[currentQuestionIndex];
    
    try {
        const response = await API.post('/training/submit-answer', {
            question_id: question.id,
            answer: answer
        });
        
        if (response.is_correct) {
            correctAnswers++;
            totalPointsEarned += response.points_earned;
            showFeedback(true, response.points_earned);
        } else {
            showFeedback(false, 0);
        }
        
        document.getElementById('pointsDisplay').textContent = response.total_points;
        
        // Disable all option buttons
        document.querySelectorAll('.option-btn').forEach(btn => {
            btn.disabled = true;
        });
        
        document.getElementById('nextBtn').style.display = 'block';
    } catch (error) {
        alert('Error submitting answer: ' + error.message);
    }
}

async function submitSpeakingAnswer() {
    const answer = document.getElementById('speakingAnswer').value.trim();
    
    if (!answer) {
        alert('Please type your answer');
        return;
    }
    
    await selectAnswer(answer);
}

function showFeedback(isCorrect, points) {
    const feedback = document.getElementById('feedback');
    
    if (isCorrect) {
        feedback.innerHTML = `
            <div class="feedback-correct">
                ✅ Correct! You earned ${points} points!
            </div>
        `;
    } else {
        feedback.innerHTML = `
            <div class="feedback-incorrect">
                ❌ Incorrect. Try the next question!
            </div>
        `;
    }
}

function nextQuestion() {
    currentQuestionIndex++;
    
    if (currentQuestionIndex >= questions.length) {
        showResults();
    } else {
        document.getElementById('nextBtn').style.display = 'none';
        displayQuestion();
    }
}

function showResults() {
    document.getElementById('questionContainer').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'block';
    
    document.getElementById('correctCount').textContent = correctAnswers;
    document.getElementById('pointsEarned').textContent = totalPointsEarned;
    
    const profile = JSON.parse(localStorage.getItem('profile'));
    document.getElementById('totalPoints').textContent = profile.points_balance + totalPointsEarned;
}

// Load initial points
async function loadPoints() {
    try {
        const balance = await API.get('/points/balance');
        document.getElementById('pointsDisplay').textContent = balance.points_balance;
    } catch (error) {
        console.error('Error loading points:', error);
    }
}

loadPoints();


 