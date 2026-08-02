import curses
import json
import os
import platformdirs
from goban.board import Board
from goban.engine import GnuGo
from goban.input import move  # Import the move function

USER_DATA_DIR = platformdirs.user_data_dir("vim-goban")
SAVE_FILE = os.path.join(USER_DATA_DIR, "savegame.json")
LEGACY_SAVE_FILE = "savegame.json"

# Migrate legacy save file if it exists and new one does not
if not os.path.exists(SAVE_FILE) and os.path.exists(LEGACY_SAVE_FILE):
    try:
        os.makedirs(USER_DATA_DIR, exist_ok=True)
        import shutil
        shutil.move(LEGACY_SAVE_FILE, SAVE_FILE)
    except Exception:
        pass


def save_game(board, moves, turn, game_over, consecutive_passes, cursor, history):
    data = {
        "board_state": board.save_state(),
        "moves": moves,
        "turn": turn,
        "game_over": game_over,
        "consecutive_passes": consecutive_passes,
        "cursor": list(cursor),
        "history": history,
    }
    os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE, "r") as f:
        return json.load(f)


def prompt_save(
    stdscr, board, moves, turn, game_over, consecutive_passes, cursor, history
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
                    board, moves, turn, game_over, consecutive_passes, cursor, history
                )
                break
            elif key in ("n", "N"):
                break
        except (curses.error, KeyboardInterrupt):
            # If Ctrl+C is pressed again or any curses error (like no input) occurs, break and exit safely
            break


def prompt_load(stdscr):
    if not os.path.exists(SAVE_FILE):
        return None
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()
    msg = "Found saved game. Load? [y/n]: "
    try:
        stdscr.addstr(0, 0, msg[: max_x - 1])
    except curses.error:
        pass
    stdscr.refresh()
    while True:
        try:
            key = stdscr.getkey()
            if key in ("y", "Y"):
                return load_game()
            elif key in ("n", "N"):
                return None
        except (curses.error, KeyboardInterrupt):
            # If Ctrl+C is pressed or any curses error occurs, start a new game by default
            return None


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
            elif key in ("n", "N"):
                return False
        except (curses.error, KeyboardInterrupt):
            # If Ctrl+C is pressed or any error occurs, do not start a new game by default
            return False


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

    for i, line in enumerate(lines):
        if i >= max_y:
            break
        # To avoid error on bottom-right character and handle narrow width safely
        safe_len = max_x - 1
        if i == max_y - 1:
            safe_len = max_x - 2
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
                        stdscr.addch(i, col_idx, char, attr)
                    except curses.error:
                        pass
            else:
                stdscr.addstr(i, 0, safe_line)
        except curses.error:
            pass

    stdscr.refresh()


def main():

    try:
        curses.wrapper(run)

    except KeyboardInterrupt:
        pass


