import subprocess


def open_app(app_name: str) -> str:
    try:
        subprocess.Popen(["open", "-a", app_name])
        return f"Opened {app_name}."
    except Exception as e:
        return f"Couldn't open {app_name}: {e}"


def close_app(app_name: str) -> str:
    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                f'tell application "{app_name}" to quit'
            ],
            check=True
        )
        return f"Closed {app_name}."
    except Exception as e:
        return f"Couldn't close {app_name}: {e}"


def list_open_apps() -> str:
    """Return applications currently running."""
    try:
        result = subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to get name of every process whose background only is false'
            ],
            capture_output=True,
            text=True,
            check=True
        )

        return result.stdout.strip()

    except Exception as e:
        return f"Couldn't get open applications: {e}"

