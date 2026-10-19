import sys
import os
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtMultimedia import QSoundEffect, QSound

def resource_path(relative_path):
    """Returnează calea absolută către fișierul inclus, funcționează și în exe PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

symbols = ['🍒','🍉','🍋','🍇','🔔','⭐']  # ⭐ = wild, înlocuiește orice simbol
# Ponderi: ⭐ apare de 4.5 ori mai rar decât celelalte simboluri (2 vs 9)
symbol_weights = [9, 9, 9, 9, 9, 2]
# Șansa ca un spin să aibă o linie câștigătoare forțată.
# Cu valorile de mai sus: ~15% spin-uri câștigătoare, RTP ~90% (simulat pe 600.000 de spin-uri)
FORCE_WIN_CHANCE = 0.12

def random_row(cols):
    return random.choices(symbols, weights=symbol_weights, k=cols)

def spin_grid(rows=5, cols=5, force_win=False):
    if force_win:
        win_symbol = random.choice(symbols[:-1])  # linia forțată nu e niciodată din stele
        grid = [random_row(cols) for _ in range(rows)]
        # facem o linie orizontală câștigătoare
        grid[random.randint(0, rows-1)] = [win_symbol]*cols
        return grid
    else:
        return [random_row(cols) for _ in range(rows)]

def line_symbol(line):
    """Simbolul care contează pe linie: primul simbol care nu e wild (⭐)."""
    for s in line:
        if s != '⭐':
            return s
    return '⭐'  # linie formată doar din stele

def is_winning_line(line):
    target = line_symbol(line)
    return all(s == target or s == '⭐' for s in line)

def symbol_multiplier(symbol):
    multipliers={'🍒':3,'🍉':4,'🍋':5,'🍇':6,'🔔':10,'⭐':25}
    return multipliers.get(symbol,1)

def get_payout(grid,bet):
    payout=0
    rows, cols=len(grid),len(grid[0])
    for row in grid:
        if is_winning_line(row):
            payout += bet*symbol_multiplier(line_symbol(row))
    for c in range(cols):
        col_symbols=[grid[r][c] for r in range(rows)]
        if is_winning_line(col_symbols):
            payout += bet*symbol_multiplier(line_symbol(col_symbols))
    diag1=[grid[i][i] for i in range(rows)]
    diag2=[grid[i][cols-1-i] for i in range(rows)]
    if is_winning_line(diag1):
        payout += bet*symbol_multiplier(line_symbol(diag1))
    if is_winning_line(diag2):
        payout += bet*symbol_multiplier(line_symbol(diag2))
    return payout

class SlotMachine(QWidget):
    def __init__(self):
        super().__init__()
        self.balance = 1000
        self.initial_balance = 1000
        self.grid_size = 5
        self.current_grid = spin_grid(self.grid_size, self.grid_size)
        self.spin_sound = QSoundEffect()
        self.spin_sound.setSource(QUrl.fromLocalFile(resource_path("spin.wav")))
        self.spin_sound.setLoopCount(QSoundEffect.Infinite)
        self.spin_sound.setVolume(0.5)

        self.setWindowTitle("Lucky Grid Slots")
        self.setGeometry(200, 100, 650, 650)

        main_layout = QVBoxLayout()
        self.balance_label = QLabel(f"Balance: ${self.balance}")
        self.balance_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.balance_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.balance_label)

        # GRID
        self.grid_layout = QGridLayout()
        self.grid_labels = [[QLabel("❓") for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                label = self.grid_labels[i][j]
                label.setFont(QFont("Arial", 20))
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("border:2px solid gold; background-color:darkred; color:yellow;")
                self.grid_layout.addWidget(label, i, j)
        main_layout.addLayout(self.grid_layout)

        # MESSAGE ZONE
        self.message_label = QLabel("")
        self.message_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.message_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.message_label)

        # CONTROLS
        controls_layout = QHBoxLayout()
        self.bet_input = QLineEdit()
        self.bet_input.setPlaceholderText("Enter bet")
        self.bet_input.setFixedWidth(100)

        self.spin_button = QPushButton("SPIN")
        self.spin_button.setFont(QFont("Arial", 16, QFont.Bold))
        self.spin_button.setStyleSheet("background-color:green; color:white; padding:10px; border-radius:10px;")
        self.spin_button.clicked.connect(self.start_spin)

        # Buton restart balance
        self.restart_button = QPushButton("Restart Balance")
        self.restart_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.restart_button.setStyleSheet("background-color:blue; color:white; padding:8px; border-radius:8px;")
        self.restart_button.clicked.connect(self.reset_balance)

        controls_layout.addWidget(self.bet_input)
        controls_layout.addWidget(self.spin_button)
        controls_layout.addWidget(self.restart_button)
        main_layout.addLayout(controls_layout)

        self.setLayout(main_layout)
        self.setStyleSheet("QWidget{background-color:black; color:gold;} QLineEdit{background:white; color:black; font-size:16px;}")

        # Timer pentru animație
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_spin)
        self.spin_steps = 0

    def start_spin(self):
        bet_text = self.bet_input.text()
        if not bet_text.isdigit():
            self.message_label.setText("Invalid bet!")
            return
        bet = int(bet_text)
        if bet <= 0 or bet > self.balance:
            self.message_label.setText("Invalid amount!")
            return

        self.bet = bet
        self.balance -= bet
        self.balance_label.setText(f"Balance: ${self.balance}")
        self.spin_steps = 0
        self.timer.start(100)  # update la 100 ms
        self.spin_sound.play()

        # Reset highlight
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.grid_labels[i][j].setStyleSheet("border:2px solid gold; background-color:darkred; color:yellow;")

    def animate_spin(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.grid_labels[i][j].setText(random.choices(symbols, weights=symbol_weights)[0])

        self.spin_steps += 1
        if self.spin_steps > 10:
            self.timer.stop()
            self.finish_spin()

    def finish_spin(self):
        self.spin_sound.stop()
        force_win = random.random() < FORCE_WIN_CHANCE
        self.current_grid = spin_grid(self.grid_size, self.grid_size, force_win=force_win)
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.grid_labels[i][j].setText(self.current_grid[i][j])

        payout = get_payout(self.current_grid, self.bet)
        self.balance += payout
        self.balance_label.setText(f"Balance: ${self.balance}")

        if payout > 0:
            self.message_label.setText(f"🎉 WIN! You got ${payout}! 🎉")
            self.highlight_winning_lines()
        else:
            self.message_label.setText("No win, try again!")

    def highlight_winning_lines(self):
        rows, cols = self.grid_size, self.grid_size
        # reset stiluri
        for i in range(rows):
            for j in range(cols):
                self.grid_labels[i][j].setStyleSheet("border:2px solid gold; background-color:darkred; color:yellow;")

        # orizontale
        for i, row in enumerate(self.current_grid):
            if is_winning_line(row):
                for j in range(cols):
                    self.grid_labels[i][j].setStyleSheet("border:3px solid gold; background-color:orange; color:black;")

        # verticale
        for j in range(cols):
            col = [self.current_grid[i][j] for i in range(rows)]
            if is_winning_line(col):
                for i in range(rows):
                    self.grid_labels[i][j].setStyleSheet("border:3px solid gold; background-color:orange; color:black;")

        # diagonale
        diag1 = [self.current_grid[i][i] for i in range(rows)]
        diag2 = [self.current_grid[i][cols-1-i] for i in range(rows)]
        if is_winning_line(diag1):
            for i in range(rows):
                self.grid_labels[i][i].setStyleSheet("border:3px solid gold; background-color:orange; color:black;")
        if is_winning_line(diag2):
            for i in range(rows):
                self.grid_labels[i][cols-1-i].setStyleSheet("border:3px solid gold; background-color:orange; color:black;")

    def reset_balance(self):
        self.balance = self.initial_balance
        self.balance_label.setText(f"Balance: ${self.balance}")
        self.message_label.setText("Balance reset! Good luck!")

if __name__=="__main__":
    app=QApplication(sys.argv)
    window=SlotMachine()
    window.show()
    sys.exit(app.exec_())
