# ui/dialogs.py
import tkinter as tk
from tkinter import simpledialog

class CreateTaskDialog(simpledialog.Dialog):
    def __init__(self, parent):
        self.title_str = None
        self.desc_str = None
        super().__init__(parent, title="Create New Task")

    def body(self, master):
        tk.Label(master, text="Title:").grid(row=0, sticky=tk.W)
        self.title_entry = tk.Entry(master, width=30)
        self.title_entry.grid(row=0, column=1)

        tk.Label(master, text="Description:").grid(row=1, sticky=tk.W, pady=(10, 0))
        self.desc_text = tk.Text(master, width=30, height=5)
        self.desc_text.grid(row=1, column=1, pady=(10, 0))
        return self.title_entry # initial focus

    def apply(self):
        self.title_str = self.title_entry.get()
        self.desc_str = self.desc_text.get("1.0", tk.END).strip()

def ask_new_task_info(parent):
    dialog = CreateTaskDialog(parent)
    return dialog.title_str, dialog.desc_str