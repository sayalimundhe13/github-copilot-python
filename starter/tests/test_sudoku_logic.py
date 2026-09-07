import sudoku_logic


def test_create_empty_board_returns_nine_by_nine_board_of_zeroes():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_rejects_row_column_and_box_conflicts():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    board[1][1] = 6
    board[0][0] = 5

    assert sudoku_logic.is_safe(board, 0, 1, 5) is False
    assert sudoku_logic.is_safe(board, 1, 0, 5) is False
    assert sudoku_logic.is_safe(board, 2, 2, 6) is False
    assert sudoku_logic.is_safe(board, 0, 1, 1) is True


def test_fill_board_creates_a_valid_complete_board():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board) is True
    assert all(cell in range(1, sudoku_logic.SIZE + 1) for row in board for cell in row)

    for index in range(sudoku_logic.SIZE):
        assert set(board[index]) == set(range(1, sudoku_logic.SIZE + 1))
        assert {board[row][index] for row in range(sudoku_logic.SIZE)} == set(
            range(1, sudoku_logic.SIZE + 1)
        )


def test_generate_puzzle_returns_requested_clues_matching_solution():
    clues = 40

    puzzle, solution = sudoku_logic.generate_puzzle(clues)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == clues
    assert all(
        puzzle[row][col] == sudoku_logic.EMPTY
        or puzzle[row][col] == solution[row][col]
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )


def test_generate_puzzle_has_exactly_one_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert sudoku_logic.count_solutions(puzzle) == 1
    assert sudoku_logic.count_solutions(solution) == 1
