def is_valid_board(board, size=9):
    return (
        isinstance(board, list)
        and len(board) == size
        and all(
            isinstance(row, list)
            and len(row) == size
            and all(type(cell) is int and 0 <= cell <= size for cell in row)
            for row in board
        )
    )


def parse_clues(difficulty, raw_clues, difficulty_clues, size=9):
    if difficulty in difficulty_clues:
        return difficulty_clues[difficulty]

    try:
        clues = int(raw_clues if raw_clues is not None else 35)
    except (TypeError, ValueError):
        return None

    if not 17 <= clues <= size * size:
        return None
    return clues
