import customtkinter as ctk
import urllib.request
import json
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
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
    "AED":"Dirham Emirati","AFN":"Afghani Afegão","ALL":"Lek Albanês","AMD":"Dram Armênio",
    "ANG":"Florim Antilhano","AOA":"Kwanza Angolano","ARS":"Peso Argentino","AUD":"Dólar Australiano",
    "AWG":"Florim Arubês","AZN":"Manat Azeri","BAM":"Marco Bósnio","BBD":"Dólar Barbadiano",
    "BDT":"Taka Bangladês","BGN":"Lev Búlgaro","BHD":"Dinar Barmainês","BIF":"Franco Burundês",
    "BMD":"Dólar Bermudiano","BND":"Dólar Bruneano","BOB":"Boliviano","BRL":"Real Brasileiro",
    "BSD":"Dólar Bahamiano","BTC":"Bitcoin","BTN":"Ngultrum Butanês","BWP":"Pula Botsuano",
    "BYN":"Rúbel Bielorrusso","BZD":"Dólar Belizenho","CAD":"Dólar Canadense","CDF":"Franco Congolês",
    "CHF":"Franco Suíço","CLP":"Peso Chileno","CNY":"Yuan Chinês","COP":"Peso Colombiano",
    "CRC":"Colón Costarriquenho","CUP":"Peso Cubano","CVE":"Escudo Caboverdiano","CZK":"Coroa Tcheca",
    "DJF":"Franco Djiboutiano","DKK":"Coroa Dinamarquesa","DOP":"Peso Dominicano","DZD":"Dinar Argelino",
    "EGP":"Libra Egípcia","ERN":"Nakfa Eritreu","ETB":"Birr Etíope","EUR":"Euro",
    "FJD":"Dólar Fijiano","GBP":"Libra Esterlina","GEL":"Lari Georgiano","GHS":"Cedi Ganes",
    "GMD":"Dalasi Gâmbiano","GNF":"Franco Guineense","GTQ":"Quetzal Guatemalho","GYD":"Dólar Guianense",
    "HKD":"Dólar Hong Kong","HNL":"Lempira Hondurenho","HRK":"Kuna Croata","HTG":"Gourde Haitiano",
    "HUF":"Florim Húngaro","IDR":"Rupia Indonésia","ILS":"Shekel Israelense","INR":"Rúpi Indiana",
    "IQD":"Dinar Iraquiano","IRR":"Rial Iraniense","ISK":"Coroa Islandesa","JMD":"Dólar Jamaicano",
    "JOD":"Dinar Jordaniano","JPY":"Iene Japonês","KES":"Xelim Queniano","KGS":"Som Quirguistão",
    "KHR":"Riel Cambojano","KMF":"Franco Comorense","KRW":"Won Coreano","KWD":"Dinar Kuwaitiano",
    "KYD":"Dólar Cayman","KZT":"Tenge Cazaque","LAK":"Kip Laociano","LBP":"Libra Libanesa",
    "LKR":"Rúpi Sri Lankan","LRD":"Dólar Liberiano","LSL":"Loti Lesotiano","LYD":"Dinar Líbio",
    "MAD":"Dirham Marroquino","MDL":"Leu Moldavo","MGA":"Ariary Malgaxe","MKD":"Denar Macedônio",
    "MMK":"Kyat Mianmar","MNT":"Tugrik Mongol","MOP":"Pataca Macau","MRU":"Ouguiya Mauritano",
    "MUR":"Rupia Mauricana","MVR":"Rufiyaa Maldiva","MWK":"Kwacha Malauiano","MXN":"Peso Mexicano",
    "MYR":"Ringgit Malai","MZN":"Metical Moçambicano","NAD":"Dólar Namibiano","NGN":"Naira Nigeriano",
    "NIO":"Córdoba Nicaraguense","NOK":"Coroa Norueguesa","NPR":"Rúpi Nepalesa","NZD":"Dólar Neo-Zelandês",
    "OMR":"Rial Omanense","PAB":"Balboa Panamenho","PEN":"Sol Peruano","PGK":"Kina Papuano",
    "PHP":"Peso Filipino","PKR":"Rupia Paquistanesa","PLN":"Zloty Polonês","PYG":"Guarani Paraguaio",
    "QAR":"Rial Qatari","RON":"Leu Romeno","RSD":"Dinar Sérvio","RUB":"Rúbel Russo",
    "RWF":"Franco Ruandês","SAR":"Rial Saudita","SBD":"Dólar Salomonense","SCR":"Dólar Sechelense",
    "SDG":"Libra Sudanesa","SEK":"Coroa Sueca","SGD":"Dólar Singapuriano","SHP":"Libra Santa Helena",
    "SLE":"Leoa Serra-Leonense","SOS":"Xelim Somali","SRD":"Dólar Surinamês","SSP":"Xelim Sud-Sudanês",
    "STN":"Dobra Santomeense","SVC":"Colón Salvadorenho","SYP":"Libra Síria","SZL":"Lilangeni Suasilandês",
    "THB":"Baht Tailandês","TJS":"Somoni Tajique","TMT":"Manat Turcomene","TND":"Dinar Tunisiano",
    "TOP":"Pa'anga Tongan","TRY":"Lira Turca","TTD":"Dólar Trinidiano","TWD":"Dólar Taiwan",
    "TZS":"Xelim Tanzanian","UAH":"Hryvnia Ucraniano","UGX":"Xelim Uguandês","USD":"Dólar Americano",
    "UYU":"Peso Uruguaio","UZS":"Som Uzbeque","VEF":"Bolivar Venezuelano","VND":"Dong Vietnamita",
    "VUV":"Vatu Vanuatu","WST":"Tala Samoa","XAF":"Franco CFA Central","XCD":"Dólar Caribenho",
    "XOF":"Franco CFA Ocidental","XPF":"Franco CFP","YER":"Rial Iemenita","ZAR":"Rand Sul-Africano",
    "ZMW":"Kwacha Zambiano","ZWL":"Dólar Zimbabuense",
}
class Conversor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("💰 Conversor de Moedas")
        self.geometry("520x650")
        self.resizable(False, False)
        self.configure(fg_color="#1a1b26")
        self.cotacoes = {}
        ctk.CTkLabel(self, text="💰 Conversor de Moedas",
                     font=("Segoe UI", 20, "bold"), text_color="#c0caf5").pack(pady=(14, 6))
        ctk.CTkLabel(self, text="Valor:", font=("Segoe UI", 12), text_color="#9aa5ce").pack(anchor="w", padx=16)
        self.valor = ctk.CTkEntry(self, font=("Segoe UI", 16), placeholder_text="Digite o valor")
        self.valor.insert(0, "100")
        self.valor.pack(fill="x", padx=16, pady=(2, 10))
        ctk.CTkLabel(self, text="De:", font=("Segoe UI", 12), text_color="#9aa5ce").pack(anchor="w", padx=16)
        self.de = ctk.CTkComboBox(self, font=("Segoe UI", 12), state="readonly")
        self.de.pack(fill="x", padx=16, pady=(2, 4))
        ctk.CTkButton(self, text="⇄ Trocar", height=32,
                      fg_color="#7aa2f7", hover_color="#5d84e0", text_color="#1a1b26",
                      font=("Segoe UI", 11, "bold"), command=self.trocar).pack(pady=4)
        ctk.CTkLabel(self, text="Para:", font=("Segoe UI", 12), text_color="#9aa5ce").pack(anchor="w", padx=16)
        self.para = ctk.CTkComboBox(self, font=("Segoe UI", 12), state="readonly")
        self.para.pack(fill="x", padx=16, pady=(2, 10))
        ctk.CTkButton(self, text="🔄 Converter", height=44,
                      fg_color="#7aa2f7", hover_color="#5d84e0", text_color="#1a1b26",
                      font=("Segoe UI", 14, "bold"), command=self.converter).pack(fill="x", padx=16, pady=6)
        self.resultado = ctk.CTkLabel(self, text="", font=("Segoe UI", 20, "bold"),
                                       text_color="#9ece6a", wraplength=480)
        self.resultado.pack(pady=8)
        self.info = ctk.CTkLabel(self, text="", font=("Segoe UI", 10),
                                  text_color="#565f89", wraplength=480)
        self.info.pack(pady=2)
        self.status = ctk.CTkLabel(self, text="⏳ Carregando cotações...",
                                    font=("Segoe UI", 10), text_color="#e0af68")
        self.status.pack(pady=(4, 10))
        self._preencher()
        threading.Thread(target=self._buscar, daemon=True).start()
    def _preencher(self):
        itens_de = ["— 🇧🇷 Moedas Brasileiras —"]
        itens_de += list(MOEDAS_BR.keys())
        itens_de.append("— 🌍 Moedas do Mundo —")
        itens_de += [f"{MOEDAS_MUNDO[s]} [{s}]" for s in sorted(MOEDAS_MUNDO)]
        self.de.configure(values=itens_de)
        self.para.configure(values=itens_de)
        self.de.set("Real (R$) [1994-presente]")
        self.para.set("Cruzeiro (CR$) [1942-1967]")
    def _buscar(self):
        try:
            url = "https://open.er-api.com/v6/latest/BRL"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            if data.get("result") == "success":
                self.cotacoes = data["rates"]
                self.after(0, lambda: self.status.configure(
                    text=f"✓ {len(self.cotacoes)} moedas | 1 BRL = {self.cotacoes.get('USD',0):.4f} USD",
                    text_color="#9ece6a"))
        except Exception as e:
            self.after(0, lambda: self.status.configure(
                text=f"⚠ Sem internet — apenas moedas BR", text_color="#e0af68"))
    def trocar(self):
        d, p = self.de.get(), self.para.get()
        self.de.set(p)
        self.para.set(d)
    def converter(self):
        try:
            v = float(self.valor.get().replace(",", "."))
        except:
            self.resultado.configure(text="Valor inválido", text_color="#f7768e")
            return
        de = self.de.get()
        para = self.para.get()
        if de in MOEDAS_BR and para in MOEDAS_BR:
            taxa = MOEDAS_BR[para] / MOEDAS_BR[de]
            r = v * taxa
            self.resultado.configure(text=f"{v:,.4f} → {r:,.6f}", text_color="#9ece6a")
            self.info.configure(text=f"Taxa fixa: 1 {de.split(' [')[0]} = {taxa:,.4f} {para.split(' [')[0]}")
        elif de in self.cotacoes and para in self.cotacoes:
            brl = v / self.cotacoes[de] if de != "BRL" else v
            r = brl * self.cotacoes[para] if para != "BRL" else brl
            self.resultado.configure(text=f"{v:,.4f} → {r:,.6f}", text_color="#9ece6a")
            self.info.configure(text=f"1 {de} = {self.cotacoes[de]:.6f} BRL | 1 {para} = {self.cotacoes[para]:.6f} BRL")
        elif de in MOEDAS_BR and para in self.cotacoes:
            real = v * (MOEDAS_BR["Real (R$) [1994-presente]"] / MOEDAS_BR[de])
            r = real * self.cotacoes[para]
            self.resultado.configure(text=f"{v:,.4f} → {r:,.6f}", text_color="#9ece6a")
            self.info.configure(text=f"Via Real: {real:,.4f} R$ → {para}")
        elif de in self.cotacoes and para in MOEDAS_BR:
            brl = v / self.cotacoes[de] if de != "BRL" else v
            r = brl * (MOEDAS_BR[para] / MOEDAS_BR["Real (R$) [1994-presente]"])
            self.resultado.configure(text=f"{v:,.4f} → {r:,.6f}", text_color="#9ece6a")
            self.info.configure(text=f"Via Real: {brl:,.4f} R$ → {para.split(' [')[0]}")
        else:
            self.resultado.configure(text="Selecione moedas válidas", text_color="#f7768e")
if __name__ == "__main__":
    app = Conversor()
    app.mainloop()   