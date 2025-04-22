import subprocess
import platform

def list_connections() -> str:
    try:
        if platform.system() == "Windows":
            cmd = ["netstat", "-ano"]
        else:
            cmd = ["netstat", "-tunap"]  
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return f"[X] Error listing network connections: {str(e)}"