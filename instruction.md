# Project Instructions

## Project Goal

Refactor the existing Python Flask Sudoku application into a clean, maintainable
Sudoku game while keeping the project focused on the requirements in the rubric.

## Code Style

- Use clear and readable Python code.
- Follow modern Python practices where they improve readability and maintainability.
- Keep functions focused on one responsibility.
- Use meaningful variable and function names.
- Avoid unnecessary duplication.
- Add comments only where they help explain important logic.
- Handle errors clearly and safely.

## Project Structure

- Keep the Flask application organized into logical components.
- Keep Sudoku game logic separate from Flask route handling where practical.
- Keep HTML, CSS, and JavaScript organized and easy to maintain.
- Reuse existing project code when it is appropriate instead of unnecessarily
  rewriting working code.

## Sudoku Requirements

The application must:

- Generate valid Sudoku puzzles with exactly one unique solution.
- Provide Easy, Medium, and Hard difficulty levels.
- Adjust the number of prefilled cells according to difficulty.
- Keep prefilled cells locked.
- Give immediate visual feedback for invalid entries.
- Display a completion message when the puzzle is solved correctly.

## Required Game Features

- Hint button that fills one correct empty cell and locks it.
- Check button that highlights incorrect entries.
- Timer for the current game.
- Top 10 fastest scores containing player name, time, difficulty, and hints.
- Store the Top 10 scores in browser local storage so they remain after refresh.
- Dark/light mode toggle.

## UI Requirements

- Use clean and responsive styling.
- Support both desktop and mobile screen sizes.
- Support both light and dark modes.
- Use alternating colors for the 3x3 Sudoku sections.
- Keep text and controls readable in both modes.
- Avoid layout shifts when styling the Sudoku grid.

## Testing

- Set up the testing framework before changing the existing application.
- Run the tests after changes to make sure existing functionality is not broken.
- Prefer adding tests for important new functionality when appropriate.

## Copilot Guidance

- First understand the existing code before changing it.
- Make changes incrementally.
- Explain important changes when requested.
- Do not introduce unnecessary libraries or features.
- If there are multiple possible approaches, prefer the simplest maintainable solution.
- Do not remove working functionality unless it is necessary for the refactor.
- Treat generated code as a suggestion and verify that it works before accepting it.
