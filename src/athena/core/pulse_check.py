"""
athena.core.pulse_check
=======================
Checks daemon activity and ensures core services are active.
"""

import subprocess


def is_daemon_running() -> bool:
    """Returns True if athenad.py process is currently running."""
    try:
        # pgrep -f matches full command line
        check = subprocess.run(["pgrep", "-f", "athenad.py"], capture_output=True)
        return check.returncode == 0
    except Exception:
        return False

def ensure_active():
    """Revives the daemon if it is not running."""
    if not is_daemon_running():
        from athena.boot.loaders.system import SystemLoader
        SystemLoader.enforce_daemon()
