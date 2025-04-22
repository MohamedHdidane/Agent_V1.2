import subprocess
import platform

def list_processes() -> str:
    try:
        if platform.system() == "Windows":
            cmd = ["tasklist"]
        else:
            cmd = ["ps", "aux"]  # Use list instead of string for safer execution
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return f"[X] Error listing processes: {str(e)}"