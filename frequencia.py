import cmath
import math
from dataclasses import dataclass
from typing import Optional, Tuple, List
import json
@dataclass
class ComplexNumber:
    real: float = 0.0
    imag: float = 0.0
    @property
    def magnitude(self) -> float:
        """|Z| = √(a² + b²)"""
        return math.hypot(self.real, self.imag)
    @property
    def phase(self) -> float:
        """θ = arctan(b/a) em radianos"""
        return math.atan2(self.imag, self.real)
    @property
    def phase_deg(self) -> float:
        """Fase em graus"""
        return math.degrees(self.phase)
    @property
    def conjugate(self) -> 'ComplexNumber':
        """Conjugado: a - jb"""
        return ComplexNumber(self.real, -self.imag)
    @property
    def reciprocal(self) -> 'ComplexNumber':
        """1/Z"""
        mag2 = self.real**2 + self.imag**2
        if mag2 == 0:
            raise ZeroDivisionError("Não é possível inverter zero")
        return ComplexNumber(self.real / mag2, -self.imag / mag2)
    @property
    def as_polar(self) -> Tuple[float, float]:
        """Retorna (módulo, ângulo em radianos)"""
        return (self.magnitude, self.phase)
    def __add__(self, other: 'ComplexNumber') -> 'ComplexNumber':
        return ComplexNumber(self.real + other.real, self.imag + other.imag)
    def __sub__(self, other: 'ComplexNumber') -> 'ComplexNumber':
        return ComplexNumber(self.real - other.real, self.imag - other.imag)
    def __mul__(self, other: 'ComplexNumber') -> 'ComplexNumber':
        return ComplexNumber(
            self.real * other.real - self.imag * other.imag,
            self.real * other.imag + self.imag * other.real
        )
    def __truediv__(self, other: 'ComplexNumber') -> 'ComplexNumber':
        return self * other.reciprocal
    def __pow__(self, n: int) -> 'ComplexNumber':
        """Potência de n (inteiro)"""
        if n == 0:
            return ComplexNumber(1, 0)
        if n == 1:
            return self
        result = ComplexNumber(1, 0)
        for _ in range(abs(n)):
            result = result * self
        if n < 0:
            result = result.reciprocal
        return result
    def __neg__(self) -> 'ComplexNumber':
        return ComplexNumber(-self.real, -self.imag)
    def __repr__(self) -> str:
        if self.imag >= 0:
            return f"({self.real:.4g} + {self.imag:.4g}j)"
        return f"({self.real:.4g} - {-self.imag:.4g}j)"
    def __str__(self) -> str:
     mag = self.magnitude
     return f"({self.real:.4g} + {self.imag:.4g}j)  |  {mag:.4g}∠{self.phase_deg:.2f}°" 
    @classmethod
    def from_polar(cls, magnitude: float, phase_rad: float) -> 'ComplexNumber':
        """Cria a partir de forma polar (módulo, ângulo em rad)"""
        return cls(magnitude * math.cos(phase_rad), magnitude * math.sin(phase_rad))
    @classmethod
    def from_polar_deg(cls, magnitude: float, phase_deg: float) -> 'ComplexNumber':
        """Cria a partir de forma polar (módulo, ângulo em graus)"""
        return cls.from_polar(magnitude, math.radians(phase_deg))
    @classmethod
    def from_euler(cls, magnitude: float, phase_rad: float) -> 'ComplexNumber':
        """e^(jθ) × magnitude"""
        return cls.from_polar(magnitude, phase_rad)

def euler_formula(theta: float) -> ComplexNumber:
    """e^(jθ) = cos(θ) + j·sin(θ)"""
    return ComplexNumber(math.cos(theta), math.sin(theta))

def de_moivre(magnitude: float, angle_rad: float, n: int) -> ComplexNumber:
    """(r·e^(jθ))^n = r^n · e^(jnθ)"""
    return ComplexNumber.from_polar(magnitude**n, n * angle_rad)

def j_powers(n: int) -> str:
    """j^n cicla: 1, j, -1, -j, 1, j, ..."""
    cycle = ["1", "j", "-1", "-j"]
    return cycle[n % 4]

