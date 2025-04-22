import os
import socket
import getpass
import sys
def list_env(_: str = "") -> str:
    try:
        return "\n".join([f"{k}={v}" for k, v in os.environ.items()])
    except Exception as e:
        return f"[X] Error listing environment variables: {str(e)}"

def get_user(_: str = "") -> str:
    try:
        return getpass.getuser()
    except Exception as e:
        return f"[X] Error getting user: {str(e)}"

def get_hostname(_: str = "") -> str:
    try:
        return socket.gethostname()
    except Exception as e:
        return f"[X] Error getting hostname: {str(e)}"

def exit_agent(_: str = "") -> str:
    try:
        print("[*] Agent exiting...")
        sys.exit(0)
    except Exception as e:
        return f"[X] Error exiting agent: {str(e)}"