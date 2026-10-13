import sys
import urllib.request
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QComboBox,
                             QDoubleSpinBox, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

MOEDAS_BR = {
    "Cruzeiro (CR$) [1942-1967]": 1.0,
    "Cruzeiro Novo (CN$) [1967-1970]": 1000.0,
    "Cruzeiro (CR$) [1970-1983]": 1000.0,
    "Cruzado (Cz$) [1986-1989]": 1000000.0,
    "Cruzado Novo (NCz$) [1989-1990]": 1000000000.0,
    "Cruzeiro (CR$) [1990-1993]": 1000000000.0,
    "Cruzeiro Real (CR$) [1993-1994]": 2750000000000.0,
    "Real (R$) [1994-presente]": 2750000000000000.0,
}
class BuscaCotacoes(QThread):
    pronto = pyqtSignal(dict)
    erro = pyqtSignal(str)
    def run(self):
        try:
            url = "https://open.er-api.com/v6/latest/BRL"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            if data.get("result") == "success":
                self.pronto.emit(data["rates"])
            else:
                self.erro.emit("Falha ao buscar cotações")
        except Exception as e:
            self.erro.emit(str(e))
class Conversor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💰 Conversor de Moedas")
        self.setFixedSize(500, 560)
        self.setStyleSheet("background-color: #1a1b26;")
        self.cotacoes = {}
        self.thread = None
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)
        titulo = QLabel("💰 Conversor de Moedas")
        titulo.setFont(QFont("Segoe UI", 20, QFont.Bold))
        titulo.setStyleSheet("color: #c0caf5;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        self.tipo_label = QLabel("Conversão: Moedas Atuais")
        self.tipo_label.setFont(QFont("Segoe UI", 11))
        self.tipo_label.setStyleSheet("color: #7aa2f7;")
        self.tipo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.tipo_label)
        val_label = QLabel("Valor:")
        val_label.setFont(QFont("Segoe UI", 11))
        val_label.setStyleSheet("color: #9aa5ce;")
        layout.addWidget(val_label)
        self.valor = QDoubleSpinBox()
        self.valor.setDecimals(2)
        self.valor.setRange(0, 999999999)
        self.valor.setValue(100.0)
        self.valor.setFont(QFont("Segoe UI", 14))
        self.valor.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #24283b; color: white;
                border-radius: 6px; padding: 8px 12px;
                border: 1px solid #414868;
            }
        """)
        layout.addWidget(self.valor)
        linha = QHBoxLayout()
        linha.setSpacing(10)
        self.de = QComboBox()
        self.de.setFont(QFont("Segoe UI", 11))
        self.de.setStyleSheet("""
            QComboBox {
                background-color: #24283b; color: white;
                border-radius: 6px; padding: 8px;
                border: 1px solid #414868;
            }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox QAbstractItemView {
                background-color: #24283b; color: white;
                selection-background-color: #414868;
            }
        """)
        linha.addWidget(self.de)
        btn_trocar = QPushButton("⇄")
        btn_trocar.setFixedSize(40, 36)
        btn_trocar.setFont(QFont("Segoe UI", 14))
        btn_trocar.setStyleSheet("""
            QPushButton {
                background-color: #7aa2f7; color: #1a1b26;
                border: none; border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #5d84e0; }
        """)
        btn_trocar.clicked.connect(self.trocar)
        linha.addWidget(btn_trocar)

        self.para = QComboBox()
        self.para.setFont(QFont("Segoe UI", 11))
        self.para.setStyleSheet(self.de.styleSheet())
        linha.addWidget(self.para)
        layout.addLayout(linha)
        btn_conv = QPushButton("Converter")
        btn_conv.setFixedHeight(44)
        btn_conv.setFont(QFont("Segoe UI", 14, QFont.Bold))
        btn_conv.setStyleSheet("""
            QPushButton {
                background-color: #7aa2f7; color: #1a1b26;
                border: none; border-radius: 8px; font-size: 14px;
            }
            QPushButton:hover { background-color: #5d84e0; }
        """)
        btn_conv.clicked.connect(self.converter)
        layout.addWidget(btn_conv)
        self.resultado = QLabel("")
        self.resultado.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.resultado.setStyleSheet("color: #9ece6a; padding: 10px;")
        self.resultado.setAlignment(Qt.AlignCenter)
        self.resultado.setWordWrap(True)
        layout.addWidget(self.resultado)
        self.info = QLabel("")
        self.info.setFont(QFont("Segoe UI", 10))
        self.info.setStyleSheet("color: #565f89;")
        self.info.setAlignment(Qt.AlignCenter)
        self.info.setWordWrap(True)
        layout.addWidget(self.info)
        self.status = QLabel("Carregando cotações...")
        self.status.setFont(QFont("Segoe UI", 10))
        self.status.setStyleSheet("color: #e0af68;")
        self.status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status)
        self.de.addItems(list(MOEDAS_BR.keys()))
        self.para.addItems(list(MOEDAS_BR.keys()))
        self.de.setCurrentIndex(7)  # Real
        self.para.setCurrentIndex(0)  # Cruzeiro antigo
        self.de.currentIndexChanged.connect(self._atualizar_info)
        self.para.currentIndexChanged.connect(self._atualizar_info)
        self._buscar()
    def _buscar(self):
        self.thread = BuscaCotacoes()
        self.thread.pronto.connect(self._cotas_prontas)
        self.thread.erro.connect(self._cotas_erro)
        self.thread.start()
    def _cotas_prontas(self, rates):
        self.cotacoes = rates
        self.status.setText(f"✓ Cotações atualizadas ({rates.get('USD', 0):.4f} USD = 1 BRL)")
        self.status.setStyleSheet("color: #9ece6a;")
        # Adicionar moedas atuais aos comboboxes
        atuais = [
            ("USD", "Dólar Americano ($)", rates.get("USD", 0)),
            ("EUR", "Euro (€)", rates.get("EUR", 0)),
            ("GBP", "Libra Esterlina (£)", rates.get("GBP", 0)),
            ("JPY", "Iene Japonês (¥)", rates.get("JPY", 0)),
            ("CHF", "Franco Suíço (Fr)", rates.get("CHF", 0)),
            ("CAD", "Dólar Canadense (C$)", rates.get("CAD", 0)),
            ("AUD", "Dólar Australiano (A$)", rates.get("AUD", 0)),
            ("CNY", "Yuan Chinês (¥)", rates.get("CNY", 0)),
            ("INR", "Rúpi Indiana (₹)", rates.get("INR", 0)),
            ("ARS", "Peso Argentino ($)", rates.get("ARS", 0)),
            ("CLP", "Peso Chileno ($)", rates.get("CLP", 0)),
            ("MXN", "Peso Mexicano ($)", rates.get("MXN", 0)),
            ("COP", "Peso Colombiano ($)", rates.get("COP", 0)),
            ("UYU", "Peso Uruguaio ($U)", rates.get("UYU", 0)),
            ("BRL", "Real Brasileiro (R$)", 1.0),
        ]
        self.de.clear()
        self.para.clear()
        self.de.addItem("— Moedas Brasileiras —", "")
        for nome in MOEDAS_BR:
            self.de.addItem(nome, nome)
        self.de.addItem("— Moedas Atuais —", "")
        for sigla, nome, _ in atuais:
            self.de.addItem(f"{nome} [{sigla}]", sigla)
        self.para.addItem("— Moedas Brasileiras —", "")
        for nome in MOEDAS_BR:
            self.para.addItem(nome, nome)
        self.para.addItem("— Moedas Atuais —", "")
        for sigla, nome, _ in atuais:
            self.para.addItem(f"{nome} [{sigla}]", sigla)
        self.de.setCurrentIndex(8)   
        self.para.setCurrentIndex(1) 
        self._atualizar_info()

    def _cotas_erro(self, msg):
        self.status.setText(f"⚠ Sem internet — apenas moedas BR disponíveis")
        self.status.setStyleSheet("color: #e0af68;")
        self.de.clear()
        self.para.clear()
        for nome in MOEDAS_BR:
            self.de.addItem(nome, nome)
            self.para.addItem(nome, nome)
        self.de.setCurrentIndex(7)
        self.para.setCurrentIndex(0)
        self._atualizar_info()

    def trocar(self):
        i, j = self.de.currentIndex(), self.para.currentIndex()
        self.de.setCurrentIndex(j)
        self.para.setCurrentIndex(i)

    def _atualizar_info(self):
        de = self.de.currentData()
        para = self.para.currentData()
        if de in MOEDAS_BR and para in MOEDAS_BR:
            taxa = MOEDAS_BR[para] / MOEDAS_BR[de]
            self.info.setText(f"Taxa fixa: 1 {de.split(' [')[0]} = {taxa:.2f} {para.split(' [')[0]}")
        elif de and para and de in self.cotacoes and para in self.cotacoes:
            self.info.setText(f"1 BRL = {self.cotacoes.get(de, 0):.4f} {de} | 1 BRL = {self.cotacoes.get(para, 0):.4f} {para}")
        elif de and para:
            self.info.setText("Convertendo via BRL")
        else:
            self.info.setText("")
    def converter(self):
        v = self.valor.value()
        de = self.de.currentData()
        para = self.para.currentData()
        if not de or not para:
            self.resultado.setText("Selecione moedas válidas")
            self.resultado.setStyleSheet("color: #f7768e;")
            return
        try:
            if de in MOEDAS_BR and para in MOEDAS_BR:
                taxa = MOEDAS_BR[para] / MOEDAS_BR[de]
                resultado = v * taxa
                self.resultado.setText(f"{v:,.2f} → {resultado:,.2f}")
                self.resultado.setStyleSheet("color: #9ece6a;")
                self.info.setText(f"Taxa: 1 {de.split(' [')[0]} = {taxa:,.2f} {para.split(' [')[0]}")
            elif de in self.cotacoes and para in self.cotacoes:
                brl = v / self.cotacoes[de] if de != "BRL" else v
                resultado = brl * self.cotacoes[para] if para != "BRL" else brl
                self.resultado.setText(f"{v:,.2f} → {resultado:,.4f}")
                self.resultado.setStyleSheet("color: #9ece6a;")
                self.info.setText(f"1 {de} = {self.cotacoes[de]:.4f} BRL | 1 {para} = {self.cotacoes[para]:.4f} BRL")
            elif de in MOEDAS_BR and para in self.cotacoes:
                real = v * (MOEDAS_BR["Real (R$) [1994-presente]"] / MOEDAS_BR[de])
                resultado = real * self.cotacoes[para]
                self.resultado.setText(f"{v:,.2f} → {resultado:,.4f}")
                self.resultado.setStyleSheet("color: #9ece6a;")
                self.info.setText(f"Convertido via Real: {real:,.2f} R$ → {para}")
            elif de in self.cotacoes and para in MOEDAS_BR:
                brl = v / self.cotacoes[de] if de != "BRL" else v
                resultado = brl * (MOEDAS_BR[para] / MOEDAS_BR["Real (R$) [1994-presente]"])
                self.resultado.setText(f"{v:,.2f} → {resultado:,.2f}")
                self.resultado.setStyleSheet("color: #9ece6a;")
                self.info.setText(f"Convertido via Real: {brl:,.2f} R$ → {para.split(' [')[0]}")
            else:
                self.resultado.setText("Moedas incompatíveis")
                self.resultado.setStyleSheet("color: #f7768e;")
        except Exception as e:
            self.resultado.setText(f"Erro: {e}")
            self.resultado.setStyleSheet("color: #f7768e;")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Conversor()
    window.show()
    sys.exit(app.exec_())   