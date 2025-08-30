from datetime import datetime


def add_log(message: str):
    """
    Short helper function to print log messages, including time stamps.

    Args:
        message: Message to be printed
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
