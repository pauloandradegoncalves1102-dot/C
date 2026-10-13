import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QPushButton, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class Calculadora(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora")   
        self.setGeometry(100, 100, 380, 520)   
        self.setFixedSize(380, 520)
        self.expr = ""
        self.grid = QGridLayout(self)
        self.grid.setSpacing(6)
        self.grid.setContentsMargins(12, 12, 12, 12)
        self.setStyleSheet("background-color: #1a1b26;")
        self.display = QLabel("0")
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setFont(QFont("Segoe UI", 28))
        self.display.setStyleSheet("""
            background-color: #24283b; color: white;
            border-radius: 8px; padding: 10px 16px;
        """)
        self.grid.addWidget(self.display, 0, 0, 1, 4)
        self.sub = QLabel("")
        self.sub.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sub.setFont(QFont("Segoe UI", 12))
        self.sub.setStyleSheet("color: #565f89; padding-right: 8px;")
        self.grid.addWidget(self.sub, 1, 0, 1, 4)
        botoes = [
            ("C", "#f7768e", "#e05a70", "white"),
            ("⌫", "#3b3f5c", "#4a4f70", "white"),
            ("%", "#3b3f5c", "#4a4f70", "white"),
            ("÷", "#3b3f5c", "#4a4f70", "white"),
            ("7", "#2a2e42", "#3b3f5c", "white"),
            ("8", "#2a2e42", "#3b3f5c", "white"),
            ("9", "#2a2e42", "#3b3f5c", "white"),
            ("×", "#3b3f5c", "#4a4f70", "white"),
            ("4", "#2a2e42", "#3b3f5c", "white"),
            ("5", "#2a2e42", "#3b3f5c", "white"),
            ("6", "#2a2e42", "#3b3f5c", "white"),
            ("−", "#3b3f5c", "#4a4f70", "white"),
            ("1", "#2a2e42", "#3b3f5c", "white"),
            ("2", "#2a2e42", "#3b3f5c", "white"),
            ("3", "#2a2e42", "#3b3f5c", "white"),
            ("+", "#3b3f5c", "#4a4f70", "white"),
            ("0", "#2a2e42", "#3b3f5c", "white"),
            (".", "#2a2e42", "#3b3f5c", "white"),
            ("=", "#7aa2f7", "#5d84e0", "#1a1b26"),
        ]
        pos = [(2,0),(2,1),(2,2),(2,3),
               (3,0),(3,1),(3,2),(3,3),
               (4,0),(4,1),(4,2),(4,3),
               (5,0),(5,1),(5,2),(5,3),
               (6,0),(6,1),(6,2)]
        for i, (txt, cor, hover, txt_cor) in enumerate(botoes):
            btn = QPushButton(txt)
            btn.setFont(QFont("Segoe UI", 18))
            btn.setFixedHeight(52)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {cor}; color: {txt_cor};
                    border: none; border-radius: 8px;
                    font-size: 18px;
                }}
                QPushButton:hover {{ background-color: {hover}; }}
                QPushButton:pressed {{ background-color: {hover}; }}
            """)
            btn.clicked.connect(lambda checked, t=txt: self.clicar(t))
            r, c = pos[i]
            self.grid.addWidget(btn, r, c)
    def clicar(self, t):
        if t == "C":
            self.expr = ""
            self.sub.setText("")
            self.display.setText("0")
        elif t == "⌫":
            self.expr = self.expr[:-1]
            self.display.setText(self.expr or "0")
        elif t == "÷":
            self.expr += "/"
        elif t == "×":
            self.expr += "*"
        elif t == "−":
            self.expr += "-"
        elif t == "+":
            self.expr += "+"
        elif t == "%":
            self.expr += "/100"
        elif t == "=":
            self.igual()
        else:
            self.expr += t
        if t != "=":
            self.display.setText(self.expr or "0")
    def igual(self):
        try:
            if not self.expr:
                return
            self.sub.setText(self.expr + " =")
            r = eval(self.expr)
            if isinstance(r, float) and r == int(r):
                r = int(r)
            self.expr = str(r)
            self.display.setText(self.expr)
        except:
            self.display.setText("Erro")
            self.expr = ""
    def keyPressEvent(self, e):
        ch = e.text()
        if ch in "0123456789.+-*/%":
            self.clicar(ch)
        elif ch == "\r":
            self.igual()
        elif ch == "\b":
            self.clicar("⌫")
        elif ch == "\x1b":
            self.clicar("C")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calculadora()
    window.show()
    sys.exit(app.exec_())   