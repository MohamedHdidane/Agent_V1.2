import os

def _sanitize_path(user_path: str) -> str:
    """Resolve absolute path and block traversal outside allowed directories."""
    root_dir = os.getcwd()  # Restrict to current working directory
    full_path = os.path.abspath(os.path.join(root_dir, user_path))

    if not full_path.startswith(root_dir):
        raise ValueError("Path traversal blocked!")
    return full_path

def cat_file(path: str) -> str:
    try:
        safe_path = _sanitize_path(path)
        with open(safe_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"[X] Error reading file: {str(e)}"

def list_files(path: str) -> str:
    try:
        safe_path = _sanitize_path(path) if path else os.getcwd()
        return "\n".join(os.listdir(safe_path))
    except Exception as e:
        return f"[X] Error listing files: {str(e)}"

def change_dir(path: str) -> str:
    try:
        safe_path = _sanitize_path(path)
        os.chdir(safe_path)
        return f"Changed directory to: {os.getcwd()}"
    except Exception as e:
        return f"[X] Error changing directory: {str(e)}"

def get_pwd() -> str:
    try:
        return os.getcwd()
    except Exception as e:
        return f"[X] Error getting current directory: {str(e)}"