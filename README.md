# vim-goban

[![PyPI version](https://img.shields.io/pypi/v/vim-goban.svg)](https://pypi.org/project/vim-goban/)
[![Python](https://img.shields.io/pypi/pyversions/vim-goban.svg)](https://pypi.org/project/vim-goban/)
[![License](https://img.shields.io/github/license/yonghun16/vim-goban.svg)](LICENSE)

A terminal-based Go (Baduk) game controlled by Vim motions.

`vim-goban` lets you play Go directly in your terminal with familiar Vim keybindings.

Built with Python and powered by GNU Go AI.


## Features

- 🏁 Terminal UI based Go board
- 🎮 Vim-style keyboard navigation (`h`, `j`, `k`, `l`) or arrow keys
- ⏩ Jump and position movement inspired by Vim motions
- 🤖 GNU Go AI integration for opponent gameplay
- ⚫⚪ Go rule based stone placement and capture system
- 🔄 Undo and recent move tracking support
- ⏸️ Pass system with automatic scoring after consecutive passes
- 🎨 Terminal color board rendering
- ⌨️ Keyboard-focused lightweight gameplay experience


## Screenshot

![vim-goban](https://raw.githubusercontent.com/yonghun16/vim-goban/refs/heads/main/previews/preview_gif.gif)


# Installation

## Requirements

- Python 3.10+
- GNU Go


## Install GNU Go

### macOS

```bash
brew install gnugo
```

### Ubuntu / Debian

```bash
sudo apt install gnugo
```

Check installation:

```bash
gnugo --version
```


## Install vim-goban

### Using pipx (Recommended)

`vim-goban` is a terminal application, so installing with `pipx` is recommended.

If you don't have pipx installed:

### macOS

```bash
brew install pipx
pipx ensurepath
```

### Linux

```bash
python3 -m pip install --user pipx
pipx ensurepath
```

Install `vim-goban`:

```bash
pipx install vim-goban
```


## Run

```bash
goban
```


# Controls

## Movement

`vim-goban` uses Vim style movement.

| Key | Action |
|---|---|
| `h`, `←` | Move left |
| `j`, `↓` | Move down |
| `k`, `↑` | Move up |
| `l`, `→` | Move right |


## Jump Movement

| Key | Action |
|---|---|
| `Ctrl+h`, `b` | Jump left |
| `Ctrl+j`, `]` | Jump down |
| `Ctrl+k`, `[` | Jump up |
| `Ctrl+l`, `w` | Jump right |


## Position Movement

| Key | Action |
|---|---|
| `Shift + A` | Move to far left |
| `Shift + I` | Move to far right |
| `Shift + H` | Move to top of column |
| `Shift + M` | Move to middle of column |
| `Shift + L` | Move to bottom of column |


> Note: Some Ctrl key bindings may conflict with terminal shortcuts depending on your terminal emulator.


# Game Controls

| Key | Action |
|---|---|
| `Enter` | Place stone |
| `p` | Pass |
|     | Two consecutive passes end the game (Score) |
| `r` | Show recent move positions |
| `c` | Toggle Color Theme |
| `n` | Start a new game |
| `u` | Undo last move |
| `?` | Toggle help |
| `q` | Quit game |


# Gameplay

## Capturing Stones

When a group of stones has no remaining liberties, the stones are removed from the board.

Example:

Before:

```
. ○ .
○ ● ○
. ○ .
```

After:

```
. . .
. . .
. . .
```


## AI

After placing a stone, GNU Go responds automatically.

GNU Go provides the computer opponent while `vim-goban` handles:

- Board rendering
- User input
- Game state
- Go rules


## Rules
 Pass + Pass   : Both players pass consecutively → Game ends
 Score         : GNU Go calculates territory and winner

# Project Structure

```
vim-goban/
│
├── goban/
│   ├── main.py        # Game loop
│   ├── board.py       # Go rules and board state
│   ├── renderer.py    # Terminal renderer
│   ├── input.py       # Vim motion input
│   └── engine.py      # GNU Go communication
│
├── tests/             # Unit tests
│
├── README.md
├── LICENSE
└── pyproject.toml
```


# Development

Create virtual environment:

```bash
python -m venv .venv

source .venv/bin/activate
```

Install package locally:

```bash
pip install -e .
```

Run:

```bash
goban
```


# License

MIT License

See [LICENSE](LICENSE).


# Author

[@yonghun16](https://github.com/yonghun16)
