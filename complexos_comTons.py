import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import sounddevice as sd
import threading
import math
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
SAMPLE_RATE = 44100 
def generate_tone(frequency, duration=2.0, amplitude=0.5, waveform="sine"):
    """Gera um sinal de áudio na frequência dada."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    if waveform == "sine":
        y = amplitude * np.sin(2 * np.pi * frequency * t)
    elif waveform == "square":
        y = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
    elif waveform == "sawtooth":
        y = amplitude * (2 * ((frequency * t) % 1) - 1)
    elif waveform == "triangle":
        y = amplitude * (2 / np.pi) * np.arcsin(np.sin(2 * np.pi * frequency * t))
    else:
        y = amplitude * np.sin(2 * np.pi * frequency * t)
    return t, y.astype(np.float32)
def play_tone(frequency, duration=2.0, amplitude=0.5, waveform="sine"):
    """Toca o tom em segundo plano."""
    _, y = generate_tone(frequency, duration, amplitude, waveform)
    sd.play(y, samplerate=SAMPLE_RATE)
    return sd.wait()
class ToneGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🔊 Gerador de Tons – Frequência → Som + Onda")
        self.geometry("1100x750")
        self.minsize(900, 650)
        self._playing = False
        self._build_ui()
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=3)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        ctk.CTkLabel(
            self, text="🔊 Gerador de Tons",
            font=("Segoe UI", 22, "bold"), text_color="#64b5f6"
        ).grid(row=0, column=0, pady=(15, 5))
        controls = ctk.CTkFrame(self, fg_color="#2a2a3e", corner_radius=10)
        controls.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        controls.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        ctk.CTkLabel(controls, text="Frequência (Hz)", font=("Segoe UI", 12)).grid(row=0, column=0, padx=15, pady=(10, 2), sticky="w")
        self.freq_var = ctk.StringVar(value="440")
        ctk.CTkEntry(controls, textvariable=self.freq_var, font=("Segoe UI", 16, "bold"), width=120).grid(row=1, column=0, padx=15, pady=(0, 10))
        ctk.CTkLabel(controls, text="Duração (s)", font=("Segoe UI", 12)).grid(row=0, column=1, padx=15, pady=(10, 2), sticky="w")
        self.dur_var = ctk.StringVar(value="2.0")
        ctk.CTkEntry(controls, textvariable=self.dur_var, font=("Segoe UI", 14), width=80).grid(row=1, column=1, padx=15, pady=(0, 10))
        ctk.CTkLabel(controls, text="Amplitude (0–1)", font=("Segoe UI", 12)).grid(row=0, column=2, padx=15, pady=(10, 2), sticky="w")
        self.amp_var = ctk.StringVar(value="0.5")
        ctk.CTkEntry(controls, textvariable=self.amp_var, font=("Segoe UI", 14), width=80).grid(row=1, column=2, padx=15, pady=(0, 10))
        ctk.CTkLabel(controls, text="Forma de Onda", font=("Segoe UI", 12)).grid(row=0, column=3, padx=15, pady=(10, 2), sticky="w")
        self.wave_var = ctk.StringVar(value="sine")
        wave_menu = ctk.CTkOptionMenu(
            controls, variable=self.wave_var,
            values=["sine", "square", "sawtooth", "triangle"],
            font=("Segoe UI", 13), width=120
        )
        wave_menu.grid(row=1, column=3, padx=15, pady=(0, 10))
        self.play_btn = ctk.CTkButton(
            controls, text="▶  Tocar",
            font=("Segoe UI", 15, "bold"),
            fg_color="#1e8449", hover_color="#27ae60",
            width=140, height=50,
            command=self._toggle_play
        )
        self.play_btn.grid(row=0, column=4, rowspan=2, padx=15, pady=10)
        ctk.CTkButton(
            controls, text="⏹  Parar",
            font=("Segoe UI", 14, "bold"),
            fg_color="#922b21", hover_color="#c0392b",
            width=100, height=50,
            command=self._stop
        ).grid(row=0, column=5, rowspan=2, padx=15, pady=10)
        presets_frame = ctk.CTkFrame(controls, fg_color="transparent")
        presets_frame.grid(row=2, column=0, columnspan=6, padx=10, pady=(0, 8))
        ctk.CTkLabel(presets_frame, text="Presets:", font=("Segoe UI", 11), text_color="gray").pack(side="left", padx=(5, 10))
        presets = [
            ("110 Hz (La)", "110"), ("220 Hz (Lá)", "220"),
            ("440 Hz (Lá4)", "440"), ("880 Hz (Lá5)", "880"),
            ("1000 Hz", "1000"), ("2000 Hz", "2000"),
        ]
        for label, val in presets:
            ctk.CTkButton(
                presets_frame, text=label,
                font=("Segoe UI", 11), width=90, height=28,
                fg_color="#34495e", hover_color="#4a6a8a",
                command=lambda v=val: self.freq_var.set(v)
            ).pack(side="left", padx=3)
        self.plot_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.plot_frame.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")
        info_frame = ctk.CTkFrame(self, fg_color="#2a2a3e", corner_radius=10)
        info_frame.grid(row=3, column=0, padx=20, pady=(5, 15), sticky="ew")
        self.info_label = ctk.CTkLabel(
            info_frame,
            text="Digite uma frequência e clique em ▶ Tocar. O som será gerado e a onda exibida abaixo.",
            font=("Segoe UI", 12), text_color="gray",
            justify="left", wraplength=1000
        )
        self.info_label.pack(padx=15, pady=10)
        self._plot_wave(440, 2.0, 0.5, "sine")
    def _toggle_play(self):
        if self._playing:
            self._stop()
            return
        try:
            freq = float(self.freq_var.get())
            dur = float(self.dur_var.get())
            amp = float(self.amp_var.get())
            wave = self.wave_var.get()
        except ValueError:
            self.info_label.configure(text="⚠️ Valores inválidos. Verifique os campos.")
            return
        if freq <= 0 or freq > 20000:
            self.info_label.configure(text="⚠️ Frequência deve estar entre 1 Hz e 20000 Hz (limite audível).")
            return
        if amp < 0 or amp > 1:
            self.info_label.configure(text="⚠️ Amplitude deve estar entre 0 e 1.")
            return
        self._plot_wave(freq, dur, amp, wave)
        T = 1 / freq
        omega = 2 * math.pi * freq
        self.info_label.configure(
            text=f"🎵 Tocando: f = {freq:.1f} Hz | ω = {omega:.2f} rad/s | T = {T*1000:.3f} ms | "
                 f"Vpp = {2*amp:.2f} | Forma: {wave}"
        )
        self._playing = True
        self.play_btn.configure(text="⏳ Tocando...", fg_color="#f39c12", hover_color="#f5b041")
        thread = threading.Thread(target=self._play_thread, args=(freq, dur, amp, wave), daemon=True)
        thread.start()
    def _play_thread(self, freq, dur, amp, wave):
        play_tone(freq, dur, amp, wave)
        self.after(0, self._play_done)
    def _play_done(self):
        self._playing = False
        self.play_btn.configure(text="▶  Tocar", fg_color="#1e8449", hover_color="#27ae60")
    def _stop(self):
        sd.stop()
        self._playing = False
        self.play_btn.configure(text="▶  Tocar", fg_color="#1e8449", hover_color="#27ae60")
        self.info_label.configure(text="⏹ Parado.")
    def _plot_wave(self, freq, duration, amplitude, waveform):
        for w in self.plot_frame.winfo_children():
            w.destroy()
        t, y = generate_tone(freq, duration, amplitude, waveform)
        max_cycles = 5
        T = 1 / freq
        t_end = min(duration, max_cycles * T)
        mask = t <= t_end
        t_show = t[mask]
        y_show = y[mask]
        fig = Figure(figsize=(10, 5), dpi=100, facecolor="#1e1e2e")
        fig.patch.set_facecolor("#1e1e2e")
        gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.35)
        ax1 = fig.add_subplot(gs[0])
        ax1.set_facecolor("#1e1e2e")
        ax1.plot(t_show * 1000, y_show, color="#4fc3f7", linewidth=1.5)
        ax1.axhline(0, color="gray", linewidth=0.5, linestyle="--")
        ax1.axhline(amplitude, color="red", linewidth=0.5, linestyle=":", alpha=0.6)
        ax1.axhline(-amplitude, color="red", linewidth=0.5, linestyle=":", alpha=0.6)
        ax1.set_xlabel("Tempo (ms)", color="white")
        ax1.set_ylabel("Amplitude", color="white")
        ax1.set_title(f"Onda – f = {freq:.1f} Hz | {waveform}", color="white", fontsize=12, fontweight="bold")
        ax1.tick_params(colors="white")
        ax1.grid(True, alpha=0.2, color="gray")
        for spine in ax1.spines.values():
            spine.set_color("gray")
        # Marca o período
        if T * 1000 < (t_show[-1] - t_show[0]) * 1000:
            ax1.axvspan(0, T * 1000, alpha=0.08, color="green")
            ax1.annotate(f"T = {T*1000:.2f} ms", xy=(T*500, amplitude*0.8),
                         fontsize=9, color="green")
        ax2 = fig.add_subplot(gs[1])
        ax2.set_facecolor("#1e1e2e")
        n = len(y)
        fft_vals = np.fft.rfft(y)
        freqs = np.fft.rfftfreq(n, d=1/SAMPLE_RATE)
        magnitude = 2.0 / n * np.abs(fft_vals)
        f_max = min(freq * 5, SAMPLE_RATE / 2)
        mask_f = freqs <= f_max
        ax2.bar(freqs[mask_f], magnitude[mask_f], width=max(freq*0.1, 1), color="#ab47bc", alpha=0.8)
        ax2.set_xlabel("Frequência (Hz)", color="white")
        ax2.set_ylabel("|X(f)|", color="white")
        ax2.set_title("Espectro (FFT)", color="white", fontsize=10)
        ax2.tick_params(colors="white")
        ax2.grid(True, alpha=0.2, color="gray")
        for spine in ax2.spines.values():
            spine.set_color("gray")
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
if __name__ == "__main__":
    app = ToneGenerator()
    app.mainloop()   