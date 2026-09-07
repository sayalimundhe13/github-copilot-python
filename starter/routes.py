from flask import Blueprint, jsonify, render_template, request

import sudoku_logic
from game_state import CURRENT, DIFFICULTY_CLUES
from validation import is_valid_board, parse_clues

routes = Blueprint('routes', __name__)


@routes.route('/')
def index():
    return render_template('index.html')


@routes.route('/new')
def new_game():
    clues = parse_clues(
        request.args.get('difficulty'),
        request.args.get('clues'),
        DIFFICULTY_CLUES,
        sudoku_logic.SIZE,
    )
    if clues is None:
        return jsonify({'error': 'Invalid clues'}), 400

    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle})


@routes.route('/check', methods=['POST'])
def check_solution():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid JSON'}), 400

    board = data.get('board')
    if not is_valid_board(board, sudoku_logic.SIZE):
        return jsonify({'error': 'Invalid board'}), 400

    solution = CURRENT.get('solution')
    puzzle = CURRENT.get('puzzle')
    if solution is None or puzzle is None:
        return jsonify({'error': 'No game in progress'}), 400

    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if puzzle[i][j] == sudoku_logic.EMPTY and board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})


@routes.route('/hint', methods=['POST'])
def get_hint():
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if puzzle[i][j] == sudoku_logic.EMPTY:
                puzzle[i][j] = solution[i][j]
                return jsonify({'row': i, 'col': j, 'value': solution[i][j]})

    return jsonify({'error': 'No empty cells'}), 400
