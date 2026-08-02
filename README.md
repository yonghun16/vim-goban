# vim-goban

A terminal-based Go (Baduk) game controlled by Vim motions.

`vim-goban` lets you play Go directly in your terminal with familiar Vim keybindings.

Built with Python and powered by GNU Go AI.

![vim-goban](https://github.com/yourname/vim-goban/assets/demo.gif)


## Features

- 🏁 Terminal UI based Go board
- 🎮 Vim motion controls
- 🤖 GNU Go AI integration
- ⚫⚪ Stone capture system
- 🔄 Undo support
- ⏩ Pass / Resign support
- 🌱 Lightweight and keyboard focused


## Screenshot

```text
White ○ captured: 0
Black ● captured: 0
Turn: ● Black
Status: Game loaded successfully!

┌───────────────────────────────────────┐
│ . . . . . . . . . . . . . . . . . . . │
│ . . . . . . . . . . . . . . . . . . . │
│ . . . ○ . . . . . . . . . . . . . . . │
│ . . . + . . . . . + . . . . . + . . . │
│                                       │
│              ...                      │
│                                       │
│ . . . . . . . . . . . . . . . . . . . │
└───────────────────────────────────────┘
```


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

Clone the repository:

```bash
git clone https://github.com/yourname/vim-goban.git

cd vim-goban
```

Install dependencies:

```bash
pip install -e .
```


Run:

```bash
goban
```

or:

```bash
python -m goban.main
```



# Controls

## Movement

vim-goban uses Vim style movement.

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
| `Shift + M` | Move to middle |



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

```
. ● ○ .
. ● ○ .
. ● . .
```

After capture:

```
. ● . .
. ● . .
. ● . .
```


## AI

After placing a stone, GNU Go responds automatically.

GNU Go provides the computer opponent while vim-goban handles:

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
├── tests/
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


Install development dependencies:

```bash
pip install -e ".[dev]"
```



# License

MIT License

See [LICENSE](LICENSE).


# Author

yonghun16