@dataclass
class Sinusoid:
    amplitude: float        # A (V ou A)
    frequency: float        # f (Hz)
    phase_deg: float = 0.0  # φ (graus)
    @property
    def omega(self) -> float:
        """ω = 2πf (rad/s)"""
        return 2 * math.pi * self.frequency
    @property
    def period(self) -> float:
        """T = 1/f (s)"""
        return 1.0 / self.frequency
    @property
    def peak_to_peak(self) -> float:
        """Vpp = 2A"""
        return 2 * self.amplitude
    @property
    def rms(self) -> float:
        """Vrms = A/√2"""
        return self.amplitude / math.sqrt(2)
    @property
    def phase_rad(self) -> float:
        return math.radians(self.phase_deg)
    def value_at(self, t: float) -> float:
        """Valor instantâneo v(t)"""
        return self.amplitude * math.sin(self.omega * t + self.phase_rad)
    def to_phasor(self) -> ComplexNumber:
        """Converte para fasor (forma RMS, ângulo em graus)"""
        return ComplexNumber.from_polar_deg(self.rms, self.phase_deg)     
    def __repr__(self):
        return (f"v(t) = {self.amplitude:.4g}·sin({self.omega:.4g}t + {self.phase_deg:.1f}°) "
                f"[f={self.frequency} Hz, T={self.period*1000:.2f} ms, "
                f"Vrms={self.rms:.4g}, Vpp={self.peak_to_peak:.4g}]")
def freq_to_omega(f_hz: float) -> float:
    """Hz → rad/s"""
    return 2 * math.pi * f_hz
def omega_to_freq(omega: float) -> float:
    """rad/s → Hz"""
    return omega / (2 * math.pi)
def freq_to_period(f_hz: float) -> float:
    """Hz → s"""
    return 1.0 / f_hz
def period_to_freq(t_s: float) -> float:
    """s → Hz"""
    return 1.0 / t_s
def freq_to_wavelength(f_hz: float, v: float = 3e8) -> float:
    """λ = v/f (v = velocidade de propagação, default: velocidade da luz)"""
    return v / f_hz
def hz_to_db(value: float, ref: float = 1.0) -> float:
    """Converte razão para dB (potência)"""
    return 10 * math.log10(value / ref)
def voltage_to_db(value: float, ref: float = 1.0) -> float:
    """Converte razão de tensão para dB"""
    return 20 * math.log10(value / ref)
def db_to_gain(db: float) -> float:
    """dB → ganho (tensão)"""
    return 10 ** (db / 20)
@dataclass
class Impedance:
    resistance: float       
    reactance: float        
    frequency: float = 50.0
    @property
    def omega(self) -> float:
        return 2 * math.pi * self.frequency
    @property
    def as_complex(self) -> ComplexNumber:
        return ComplexNumber(self.resistance, self.reactance)
    @property
    def magnitude(self) -> float:
        """|Z| = √(R² + X²)"""
        return self.as_complex.magnitude
    @property
    def angle_deg(self) -> float:
        """θ = arctan(X/R)"""
        return self.as_complex.phase_deg
    @property
    def admittance(self) -> 'Admittance':
        """Y = 1/Z = G + jB"""
        z = self.as_complex
        y = z.reciprocal
        return Admittance(y.real, y.imag, self.frequency)
    def __repr__(self):
        return f"Z = {self.resistance:.4g} + j{self.reactance:.4g} Ω  |  |Z|={self.magnitude:.4g} Ω ∠{self.angle_deg:.2f}°"
def inductive_reactance(inductance_h: float, f_hz: float) -> float:
    """X_L = 2πfL (Ω)"""
    return 2 * math.pi * f_hz * inductance_h
def capacitive_reactance(capacitance_f: float, f_hz: float) -> float:
    """X_C = -1/(2πfC) (Ω)"""
    return -1.0 / (2 * math.pi * f_hz * capacitance_f)
