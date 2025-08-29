import subprocess
#cmd utils
def run_ssh_cmd(user_at_host: str, cmd: str, path: str) -> str:
    """Run on remote via SSH and return stdout+stderr."""
    try:
        full = f"ssh {user_at_host} 'cd {path} && bash -lc {sh_quote(cmd)}'"
        proc = subprocess.run(full, shell=True, capture_output=True, text=True)
        return (proc.stdout or "") + (proc.stderr or "")
    except Exception as e:
        return f"❌ run_ssh_cmd error: {e}\n"


def run_local_cmd(cmd: str, path: str) -> str:
    """Run locally in cwd=path and return stdout+stderr."""
    try:
        proc = subprocess.run(["bash", "-lc", cmd], cwd=path, capture_output=True, text=True)
        return (proc.stdout or "") + (proc.stderr or "")
    except Exception as e:
        return f"❌ run_local_cmd error: {e}\n"

