import app as app_module
from game_state import CURRENT, DIFFICULTY_CLUES
from validation import is_valid_board, parse_clues


def test_backend_components_are_separated():
    assert app_module.create_app().url_map is not None
    assert app_module.CURRENT is CURRENT
    assert app_module.DIFFICULTY_CLUES is DIFFICULTY_CLUES


def test_validation_components_preserve_board_and_clue_rules():
    assert is_valid_board([[0] * 9 for _ in range(9)]) is True
    assert is_valid_board([[0] * 8 for _ in range(9)]) is False
    assert parse_clues('Hard', None, DIFFICULTY_CLUES) == 25
    assert parse_clues(None, '40', DIFFICULTY_CLUES) == 40
    assert parse_clues(None, 'invalid', DIFFICULTY_CLUES) is None


def test_index_returns_game_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data
    assert b'id="timer"' in response.data
    assert b'id="difficulty"' in response.data
    assert b'id="theme-toggle"' in response.data
    assert b'value="Easy"' in response.data
    assert b'value="Medium"' in response.data
    assert b'value="Hard"' in response.data
    assert b'Top 10 Fastest Scores' in response.data
    assert b'id="score-list"' in response.data


def test_timer_script_resets_and_starts_for_new_games(client):
    response = client.get('/static/main.js')

    assert response.status_code == 200
    script = response.text
    assert 'function startTimer()' in script
    assert 'startTimer();' in script
    assert 'setInterval' in script
    assert 'function stopTimer()' in script
    assert 'stopTimer();' in script


def test_check_solution_script_displays_completion_message(client):
    response = client.get('/static/main.js')

    assert response.status_code == 200
    script = response.text
    assert "const msg = document.getElementById('message');" in script
    assert 'if (incorrect.size === 0)' in script
    assert "msg.innerText = 'Congratulations! You solved it!'" in script


def test_score_script_tracks_and_persists_top_ten_scores(client):
    response = client.get('/static/main.js')

    assert response.status_code == 200
    script = response.text
    assert "const SCORES_KEY = 'sudokuTopScores';" in script
    assert 'localStorage.getItem' in script
    assert 'localStorage.setItem' in script
    assert 'scores.slice(0, 10)' in script
    assert 'difficulty' in script
    assert 'hintsUsed' in script
    assert 'saveScore();' in script


def test_new_game_returns_requested_puzzle(client):
    response = client.get('/new?clues=40')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)
    assert sum(cell != 0 for row in puzzle for cell in row) == 40


def test_new_game_uses_difficulty_to_set_prefilled_cells(client):
    for difficulty, clues in [('Easy', 45), ('Medium', 35), ('Hard', 25)]:
        response = client.get(f'/new?difficulty={difficulty}')

        assert response.status_code == 200
        puzzle = response.get_json()['puzzle']
        assert sum(cell != 0 for row in puzzle for cell in row) == clues


def test_new_game_rejects_invalid_clue_values(client):
    for clues in ('not-a-number', '16', '82', '35.5'):
        response = client.get(f'/new?clues={clues}')

        assert response.status_code == 400
        assert response.get_json() == {'error': 'Invalid clues'}


def test_score_script_uses_selected_difficulty(client):
    response = client.get('/static/main.js')

    assert response.status_code == 200
    script = response.text
    assert "document.getElementById('difficulty').value" in script
    assert 'difficulty=${encodeURIComponent(difficulty)}' in script


def test_input_script_validates_invalid_sudoku_entries_immediately(client):
    response = client.get('/static/main.js')

    assert response.status_code == 200
    script = response.text
    assert 'function hasConflict(input, value)' in script
    assert 'function validateInput(input)' in script
    assert 'validateInput(e.target);' in script
    assert "input.className = 'sudoku-cell incorrect';" in script


def test_theme_toggle_script_wires_dark_mode_class(client):
    response = client.get('/static/main.js')

    assert response.status_code == 200
    script = response.text
    assert 'function toggleTheme()' in script
    assert "document.body.classList.toggle('dark-mode', darkMode);" in script
    assert "document.getElementById('theme-toggle').addEventListener('click', toggleTheme);" in script


def test_theme_styles_define_light_and_dark_colors(client):
    response = client.get('/static/styles.css')

    assert response.status_code == 200
    styles = response.text
    assert ':root {' in styles
    assert 'body.dark-mode {' in styles
    assert '--page-background:' in styles
    assert '--board-background:' in styles
    assert '--cell-background:' in styles
    assert '--button-background:' in styles
    assert '--success-color:' in styles
    assert '--error-color:' in styles


