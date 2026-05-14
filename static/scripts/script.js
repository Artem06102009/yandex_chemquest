const startButton = document.getElementById('startButton');
    const themeSelect = document.getElementById('themeSelect');
    const timerDiv = document.getElementById('timerDiv');
    const timeElement = document.getElementById('time');
    const gameScreen = document.getElementById('gameScreen');
    const questionText = document.getElementById('questionText');
    const optionsContainer = document.getElementById('optionsContainer');
    const answerButton = document.getElementById('answerButton');
    const currentQuestionNum = document.getElementById('currentQuestionNum');
    const totalQuestions = document.getElementById('totalQuestions');
    const resultText = document.getElementById('resultText');
    const restartButton = document.getElementById('restartButton');
    const welcomeScreen = document.getElementById('welcomeScreen');
    const resultsScreen = document.getElementById('resultsScreen');
    const tabButtons = document.querySelectorAll('.tab-button');


let currentMode = 'time';
let currentQuestions = [];
let currentQuestionIndex = 0;
let score = 0;
let timer = null;
let timeLeft = 60;
let selectedOption = null;
let totalQuestionsCount = 20;
let isAnswered = false;

document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('startButton');
    if (startButton) {
        startButton.addEventListener('click', startGame);
    }

    const restartButton = document.getElementById('restartButton');
    if (restartButton) {
        restartButton.addEventListener('click', restartGame);
    }

    const tabButtons = document.querySelectorAll('.tab-button');
    if (tabButtons.length) {
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                tabButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                currentMode = button.dataset.mode;
            });
        });
    }

    const answerBtn = document.getElementById('answerButton');
    if (answerBtn) {
        answerBtn.addEventListener('click', handleAnswer);
    }
});

function startGame() {
    const themeSelect = document.getElementById('themeSelect');
    if (!themeSelect) return;

    const theme = themeSelect.value;
    currentQuestions = [...quizData[theme]];
    shuffleArray(currentQuestions);

    if (currentMode === 'count') {
        totalQuestionsCount = Math.min(20, currentQuestions.length);
    } else {
        totalQuestionsCount = currentQuestions.length;
    }

    document.getElementById('totalQuestions').textContent = totalQuestionsCount;
    currentQuestionIndex = 0;
    score = 0;
    timeLeft = 60;
    selectedOption = null;
    isAnswered = false;

    document.getElementById('welcomeScreen').classList.add('hidden');
    document.getElementById('gameScreen').classList.remove('hidden');
    document.getElementById('resultsScreen').classList.add('hidden');

    if (currentMode === 'time') {
        document.getElementById('timerDiv').classList.remove('hidden');
        updateTimerDisplay();
        if (timer) clearInterval(timer);
        timer = setInterval(updateTimer, 1000);
    } else {
        document.getElementById('timerDiv').classList.add('hidden');
    }

    showQuestion();
}


function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}


function updateTimerDisplay() {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    const timeElement = document.getElementById('time');
    if (timeElement) {
        timeElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

function updateTimer() {
    timeLeft--;
    updateTimerDisplay();

    if (timeLeft < 0) {
        if (timer) clearInterval(timer);
        endGame();
    }
}

function showQuestion() {
    if (currentQuestionIndex >= totalQuestionsCount || currentQuestionIndex >= currentQuestions.length) {
        endGame();
        return;
    }
    const currentQuestion = currentQuestions[currentQuestionIndex];
    const questionText = document.getElementById('questionText');
    if (questionText) questionText.textContent = currentQuestion.question;
    const currentQuestionNum = document.getElementById('currentQuestionNum');
    if (currentQuestionNum) currentQuestionNum.textContent = currentQuestionIndex + 1;

    const optionsContainer = document.getElementById('optionsContainer');
    if (!optionsContainer) return;

    optionsContainer.innerHTML = '';
    const shuffledOptions = shuffleArray([...currentQuestion.options]);

    shuffledOptions.forEach((option) => {
        const radioDiv = document.createElement('label');
        radioDiv.className = 'radio';

        const input = document.createElement('input');
        input.type = 'radio';
        input.name = 'answer';
        input.value = option;

        input.addEventListener('change', () => {
            selectedOption = option;
            const answerButton = document.getElementById('answerButton');
            if (answerButton) answerButton.disabled = false;

            document.querySelectorAll('.radio').forEach(el => {
                el.classList.remove('selected');
            });
            radioDiv.classList.add('selected');
        });

        radioDiv.appendChild(input);
        radioDiv.appendChild(document.createTextNode(option));
        optionsContainer.appendChild(radioDiv);
    });

    selectedOption = null;
    const answerButton = document.getElementById('answerButton');
    if (answerButton) answerButton.disabled = true;
    isAnswered = false;
}

function handleAnswer() {
    if (isAnswered) return;
    if (selectedOption === null) return;

    isAnswered = true;
    const currentQuestion = currentQuestions[currentQuestionIndex];
    const isCorrect = selectedOption === currentQuestion.answer;

    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.disabled = true;
    });

    document.querySelectorAll('.radio').forEach(el => {
        const radioText = el.textContent.trim();
        if (radioText === currentQuestion.answer) {
            el.classList.add('correct');
        } else if (el.classList.contains('selected')) {
            el.classList.add('incorrect');
        }
    });

    if (isCorrect) {
        score++;
    }

    const answerButton = document.getElementById('answerButton');
    if (answerButton) answerButton.disabled = true;

    setTimeout(() => {
        currentQuestionIndex++;
        showQuestion();
    }, 1000);
}

function endGame() {
    if (timer) {
        clearInterval(timer);
        timer = null;
    }
    const themeSelect = document.getElementById('themeSelect');
    const theme = themeSelect ? themeSelect.value : 'formulaToName';

    fetch('/check_auth')
        .then(response => response.json())
        .then(data => {
            if (data.authenticated) {
                saveGameResult(score, currentMode, theme);
            }
        })
        .catch(err => console.log('Ошибка:', err));

    const gameScreen = document.getElementById('gameScreen');
    const resultsScreen = document.getElementById('resultsScreen');

    if (gameScreen) gameScreen.classList.add('hidden');
    if (resultsScreen) resultsScreen.classList.remove('hidden');

    const resultText = document.getElementById('resultText');
    if (resultText) {
        if (currentMode === 'time') {
            resultText.textContent = `Вы ответили правильно на ${score} вопрос(ов) за 1 минуту!`;
        } else {
            resultText.textContent = `Вы ответили правильно на ${score} из ${totalQuestionsCount} вопрос(ов)!`;
        }
    }
}

function restartGame() {
    const resultsScreen = document.getElementById('resultsScreen');
    const welcomeScreen = document.getElementById('welcomeScreen');

    if (resultsScreen) resultsScreen.classList.add('hidden');
    if (welcomeScreen) welcomeScreen.classList.remove('hidden');
}

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

async function saveGameResult(score, mode, theme) {
    try {
        const response = await fetch('/save_result', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                score: score,
                mode: mode,
                theme: theme
            })
        });
        const data = await response.json();
        if (data.success) {
            console.log('Результат сохранен');
        }
    } catch (error) {
        console.error('Ошибка сохранения:', error);
    }
}