def inductance_from_reactance(xl: float, f_hz: float) -> float:
    """L = X_L / (2πf) (H)"""
    return xl / (2 * math.pi * f_hz)
def capacitance_from_reactance(xc: float, f_hz: float) -> float:
    """C = -1/(2πf·X_C) (F)"""
    return -1.0 / (2 * math.pi * f_hz * xc)
@dataclass
class Admittance:
    """Y = G + jB (S – Siemens)"""
    conductance: float   # G (S)
    susceptance: float   # B (S)
    frequency: float = 50.0
    @property
    def as_complex(self) -> ComplexNumber:
        return ComplexNumber(self.conductance, self.susceptance)
    @property
    def impedance(self) -> Impedance:
        y = self.as_complex
        z = y.reciprocal
        return Impedance(z.real, z.imag, self.frequency)
def series_impedance(r: float, l_h: float, c_f: float, f_hz: float) -> Impedance:
    """Z_série = R + j(ωL - 1/(ωC))"""
    omega = 2 * math.pi * f_hz
    xl = omega * l_h
    xc = -1.0 / (omega * c_f)
    return Impedance(r, xl + xc, f_hz)
def parallel_impedance(r: float, l_h: float, c_f: float, f_hz: float) -> Impedance:
    """Z_paralelo = 1 / (1/R + 1/(jωL) + jωC)"""
    omega = 2 * math.pi * f_hz
    y_r = ComplexNumber(1.0 / r, 0)
    y_l = ComplexNumber(0, -1.0 / (omega * l_h))
    y_c = ComplexNumber(0, omega * c_f)
    y_total = y_r + y_l + y_c
    z_total = y_total.reciprocal
    return Impedance(z_total.real, z_total.imag, f_hz)
def resonance_frequency(l_h: float, c_f: float) -> float:
    """f₀ = 1/(2π√(LC)) (Hz)"""
    return 1.0 / (2 * math.pi * math.sqrt(l_h * c_f))
def quality_factor(r: float, l_h: float, c_f: float, f_hz: float) -> float:
    """Q = (1/R)·√(L/C)  ou  Q = f₀ / Δf"""
    return (1.0 / r) * math.sqrt(l_h / c_f)
def bandwidth(q: float, f0_hz: float) -> float:
    """Δf = f₀ / Q (Hz)"""
    return f0_hz / q
@dataclass
class AC_Power:
    v_rms: float       
    i_rms: float       
    phase_deg: float
    @property
    def apparent_power(self) -> float:
        """S = V·I (VA)"""
        return self.v_rms * self.i_rms
    @property
    def active_power(self) -> float:
        """P = V·I·cos(θ) (W)"""
        return self.apparent_power * math.cos(math.radians(self.phase_deg))
    @property
    def reactive_power(self) -> float:
        """Q = V·I·sin(θ) (VAR)"""
        return self.apparent_power * math.sin(math.radians(self.phase_deg))
    @property
    def power_factor(self) -> float:
        """pf = cos(θ)"""
        return math.cos(math.radians(self.phase_deg))
    @property
    def complex_power(self) -> ComplexNumber:
        """S = P + jQ (VA)"""
        return ComplexNumber(self.active_power, self.reactive_power)
    def __repr__(self):
        return (f"S = {self.apparent_power:.4g} VA  |  P = {self.active_power:.4g} W  "
                f"|  Q = {self.reactive_power:.4g} VAR  |  pf = {self.power_factor:.4f}")
def fourier_coefficients(signal: List[float], n_harmonics: int, f0: float) -> List[ComplexNumber]:
    t = 1.0 / f0
    n_samples = len(signal)
    dt = t / n_samples
    coeffs = []

    for n in range(n_harmonics):
        re, im = 0.0, 0.0
        for k, x in enumerate(signal):
            theta = 2 * math.pi * n * k / n_samples
            re += x * math.cos(theta)
            im += -x * math.sin(theta)
        re /= n_samples
        im /= n_samples
        coeffs.append(ComplexNumber(re, im))
    return coeffs
