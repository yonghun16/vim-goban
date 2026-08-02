def move(key, cursor):
    x, y = cursor

    # Normal movement (1 space)
    if key == "h":
        x -= 1

    elif key == "l":
        x += 1

    elif key == "k":
        y -= 1

    elif key == "j":
        y += 1

    # Jump movement (3 spaces) - Support both Ctrl+hjkl and b/w
    # Ctrl-H is '\x08' (or '\x7f' / 'KEY_BACKSPACE' on modern terminal emulators).
    # Ctrl-K is '\x0b', Ctrl-L is '\x0c'
    # Note: Ctrl-J is '\x0a' (identical to Enter/Newline '\n').
    # We support Ctrl-J by configuring curses with nonl() in the main loop to prevent conflicts.
    elif key in ("\x08", "\x7f", "KEY_BACKSPACE", "b"):
        x -= 3

    elif key in ("\x0c", "w"):
        x += 3

    elif key == "\x0b":
        y -= 3

    elif key == "\x0a":
        y += 3

    # Additional movement keys
    elif key == "n":
        y += 3

    elif key == "p":
        y -= 3

    # Absolute positioning (Vim-style)
    elif key == "H":  # Shift+H: Top of the current column
        y = 0

    elif key == "L":  # Shift+L: Bottom of the current column
        y = 18

    elif key == "M":  # Shift+M: Middle of the current column
        y = 9

    elif key == "A":  # Shift+A: Far left of the row
        x = 0

    elif key == "I":  # Shift+I: Far right of the row
        x = 18

    x = max(0, min(18, x))
    y = max(0, min(18, y))

    return x, y
