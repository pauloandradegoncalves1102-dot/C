import customtkinter as ctk
import math
import ast
import operator
import json
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
class SafeEvaluator:
    _ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    _funcs = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "asin": math.asin, "acos": math.acos, "atan": math.atan,
        "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
        "sqrt": math.sqrt, "log": math.log10, "ln": math.log,
        "log2": math.log2, "abs": abs, "fact": math.factorial,
        "exp": math.exp, "ceil": math.ceil, "floor": math.floor,
    }
    _constants = {"pi": math.pi, "e": math.e}
    @classmethod
    def evaluate(cls, expression: str, degrees: bool = False) -> float:
        expr = expression.replace("^", "**").replace("π", "pi")
        if degrees:
            for fn in ("sin", "cos", "tan"):
                expr = expr.replace(f"{fn}(", f"__deg_{fn}(")
            cls._funcs["__deg_sin"] = lambda x: math.sin(math.radians(x))
            cls._funcs["__deg_cos"] = lambda x: math.cos(math.radians(x))
            cls._funcs["__deg_tan"] = lambda x: math.tan(math.radians(x))
            cls._funcs["asin"] = lambda x: math.degrees(math.asin(x))
            cls._funcs["acos"] = lambda x: math.degrees(math.acos(x))
            cls._funcs["atan"] = lambda x: math.degrees(math.atan(x))
        else:
            cls._funcs.pop("__deg_sin", None)
            cls._funcs.pop("__deg_cos", None)
            cls._funcs.pop("__deg_tan", None)
        tree = ast.parse(expr, mode="eval")
        return cls._eval_node(tree.body)
    @classmethod
    def _eval_node(cls, node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = cls._eval_node(node.left)
            right = cls._eval_node(node.right)
            op = cls._ops.get(type(node.op))
            if op is None:
                raise ValueError("Operador não suportado")
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = cls._eval_node(node.operand)
            op = cls._ops.get(type(node.op))
            if op is None:
                raise ValueError("Operador unário não suportado")
            return op(operand)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                fname = node.func.id
                if fname in cls._funcs:
                    args = [cls._eval_node(a) for a in node.args]
                    return cls._funcs[fname](*args)
                else:
                    raise ValueError(f"Função desconhecida: {fname}")
            else:
                raise ValueError("Chamada inválida")
        elif isinstance(node, ast.Name):
            if node.id in cls._constants:
                return cls._constants[node.id]
            else:
                raise ValueError(f"Nome desconhecido: {node.id}")
        else:
            raise ValueError(f"Nó não suportado: {type(node).__name__}")
class ScientificCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora Científica")
        self.geometry("820x700")
        self.resizable(False, False)
        self.degrees = True
        self.memory = 0.0
        self.history = []
        self._load_history()
        self._build_ui()
        self._bind_keyboard()
    def _build_ui(self):
        # ── DISPLAY ──
        self.display_var = ctk.StringVar(value="")
        self.display = ctk.CTkEntry(
            self, textvariable=self.display_var,
            font=("Segoe UI", 26), justify="right", height=55
        )
        self.display.grid(row=0, column=0, columnspan=8, padx=10, pady=(10, 2), sticky="nsew")
        self.status = ctk.CTkLabel(
            self, text="DEG | Mem: 0", font=("Segoe UI", 11), text_color="gray"
        )
        self.status.grid(row=1, column=0, columnspan=8, padx=10, pady=(0, 5))
        buttons = [
            ("MC", 2, 0, 1), ("MR", 2, 1, 1), ("M+", 2, 2, 1), ("M-", 2, 3, 1),
            ("DEG", 2, 4, 1), ("(", 2, 5, 1), (")", 2, 6, 1), ("⌫", 2, 7, 1),
            ("sin", 3, 0, 1), ("cos", 3, 1, 1), ("tan", 3, 2, 1), ("π", 3, 3, 1),
            ("e", 3, 4, 1), ("x!", 3, 5, 1), ("^", 3, 6, 1), ("√", 3, 7, 1),
            ("ln", 4, 0, 1), ("log", 4, 1, 1), ("log₂", 4, 2, 1), ("10ˣ", 4, 3, 1),
            ("eˣ", 4, 4, 1), ("1/x", 4, 5, 1), ("|x|", 4, 6, 1), ("C", 4, 7, 1),
            ("7", 5, 0, 1), ("8", 5, 1, 1), ("9", 5, 2, 1), ("÷", 5, 3, 1),
            ("%", 5, 4, 1), ("±", 5, 5, 1), ("Ans", 5, 6, 1), ("AC", 5, 7, 1),
            ("4", 6, 0, 1), ("5", 6, 1, 1), ("6", 6, 2, 1), ("×", 6, 3, 1),
            ("+", 6, 4, 1), ("-", 6, 5, 1), (".", 6, 6, 1), ("=", 6, 7, 1),
            ("1", 7, 0, 1), ("2", 7, 1, 1), ("3", 7, 2, 1), ("0", 7, 3, 2),
            ("00", 7, 5, 1), ("⌫", 7, 6, 1), ("=", 7, 7, 1),
        ]
        for text, row, col, span in buttons:
            # Cores por tipo
            if text in "0123456789" or text == "00" or text == ".":
                fg = "#2b2b2b"
                hover = "#404040"
            elif text in "+-×÷^":
                fg = "#1a5276"
                hover = "#2980b9"
            elif text in "AC C ⌫":
                fg = "#922b21"
                hover = "#c0392b"
            elif text == "=":
                fg = "#1e8449"
                hover = "#27ae60"
            else:
                fg = "#34495e"
                hover = "#4a6a8a"
            btn = ctk.CTkButton(
                self, text=text,
                width=80, height=50,
                font=("Segoe UI", 15, "bold"),
                fg_color=fg, hover_color=hover,
                command=lambda t=text: self._on_button(t),
            )
            btn.grid(row=row, column=col, columnspan=span, padx=2, pady=2, sticky="nsew")
        hist_frame = ctk.CTkFrame(self, fg_color="transparent")
        hist_frame.grid(row=8, column=0, columnspan=8, padx=10, pady=(5, 10), sticky="nsew")
        ctk.CTkLabel(hist_frame, text="Histórico", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.hist_box = ctk.CTkTextbox(hist_frame, height=70, font=("Consolas", 10))
        self.hist_box.pack(fill="x", pady=(2, 0))
        self.hist_box.configure(state="disabled")
        self._update_history_display()
        for i in range(8):
            self.grid_columnconfigure(i, weight=1)
        for i in range(2, 8):
            self.grid_rowconfigure(i, weight=1)
    def _get_display(self) -> str:
        return self.display_var.get()
    def _set_display(self, text: str):
        self.display_var.set(text)
    def _append(self, text: str):
        current = self._get_display()
        if current in ("Erro", ""):
            self._set_display(text)
        else:
            self._set_display(current + text)
    def _on_button(self, text: str):
        if text == "AC":
            self._set_display("")
        elif text == "C":
            self._set_display("")
        elif text == "⌫":
            self._set_display(self._get_display()[:-1])
        elif text == "=":
            self._calculate()
        elif text == "DEG":
            self.degrees = not self.degrees
            self._update_status()
        elif text == "MC":
            self.memory = 0.0
            self._update_status()
        elif text == "MR":
            self._append(str(self.memory))
        elif text == "M+":
            try:
                self.memory += SafeEvaluator.evaluate(self._get_display(), self.degrees)
                self._update_status()
            except Exception:
                pass
        elif text == "M-":
            try:
                self.memory -= SafeEvaluator.evaluate(self._get_display(), self.degrees)
                self._update_status()
            except Exception:
                pass
        elif text == "Ans":
            self._append(self._last_result())
        elif text == "±":
            c = self._get_display()
            self._set_display(c[1:] if c.startswith("-") else "-" + c if c else "")
        elif text == "π":
            self._append("π")
        elif text == "e":
            self._append("e")
        elif text == "√":
            self._append("sqrt(")
        elif text == "x!":
            self._append("fact(")
        elif text == "1/x":
            self._append("1/(")
        elif text == "|x|":
            self._append("abs(")
        elif text == "10ˣ":
            self._append("10^(")
        elif text == "eˣ":
            self._append("exp(")
        elif text == "%":
            self._append("/100")
        elif text == "÷":
            self._append("/")
        elif text == "×":
            self._append("*")
        elif text == "00":
            self._append("00")
        else:
            self._append(text)
    def _last_result(self) -> str:
        if self.history:
            return self.history[-1].split(" = ")[-1]
        return "0"
    def _calculate(self):
        expr = self._get_display()
        if not expr:
            return
        try:
            result = SafeEvaluator.evaluate(expr, self.degrees)
            if isinstance(result, float) and result == int(result) and abs(result) < 1e15:
                result = int(result)
            result_str = str(result)
            self.history.append(f"{expr} = {result_str}")
            self._save_history()
            self._update_history_display()
            self._set_display(result_str)
        except (ValueError, ZeroDivisionError, OverflowError, SyntaxError):
            self._set_display("Erro")
    def _load_history(self):
        if os.path.exists("calc_history.json"):
            try:
                with open("calc_history.json", "r") as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []
    def _save_history(self):
        try:
            with open("calc_history.json", "w") as f:
                json.dump(self.history[-50:], f)
        except Exception:
            pass
    def _update_history_display(self):
        self.hist_box.configure(state="normal")
        self.hist_box.delete("1.0", "end")
        for item in self.history[-8:]:
            self.hist_box.insert("end", item + "\n")
        self.hist_box.configure(state="disabled")
    def _update_status(self):
        mode = "DEG" if self.degrees else "RAD"
        self.status.configure(text=f"{mode} | Mem: {self.memory:.4g}")
    def _bind_keyboard(self):
        self.bind("<Key>", self._on_key)
    def _on_key(self, event):
        key = event.char
        if key in "0123456789.+-*/()":
            self._append(key)
        elif key == "\r" or key == "\n":
            self._calculate()
        elif event.keysym == "BackSpace":
            self._set_display(self._get_display()[:-1])
        elif event.keysym == "Escape":
            self._set_display("")
if __name__ == "__main__":
    app = ScientificCalculator()
    app.mainloop()   