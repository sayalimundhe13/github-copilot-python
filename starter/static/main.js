// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const SCORES_KEY = 'sudokuTopScores';
let puzzle = [];
let timerInterval = null;
let elapsedSeconds = 0;
let hintsUsed = 0;
let gameCompleted = false;
let difficulty = 'Medium';
let darkMode = false;

function toggleTheme() {
  darkMode = !darkMode;
  document.body.classList.toggle('dark-mode', darkMode);
  document.getElementById('theme-toggle').innerText = darkMode ? 'Light Mode' : 'Dark Mode';
}

function getScores() {
  try {
    const scores = JSON.parse(localStorage.getItem(SCORES_KEY) || '[]');
    return Array.isArray(scores) ? scores : [];
  } catch (error) {
    return [];
  }
}

function renderScores() {
  const scoreList = document.getElementById('score-list');
  scoreList.innerHTML = '';
  getScores().forEach((score) => {
    const item = document.createElement('li');
    item.innerText = `${score.name} - ${score.time}s - ${score.difficulty} - ${score.hints} hints`;
    scoreList.appendChild(item);
  });
}

function saveScore() {
  if (gameCompleted) return;
  gameCompleted = true;
  const name = window.prompt('Enter your name for the scoreboard:');
  if (!name) return;

  const scores = getScores();
  scores.push({
    name: name.trim(),
    time: elapsedSeconds,
    difficulty,
    hints: hintsUsed
  });
  scores.sort((first, second) => first.time - second.time);
  localStorage.setItem(SCORES_KEY, JSON.stringify(scores.slice(0, 10)));
  renderScores();
}

function updateTimer() {
  const minutes = Math.floor(elapsedSeconds / 60).toString().padStart(2, '0');
  const seconds = (elapsedSeconds % 60).toString().padStart(2, '0');
  document.getElementById('timer').innerText = `Time: ${minutes}:${seconds}`;
}

function startTimer() {
  clearInterval(timerInterval);
  elapsedSeconds = 0;
  updateTimer();
  timerInterval = setInterval(() => {
    elapsedSeconds += 1;
    updateTimer();
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
  timerInterval = null;
}

function hasConflict(input, value) {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const row = Number(input.dataset.row);
  const col = Number(input.dataset.col);
  const boxRow = Math.floor(row / 3);
  const boxCol = Math.floor(col / 3);

  return Array.from(inputs).some((cell) => {
    if (cell === input || cell.value !== value) return false;
    const cellRow = Number(cell.dataset.row);
    const cellCol = Number(cell.dataset.col);
    return cellRow === row
      || cellCol === col
      || (Math.floor(cellRow / 3) === boxRow && Math.floor(cellCol / 3) === boxCol);
  });
}

function validateInput(input) {
  input.className = 'sudoku-cell';
  if (input.value && hasConflict(input, input.value)) {
    input.className = 'sudoku-cell incorrect';
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        validateInput(e.target);
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  hintsUsed = 0;
  gameCompleted = false;
  startTimer();
  const msg = document.getElementById('message');
  msg.innerText = '';
  msg.className = '';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.className = 'message-error';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (incorrect.size === 0) {
    stopTimer();
    saveScore();
    msg.className = 'message-success';
    msg.innerText = 'Congratulations! You solved it!';
  } else {
    msg.className = 'message-error';
    msg.innerText = 'Some cells are incorrect.';
  }
}

async function getHint() {
  const res = await fetch('/hint', {method: 'POST'});
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.className = 'message-error';
    msg.innerText = data.error;
    return;
  }

  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const input = inputs[data.row * SIZE + data.col];
  input.value = data.value;
  input.disabled = true;
  input.className = 'sudoku-cell prefilled';
  hintsUsed += 1;
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', getHint);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  renderScores();
  // initialize
  newGame();
});