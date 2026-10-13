import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import math
import cmath
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def generate_sinusoid(amplitude=1.0, frequency=1.0, phase_deg=0.0,
                      t_start=0.0, t_end=2.0, samples=1000):
    t = np.linspace(t_start, t_end, samples)
    omega = 2 * np.pi * frequency
    phase = np.radians(phase_deg)
    y = amplitude * np.sin(omega * t + phase)
    return t, y
def generate_square(amplitude=1.0, frequency=1.0, t_start=0.0, t_end=2.0, samples=1000):
    t = np.linspace(t_start, t_end, samples)
    y = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
    return t, y
def generate_sawtooth(amplitude=1.0, frequency=1.0, t_start=0.0, t_end=2.0, samples=1000):
    t = np.linspace(t_start, t_end, samples)
    y = amplitude * (2 * (frequency * t % 1) - 1)
    return t, y
def generate_triangle(amplitude=1.0, frequency=1.0, t_start=0.0, t_end=2.0, samples=1000):
    t = np.linspace(t_start, t_end, samples)
    y = amplitude * (2 / np.pi) * np.arcsin(np.sin(2 * np.pi * frequency * t))
    return t, y
def fourier_square(n_harmonics, t_start=0.0, t_end=2.0, samples=2000):
    """Soma de harmônicos para aproximar onda quadrada"""
    t = np.linspace(t_start, t_end, samples)
    y = np.zeros_like(t)
    for n in range(1, n_harmonics + 1, 2):  # só ímpares
        y += (4 / (n * np.pi)) * np.sin(n * 2 * np.pi * t)
    return t, y
def rlc_series_response(R, L, C, f_start=0.1, f_end=10000, n_points=200):
    """Resposta em frequência de RLC série (magnitude em dB)"""
    f = np.logspace(np.log10(f_start), np.log10(f_end), n_points)
    omega = 2 * np.pi * f
    Z = R + 1j * (omega * L - 1 / (omega * C))
    H = 1.0 / Z  # corrente / tensão
    mag_db = 20 * np.log10(np.abs(H) + 1e-15)
    phase = np.angle(H, deg=True)
    return f, mag_db, phase
def bode_rc_lowpass(R, C, f_start=0.1, f_end=1e6, n_points=300):
    """Bode de passa-baixa RC"""
    f = np.logspace(np.log10(f_start), np.log10(f_end), n_points)
    omega = 2 * np.pi * f
    H = 1.0 / (1.0 + 1j * omega * R * C)
    mag_db = 20 * np.log10(np.abs(H) + 1e-15)
    phase = np.angle(H, deg=True)
    fc = 1 / (2 * np.pi * R * C)
    return f, mag_db, phase, fc
class SignalViewer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("📡 Visualizador de Sinais & Circuitos")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self._build_ui()
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        sidebar.grid_propagate(False)
        ctk.CTkLabel(sidebar, text="📡 Visualizador",
                     font=("Segoe UI", 18, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(sidebar, text="Sinais & Circuitos",
                     font=("Segoe UI", 12), text_color="gray").pack(pady=(0, 20))
        self.tabs = {
            "Senoide": self._tab_sinusoid,
            "Onda Quadrada": self._tab_square,
            "Dente de Serra": self._tab_sawtooth,
            "Triangular": self._tab_triangle,
            "Fourier (Quadrada)": self._tab_fourier,
            "RLC Série": self._tab_rlc,
            "Passa-Baixa RC": self._tab_rc,
            "Fasores": self._tab_phasors,
        }
        for name, method in self.tabs.items():
            btn = ctk.CTkButton(
                sidebar, text=name, anchor="w",
                font=("Segoe UI", 13),
                height=38,
                command=method
            )
            btn.pack(fill="x", padx=10, pady=2)
        content = ctk.CTkFrame(self, corner_radius=0)
        content.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(0, 10), pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=3)
        content.grid_rowconfigure(0, weight=1)
        self.params_frame = ctk.CTkFrame(content, fg_color="transparent")
        self.params_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.plot_frame = ctk.CTkFrame(content, fg_color="transparent")
        self.plot_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.explain_frame = ctk.CTkFrame(content, fg_color="transparent")
        self.explain_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        self._tab_sinusoid()
    def _clear_params(self):
        for w in self.params_frame.winfo_children():
            w.destroy()
    def _clear_plot(self):
        for w in self.plot_frame.winfo_children():
            w.destroy()
    def _clear_explain(self):
        for w in self.explain_frame.winfo_children():
            w.destroy()
    def _add_param(self, label, default, min_val, max_val, unit="", row=0, col=0):
        frame = ctk.CTkFrame(self.params_frame, fg_color="transparent")
        frame.grid(row=row, column=col, padx=8, pady=4, sticky="w")
        ctk.CTkLabel(frame, text=label, font=("Segoe UI", 11)).pack(anchor="w")
        var = ctk.DoubleVar(value=default)
        entry = ctk.CTkEntry(frame, textvariable=var, width=80, font=("Segoe UI", 12))
        entry.pack(anchor="w")
        ctk.CTkLabel(frame, text=unit, font=("Segoe UI", 10), text_color="gray").pack(anchor="w")
        return var
    def _add_button(self, text, command, row=0, col=0):
        btn = ctk.CTkButton(
            self.params_frame, text=text,
            font=("Segoe UI", 12, "bold"),
            fg_color="#1a5276", hover_color="#2980b9",
            command=command
        )
        btn.grid(row=row, column=col, padx=8, pady=4)
        return btn
    def _plot(self, plot_func, title=""):
        """Cria o canvas matplotlib dentro do plot_frame"""
        self._clear_plot()
        fig = Figure(figsize=(10, 5), dpi=100, facecolor="#1e1e2e")
        fig.patch.set_facecolor("#1e1e2e")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#1e1e2e")
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")
        ax.grid(True, alpha=0.3, color="gray")
        for spine in ax.spines.values():
            spine.set_color("gray")

        plot_func(ax)
        if title:
            ax.set_title(title, fontsize=12, fontweight="bold")
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    def _explain(self, title, formula, description, extra=""):
        """Mostra a explicação no painel inferior"""
        self._clear_explain()
        frame = ctk.CTkFrame(self.explain_frame, fg_color="#2a2a3e", corner_radius=8)
        frame.pack(fill="x", pady=2)
        ctk.CTkLabel(frame, text=f"📖 {title}",
                     font=("Segoe UI", 13, "bold"), text_color="#64b5f6").pack(anchor="w", padx=15, pady=(10, 2))
        ctk.CTkLabel(frame, text=formula,
                     font=("Consolas", 12), text_color="#ffab40").pack(anchor="w", padx=15)
        ctk.CTkLabel(frame, text=description,
                     font=("Segoe UI", 11), text_color="white",
                     justify="left", wraplength=900).pack(anchor="w", padx=15, pady=(4, 0))
        if extra:
            ctk.CTkLabel(frame, text=extra,
                         font=("Segoe UI", 10), text_color="gray",
                         justify="left", wraplength=900).pack(anchor="w", padx=15, pady=(0, 10))
        else:
            frame.update_idletasks()
    def _tab_sinusoid(self):
        self._clear_params()
        self._clear_explain()
        self._sin_amp = self._add_param("Amplitude (V)", 1.0, 0.1, 10, "V", 0, 0)
        self._sin_freq = self._add_param("Frequência (Hz)", 1.0, 0.1, 10, "Hz", 0, 1)
        self._sin_phase = self._add_param("Fase (°)", 0.0, -360, 360, "°", 0, 2)
        self._sin_cycles = self._add_param("Períodos", 2.0, 1, 10, "T", 0, 3)
        self._add_button("▶ Gerar", self._plot_sinusoid, 0, 4)
        self._explain(
            "Senoide (Sinal Senoidal)",
            "v(t) = A · sin(ωt + φ)     onde: ω = 2πf,  T = 1/f",
            "A senoide é o sinal mais fundamental em engenharia elétrica. "
            "Ela representa a forma de onda da corrente alternada (CA) nas tomadas. "
            "A amplitude (A) é o valor de pico, a frequência (f) quantas vezes ela "
            "cicla por segundo (Hz), e a fase (φ) desloca o sinal no tempo. "
            "O valor RMS (eficaz) é A/√2 — é o que o voltímetro mede (ex: 220V RMS ≈ 311V de pico).",
            "Relações: ω = 2πf | T = 1/f | Vrms = A/√2 | Vpp = 2A"
        )
    def _plot_sinusoid(self):
        A = self._sin_amp.get()
        f = self._sin_freq.get()
        phi = self._sin_phase.get()
        cycles = self._sin_cycles.get()
        T = 1 / f
        t_end = cycles * T
        def draw(ax):
            t, y = generate_sinusoid(A, f, phi, 0, t_end)
            ax.plot(t, y, color="#4fc3f7", linewidth=2, label="v(t)")
            ax.axhline(0, color="gray", linewidth=0.5, linestyle="--")
            ax.axhline(A, color="red", linewidth=0.5, linestyle=":", alpha=0.7)
            ax.axhline(-A, color="red", linewidth=0.5, linestyle=":", alpha=0.7)
            ax.axhline(A / np.sqrt(2), color="orange", linewidth=0.5, linestyle=":", alpha=0.7)
            ax.axhline(-A / np.sqrt(2), color="orange", linewidth=0.5, linestyle=":", alpha=0.7)
            ax.annotate(f"A = {A:.2f} V", xy=(0, A), fontsize=9, color="red")
            ax.annotate(f"Vrms = {A/np.sqrt(2):.2f} V", xy=(0, A/np.sqrt(2)), fontsize=9, color="orange")
            ax.set_xlabel("Tempo (s)")
            ax.set_ylabel("Tensão (V)")
            ax.legend(loc="upper right", facecolor="#2a2a3e", edgecolor="gray", labelcolor="white")
            # Marca um período
            ax.axvspan(0, T, alpha=0.1, color="green")
            ax.annotate(f"T = {T*1000:.2f} ms", xy=(T/2, A*0.85), fontsize=9, color="green")
        self._plot(draw, f"Senoide: A={A}V, f={f}Hz, φ={phi}°")
    def _tab_square(self):
        self._clear_params()
        self._clear_explain()
        self._sq_amp = self._add_param("Amplitude (V)", 1.0, 0.1, 10, "V", 0, 0)
        self._sq_freq = self._add_param("Frequência (Hz)", 1.0, 0.1, 10, "Hz", 0, 1)
        self._sq_cycles = self._add_param("Períodos", 3.0, 1, 10, "T", 0, 2)
        self._add_button("▶ Gerar", self._plot_square, 0, 3)
        self._explain(
            "Onda Quadrada",
            "v(t) = A · sign(sin(2πft))     →  +A (metade) / -A (metade)",
            "A onda quadrada alterna entre +A e -A a cada meio período. "
            "É fundamental em eletrônica digital (sinais de clock, PWM). "
            "Pela série de Fourier, uma onda quadrada é composta apenas por "
            "harmônicos ÍMPARES de uma senoide: b_n = 4/(nπ) para n = 1, 3, 5, ...",
            "Série de Fourier: v(t) = (4A/π)[sin(ωt) + (1/3)sin(3ωt) + (1/5)sin(5ωt) + ...]"
        )
    def _plot_square(self):
        A = self._sq_amp.get()
        f = self._sq_freq.get()
        cycles = self._sq_cycles.get()
        t_end = cycles / f
        def draw(ax):
            t, y = generate_square(A, f, 0, t_end)
            ax.plot(t, y, color="#ab47bc", linewidth=2)
            ax.axhline(0, color="gray", linewidth=0.5, linestyle="--")
            ax.set_xlabel("Tempo (s)")
            ax.set_ylabel("Tensão (V)")
            T = 1/f
            ax.axvspan(0, T, alpha=0.1, color="yellow")
            ax.annotate(f"T = {T*1000:.2f} ms", xy=(T/2, A*0.6), fontsize=9, color="yellow")
        self._plot(draw, f"Onda Quadrada: A={A}V, f={f}Hz")
    def _tab_sawtooth(self):
        self._clear_params()
        self._clear_explain()
        self._sw_amp = self._add_param("Amplitude (V)", 1.0, 0.1, 10, "V", 0, 0)
        self._sw_freq = self._add_param("Frequência (Hz)", 1.0, 0.1, 10, "Hz", 0, 1)
        self._sw_cycles = self._add_param("Períodos", 3.0, 1, 10, "T", 0, 2)
        self._add_button("▶ Gerar", self._plot_sawtooth, 0, 3)
        self._explain(
            "Dente de Serra (Sawtooth)",
            "v(t) = A · (2(f·t mod 1) - 1)",
            "O dente de serra sobe linearmente e cai abruptamente (ou vice-versa). "
            "É usado em osciladores, sintetizadores de áudio e varredura de CRT. "
            "Sua série de Fourier contém TODOS os harmônicos (ímpares e pares): b_n = -2/(nπ).",
            "Série: v(t) = -(2A/π)[sin(ωt) + (1/2)sin(2ωt) + (1/3)sin(3ωt) + ...]"
        )

    def _plot_sawtooth(self):
        A = self._sw_amp.get()
        f = self._sw_freq.get()
        cycles = self._sw_cycles.get()
        t_end = cycles / f
        def draw(ax):
            t, y = generate_sawtooth(A, f, 0, t_end)
            ax.plot(t, y, color="#66bb6a", linewidth=2)
            ax.axhline(0, color="gray", linewidth=0.5, linestyle="--")
            ax.set_xlabel("Tempo (s)")
            ax.set_ylabel("Tensão (V)")
        self._plot(draw, f"Dente de Serra: A={A}V, f={f}Hz")
    def _tab_triangle(self):
        self._clear_params()
        self._clear_explain()
        self._tr_amp = self._add_param("Amplitude (V)", 1.0, 0.1, 10, "V", 0, 0)
        self._tr_freq = self._add_param("Frequência (Hz)", 1.0, 0.1, 10, "Hz", 0, 1)
        self._tr_cycles = self._add_param("Períodos", 3.0, 1, 10, "T", 0, 2)
        self._add_button("▶ Gerar", self._plot_triangle, 0, 3)
        self._explain(
            "Onda Triangular",
            "v(t) = (2A/π) · arcsin(sin(2πft))",
            "A onda triangular sobe e desce linearmente, sem descontinuidades na derivada. "
            "É usada em modulação triangular (TRAM) e em osciladores. "
            "Sua série de Fourier decai mais rápido (1/n²) que a do dente de serra (1/n), "
            "o que significa menos ruído em harmônicos de alta frequência.",
            "Série: v(t) = (8A/π²)[sin(ωt) - (1/9)sin(3ωt) + (1/25)sin(5ωt) - ...]"
        )

    def _plot_triangle(self):
        A = self._tr_amp.get()
        f = self._tr_freq.get()
        cycles = self._tr_cycles.get()
        t_end = cycles / f
        def draw(ax):
            t, y = generate_triangle(A, f, 0, t_end)
            ax.plot(t, y, color="#ffa726", linewidth=2)
            ax.axhline(0, color="gray", linewidth=0.5, linestyle="--")
            ax.set_xlabel("Tempo (s)")
            ax.set_ylabel("Tensão (V)")
        self._plot(draw, f"Onda Triangular: A={A}V, f={f}Hz")
    def _tab_fourier(self):
        self._clear_params()
        self._clear_explain()
        self._ft_harm = self._add_param("Nº de Harmônicos", 5.0, 1, 50, "", 0, 0)
        self._ft_cycles = self._add_param("Períodos", 2.0, 1, 5, "T", 0, 1)
        self._add_button("▶ Gerar", self._plot_fourier, 0, 2)
        self._explain(
            "Série de Fourier – Aproximação da Onda Quadrada",
            "v(t) = (4/π) Σ [sin(nωt)/n]  para n = 1, 3, 5, 7, ...",
            "A série de Fourier decompõe qualquer sinal periódico em uma soma de senoides "
            "(harmônicos). A onda quadrada só tem harmônicos ímpares. Quanto mais harmônicos "
            "somarmos, mais a aproximação se assemelha à forma ideal. "
            "O 'ringing' nas bordas é o fenômeno de Gibbs — ele não desaparece, "
            "mas fica confinado em uma região cada vez menor.",
            "Fenômeno de Gibbs: overshoot ≈ 9% da descontinuidade, independente do nº de termos."
        )
    def _plot_fourier(self):
        n_harm = int(self._ft_harm.get())
        cycles = self._ft_cycles.get()
        t_end = cycles
        def draw(ax):
            t, y_approx = fourier_square(n_harm, 0, t_end)
            t_sq, y_sq = generate_square(1.0, 1.0, 0, t_end)
            ax.plot(t_sq, y_sq, color="gray", linewidth=1, linestyle="--", alpha=0.5, label="Ideal")
            ax.plot(t, y_approx, color="#ef5350", linewidth=1.5, label=f"{n_harm} harmônicos")
            ax.axhline(0, color="gray", linewidth=0.5)
            ax.set_xlabel("Tempo (s)")
            ax.set_ylabel("Amplitude")
            ax.legend(loc="upper right", facecolor="#2a2a3e", edgecolor="gray", labelcolor="white")
        self._plot(draw, f"Fourier: {n_harm} harmônicos → Onda Quadrada")
    def _tab_rlc(self):
        self._clear_params()
        self._clear_explain()
        self._rlc_r = self._add_param("R (Ω)", 100.0, 1, 10000, "Ω", 0, 0)
        self._rlc_l = self._add_param("L (mH)", 10.0, 0.1, 1000, "mH", 0, 1)
        self._rlc_c = self._add_param("C (μF)", 100.0, 0.1, 10000, "μF", 0, 2)
        self._add_button("▶ Gerar", self._plot_rlc, 0, 3)
        self._explain(
            "Circuito RLC Série – Resposta em Frequência",
            "Z = R + j(ωL - 1/ωC)   |   f₀ = 1/(2π√(LC))   |   Q = (1/R)√(L/C)",
            "Em ressonância (f₀), a reatância indutiva cancela a capacitiva (X_L = X_C), "
            "e a impedância é puramente resistiva (mínima). O pico no gráfico de magnitude "
            "indica a frequência de ressonância. O fator Q determina a seletividade: "
            "Q alto = pico estreito (seletivo), Q baixo = pico largo.",
            "Largura de banda: Δf = f₀/Q  |  Admitância: Y = 1/Z"
        )
    def _plot_rlc(self):
        R = self._rlc_r.get()
        L = self._rlc_l.get() * 1e-3
        C = self._rlc_c.get() * 1e-6
        def draw(ax):
            f, mag_db, phase = rlc_series_response(R, L, C)
            f0 = 1 / (2 * np.pi * np.sqrt(L * C))
            Q = (1 / R) * np.sqrt(L / C)
            ax.semilogx(f, mag_db, color="#4fc3f7", linewidth=2, label="|H(jω)| (dB)")
            ax.axvline(f0, color="red", linewidth=1, linestyle="--", alpha=0.7)
            ax.annotate(f"f₀ = {f0:.1f} Hz\nQ = {Q:.2f}", xy=(f0, -5),
                        fontsize=9, color="red",
                        arrowprops=dict(arrowstyle="->", color="red"))
            ax.set_xlabel("Frequência (Hz) [log]")
            ax.set_ylabel("Magnitude (dB)")
            ax.legend(loc="upper right", facecolor="#2a2a3e", edgecolor="gray", labelcolor="white")
        self._plot(draw, f"RLC Série: R={R}Ω, L={L*1e3:.1f}mH, C={C*1e6:.1f}μF")
    def _tab_rc(self):
        self._clear_params()
        self._clear_explain()
        self._rc_r = self._add_param("R (kΩ)", 1.0, 0.1, 100, "kΩ", 0, 0)
        self._rc_c = self._add_param("C (nF)", 100.0, 1, 10000, "nF", 0, 1)
        self._add_button("▶ Gerar", self._plot_rc, 0, 2)
        self._explain(
            "Filtro Passa-Baixa RC – Diagrama de Bode",
            "H(s) = 1/(1 + sRC)   |   f_c = 1/(2πRC)   |   |H| = 1/√(1 + (f/fc)²)",
            "O filtro passa-baixa RC atenua frequências acima da frequência de corte (f_c). "
            "Em f_c, a atenuação é -3 dB (70.7% da amplitude). Acima de f_c, "
            "a atenuação cai a -20 dB/década (magnitude) e a fase tende a -90°. "
            "É o filtro mais simples e ubíquo em eletrônica.",
            "Rolloff: -20 dB/década | Fase em f_c: -45° | Fase em alta freq: → -90°"
        )
    def _plot_rc(self):
        R = self._rc_r.get() * 1e3
        C = self._rc_c.get() * 1e-9
        def draw(ax):
            f, mag_db, phase, fc = bode_rc_lowpass(R, C)
            ax.semilogx(f, mag_db, color="#66bb6a", linewidth=2, label="Magnitude (dB)")
            ax.axvline(fc, color="red", linewidth=1, linestyle="--", alpha=0.7)
            ax.axhline(-3, color="orange", linewidth=0.5, linestyle=":", alpha=0.7)
            ax.annotate(f"f_c = {fc:.1f} Hz (-3dB)", xy=(fc, -3),
                        fontsize=9, color="red",
                        arrowprops=dict(arrowstyle="->", color="red"))
            ax.set_xlabel("Frequência (Hz) [log]")
            ax.set_ylabel("Magnitude (dB)")
            ax.legend(loc="upper right", facecolor="#2a2a3e", edgecolor="gray", labelcolor="white")

        self._plot(draw, f"Passa-Baixa RC: R={R/1e3:.1f}kΩ, C={C*1e9:.0f}nF")
    def _tab_phasors(self):
        self._clear_params()
        self._clear_explain()
        self._ph1_mag = self._add_param("|V₁| (V)", 220.0, 1, 500, "V", 0, 0)
        self._ph1_ang = self._add_param("∠V₁ (°)", 0.0, -180, 180, "°", 0, 1)
        self._ph2_mag = self._add_param("|V₂| (V)", 110.0, 1, 500, "V", 0, 2)
        self._ph2_ang = self._add_param("∠V₂ (°)", 90.0, -180, 180, "°", 0, 3)
        self._add_button("▶ Gerar", self._plot_phasors, 0, 4)
        self._explain(
            "Fasores – Representação Gráfica",
            "V = Vrms ∠ θ  =  Vrms·cos(θ) + j·Vrms·sin(θ)  =  Vrms·e^(jθ)",
            "Um fasor é um vetor no plano complexo que representa a amplitude e fase "
            "de uma senoide em regime permanente. A soma de fasores é feita "
            "vetorialmente (paralelogramo). Aqui estão dois fasores e sua soma resultante. "
            "É a base da análise de circuitos trifásicos e de potência.",
            "Soma: V₁ + V₂ → módulo e ângulo do vetor resultante (diagonal do paralelogramo)."
        )
    def _plot_phasors(self):
        m1 = self._ph1_mag.get()
        a1 = self._ph1_ang.get()
        m2 = self._ph2_mag.get()
        a2 = self._ph2_ang.get()
        def draw(ax):
            # V1
            v1x, v1y = m1 * np.cos(np.radians(a1)), m1 * np.sin(np.radians(a1))
            # V2
            v2x, v2y = m2 * np.cos(np.radians(a2)), m2 * np.sin(np.radians(a2))
            # Soma
            sx, sy = v1x + v2x, v1y + v2y
            smag = np.hypot(sx, sy)
            sang = np.degrees(np.arctan2(sy, sx))
            ax.arrow(0, 0, v1x, v1y, head_width=5, head_length=3,
                     fc="#4fc3f7", ec="#4fc3f7", linewidth=2)
            ax.arrow(0, 0, v2x, v2y, head_width=5, head_length=3,
                     fc="#ff7043", ec="#ff7043", linewidth=2)
            ax.arrow(0, 0, sx, sy, head_width=5, head_length=3,
                     fc="#66bb6a", ec="#66bb6a", linewidth=2.5, linestyle="--")
            ax.plot([v1x, v1x + v2x], [v1y, v1y + v2y], "gray", linewidth=0.5, linestyle=":")
            ax.plot([v2x, v1x + v2x], [v2y, v1y + v2y], "gray", linewidth=0.5, linestyle=":")
            ax.annotate(f"V₁ = {m1:.0f}∠{a1:.0f}°", xy=(v1x*0.6, v1y*0.6 + 10),
                        fontsize=10, color="#4fc3f7", fontweight="bold")
            ax.annotate(f"V₂ = {m2:.0f}∠{a2:.0f}°", xy=(v2x*0.6 + 10, v2y*0.6),
                        fontsize=10, color="#ff7043", fontweight="bold")
            ax.annotate(f"V₁+V₂ = {smag:.1f}∠{sang:.1f}°", xy=(sx*0.5, sy*0.5 - 15),
                        fontsize=10, color="#66bb6a", fontweight="bold")
            lim = max(m1, m2, smag) * 1.3
            ax.set_xlim(-lim, lim)
            ax.set_ylim(-lim, lim)
            ax.axhline(0, color="gray", linewidth=0.5)
            ax.axvline(0, color="gray", linewidth=0.5)
            ax.set_xlabel("Real (V)")
            ax.set_ylabel("Imaginário (V)")
            ax.set_aspect("equal")
            ax.grid(True, alpha=0.2)
        self._plot(draw, "Plano Fasorial")
if __name__ == "__main__":
    app = SignalViewer()
    app.mainloop()   