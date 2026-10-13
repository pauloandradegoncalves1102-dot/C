import sys
import urllib.request
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QComboBox,
                             QDoubleSpinBox, QScrollArea, QFrame)
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

MOEDAS_MUNDO = {
    "AED": "Dirham Emirati",
    "AFN": "Afghani Afegão",
    "ALL": "Lek Albanês",
    "AMD": "Dram Armênio",
    "ANG": "Florim Antilhano",
    "AOA": "Kwanza Angolano",
    "ARS": "Peso Argentino",
    "AUD": "Dólar Australiano",
    "AWG": "Florim Arubês",
    "AZN": "Manat Azeri",
    "BAM": "Marco Convertível Bósnio",
    "BBD": "Dólar Barbadiano",
    "BDT": "Taka Bangladês",
    "BGN": "Lev Búlgaro",
    "BHD": "Dinar Barmainês",
    "BIF": "Franco Burundês",
    "BMD": "Dólar Bermudiano",
    "BND": "Dólar Bruneano",
    "BOB": "Boliviano Boliviano",
    "BRL": "Real Brasileiro",
    "BSD": "Dólar Bahamiano",
    "BTC": "Bitcoin",
    "BTN": "Ngultrum Butanês",
    "BWP": "Pula Botsuano",
    "BYN": "Rúbel Bielorrusso",
    "BZD": "Dólar Belizenho",
    "CAD": "Dólar Canadense",
    "CDF": "Franco Congolês",
    "CHF": "Franco Suíço",
    "CLP": "Peso Chileno",
    "CNY": "Yuan Chinês",
    "COP": "Peso Colombiano",
    "CRC": "Colón Costarriquenho",
    "CUC": "Peso Convertível Cubano",
    "CUP": "Peso Cubano",
    "CVE": "Escudo Caboverdiano",
    "CZK": "Coroa Tcheca",
    "DJF": "Franco Djiboutiano",
    "DKK": "Coroa Dinamarquesa",
    "DOP": "Peso Dominicano",
    "DZD": "Dinar Argelino",
    "EGP": "Libra Egípcia",
    "ERN": "Nakfa Eritreu",
    "ETB": "Birr Etíope",
    "EUR": "Euro",
    "FJD": "Dólar Fijiano",
    "FKP": "Libra das Malvinas",
    "GBP": "Libra Esterlina",
    "GEL": "Lari Georgiano",
    "GHS": "Cedi Ganes",
    "GIP": "Libra de Gilbraltar",
    "GMD": "Dalasi Gâmbiano",
    "GNF": "Franco Guineense",
    "GTQ": "Quetzal Guatemalho",
    "GYD": "Dólar Guianense",
    "HKD": "Dólar de Hong Kong",
    "HNL": "Lempira Hondurenho",
    "HRK": "Kuna Croata",
    "HTG": "Gourde Haitiano",
    "HUF": "Florim Húngaro",
    "IDR": "Rupia Indonésia",
    "ILS": "Novo Shekel Israelense",
    "INR": "Rúpi Indiana",
    "IQD": "Dinar Iraquiano",
    "IRR": "Rial Iraniense",
    "ISK": "Coroa Islandesa",
    "JMD": "Dólar Jamaicano",
    "JOD": "Dinar Jordaniano",
    "JPY": "Iene Japonês",
    "KES": "Xelim Queniano",
    "KGS": "Som Quirguistão",
    "KHR": "Riel Cambojano",
    "KMF": "Franco Comorense",
    "KRW": "Won Coreano",
    "KWD": "Dinar Kuwaitiano",
    "KYD": "Dólar das Cayman",
    "KZT": "Tenge Cazaque",
    "LAK": "Kip Laociano",
    "LBP": "Libra Libanesa",
    "LKR": "Rúpi Sri Lankan",
    "LRD": "Dólar Liberiano",
    "LSL": "Loti Lesotiano",
    "LYD": "Dinar Líbio",
    "MAD": "Dirham Marroquino",
    "MDL": "Leu Moldavo",
    "MGA": "Ariary Malgaxe",
    "MKD": "Denar Macedônio",
    "MMK": "Kyat Mianmar",
    "MNT": "Tugrik Mongol",
    "MOP": "Pataca de Macau",
    "MRU": "Ouguiya Mauritano",
    "MUR": "Rupia Mauricana",
    "MVR": "Rufiyaa Maldiva",
    "MWK": "Kwacha Malauiano",
    "MXN": "Peso Mexicano",
    "MYR": "Ringgit Malai",
    "MZN": "Metical Moçambicano",
    "NAD": "Dólar Namibiano",
    "NGN": "Naira Nigeriano",
    "NIO": "Córdoba Nicaraguense",
    "NOK": "Coroa Norueguesa",
    "NPR": "Rúpi Nepalesa",
    "NZD": "Dólar Neo-Zelandês",
    "OMR": "Rial Omanense",
    "PAB": "Balboa Panamenho",
    "PEN": "Sol Peruano",
    "PGK": "Kina Papuano",
    "PHP": "Peso Filipino",
    "PKR": "Rupia Paquistanesa",
    "PLN": "Zloty Polonês",
    "PYG": "Guarani Paraguaio",
    "QAR": "Rial Qatari",
    "RON": "Leu Romeno",
    "RSD": "Dinar Sérvio",
    "RUB": "Rúbel Russo",
    "RWF": "Franco Ruandês",
    "SAR": "Rial Saudita",
    "SBD": "Dólar Salomonense",
    "SCR": "Dólar Sechelense",
    "SDG": "Libra Sudanesa",
    "SEK": "Coroa Sueca",
    "SGD": "Dólar Singapuriano",
    "SHP": "Libra de Santa Helena",
    "SLE": "Leoa Serra-Leonense",
    "SOS": "Xelim Somali",
    "SRD": "Dólar Surinamês",
    "SSP": "Xelim Sud-Sudanês",
    "STN": "Dobra Santomeense",
    "SVC": "Colón Salvadorenho",
    "SYP": "Libra Síria",
    "SZL": "Lilangeni Suasilandês",
    "THB": "Baht Tailandês",
    "TJS": "Somoni Tajique",
    "TMT": "Manat Turcomene",
    "TND": "Dinar Tunisiano",
    "TOP": "Pa'anga Tongan",
    "TRY": "Lira Turca",
    "TTD": "Dólar Trinidiano",
    "TWD": "Novo Dólar de Taiwan",
    "TZS": "Xelim Tanzanian",
    "UAH": "Hryvnia Ucraniano",
    "UGX": "Xelim Uguandês",
    "USD": "Dólar Americano",
    "UYU": "Peso Uruguaio",
    "UZS": "Som Uzbeque",
    "VEF": "Bolivar Venezuelano",
    "VND": "Dong Vietnamita",
    "VUV": "Vatu Vanuatu",
    "WST": "Tala Samoa",
    "XAF": "Franco CFA (África Central)",
    "XCD": "Dólar Caribenho",
    "XOF": "Franco CFA (África Ocidental)",
    "XPF": "Franco CFP",
    "YER": "Rial Iemenita",
    "ZAR": "Rand Sul-Africano",
    "ZMW": "Kwacha Zambiano",
    "ZWL": "Dólar Zimbabuense",
}
class BuscaCotacoes(QThread):
    pronto = pyqtSignal(dict)
    erro = pyqtSignal(str)
    def run(self):
        try:
            url = "https://open.er-api.com/v6/latest/BRL"
            with urllib.request.urlopen(url, timeout=10) as resp:
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
        self.setFixedSize(540, 620)
        self.setStyleSheet("background-color: #1a1b26;")
        self.cotacoes = {}
        self.thread = None
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(14, 14, 14, 14)
        titulo = QLabel("💰 Conversor de Moedas")
        titulo.setFont(QFont("Segoe UI", 18, QFont.Bold))
        titulo.setStyleSheet("color: #c0caf5;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        self.valor = QDoubleSpinBox()
        self.valor.setDecimals(4)
        self.valor.setRange(0, 999999999999)
        self.valor.setValue(100.0)
        self.valor.setFont(QFont("Segoe UI", 14))
        self.valor.setStyleSheet("QDoubleSpinBox{background:#24283b;color:white;border-radius:6px;padding:8px 12px;border:1px solid #414868;}")
        layout.addWidget(self.valor)
        lbl_de = QLabel("De:")
        lbl_de.setFont(QFont("Segoe UI", 10))
        lbl_de.setStyleSheet("color:#9aa5ce;")
        layout.addWidget(lbl_de)
        self.de = QComboBox()
        self.de.setFont(QFont("Segoe UI", 11))
        self.de.setStyleSheet("QComboBox{background:#24283b;color:white;border-radius:6px;padding:8px;border:1px solid #414868;}QComboBox QAbstractItemView{background:#24283b;color:white;selection-background-color:#414868;}")
        layout.addWidget(self.de)
        btn_trocar = QPushButton("⇄ Trocar")
        btn_trocar.setFixedHeight(34)
        btn_trocar.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_trocar.setStyleSheet("QPushButton{background:#7aa2f7;color:#1a1b26;border:none;border-radius:6px;}QPushButton:hover{background:#5d84e0;}")
        btn_trocar.clicked.connect(self.trocar)
        layout.addWidget(btn_trocar)
        lbl_para = QLabel("Para:")
        lbl_para.setFont(QFont("Segoe UI", 10))
        lbl_para.setStyleSheet("color:#9aa5ce;")
        layout.addWidget(lbl_para)
        self.para = QComboBox()
        self.para.setFont(QFont("Segoe UI", 11))
        self.para.setStyleSheet(self.de.styleSheet())
        layout.addWidget(self.para)
        btn_conv = QPushButton("🔄 Converter")
        btn_conv.setFixedHeight(44)
        btn_conv.setFont(QFont("Segoe UI", 14, QFont.Bold))
        btn_conv.setStyleSheet("QPushButton{background:#7aa2f7;color:#1a1b26;border:none;border-radius:8px;font-size:14px;}QPushButton:hover{background:#5d84e0;}")
        btn_conv.clicked.connect(self.converter)
        layout.addWidget(btn_conv)
        self.resultado = QLabel("")
        self.resultado.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.resultado.setStyleSheet("color:#9ece6a;padding:8px;")
        self.resultado.setAlignment(Qt.AlignCenter)
        self.resultado.setWordWrap(True)
        layout.addWidget(self.resultado)
        self.info = QLabel("")
        self.info.setFont(QFont("Segoe UI", 10))
        self.info.setStyleSheet("color:#565f89;")
        self.info.setAlignment(Qt.AlignCenter)
        self.info.setWordWrap(True)
        layout.addWidget(self.info)
        self.status = QLabel("⏳ Carregando cotações...")
        self.status.setFont(QFont("Segoe UI", 10))
        self.status.setStyleSheet("color:#e0af68;")
        self.status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status)
        self._preencher()
        self._buscar()
    def _preencher(self):
        self.de.clear()
        self.para.clear()
        self.de.addItem("— 🇧🇷 Moedas Brasileiras —", "")
        for nome in MOEDAS_BR:
            self.de.addItem(nome, nome)
        self.de.addItem("— 🌍 Moedas do Mundo —", "")
        for sigla in sorted(MOEDAS_MUNDO.keys()):
            self.de.addItem(f"{MOEDAS_MUNDO[sigla]} [{sigla}]", sigla)
        self.para.addItem("— 🇧🇷 Moedas Brasileiras —", "")
        for nome in MOEDAS_BR:
            self.para.addItem(nome, nome)
        self.para.addItem("— 🌍 Moedas do Mundo —", "")
        for sigla in sorted(MOEDAS_MUNDO.keys()):
            self.para.addItem(f"{MOEDAS_MUNDO[sigla]} [{sigla}]", sigla)
        self.de.setCurrentIndex(8)   # Real
        self.para.setCurrentIndex(1)  # Cruzeiro antigo
    def _buscar(self):
        self.thread = BuscaCotacoes()
        self.thread.pronto.connect(self._prontas)
        self.thread.erro.connect(self._erro)
        self.thread.start()
    def _prontas(self, rates):
        self.cotacoes = rates
        n = len(rates)
        self.status.setText(f"✓ {n} moedas carregadas | 1 BRL = {rates.get('USD',0):.4f} USD")
        self.status.setStyleSheet("color:#9ece6a;")
    def _erro(self, msg):
        self.status.setText(f"⚠ Sem internet — apenas moedas BR")
        self.status.setStyleSheet("color:#e0af68;")
    def trocar(self):
        i, j = self.de.currentIndex(), self.para.currentIndex()
        self.de.setCurrentIndex(j)
        self.para.setCurrentIndex(i)
    def converter(self):
        v = self.valor.value()
        de = self.de.currentData()
        para = self.para.currentData()
        if not de or not para:
            self.resultado.setText("Selecione moedas válidas")
            self.resultado.setStyleSheet("color:#f7768e;")
            return
        try:
            if de in MOEDAS_BR and para in MOEDAS_BR:
                taxa = MOEDAS_BR[para] / MOEDAS_BR[de]
                r = v * taxa
                self.resultado.setText(f"{v:,.4f} → {r:,.6f}")
                self.info.setText(f"Taxa fixa: 1 {de.split(' [')[0]} = {taxa:,.4f} {para.split(' [')[0]}")
            elif de in self.cotacoes and para in self.cotacoes:
                brl = v / self.cotacoes[de] if de != "BRL" else v
                r = brl * self.cotacoes[para] if para != "BRL" else brl
                self.resultado.setText(f"{v:,.4f} → {r:,.6f}")
                self.info.setText(f"1 {de} = {self.cotacoes[de]:.6f} BRL | 1 {para} = {self.cotacoes[para]:.6f} BRL")
            elif de in MOEDAS_BR and para in self.cotacoes:
                real = v * (MOEDAS_BR["Real (R$) [1994-presente]"] / MOEDAS_BR[de])
                r = real * self.cotacoes[para]
                self.resultado.setText(f"{v:,.4f} → {r:,.6f}")
                self.info.setText(f"Via Real: {real:,.4f} R$ → {para}")
            elif de in self.cotacoes and para in MOEDAS_BR:
                brl = v / self.cotacoes[de] if de != "BRL" else v
                r = brl * (MOEDAS_BR[para] / MOEDAS_BR["Real (R$) [1994-presente]"])
                self.resultado.setText(f"{v:,.4f} → {r:,.6f}")
                self.info.setText(f"Via Real: {brl:,.4f} R$ → {para.split(' [')[0]}")
            else:
                self.resultado.setText("Moedas incompatíveis")
                self.resultado.setStyleSheet("color:#f7768e;")
            self.resultado.setStyleSheet("color:#9ece6a;")
        except Exception as e:
            self.resultado.setText(f"Erro: {e}")
            self.resultado.setStyleSheet("color:#f7768e;")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Conversor()
    window.show()
    sys.exit(app.exec_())   