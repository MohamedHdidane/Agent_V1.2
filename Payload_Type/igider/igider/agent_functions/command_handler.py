from .shell import run_shell_command
from .files import cat_file, list_files, change_dir, get_pwd
from .system import list_env, get_user, get_hostname, exit_agent
from .processes import list_processes
from .network import list_connections

COMMAND_MAP = {
    "shell": run_shell_command,
    "cat": cat_file,
    "ls": list_files,
    "cd": change_dir,
    "pwd": get_pwd,
    "env": list_env,
    "whoami": get_user,
    "hostname": get_hostname,
    "ps": list_processes,
    "netstat": list_connections,
    "exit": exit_agent,
}

def handle_command(command: str, args: str) -> str:
    try:
        if command in COMMAND_MAP:
            return COMMAND_MAP[command](args)
        return f"[X] Unknown command: {command}"
    except Exception as e:
        return f"[X] Error executing {command}: {str(e)}"