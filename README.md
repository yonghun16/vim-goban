# vim-goban

[![PyPI version](https://img.shields.io/pypi/v/vim-goban.svg)](https://pypi.org/project/vim-goban/)
[![Python](https://img.shields.io/pypi/pyversions/vim-goban.svg)](https://pypi.org/project/vim-goban/)
[![License](https://img.shields.io/github/license/yonghun16/vim-goban.svg)](LICENSE)

A terminal-based Go (Baduk) game controlled by Vim motions.

`vim-goban` lets you play Go directly in your terminal with familiar Vim keybindings.

Built with Python and powered by GNU Go AI.


## Features

- 🏁 Terminal UI based Go board
- 🎮 Vim motion controls
- 🤖 GNU Go AI integration
- ⚫⚪ Stone capture system
- 🔄 Undo support
- ⏩ Pass / Resign support
- 🌱 Lightweight and keyboard focused


## Screenshot

![vim-goban](https://raw.githubusercontent.com/yonghun16/vim-goban/refs/heads/main/preview.gif)


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
| `h` | Move left |
| `j` | Move down |
| `k` | Move up |
| `l` | Move right |


## Jump Movement

| Key | Action |
|---|---|
| `Ctrl+h` | Jump left |
| `Ctrl+j` | Jump down |
| `Ctrl+k` | Jump up |
| `Ctrl+l` | Jump right |
| `b` | Jump left |
| `w` | Jump right |


## Position Movement

| Key | Action |
|---|---|
| `Shift + H` | Move to top of column |
| `Shift + L` | Move to bottom of column |
| `Shift + A` | Move to far left |
| `Shift + I` | Move to far right |
| `Shift + M` | Move to middle of column |


> Note: Some Ctrl key bindings may conflict with terminal shortcuts depending on your terminal emulator.


# Game Controls

| Key | Action |
|---|---|
| `Enter` | Place stone |
| `p` | Pass |
| `r` | Resign |
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


# Roadmap

- [x] Terminal Go board
- [x] Vim motion controls
- [x] GNU Go AI integration
- [x] Stone capture rules
- [x] Undo support
- [ ] Ko rule
- [ ] SGF export/import
- [ ] Game replay
- [ ] Neovim plugin integration


# License

MIT License

See [LICENSE](LICENSE).


# Author

[@yonghun16](https://github.com/yonghun16)
