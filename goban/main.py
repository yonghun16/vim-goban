import curses
import json
import os
import shutil
import sys
import platformdirs
from goban.board import Board, SIZE
from goban.engine import GnuGo
from goban.input import move  # Import the move function

USER_DATA_DIR = platformdirs.user_data_dir("vim-goban")
SAVE_FILE = os.path.join(USER_DATA_DIR, "savegame.json")
SETTINGS_FILE = os.path.join(USER_DATA_DIR, "settings.json")
LEGACY_SAVE_FILE = "savegame.json"

DEFAULT_SETTINGS = {"ai_level": 10}

# Migrate legacy save file if it exists and new one does not
if not os.path.exists(SAVE_FILE) and os.path.exists(LEGACY_SAVE_FILE):
    try:
        os.makedirs(USER_DATA_DIR, exist_ok=True)
        shutil.move(LEGACY_SAVE_FILE, SAVE_FILE)
    except Exception:
        pass


def save_game(
    board, moves, turn, game_over, consecutive_passes, cursor, history,
    player_color, handicap,
):
    data = {
        "board_state": board.save_state(),
        "moves": moves,
        "turn": turn,
        "game_over": game_over,
        "consecutive_passes": consecutive_passes,
        "cursor": list(cursor),
        "history": history,
        "player_color": player_color,
        "handicap": handicap,
    }
    os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE, "r") as f:
        return json.load(f)


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
        settings = dict(DEFAULT_SETTINGS)
        settings.update(data)
        return settings
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)


def prompt_save(
    stdscr, board, moves, turn, game_over, consecutive_passes, cursor, history,
    player_color, handicap,
):
    # Give the terminal state a tiny moment to settle and flush any interrupted inputs
    curses.napms(100)
    try:
        curses.flushinp()
    except curses.error:
        pass

    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()
    msg = "Save game before exiting? [y/n]: "
    try:
        stdscr.addstr(0, 0, msg[: max_x - 1])
    except curses.error:
        pass
    stdscr.refresh()
    while True:
        try:
            key = stdscr.getkey()
            if key in ("y", "Y"):
                save_game(
                    board, moves, turn, game_over, consecutive_passes, cursor,
                    history, player_color, handicap,
                )
                break
            elif key in ("n", "N", "\x1b", "\x03"):
                break
        except (curses.error, ValueError, KeyboardInterrupt):
            # If Ctrl+C is pressed again or any curses error (like no input) occurs, break and exit safely
            break


def prompt_new_game(stdscr):
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()
    msg = "Start a new game? [y/n]: "
    try:
        stdscr.addstr(0, 0, msg[: max_x - 1])
    except curses.error:
        pass
    stdscr.refresh()
    while True:
        try:
            key = stdscr.getkey()
            if key in ("y", "Y"):
                return True
            elif key in ("n", "N", "\x1b", "\x03"):
                return False
        except (curses.error, ValueError, KeyboardInterrupt):
            # If Ctrl+C is pressed or any error occurs, do not start a new game by default
            return False


