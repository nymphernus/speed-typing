"""
Entry point for the Speed Typing Test application.
"""

import tkinter as tk
from .app import SpeedTypingApp


def main():
    """Run the application."""
    root = tk.Tk()
    app = SpeedTypingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
