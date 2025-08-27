import math, os, platform, subprocess
from sympy import symbols, Eq, solve, simplify
from sympy.parsing.sympy_parser import parse_expr

# Predefined constants
CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "c": 299792458,                    # speed of light
    "G": 6.67430e-11,                  # gravitational constant
    "h": 6.62607015e-34,               # Planck
    "ħ": 1.054571817e-34,             # Reduced Planck
    "k": 1.380649e-23,                # Boltzmann
    "Na": 6.02214076e23,              # Avogadro
    "R": 8.314462618,                 # gas constant
    "g": 9.8,                          # gravity
    "Z": 1.60217663e-19,              # electron charge
    "ϵ0": 8.8541878128e-12,           # vacuum permittivity
    "μ0": 1.25663706212e-6            # vacuum permeability
}

class Symbolic:
    def __init__(self, law):
        self.raw = law
        self.expr = parse_expr(law.split("=")[-1])
        print(f"[Symbolic] Law Defined: {law}")

class Infer:
    def __init__(self, law, values={}):
        self.law = law
        self.values = values
        self.run()

    def run(self):
        try:
            if "=" in self.law:
                lhs, rhs = self.law.split("=")
                lhs, rhs = lhs.strip(), rhs.strip()

                if "if" in rhs and "then" in rhs:
                    self._handle_conditional(rhs)
                elif lhs in self.values:
                    self._solve_equation(lhs, rhs)
                else:
                    self._evaluate_expression(rhs)
            else:
                self._evaluate_expression(self.law)
        except Exception as e:
            print(f"[Infer] Unexpected error: {e}")

    def _evaluate_expression(self, expr):
        local_env = {**CONSTANTS, **self.values}
        try:
            parsed_expr = parse_expr(expr, evaluate=False)
            result = parsed_expr.subs(local_env).evalf()
            print(f"[Infer] Solved: {result}")
        except Exception as e:
            print(f"[Infer] Eval Error: {e}")

    def _solve_equation(self, lhs, rhs):
        try:
            lhs_expr = parse_expr(lhs)
            rhs_expr = parse_expr(rhs)
            equation = Eq(lhs_expr, rhs_expr)
            result = solve(equation)
            print(f"[Infer] Equation Solved: {result}")
        except Exception as e:
            print(f"[Infer] Solve Error: {e}")

    def _handle_conditional(self, logic):
        try:
            condition, action = logic.split("then")
            condition = condition.replace("if", "").strip()
            action = action.strip()
            local_env = {**CONSTANTS, **self.values}
            condition_expr = parse_expr(condition, evaluate=True).subs(local_env)

            if condition_expr:
                print(f"[Infer] ✅ Condition True: {condition}")
                self._execute_action(action)
            else:
                print(f"[Infer] ❌ Condition False: {condition}")
        except Exception as e:
            print(f"[Infer] Conditional Error: {e}")

    def _execute_action(self, action):
        try:
            if action.startswith("open("):
                path = action.split("open(")[1].split(")")[0].strip("'\"")
                os.startfile(path) if platform.system() == "Windows" else os.system(f"xdg-open {path}")
                print(f"[System] Opened: {path}")

            elif action.startswith("say("):
                msg = action.split("say(")[1].split(")")[0].strip("'\"")
                if platform.system() == "Windows":
                    subprocess.run(["powershell", f"Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{msg}')"])
                else:
                    os.system(f'say "{msg}"')
                print(f"[System] Said: {msg}")

            elif action.startswith("cmd:"):
                cmd = action.replace("cmd:", "").strip()
                output = subprocess.check_output(cmd, shell=True)
                print(f"[Shell] Output:\n{output.decode()}")

            else:
                print(f"[Action] Unknown: {action}")

        except Exception as e:
            print(f"[System Error] {e}")
