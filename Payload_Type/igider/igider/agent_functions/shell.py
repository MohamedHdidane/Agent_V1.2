import subprocess

def run_shell_command(command: str) -> str:
    try:
        result = subprocess.run(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return f"[X] Shell command error: {str(e)}"