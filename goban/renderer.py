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
):
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
            cell = "."

            # Cursor
            if cursor == (x, y):

                if stone == board.EMPTY:
                    cell = "⊙"

                elif stone == board.BLACK:
                    if show_recent and recent_black == (x, y):
                        cell = "★"
                    else:
                        cell = "◉"

                elif stone == board.WHITE:
                    if show_recent and recent_white == (x, y):
                        cell = "☆"
                    else:
                        cell = "◎"

            # Stone
            elif stone == board.BLACK:
                if show_recent and recent_black == (x, y):
                    cell = "★"
                else:
                    cell = "●"

            elif stone == board.WHITE:
                if show_recent and recent_white == (x, y):
                    cell = "☆"
                else:
                    cell = "○"

            # Star point
            elif (x, y) in STARS:

                cell = "+"

            else:

                cell = "."

            row += cell + " "

        row += "│"

        lines.append(row)

    lines.append("└" + "─" * (width + 2) + "┘")

    if show_help:
        lines.append("")
        lines.append(" [ Help Guide ]")
        lines.append(" hjkl          : Move cursor 1 space (Left, Down, Up, Right)")
        lines.append(" Ctrl+hjkl     : Jump cursor 3 spaces")
        lines.append(" b / w         : Jump cursor 3 spaces Left / Right")
        lines.append(" Shift+H / L   : Move to Top / Bottom of the column")
        lines.append(" Shift+A / I   : Move to Far Left / Right of the row")
        lines.append(" Shift+M       : Move to Middle of the column")
        lines.append(" Enter (Return): Place stone")
        lines.append(" p             : Pass turn")
        lines.append(" r             : Show recent move positions (★/☆)")
        lines.append(" n             : Start a new game")
        lines.append(" u             : Undo last move")
        lines.append(" ?             : Toggle Help Guide")
        lines.append(" q             : Quit game")

    return lines
