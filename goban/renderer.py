from .board import SIZE

# =================
# Title logo font (5 rows tall, block letters)
# =================

FONT = {
    "V": ["█ █", "█ █", "█ █", "█ █", " █ "],
    "I": ["█", "█", "█", "█", "█"],
    "M": ["█ █", "███", "█ █", "█ █", "█ █"],
    "G": ["███", "█  ", "█ █", "█ █", "███"],
    "O": ["███", "█ █", "█ █", "█ █", "███"],
    "B": ["██ ", "█ █", "██ ", "█ █", "██ "],
    "A": ["███", "█ █", "███", "█ █", "█ █"],
    "N": ["█ █", "███", "█ █", "█ █", "█ █"],
}


def _build_word(word, gap=1):
    letters = [FONT[ch] for ch in word]
    return [(" " * gap).join(letter[row] for letter in letters) for row in range(5)]


def _build_logo(word_gap=2):
    vim = _build_word("VIM")
    goban = _build_word("GOBAN")
    return [vim[row] + (" " * word_gap) + goban[row] for row in range(5)]


def render_box(content, align="center"):
    """Wrap content lines in a board-width box. Pads to the board's height when
    shorter, but grows taller (never truncates) when content doesn't fit."""

    width = SIZE * 2 - 1  # Same width used for the board box
    inner_width = width + 2  # Same interior width as the board box

    content = list(content)
    if len(content) < SIZE:
        pad_total = SIZE - len(content)
        top_pad = pad_total // 2
        bottom_pad = pad_total - top_pad
        content = [""] * top_pad + content + [""] * bottom_pad

    lines = ["┌" + "─" * inner_width + "┐"]
    for row in content:
        row = row[:width]
        row = row.center(width) if align == "center" else row.ljust(width)
        lines.append("│ " + row + " │")
    lines.append("└" + "─" * inner_width + "┘")

    return lines


HELP_LINES = [
    "Movement",
    "hjkl / Arrows: Move 1 space",
    "Ctrl+hjkl: Jump 3 spaces",
    "b/w, [ / ]: Jump 3 spaces (L/R, U/D)",
    "Shift+H/M/L: Column Top/Mid/Bottom",
    "Shift+I/A: Row Far Left/Right",
    "",
    "Actions",
    "Enter: Place stone",
    "p: Pass (x2 ends the game)",
    "u: Undo last move",
    "r: Show recent moves",
    "c: Toggle color theme",
    "n: Start a new game",
    "?: Toggle in-game help",
    "q: Quit (offers to save)",
]


def render_help_screen():
    """Render a standalone Help screen listing all controls, boxed to board size."""

    width = SIZE * 2 - 1

    content = ["Help".center(width), ""]
    content.extend(HELP_LINES)
    content.append("")
    content.append("Press any key to continue".center(width))

    return render_box(content, align="left")


def render_main_menu(items, selected):
    """Render the 'VIM GOBAN' logo with the main menu listed directly below it."""

    content = list(_build_logo())
    content.append("")
    content.append("Vim-motion powered terminal Go board")
    content.append("")
    for i, item in enumerate(items):
        marker = "▶ " if i == selected else "  "
        content.append(f"{marker}{item}")
    content.append("")
    content.append("↑↓/kj Move   Enter Select")
    content.append("")
    content.append("Powered by GNU Go")

    return render_box(content)


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
    # Board / Help overlay
    # =================

    width = SIZE * 2 - 1

    if show_help:
        # Render help as a box the same fixed size as the board itself, so it's
        # always fully visible wherever the board would fit — never clipped by
        # a small terminal the way a long list of appended lines could be.
        help_content = ["Help Guide".center(width), ""]
        help_content.extend(HELP_LINES)
        lines.extend(render_box(help_content, align="left"))
        return lines

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

    return lines