def run(stdscr):

    curses.curs_set(0)

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

    board = Board()
    engine = GnuGo()

    cursor = (9, 9)

    turn = Board.BLACK
    game_over = False
    consecutive_passes = 0
    message = "Place stone [Enter], Pass [p], Recent [r], Quit [q]"
    show_help = False
    history = []
    moves = []
    recent_black = None
    recent_white = None
    show_recent = False
    black_territory = None
    white_territory = None
    color_mode = False

    # Prompt to load saved game
    saved_data = prompt_load(stdscr)
    if saved_data:
        board.restore_state(saved_data["board_state"])
        moves = saved_data["moves"]
        turn = saved_data["turn"]
        game_over = saved_data["game_over"]
        consecutive_passes = saved_data["consecutive_passes"]
        cursor = tuple(saved_data["cursor"])
        history = saved_data["history"]

        # Parse recent positions from loaded moves
        for color, coord in moves:
            if "PASS" not in coord:
                pos = engine.parse_coordinate(coord)
                if pos:
                    if color == "black":
                        recent_black = pos
                    else:
                        recent_white = pos

        # Replay moves to GnuGo
        engine.send("clear_board")
        for color, coord in moves:
            engine.send(f"play {color} {coord}")

        message = "Game loaded successfully! Place stone [Enter], Pass [p], Recent [r], Quit [q]"

    try:
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
            except curses.error:
                # Timeout occurred, continue to redraw and animate blinking
                continue

            if key == "q":
                prompt_save(
                    stdscr,
                    board,
                    moves,
                    turn,
                    game_over,
                    consecutive_passes,
                    cursor,
                    history,
                )
                break

            if game_over and key not in ("q", "u", "?", "r", "n", "c"):
                # When the game is over, only 'q', 'u', '?', 'r', 'n', and 'c' are allowed
                continue

            elif key in (
                "h",
                "j",
                "k",
                "l",
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
                engine.send("play black PASS")
                moves.append(("black", "PASS"))
                consecutive_passes += 1
                message = "Black passed!"

                if consecutive_passes >= 2:
                    history.append(state_before)
                    game_over = True
                    score = engine.get_final_score()
                    message = f"Game Over! Final Score: {score} (Press 'q' to quit)"
                else:
                    history.append(state_before)
                    turn = Board.WHITE
                    # Render temporary state to show White's turn and thinking status
                    safe_render_and_draw(
                        stdscr,
                        board,
                        cursor,
                        board.white_captured,
                        board.black_captured,
                        turn,
                        "Black passed! AI is thinking...",
                        show_help,
                        recent_black=recent_black,
                        recent_white=recent_white,
                        show_recent=show_recent,
                        color_mode=color_mode,
                    )

                    # AI's turn
                    ai_color = "white"
                    ai_move = engine.genmove(ai_color)

                    if ai_move:
                        ai_move_upper = ai_move.upper()
                        if "PASS" in ai_move_upper:
                            consecutive_passes += 1
                            moves.append((ai_color, "PASS"))
                            message = "Black passed! AI also passed."
                            if consecutive_passes >= 2:
                                game_over = True
                                score = engine.get_final_score()
                                message = f"Game Over! Final Score: {score} (Press 'q' to quit)"
                        elif "RESIGN" in ai_move_upper:
                            game_over = True
                            message = "AI Resigned! Black wins! (Press 'q' to quit)"
                        else:
                            ai_pos = engine.parse_coordinate(ai_move)
                            if ai_pos:
                                ax, ay = ai_pos
                                board.place(ax, ay, Board.WHITE)
                                consecutive_passes = 0
                                moves.append((ai_color, ai_move_upper))
                                recent_white = (ax, ay)
                                message = f"AI played {ai_move}"
                    turn = Board.BLACK

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
                    board = Board()
                    engine.send("clear_board")
                    cursor = (9, 9)
                    turn = Board.BLACK
                    game_over = False
                    consecutive_passes = 0
                    message = "Started a new game. Place stone [Enter], Pass [p], Recent [r], Quit [q]"
                    show_help = False
                    history = []
                    moves = []
                    recent_black = None
                    recent_white = None
                    show_recent = False
                    black_territory = None
                    white_territory = None

            elif key == "\r":

                x, y = cursor
                state_before = board.save_state()

                if board.place(x, y, turn):
                    history.append(state_before)
                    consecutive_passes = 0
                    color = "black"

                    coord = engine.coordinate(x, y)
                    engine.play(color, x, y)
                    moves.append((color, coord))

                    # Update recent positions
                    if turn == Board.BLACK:
                        recent_black = (x, y)
                    else:
                        recent_white = (x, y)

                    turn = Board.WHITE
                    # Render temporary state to show White's turn and thinking status
                    safe_render_and_draw(
                        stdscr,
                        board,
                        cursor,
                        board.white_captured,
                        board.black_captured,
                        turn,
                        "AI is thinking...",
                        show_help,
                        recent_black=recent_black,
                        recent_white=recent_white,
                        show_recent=show_recent,
                        color_mode=color_mode,
                    )

                    # AI 차례
                    ai_color = "white"
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
                            message = "AI Resigned! Black wins! (Press 'q' to quit)"
                        else:
                            ai_pos = engine.parse_coordinate(ai_move)
                            if ai_pos:
                                ax, ay = ai_pos
                                board.place(ax, ay, Board.WHITE)
                                consecutive_passes = 0
                                moves.append((ai_color, ai_move_upper))
                                recent_white = (ax, ay)
                                message = f"AI played {ai_move}"
                    turn = Board.BLACK
                else:
                    message = "Illegal move! Try again. (Self-capture or Ko)"

    except (KeyboardInterrupt, curses.error):
        prompt_save(
            stdscr,
            board,
            moves,
            turn,
            game_over,
            consecutive_passes,
            cursor,
            history,
        )
    finally:
        engine.close()


if __name__ == "__main__":
    main()
