import ast
import subprocess
import tempfile
import re
from typing import List, Dict


class CodeAutoFixEngine:
    def __init__(self, code: str):
        """Initialize the code auto-fix engine."""
        self.original_code = code

    def auto_fix_syntax_errors(self):
        """Attempt to fix common syntax errors and missing colons."""
        fixed_code = self.original_code

        # Add missing colons at the end of if/elif/for/while/def/class statements
        lines = fixed_code.split('\n')
        corrected_lines = []

        for line in lines:
            stripped = line.strip()
            if re.match(r'^(if|elif|for|while|def|class) .*(?<!:)$', stripped):
                corrected_lines.append(line + ':')
            else:
                corrected_lines.append(line)

        fixed_code = '\n'.join(corrected_lines)

        # Fix indentation (replace tabs with 4 spaces)
        fixed_code = re.sub(r'\t', '    ', fixed_code)

        # Add missing pass for empty blocks
        lines = fixed_code.split('\n')
        new_lines = []
        for i, line in enumerate(lines):
            if re.match(r'^(\s*)(if|elif|for|while|def|class) .+:$', line):
                if i + 1 >= len(lines) or lines[i + 1].strip() == '':
                    new_lines.append(line)
                    new_lines.append('    pass')
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        return '\n'.join(new_lines)

    def auto_format_with_black(self, code: str) -> str:
        """Auto-format the code using Black formatter if available."""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
                temp_file.write(code.encode())
                temp_file.flush()
                temp_filename = temp_file.name

            subprocess.run(["black", temp_filename], capture_output=True, text=True)

            with open(temp_filename, 'r') as f:
                formatted_code = f.read()
            return formatted_code

        except Exception:
            return code  # Fallback: return unformatted

    def fix_undefined_variables(self, code: str) -> str:
        """Automatically define undefined variables with default values (like x = 0)."""
        try:
            tree = ast.parse(code)
            defined_vars = set()
            used_vars = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined_vars.add(target.id)
                elif isinstance(node, ast.FunctionDef):
                    for arg in node.args.args:
                        defined_vars.add(arg.arg)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used_vars.add(node.id)

            undefined_vars = used_vars - defined_vars - set(dir(__builtins__))

            # Add undefined variables at the top of the code with default value 0
            if undefined_vars:
                declarations = ''.join(f'{var} = 0\n' for var in undefined_vars)
                code = declarations + code

            return code
        except Exception:
            return code

    def fix_undefined_returns(self, code: str) -> str:
        """Replace undefined return variables with 'None'."""
        try:
            tree = ast.parse(code)
            defined_vars = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined_vars.add(target.id)
                elif isinstance(node, ast.FunctionDef):
                    for arg in node.args.args:
                        defined_vars.add(arg.arg)

            lines = code.split('\n')
            corrected_lines = []
            for line in lines:
                if line.strip().startswith('return '):
                    return_var = line.strip().split()[1]
                    if return_var not in defined_vars:
                        line = f'return None'
                corrected_lines.append(line)

            return '\n'.join(corrected_lines)
        except Exception:
            return code

    def fix_style_issues(self, code: str) -> str:
        """Trim overly long lines and simplify style errors."""
        lines = code.split('\n')
        corrected_lines = []
        for line in lines:
            if len(line) > 100:
                corrected_lines.append(line[:100] + '  # truncated')
            else:
                corrected_lines.append(line)
        return '\n'.join(corrected_lines)

    def auto_fix_code(self):
        """Run automatic fixes and show both faulty and corrected code."""
        print("🚀 Starting Auto-Fix Engine...")

        print("\n❌ Faulty Code:")
        print(self.original_code)

        print("\n🔧 Fixing syntax errors, missing lines, and indentation...")
        fixed_code = self.auto_fix_syntax_errors()

        print("🔄 Defining undefined variables...")
        fixed_code = self.fix_undefined_variables(fixed_code)

        print("🔄 Replacing undefined return values with 'None'...")
        fixed_code = self.fix_undefined_returns(fixed_code)

        print("🎯 Fixing style issues...")
        fixed_code = self.fix_style_issues(fixed_code)

        print("✨ Formatting with Black (if available)...")
        fixed_code = self.auto_format_with_black(fixed_code)

        print("\n✅ Corrected and Modified Code:")
        print(fixed_code)

        print("\n✅ Auto-fix completed.")
        return fixed_code


# Example Usage
if __name__ == "__main__":
    faulty_code = """
def test_function():
    if x > 5
        y = x + 5
        for i in range(10):
            print(i, "This is an excessively long line that should definitely be shortened and flagged by style fixes.")
"""

    fixer = CodeAutoFixEngine(faulty_code)
    fixer.auto_fix_code()