def draw_centered_box(stdscr, lines):
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()

    box_height = len(lines)
    box_width = len(lines[0]) if lines else 0

    start_y = max(0, (max_y - box_height) // 2)
    start_x = max(0, (max_x - box_width) // 2)

    for i, line in enumerate(lines):
        y = start_y + i
        if y >= max_y or start_x >= max_x:
            break
        safe_len = max_x - start_x
        if y == max_y - 1:
            safe_len -= 1  # Avoid writing to the bottom-right corner
        safe_len = max(0, safe_len)
        try:
            stdscr.addstr(y, start_x, line[:safe_len])
        except curses.error:
            pass

    stdscr.refresh()


def show_message(stdscr, lines):
    from goban.renderer import render_box  # Avoid circular import

    draw_centered_box(stdscr, render_box(lines))

    curses.flushinp()
    try:
        stdscr.getkey()
    except (curses.error, ValueError):
        pass


def run_select_menu(stdscr, title, items, selected=0, subtitle=None, allow_back=True):
    from goban.renderer import render_box  # Avoid circular import

    selected = max(0, min(len(items) - 1, selected))

    while True:
        content = [title]
        if subtitle:
            content.append(subtitle)
        content.append("")
        for i, item in enumerate(items):
            marker = "▶ " if i == selected else "  "
            content.append(f"{marker}{item}")
        content.append("")
        hint = "↑↓/kj Move   Enter Select"
        if allow_back:
            hint += "   q Back"
        content.append(hint)

        draw_centered_box(stdscr, render_box(content))

        try:
            key = stdscr.getkey()
        except (curses.error, ValueError):
            continue

        if key in ("k", "KEY_UP"):
            selected = (selected - 1) % len(items)
        elif key in ("j", "KEY_DOWN"):
            selected = (selected + 1) % len(items)
        elif key == "\r":
            return selected
        elif key in ("q", "\x1b", "\x03"):
            curses.flushinp()  # Discard any trailing bytes of an unresolved escape sequence
            return None


def show_new_game_setup(stdscr):
    color_idx = run_select_menu(
        stdscr,
        "New Game",
        ["Black (●) — plays first", "White (○) — plays second"],
        subtitle="Choose your stone color",
    )
    if color_idx is None:
        return None
    player_color = ["black", "white"][color_idx]

    handicap_values = [0, 2, 3, 4, 5, 6, 7, 8, 9]
    handicap_items = ["0 (No handicap)"] + [str(n) for n in handicap_values[1:]]
    handicap_idx = run_select_menu(
        stdscr,
        "New Game",
        handicap_items,
        subtitle="Handicap stones for Black",
    )
    if handicap_idx is None:
        return None
    handicap = handicap_values[handicap_idx]

    return {"color": player_color, "handicap": handicap}


def show_help_menu(stdscr):
    from goban.renderer import render_help_screen  # Avoid circular import

    draw_centered_box(stdscr, render_help_screen())

    curses.flushinp()
    try:
        stdscr.getkey()
    except (curses.error, ValueError):
        pass


def show_main_menu(stdscr, selected=0):
    from goban.renderer import render_main_menu  # Avoid circular import

    items = ["New Game", "Load Game", "Difficulty", "Help", "Quit Game"]
    selected = max(0, min(len(items) - 1, selected))

    while True:
        draw_centered_box(stdscr, render_main_menu(items, selected))

        try:
            key = stdscr.getkey()
        except (curses.error, ValueError):
            continue

        if key == "\x1b":
            curses.flushinp()  # Discard any trailing bytes of an unresolved escape sequence
            continue

        if key in ("k", "KEY_UP"):
            selected = (selected - 1) % len(items)
        elif key in ("j", "KEY_DOWN"):
            selected = (selected + 1) % len(items)
        elif key == "\r":
            return items[selected], selected
        elif key in ("q", "\x03"):
            return "Quit Game", selected


def show_difficulty_selection(stdscr, settings):
    items = [f"Level {i}" for i in range(1, 11)]
    idx = run_select_menu(
        stdscr,
        "Difficulty",
        items,
        selected=settings.get("ai_level", 10) - 1,
        subtitle="GNU Go strength (1 Weak — 10 Strong)",
    )
    if idx is not None:
        settings["ai_level"] = idx + 1
        save_settings(settings)


def safe_render_and_draw(
    stdscr,
    board,
    cursor,
    white_captured,
    black_captured,
    turn,
    message,
    show_help,
    recent_black=None,
    recent_white=None,
    show_recent=False,
    game_over=False,
    black_territory=None,
    white_territory=None,
    color_mode=False,
):
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()

    # The minimum height and width to render the board safely
    MIN_HEIGHT = 26
    MIN_WIDTH = 42

    if max_y < MIN_HEIGHT or max_x < MIN_WIDTH:
        msg1 = "Terminal window is too small!"
        msg2 = f"Required: {MIN_HEIGHT}x{MIN_WIDTH}"
        msg3 = f"Current:  {max_y}x{max_x}"
        msg4 = "Please resize the window."
        try:
            if max_y > 0:
                stdscr.addstr(0, 0, msg1[: max_x - 1])
            if max_y > 1:
                stdscr.addstr(1, 0, msg2[: max_x - 1])
            if max_y > 2:
                stdscr.addstr(2, 0, msg3[: max_x - 1])
            if max_y > 3:
                stdscr.addstr(3, 0, msg4[: max_x - 1])
        except curses.error:
            pass
        stdscr.refresh()
        return

    from goban.renderer import render  # Import render function here to avoid circular import

    lines = render(
        board,
        cursor,
        white_captured=white_captured,
        black_captured=black_captured,
        turn=turn,
        message=message,
        show_help=show_help,
        recent_black=recent_black,
        recent_white=recent_white,
        show_recent=show_recent,
        game_over=game_over,
        black_territory=black_territory,
        white_territory=white_territory,
    )

    has_colors = curses.has_colors()

    # Center the board on screen, like the menu screens. Anchored to the board's
    # own fixed size (not the variable-length status/help lines) so it doesn't
    # shift around as messages change or help is toggled.
    board_width = SIZE * 2 + 3
    start_y = max(0, (max_y - MIN_HEIGHT) // 2)
    start_x = max(0, (max_x - board_width) // 2)

    for i, line in enumerate(lines):
        y = start_y + i
        if y >= max_y or start_x >= max_x:
            break
        # To avoid error on bottom-right character and handle narrow width safely
        safe_len = max_x - start_x
        if y == max_y - 1:
            safe_len -= 1
        safe_len = max(0, safe_len)
        safe_line = line[:safe_len]
        try:
            if color_mode and has_colors and line.startswith(("┌", "│", "└")):
                # Draw character by character with board colors
                for col_idx, char in enumerate(safe_line):
                    # Determine color pair based on original character
                    if char in ("┌", "┐", "└", "┘", "─", "│"):
                        attr = curses.color_pair(10)
                    elif char in ("+", "·"):
                        attr = curses.color_pair(11)
                    elif char in ("●", "◍", "•"):
                        attr = curses.color_pair(12)
                    elif char in ("○", "◌", "◦"):
                        attr = curses.color_pair(13)
                    elif char in ("⊙", "◉", "◎", "★", "☆"):
                        attr = curses.color_pair(14) | curses.A_BOLD
                    else:
                        attr = curses.color_pair(10)

                    # Map hollow white stone characters to filled counterparts for rendering
                    if char == "○":
                        char = "●"
                    elif char == "◌":
                        char = "◍"
                    elif char == "◎":
                        char = "◉"
                    elif char == "☆":
                        char = "★"

                    try:
                        stdscr.addch(y, start_x + col_idx, char, attr)
                    except curses.error:
                        pass
            else:
                stdscr.addstr(y, start_x, safe_line)
        except curses.error:
            pass

    stdscr.refresh()


def play_game(stdscr, settings, new_game_setup=None, load=False):

    engine = GnuGo()
    engine.set_level(settings.get("ai_level", 10))

    board = Board()
    cursor = (9, 9)
    turn = Board.BLACK
    game_over = False
    consecutive_passes = 0
    show_help = False
    history = []
    moves = []
    recent_black = None
    recent_white = None
    show_recent = False
    black_territory = None
    white_territory = None
    color_mode = False
    message = "Place stone [Enter], Pass [p], Recent [r], Quit [q]"

    engine.send("clear_board")

    if load:
        saved_data = load_game()
        board.restore_state(saved_data["board_state"])
        moves = saved_data["moves"]
        turn = saved_data["turn"]
        game_over = saved_data["game_over"]
        consecutive_passes = saved_data["consecutive_passes"]
        cursor = tuple(saved_data["cursor"])
        history = saved_data["history"]
        player_color = saved_data.get("player_color", "black")
        handicap = saved_data.get("handicap", 0)

        # Re-apply the handicap so the engine's internal state matches board_state,
        # then replay the moves made after the handicap stones were placed.
        if handicap >= 2:
            engine.set_handicap(handicap)
        for color, coord in moves:
            engine.send(f"play {color} {coord}")

        # Parse recent positions from loaded moves
        for color, coord in moves:
            if "PASS" not in coord:
                pos = engine.parse_coordinate(coord)
                if pos:
                    if color == "black":
                        recent_black = pos
                    else:
                        recent_white = pos

        message = "Game loaded successfully! Place stone [Enter], Pass [p], Recent [r], Quit [q]"
    else:
        player_color = new_game_setup["color"]
        handicap = new_game_setup["handicap"]

        if handicap >= 2:
            stones = engine.set_handicap(handicap)
            for hx, hy in stones:
                board.place(hx, hy, Board.BLACK)
            turn = Board.WHITE
        else:
            turn = Board.BLACK

        message = "New game started! Place stone [Enter], Pass [p], Recent [r], Quit [q]"

    player_stone = Board.BLACK if player_color == "black" else Board.WHITE
    ai_color = "white" if player_color == "black" else "black"
    ai_stone = Board.WHITE if ai_color == "white" else Board.BLACK

    def do_ai_move(thinking_message="AI is thinking..."):
        nonlocal message, consecutive_passes, game_over, recent_black, recent_white, turn

        # Render temporary state to show the AI's thinking status
        safe_render_and_draw(
            stdscr,
            board,
            cursor,
            board.white_captured,
            board.black_captured,
            turn,
            thinking_message,
            show_help,
            recent_black=recent_black,
            recent_white=recent_white,
            show_recent=show_recent,
            color_mode=color_mode,
        )

        ai_move = engine.genmove(ai_color)

        if ai_move:
            ai_move_upper = ai_move.upper()
            if "PASS" in ai_move_upper:
                consecutive_passes += 1
                moves.append((ai_color, "PASS"))
                message = "AI passed."
                if consecutive_passes >= 2:
                    game_over = True
                    score = engine.get_final_score()
                    message = f"Game Over! Final Score: {score} (Press 'q' to quit)"
            elif "RESIGN" in ai_move_upper:
                game_over = True
                message = "AI Resigned! You win! (Press 'q' to quit)"
            else:
                ai_pos = engine.parse_coordinate(ai_move)
                if ai_pos:
                    ax, ay = ai_pos
                    board.place(ax, ay, ai_stone)
                    consecutive_passes = 0
                    moves.append((ai_color, ai_move_upper))
                    if ai_stone == Board.BLACK:
                        recent_black = (ax, ay)
                    else:
                        recent_white = (ax, ay)
                    message = f"AI played {ai_move}"

        turn = player_stone

    def restart_game():
        nonlocal board, cursor, turn, game_over, consecutive_passes, message
        nonlocal show_help, history, moves, recent_black, recent_white
        nonlocal show_recent, black_territory, white_territory

        engine.send("clear_board")
        board = Board()
        cursor = (9, 9)
        game_over = False
        consecutive_passes = 0
        show_help = False
        history = []
        moves = []
        recent_black = None
        recent_white = None
        show_recent = False
        black_territory = None
        white_territory = None

        if handicap >= 2:
            stones = engine.set_handicap(handicap)
            for hx, hy in stones:
                board.place(hx, hy, Board.BLACK)
            turn = Board.WHITE
        else:
            turn = Board.BLACK

        message = "Started a new game. Place stone [Enter], Pass [p], Recent [r], Quit [q]"

        if turn == ai_stone:
            do_ai_move()

    try:
        if turn == ai_stone and not game_over:
            do_ai_move()

        while True:

            if game_over and black_territory is None:
                black_territory = engine.get_territory("black")
                white_territory = engine.get_territory("white")

            safe_render_and_draw(
                stdscr,
                board,
                cursor,
                board.white_captured,
                board.black_captured,
                turn,
                message,
                show_help,
                recent_black=recent_black,
                recent_white=recent_white,
                show_recent=show_recent,
                game_over=game_over,
                black_territory=black_territory,
                white_territory=white_territory,
                color_mode=color_mode,
            )

            if show_recent:
                stdscr.timeout(400)
            else:
                stdscr.timeout(-1)

            try:
                key = stdscr.getkey()
            except (curses.error, ValueError):
                # Timeout occurred, or an undecodable byte was received — just redraw and retry
                continue

            if key == "\x1b":
                # A bare ESC usually means curses couldn't resolve the rest of an escape
                # sequence (e.g. Shift+Arrow on a terminal whose terminfo doesn't map it).
                # Discard whatever trailing bytes are still buffered so fragments like
                # '[' or 'A' don't get misread as unrelated shortcuts (jump, Shift+A, etc).
                curses.flushinp()
                continue

            if key in ("q", "\x03"):
                # '\x03' is Ctrl+C: raw mode (see run()) stops it from raising
                # SIGINT/KeyboardInterrupt, so it's handled here like 'q' instead.
                prompt_save(
                    stdscr,
                    board,
                    moves,
                    turn,
                    game_over,
                    consecutive_passes,
                    cursor,
                    history,
                    player_color,
                    handicap,
                )
                return True  # Quitting mid-game exits the app, not just the game

            if game_over and key not in ("q", "u", "?", "r", "n", "c"):
                # When the game is over, only 'q', 'u', '?', 'r', 'n', and 'c' are allowed
                continue

            elif key in (
                "h",
                "j",
                "k",
                "l",
                "KEY_LEFT",
                "KEY_RIGHT",
                "KEY_UP",
                "KEY_DOWN",
                "H",
                "L",
                "M",
                "A",
                "I",
                "w",
                "b",
                "\x08",
                "\x0a",
                "\x0b",
                "\x0c",
                "\x7f",
                "KEY_BACKSPACE",
                "[",
                "]",
            ):

                cursor = move(key, cursor)
                show_recent = False

            elif key == "u":
                if history:
                    # Restore board state
                    last_state = history.pop()
                    board.restore_state(last_state)

                    # Revert engine moves
                    engine.send("undo")
                    engine.send("undo")

                    # Revert our move history
                    if len(moves) >= 2:
                        moves.pop()
                        moves.pop()

                    # Recompute recent positions
                    recent_black = None
                    recent_white = None
                    for color, coord in moves:
                        if "PASS" not in coord:
                            pos = engine.parse_coordinate(coord)
                            if pos:
                                if color == "black":
                                    recent_black = pos
                                else:
                                    recent_white = pos

                    show_recent = False
                    black_territory = None
                    white_territory = None

                    # Reset game status
                    consecutive_passes = 0
                    game_over = False
                    message = "Undid last move."
                else:
                    message = "No moves to undo!"

            elif key == "?":
                show_help = not show_help

            elif key == "p":
                # Player passes
                state_before = board.save_state()
                engine.send(f"play {player_color} PASS")
                moves.append((player_color, "PASS"))
                consecutive_passes += 1
                message = f"{player_color.capitalize()} passed!"

                if consecutive_passes >= 2:
                    history.append(state_before)
                    game_over = True
                    score = engine.get_final_score()
                    message = f"Game Over! Final Score: {score} (Press 'q' to quit)"
                else:
                    history.append(state_before)
                    turn = ai_stone
                    do_ai_move(
                        thinking_message=f"{player_color.capitalize()} passed! AI is thinking..."
                    )

            elif key == "r":
                # Toggle recent move highlights
                show_recent = not show_recent
                if show_recent:
                    message = "Showing recent moves (●★/○☆: Recent, ◍/◌: Existing)"
                else:
                    message = "Hidden recent moves."

            elif key == "c":
                color_mode = not color_mode
                if color_mode:
                    message = "Color theme enabled. Press 'c' to disable."
                else:
                    message = "Color theme disabled."

            elif key == "n":
                if prompt_new_game(stdscr):
                    restart_game()

            elif key == "\r":

                x, y = cursor
                state_before = board.save_state()

                if board.place(x, y, player_stone):
                    history.append(state_before)
                    consecutive_passes = 0

                    coord = engine.coordinate(x, y)
                    engine.play(player_color, x, y)
                    moves.append((player_color, coord))

                    # Update recent positions
                    if player_stone == Board.BLACK:
                        recent_black = (x, y)
                    else:
                        recent_white = (x, y)

                    turn = ai_stone
                    do_ai_move()
                else:
                    message = "Illegal move! Try again. (Self-capture or Ko)"

    except (KeyboardInterrupt, Exception):
        # Any unexpected error (bad input, a curses hiccup, ...) falls back to a
        # graceful save prompt instead of crashing out to the shell.
        prompt_save(
            stdscr,
            board,
            moves,
            turn,
            game_over,
            consecutive_passes,
            cursor,
            history,
            player_color,
            handicap,
        )
    finally:
        engine.close()


def main():

    if shutil.which("gnugo") is None:
        print("vim-goban requires GNU Go as its game engine. Please install GNU Go and try again.")
        print()
        print("  macOS         : brew install gnugo")
        print("  Ubuntu/Debian : sudo apt install gnugo")
        print()
        print("See the README for details: https://github.com/yonghun16/vim-goban")
        sys.exit(1)

    try:
        curses.wrapper(run)

    except KeyboardInterrupt:
        pass
    except Exception as exc:
        # curses.wrapper always restores the terminal before this runs, even on
        # error, so this is just a clean message instead of a raw traceback.
        print(f"vim-goban hit an unexpected error and had to close: {exc}")
        sys.exit(1)


def run(stdscr):

    curses.curs_set(0)

    # curses.wrapper() only puts the terminal in cbreak mode, which still lets
    # control characters like Ctrl+\ (SIGQUIT), Ctrl+Z (SIGTSTP) and Ctrl+S/Ctrl+Q
    # (flow control) act as raw OS-level signals that kill or freeze the process
    # before a single line of our code ever runs. raw() disables that so every
    # key press — including odd remapped combos — arrives as plain input we can
    # safely ignore instead of being terminated by it.
    curses.raw()

    stdscr.keypad(True)

    curses.use_default_colors()

    if curses.has_colors():
        curses.start_color()
        if curses.COLORS >= 256:
            curses.init_pair(10, 235, 222)  # Board grid lines
            curses.init_pair(11, 94, 222)   # Star points
            curses.init_pair(12, 0, 222)    # Black stones
            curses.init_pair(13, 15, 222)   # White stones
            curses.init_pair(14, 196, 222)  # Cursors / highlights
        else:
            curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_YELLOW)
            curses.init_pair(11, curses.COLOR_RED, curses.COLOR_YELLOW)
            curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_YELLOW)
            curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_YELLOW)
            curses.init_pair(14, curses.COLOR_RED, curses.COLOR_YELLOW)

    curses.nonl()  # Disable translation of carriage return to newline to distinguish Enter from Ctrl-J

    stdscr.bkgd(" ", curses.color_pair(0))

    settings = load_settings()

    menu_selection = 0

    while True:

        choice, menu_selection = show_main_menu(stdscr, selected=menu_selection)

        if choice == "Quit Game":
            return

        elif choice == "Difficulty":
            show_difficulty_selection(stdscr, settings)

        elif choice == "Help":
            show_help_menu(stdscr)

        elif choice == "New Game":
            setup = show_new_game_setup(stdscr)
            if setup is not None:
                if play_game(stdscr, settings, new_game_setup=setup):
                    return

        elif choice == "Load Game":
            if not os.path.exists(SAVE_FILE):
                show_message(stdscr, ["No saved game found.", "", "Press any key to continue"])
            else:
                if play_game(stdscr, settings, load=True):
                    return


if __name__ == "__main__":
    main()
