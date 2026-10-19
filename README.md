# Lucky Grid Slots – PyQt5 Desktop Game

Desktop slot machine game written in Python with a **PyQt5** graphical interface. The player places a bet, spins a 5×5 grid of symbols with an animation and a sound effect, and winning lines are highlighted on the grid. The game is packaged as a standalone Windows executable with **PyInstaller**, so it can run without Python installed.

## Features

- **Graphical interface** built with PyQt5: balance display, 5×5 symbol grid, bet input, *Spin* and *Restart Balance* buttons
- **Spin animation** driven by a `QTimer` (the grid reshuffles every 100 ms before it stops)
- **Sound effect** that loops during the spin (`QSoundEffect`)
- **Win detection** on all rows, all columns and both diagonals, with a different payout multiplier for each symbol
- **Wild symbol** (⭐) that substitutes for any other symbol in a line
- **Winning lines highlighted** on the grid after each spin
- **Bet validation**: rejects non-numeric bets, zero bets and bets above the current balance
- **Standalone `.exe`** built with PyInstaller, with the sound bundled inside and a custom icon

## Tech stack

- Python 3
- PyQt5 (Widgets, QtMultimedia)
- PyInstaller

## Project structure

```
Slots_game/
├── Slots_game.py               # game logic and PyQt5 interface
├── spin.wav                    # spin sound effect
├── slot-machine.ico            # application icon
├── Lucky Grid Slots.spec       # PyInstaller build configuration
└── requirements.txt
```

## How to run

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the game:
   ```bash
   python Slots_game.py
   ```

## How to build the executable (Windows)

```bash
pip install pyinstaller
pyinstaller "Lucky Grid Slots.spec"
```

The executable is created in the `dist/` folder.

## Screenshots

<!-- Add a screenshot of the game window and of a winning spin here -->
