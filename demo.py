import ast
import subprocess
import tempfile
from typing import List, Dict


class CodeReviewEngine:
    def __init__(self, code: str):
        """Initialize the code review engine."""
        self.code = code
        self.tree = ast.parse(code)
        self.issues: List[Dict] = []

    def detect_syntax_errors(self):
        """Detects syntax errors in the code."""
        try:
            ast.parse(self.code)
        except SyntaxError as e:
            self.issues.append({
                "type": "Syntax Error",
                "message": f"Syntax error at line {e.lineno}: {e.msg}",
                "line": e.lineno
            })

    def detect_undefined_variables(self):
        """Detects undefined variables while avoiding duplicates with flake8."""
        defined_vars = set()
        loop_vars = set()

        # Collect assigned and loop variables
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):  # Variables assigned in the script
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined_vars.add(target.id)

            elif isinstance(node, ast.For):  # Variables defined in for loops
                if isinstance(node.target, ast.Name):
                    loop_vars.add(node.target.id)

            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                # Check if variable is undefined and not a built-in
                if node.id not in defined_vars and node.id not in loop_vars and node.id not in dir(__builtins__):
                    self.issues.append({
                        "type": "Undefined Variable",
                        "message": f"Undefined variable '{node.id}'",
                        "line": node.lineno
                    })

    def detect_long_functions(self, max_lines: int = 20):
        """Detects functions that are too long."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                function_length = len(node.body)
                if function_length > max_lines:
                    self.issues.append({
                        "type": "Code Smell",
                        "message": f"Function '{node.name}' is too long ({function_length} lines).",
                        "line": node.lineno
                    })

    def check_style_and_formatting(self):
        """Uses flake8 to check for style and formatting issues."""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
                temp_file.write(self.code.encode())
                temp_file.flush()
                temp_filename = temp_file.name

            result = subprocess.run(
                ["flake8", "--format=%(row)d: %(code)s - %(text)s", temp_filename],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                for line in result.stdout.splitlines():
                    line_number, message = line.split(":", 1)
                    self.issues.append({
                        "type": "Style/Formatting Issue",
                        "message": message.strip(),
                        "line": int(line_number)
                    })

        except FileNotFoundError:
            self.issues.append({
                "type": "Error",
                "message": "flake8 is not installed. Please install it using 'pip install flake8'.",
                "line": 0
            })
        except Exception as e:
            self.issues.append({
                "type": "Error",
                "message": f"Failed to run flake8: {str(e)}",
                "line": 0
            })

    def review_code(self):
        """Runs all checks and returns the issues found."""
        print("🚀 Starting Code Review Engine...")
        
        print("🔍 Running syntax check...")
        self.detect_syntax_errors()

        print("🔍 Running undefined variable check...")
        self.detect_undefined_variables()

        print("🔍 Running long function check...")
        self.detect_long_functions()

        print("🔍 Running style check...")
        self.check_style_and_formatting()

        print("✅ Review completed.")
        return self.issues


# Example Usage with Faulty Code
if __name__ == "__main__":
    faulty_code = """
def test_function():
    x = 10
    if x > 5  # ❌ Missing colon (Syntax Error)
        y = x + 5  
        for i in range(10):
            print(i, "This is a long line that should be flagged for exceeding 79 characters in length.")  # ❌ Style issue
        
        return y  # ❌ 'y' might be undefined if the 'if' condition fails

def another_function():
    for i in range(25):  # ❌ Function too long (Code Smell)
        print("Loop iteration", i)
        print("Another line")
        print("More processing...")
        print("Still going...")
        print("Almost there...")
        print("Just a bit more...")
        print("This function is getting out of control!")
        print("Yep, it's too long.")
"""

    review_engine = CodeReviewEngine(faulty_code)
    issues = review_engine.review_code()

    print("\n🔎 Code Review Issues:")
    for issue in issues:
        print(f"Line {issue['line']}: [{issue['type']}] {issue['message']}")

    print("✅ Review Completed.")
