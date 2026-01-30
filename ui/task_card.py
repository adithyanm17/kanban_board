# ui/task_card.py
import tkinter as tk
from ui.dialogs import CreateTaskDialog

class TaskCard(tk.Frame):
    def __init__(self, parent, db, task, drag_start_callback, drag_end_callback):
        super().__init__(parent, bg="white", bd=2, relief="raised", cursor="hand2")
        self.db = db 
        self.task = task
        self.drag_start_callback = drag_start_callback
        self.drag_end_callback = drag_end_callback
        
        self.setup_ui()
        self.bind_events(self)
        for child in self.winfo_children():
            self.bind_events(child)

    def setup_ui(self):
        # Container padding ensures content doesn't touch the borders
        self.container = tk.Frame(self, bg="white", padx=5, pady=5)
        self.container.pack(fill="both", expand=True)

        # 1. Title - Allow wrapping for long titles
        tk.Label(self.container, text=self.task.title, font=("Arial", 10, "bold"), 
                 bg="white", anchor="w", justify="left", wraplength=220).pack(fill="x", pady=(0, 2))
        
        # 2. Description - wraplength prevents horizontal overflow
        if self.task.description:
            tk.Label(self.container, text=self.task.description, font=("Arial", 9), 
                     bg="white", fg="gray", anchor="w", justify="left", 
                     wraplength=220).pack(fill="x")

        # 3. Transfer History Logic
        history = self.db.get_latest_move(self.task.id)
        if history:
            from_col, move_date = history
            log_text = f"Transferred from {from_col}\non {move_date}"
            tk.Label(self.container, text=log_text, font=("Arial", 7, "italic"), 
                     bg="white", fg="#2196F3", anchor="w", justify="left").pack(fill="x", pady=(5, 0))

        # 4. Assigned Employees Display
        assignees = self.db.get_task_assignees(self.task.id)
        if assignees:
            names_text = "Assignees: " + ", ".join(assignees)
            tk.Label(self.container, text=names_text, font=("Arial", 8, "bold"), 
                     bg="white", fg="#4CAF50", anchor="w", justify="left", 
                     wraplength=220).pack(fill="x", pady=(5, 0))

    def on_edit(self, event):
        from ui.dialogs import CreateTaskDialog
        dialog = CreateTaskDialog(self)
        dialog.title_entry.insert(0, self.task.title)
        dialog.desc_text.insert("1.0", self.task.description)
        
        # Optional: Add a simple Listbox or Checkbuttons here to select employees
        # For now, let's trigger the save
        if dialog.title_str:
            self.db.update_task_details(self.task.id, dialog.title_str, dialog.desc_str)
            # To add an employee, you can call self.db.assign_employee_to_task(self.task.id, selected_id)
            self.master.master.master.master.refresh_board()

    def bind_events(self, widget):
        widget.bind("<ButtonPress-1>", self.on_drag_start)
        widget.bind("<B1-Motion>", self.on_drag_motion)
        widget.bind("<ButtonRelease-1>", self.on_drag_stop)
        widget.bind("<Double-Button-1>", self.on_edit) # Add this line

    def on_drag_start(self, event):
        self.drag_window = tk.Toplevel(self)
        self.drag_window.overrideredirect(True) 
        self.drag_window.attributes('-alpha', 0.6)
        
        placeholder_frame = tk.Frame(self.drag_window, bg=self["bg"], bd=self["bd"], relief=self["relief"])
        placeholder_frame.pack(fill="both", expand=True)
        tk.Label(placeholder_frame, text=self.task.title, font=("Arial", 10, "bold"), bg="white", anchor="w").pack(fill="x", padx=5, pady=5)
        
        self.drag_window.geometry(f"{self.winfo_width()}x{self.winfo_height()}+{event.x_root}+{event.y_root}")
        self.drag_start_callback(self)

    def on_drag_motion(self, event):
        if hasattr(self, 'drag_window'):
            self.drag_window.geometry(f"+{event.x_root}+{event.y_root}")

    def on_drag_stop(self, event):
        if hasattr(self, 'drag_window'):
            self.drag_window.destroy()
        self.drag_end_callback(self, event.x_root, event.y_root)