def square_wave_coefficients(n_harmonics: int) -> List[float]:
    coeffs = []
    for n in range(1, n_harmonics + 1):
        if n % 2 == 1:
            coeffs.append(4.0 / (n * math.pi))
        else:
            coeffs.append(0.0)
    return coeffs
def sawtooth_wave_coefficients(n_harmonics: int) -> List[float]:
    """
    Série de Fourier do dente de serra (amplitude 1):
    b_n = -2/(nπ)
    """
    return [-2.0 / (n * math.pi) for n in range(1, n_harmonics + 1)]
def bode_magnitude_db(frequencies: List[float],
                      zeros: List[ComplexNumber],
                      poles: List[ComplexNumber],
                      gain: float = 1.0) -> List[float]:
    """
    |H(jω)| em dB para um sistema com zeros e polos.
    H(s) = K · ∏(s - z_i) / ∏(s - p_i)
    """
    result = []
    for f in frequencies:
        w = 2 * math.pi * f
        s = ComplexNumber(0, w) 
        mag = gain
        for z in zeros:
            mag *= (s - z).magnitude
        for p in poles:
            mag *= 1.0 / (s - p).magnitude
        result.append(20 * math.log10(mag) if mag > 0 else -200)
    return result
CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "c_light": 299_792_458,      
    "mu0": 4 * math.pi * 1e-7,    
    "epsilon0": 8.854e-12,       
    "k_boltzmann": 1.381e-23,    
    "q_electron": 1.602e-19,     
}
SI_PREFIXES = {
    "Y": 1e24, "Z": 1e21, "E": 1e18, "P": 1e15, "T": 1e12,
    "G": 1e9,  "M": 1e6,  "k": 1e3,  "":  1,
    "m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12, "f": 1e-15,
    "a": 1e-18, "z": 1e-21, "y": 1e-24,
}
def parse_si(value: float, prefix: str) -> float:
    """Converte valor com prefixo SI para unidade base"""
    return value * SI_PREFIXES.get(prefix, 1)
def format_si(value: float, unit: str) -> str:
    """Formata valor com prefixo SI apropriado"""
    prefixes = [("T", 1e12), ("G", 1e9), ("M", 1e6), ("k", 1e3),
                ("", 1), ("m", 1e-3), ("u", 1e-6), ("n", 1e-9), ("p", 1e-12)]
    for prefix, factor in prefixes:
        if abs(value) >= factor:
            return f"{value/factor:.4g} {prefix}{unit}"
    return f"{value:.4g} p{unit}"
def phasor_multiply(p1: ComplexNumber, p2: ComplexNumber) -> ComplexNumber:
    """Multiplicação de fasores (módulos se multiplicam, ângulos se somam)"""
    m1, a1 = p1.as_polar
    m2, a2 = p2.as_polar
    return ComplexNumber.from_polar(m1 * m2, a1 + a2)
def phasor_divide(p1: ComplexNumber, p2: ComplexNumber) -> ComplexNumber:
    """Divisão de fasores (módulos se dividem, ângulos se subtraem)"""
    m1, a1 = p1.as_polar
    m2, a2 = p2.as_polar
    if m2 == 0:
        raise ZeroDivisionError("Divisão por zero")
    return ComplexNumber.from_polar(m1 / m2, a1 - a2)
def rc_lowpass_cutoff(r_ohm: float, c_farad: float) -> float:
    """f_c = 1/(2πRC) (Hz) – passa-baixa RC"""
    return 1.0 / (2 * math.pi * r_ohm * c_farad)
def rc_highpass_cutoff(r_ohm: float, c_farad: float) -> float:
    """f_c = 1/(2πRC) (Hz) – passa-alta RC"""
    return 1.0 / (2 * math.pi * r_ohm * c_farad)
def rl_lowpass_cutoff(r_ohm: float, l_henry: float) -> float:
    """f_c = R/(2πL) (Hz) – passa-baixa RL"""
    return r_ohm / (2 * math.pi * l_henry)
def rl_highpass_cutoff(r_ohm: float, l_henry: float) -> float:
    """f_c = R/(2πL) (Hz) – passa-alta RL"""
    return r_ohm / (2 * math.pi * l_henry)
