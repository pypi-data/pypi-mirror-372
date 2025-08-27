import math
import re

# Global law database for symbolic definitions
laws_db = {}

class Infer:
    def solve(self, expression):
        try:
            # Handle conditional logic: x = if condition then action
            if "if" in expression:
                match = re.match(r"(.+)=if(.+)then(.+)", expression.replace(" ", ""))
                if not match:
                    return "[Infer] Invalid conditional expression"
                _, condition, action = match.groups()
                if eval(condition):
                    return f"[Infer] Condition met, triggering: {action}"
                else:
                    return "[Infer] Condition not met"
            else:
                # Evaluate expression using symbolic law db and math
                full_context = {**math.__dict__}
                for k, v in laws_db.items():
                    full_context[k] = v()
                result = eval(expression, {}, full_context)
                return f"[Infer] Result: {result}"
        except Exception as e:
            return f"[Infer] Error: {e}"

class Symbolic:
    def define(self, definition):
        try:
            # Define symbolic law like: area = lambda r: pi * r**2
            key, expr = definition.split("=", 1)
            key = key.strip()
            expr = expr.strip()

            # Turn into a lambda expression
            if "lambda" not in expr:
                return "[Symbolic] Expression must be a lambda, e.g. f = lambda x: x**2"

            laws_db[key] = eval(expr, {"math": math})
            return f"[Symbolic] Defined: {key}"
        except Exception as e:
            return f"[Symbolic] Error: {e}"
