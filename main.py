import tkinter as tk
from tkinter import ttk
from updater import check_for_updates
from ui.login_window import LoginWindow


def main():
    should_continue = check_for_updates()
    if not should_continue:
        return

    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
