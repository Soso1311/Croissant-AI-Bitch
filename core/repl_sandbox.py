import sys
import io
import traceback
from typing import Dict, Any

class SecureREPL:
    """Stateful Python REPL kernel with namespace isolation and output capture."""

    def __init__(self):
        safe_builtins = dict(__builtins__)
        for unsafe in ["eval", "exec", "compile", "input"]:
            safe_builtins.pop(unsafe, None)

        self.global_scope: Dict[str, Any] = {
            "__builtins__": safe_builtins,
        }

    def execute(self, code: str) -> str:
        if "ctypes" in code or "os.system" in code:
            return "SECURITY REFUSAL: Direct system access blocked in Python REPL. Use terminal tools instead."

        old_stdout, old_stderr = sys.stdout, sys.stderr
        redirected_stdout, redirected_stderr = io.StringIO(), io.StringIO()

        try:
            sys.stdout, sys.stderr = redirected_stdout, redirected_stderr
            exec(code, self.global_scope)
            
            stdout_val = redirected_stdout.getvalue()
            stderr_val = redirected_stderr.getvalue()

            output = ""
            if stdout_val:
                output += f"[STDOUT]\n{stdout_val}\n"
            if stderr_val:
                output += f"[STDERR]\n{stderr_val}\n"
            
            return output.strip() if output.strip() else "Executed successfully (no output)."
        except Exception:
            return f"[RUNTIME EXCEPTION]\n{traceback.format_exc()}"
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr
