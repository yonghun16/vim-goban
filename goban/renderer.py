from .board import SIZE

STARS = {
    (3, 3),
    (9, 3),
    (15, 3),
    (3, 9),
    (9, 9),
    (15, 9),
    (3, 15),
    (9, 15),
    (15, 15),
}


def render(
    board,
    cursor,
    white_captured=0,
    black_captured=0,
    turn=None,
    message="",
    show_help=False,
    recent_black=None,
    recent_white=None,
    show_recent=False,
    game_over=False,
    black_territory=None,
    white_territory=None,
):
    import time
    blink_state = int(time.time() * 2.5) % 2 == 0  # 400ms interval for perfect blink rate

    lines = []

    # =================
    # Status
    # =================

    lines.append(f"White ○ captured: {white_captured}")
    lines.append(f"Black ● captured: {black_captured}")

    if turn == board.BLACK:
        lines.append("Turn: ● Black")
    else:
        lines.append("Turn: ○ White")

    if message:
        lines.append(f"Status: {message}")
    else:
        lines.append("")

    lines.append("")

    # =================
    # Board
    # =================

    width = SIZE * 2 - 1

    lines.append("┌" + "─" * (width + 2) + "┐")

    for y in range(SIZE):

        row = "│ "

        for x in range(SIZE):

            stone = board.get(x, y)

            # If game is over, render territories and played stones, hiding other dots
            if game_over and black_territory is not None and white_territory is not None:
                if (x, y) in black_territory:
                    cell = "•"
                elif (x, y) in white_territory:
                    cell = "◦"
                elif stone == board.BLACK:
                    cell = "●"
                elif stone == board.WHITE:
                    cell = "○"
                else:
                    cell = " "

                # Overlay cursor on top if it matches
                if cursor == (x, y):
                    if cell in (" ", "•", "◦"):
                        cell = "⊙"
                    elif cell == "●":
                        cell = "◉"
                    elif cell == "○":
                        cell = "◎"

            # Normal rendering
            else:
                cell = "·"

                # Cursor
                if cursor == (x, y):

                    if stone == board.EMPTY:
                        cell = "⊙"

                    elif stone == board.BLACK:
                        if show_recent and recent_black == (x, y):
                            cell = "●" if blink_state else "★"
                        else:
                            cell = "◉"

                    elif stone == board.WHITE:
                        if show_recent and recent_white == (x, y):
                            cell = "○" if blink_state else "☆"
                        else:
                            cell = "◎"

                # Stone
                elif stone == board.BLACK:
                    if show_recent:
                        if recent_black == (x, y):
                            cell = "●" if blink_state else "★"
                        else:
                            cell = "◍"
                    else:
                        cell = "●"

                elif stone == board.WHITE:
                    if show_recent:
                        if recent_white == (x, y):
                            cell = "○" if blink_state else "☆"
                        else:
                            cell = "◌"
                    else:
                        cell = "○"

                # Star point
                elif (x, y) in STARS:

                    cell = "+"

                else:

                    cell = "·"

            row += cell + " "

        row += "│"

        lines.append(row)

    lines.append("└" + "─" * (width + 2) + "┘")

    if show_help:
        lines.append("")
        lines.append(" [ Help Guide ]")
        lines.append("")
        lines.append(" hjkl          : Move cursor 1 space (Left, Down, Up, Right)")
        lines.append(" Ctrl+hjkl     : Jump cursor 3 spaces")
        lines.append(" [ / ]         : Jump cursor 3 spaces Up / Down")
        lines.append(" b / w         : Jump cursor 3 spaces Left / Right")
        lines.append(" Shift+H / L   : Move to Top / Bottom of the column")
        lines.append(" Shift+A / I   : Move to Far Left / Right of the row")
        lines.append(" Shift+M       : Move to Middle of the column")
        lines.append("")
        lines.append(" Enter (Return): Place stone")
        lines.append(" p             : Pass turn")
        lines.append("               : Two consecutive passes end the game (Score)")
        lines.append(" r             : Show recent move positions (●/○ vs ◍/◌)")
        lines.append(" c             : Toggle Color Theme")
        lines.append(" n             : Start a new game")
        lines.append(" u             : Undo last move")
        lines.append("")
        lines.append(" ?             : Toggle Help Guide")
        lines.append(" q             : Quit game")
        lines.append("")
        lines.append("")
        lines.append("[ Game Rules ]")
        lines.append("")
        lines.append(" Pass + Pass   : Both players pass consecutively → Game ends")
        lines.append(" Score         : GNU Go calculates territory and winner")

    return lines