if __name__ == "__main__":
    print("=" * 60)
    print("  DEMONSTRAÇÕES – NÚMEROS COMPLEXOS & CIRCUITOS")
    print("=" * 60)
    print("\n[1] NÚMEROS COMPLEXOS")
    z1 = ComplexNumber(3, 4)
    z2 = ComplexNumber.from_polar(5, math.radians(30))
    print(f"  z1 = {z1}")
    print(f"  z2 = {z2}")
    print(f"  z1 + z2 = {z1 + z2}")
    print(f"  z1 × z2 = {z1 * z2}")
    print(f"  z1 / z2 = {z1 / z2}")
    print(f"  z1* (conjugado) = {z1.conjugate}")
    print(f"  1/z1 = {z1.reciprocal}")
    print(f"  j^7 = {j_powers(7)}")
    print("\n[2] FÓRMULA DE EULER & DE MOIVRE")
    print(f"  e^(j·π) = {euler_formula(math.pi)}")
    print(f"  (2∠30°)^3 = {de_moivre(2, math.radians(30), 3)}")
    print("\n[3] SENOIDE")
    v = Sinusoid(amplitude=220, frequency=50, phase_deg=0)
    print(f"  {v}")
    print(f"  v(0) = {v.value_at(0):.4g} V")
    print(f"  v(10ms) = {v.value_at(0.01):.4g} V")
    print(f"  Fasor (RMS): {v.to_phasor()}")
    print("\n[4] CONVERSÕES DE FREQÜÊNCIA")
    f = 1000  
    print(f"  {f} Hz → ω = {freq_to_omega(f):.4g} rad/s")
    print(f"  {f} Hz → T = {freq_to_period(f)*1000:.4g} ms")
    print(f"  λ (luz) = {freq_to_wavelength(f):.4g} m")
    print(f"  20 dB → ganho = {db_to_gain(20):.4g}x")
    print("\n[5] IMPEDÂNCIA")
    r, l, c = 100, 10e-3, 100e-6
    f = 50
    z = series_impedance(r, l, c, f)
    print(f"  R={r}Ω, L={l*1e3:.1f}mH, C={c*1e6:.0f}μF @ {f} Hz")
    print(f"  X_L = {inductive_reactance(l, f):.4g} Ω")
    print(f"  X_C = {capacitive_reactance(c, f):.4g} Ω")
    print(f"  Z = {z}")
    print(f"  Y = {z.admittance.as_complex}")
    print("\n[6] RESSONÂNCIA")
    f0 = resonance_frequency(l, c)
    print(f"  f₀ = 1/(2π√(LC)) = {f0:.4g} Hz")
    print(f"  Q = {quality_factor(r, l, c, f0):.4g}")
    print(f"  Δf = {bandwidth(quality_factor(r, l, c, f0), f0):.4g} Hz")
    print("\n[7] POTÊNCIA CA")
    p = AC_Power(v_rms=220, i_rms=10, phase_deg=30)
    print(f"  {p}")
    print("\n[8] SÉRIE DE FOURIER – ONDA QUADRADA")
    coeffs = square_wave_coefficients(9)
    for n, c in enumerate(coeffs, 1):
        print(f"  b_{n} = {c:.4f}")
    print("\n[9] FREQÜÊNCIA DE CORTE")
    fc = rc_lowpass_cutoff(1e3, 1e-6)
    print(f"  RC (1kΩ, 1μF): f_c = {fc:.4g} Hz")
    fc2 = rl_lowpass_cutoff(1e3, 1e-3)
    print(f"  RL (1kΩ, 1mH): f_c = {fc2:.4g} Hz")
    print("\n[10] UNIDADES SI")
    print(f"  2.5mH = {parse_si(2.5, 'm'):.4g} H")
    print(f"  1e-6 F = {format_si(1e-6, 'F')}")
    print(f"  50000 Hz = {format_si(50000, 'Hz')}")
    print("\n" + "=" * 60)
    print("  FIM")
    print("=" * 60)   