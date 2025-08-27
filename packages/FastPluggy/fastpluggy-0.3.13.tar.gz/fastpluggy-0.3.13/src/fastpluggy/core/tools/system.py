import logging
import os
import signal
import subprocess
from pathlib import Path

def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def restart_application():
    os.kill(os.getpid(), signal.SIGINT)

def restart_application_force():
    os.kill(os.getpid(), signal.SIGKILL)


def trigger_reload(plugins_dir: Path | str, create_file:bool = False):
    plugins_dir = Path(plugins_dir)

    logging.info(f"Touching/delete an file under plugins_dir is enough to trigger uvicorn reload: {plugins_dir}")

    marker = plugins_dir / ".reload-trigger"
    # toggle it so every call is a filesystem event
    if marker.exists():
        marker.unlink()
        logging.info("Removed reload marker")
    else:
        if create_file:
            marker.write_text("reload\n")
            logging.info("Created reload marker")