def test_styles_keep_board_responsive_and_controls_wrapped(client):
    response = client.get('/static/styles.css')

    assert response.status_code == 200
    styles = response.text
    assert '--board-size: min(432px, calc(100vw - 24px));' in styles
    assert 'max-height: calc(100vw - 24px);' in styles
    assert 'aspect-ratio: 1;' in styles
    assert 'flex: 1 1 0;' in styles
    assert 'flex-wrap: wrap;' in styles
    assert '@media (max-width: 480px)' in styles
    assert 'min-height: 1.25em;' in styles


def test_styles_define_alternating_theme_aware_sudoku_sections(client):
    response = client.get('/static/styles.css')

    assert response.status_code == 200
    styles = response.text
    assert '--section-a-background:' in styles
    assert '--section-b-background:' in styles
    assert 'background: var(--section-a-background);' in styles
    assert 'background: var(--section-b-background);' in styles
    assert '.sudoku-row:nth-child(-n+3)' in styles
    assert '.sudoku-row:nth-child(n+7)' in styles
    assert '.sudoku-cell:nth-child(n+4):nth-child(-n+6)' in styles


def test_styles_keep_text_and_controls_readable_in_both_themes(client):
    response = client.get('/static/styles.css')

    assert response.status_code == 200
    styles = response.text
    assert '--control-background:' in styles
    assert '--control-border:' in styles
    assert '--control-text:' in styles
    assert 'background: var(--control-background);' in styles
    assert 'color: var(--control-text);' in styles
    assert 'select option {' in styles
    assert '.controls label {' in styles
    assert '#scores h2 {' in styles
    assert '#score-list {' in styles
    assert 'button:focus-visible' in styles
    assert 'select:focus-visible' in styles


def test_styles_reserve_stable_board_and_status_dimensions(client):
    response = client.get('/static/styles.css')

    assert response.status_code == 200
    styles = response.text
    assert '--board-size: min(432px, calc(100vw - 24px));' in styles
    assert 'width: var(--board-size);' in styles
    assert 'height: var(--board-size);' in styles
    assert 'flex: 0 0 auto;' in styles
    assert 'flex: 1 1 0;' in styles
    assert 'overflow: hidden;' in styles
    assert 'padding: 0;' in styles
    assert 'line-height: 1;' in styles
    assert 'min-height: 56px;' in styles
    assert 'min-height: 22px;' in styles


def test_check_solution_requires_a_game_in_progress(client):
    response = client.post('/check', json={'board': [[0] * 9 for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_check_solution_rejects_malformed_json(client):
    response = client.post(
        '/check',
        data='{"board":',
        content_type='application/json',
    )

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Invalid JSON'}


def test_check_solution_rejects_invalid_board_shapes_and_values(client):
    invalid_boards = [
        [[0] * 9 for _ in range(8)],
        [[0] * 8 for _ in range(9)],
        [[0] * 9 for _ in range(9)] + [0],
        [[0] * 9 for _ in range(8)] + [[0] * 8 + ['1']],
        [[0] * 9 for _ in range(8)] + [[0] * 8 + [10]],
        [[0] * 9 for _ in range(8)] + [[0] * 8 + [1.5]],
    ]

    for board in invalid_boards:
        response = client.post('/check', json={'board': board})

        assert response.status_code == 400
        assert response.get_json() == {'error': 'Invalid board'}


def test_check_solution_returns_no_incorrect_cells_for_solution(client):
    client.get('/new')
    solution = app_module.CURRENT['solution']

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}


def test_check_solution_returns_incorrect_cell_coordinates(client):
    client.get('/new')
    puzzle = app_module.CURRENT['puzzle']
    solution = app_module.CURRENT['solution']
    row, col = next(
        (row, col)
        for row in range(9)
        for col in range(9)
        if puzzle[row][col] == 0
    )
    board = [row[:] for row in solution]
    board[row][col] = (board[row][col] % 9) + 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json()['incorrect'] == [[row, col]]


def test_check_solution_ignores_given_cells_and_reports_wrong_user_entries(client):
    solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    app_module.CURRENT['puzzle'] = [row[:] for row in solution]
    app_module.CURRENT['puzzle'][0][1] = 0
    app_module.CURRENT['solution'] = solution
    board = [row[:] for row in solution]
    board[0][0] = 1
    board[0][1] = 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json()['incorrect'] == [[0, 1]]


def test_hint_requires_a_game_in_progress(client):
    response = client.post('/hint')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_hint_fills_an_empty_cell_with_the_correct_value(client):
    client.get('/new')
    puzzle = app_module.CURRENT['puzzle']
    solution = app_module.CURRENT['solution']
    empty_cells = [
        (row, col)
        for row in range(9)
        for col in range(9)
        if puzzle[row][col] == 0
    ]

    response = client.post('/hint')
    data = response.get_json()

    assert response.status_code == 200
    assert (data['row'], data['col']) == empty_cells[0]
    assert data['value'] == solution[data['row']][data['col']]
    assert puzzle[data['row']][data['col']] == data['value']
