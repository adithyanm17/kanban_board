# ui/task_card.py
import tkinter as tk

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
        # 1. Title
        tk.Label(self, text=self.task.title, font=("Arial", 10, "bold"), 
                 bg="white", anchor="w").pack(fill="x", padx=5, pady=(5, 2))
        
        # 2. Description
        if self.task.description:
            tk.Label(self, text=self.task.description, font=("Arial", 9), 
                     bg="white", fg="gray", anchor="w", justify="left", 
                     width=25).pack(fill="x", padx=5)

        # 3. Transfer History Logic
        history = self.db.get_latest_move(self.task.id)
        if history:
            from_col, move_date = history
            log_text = f"Transferred from {from_col} on {move_date}"
            tk.Label(self, text=log_text, font=("Arial", 7, "italic"), 
                     bg="white", fg="#2196F3", anchor="w").pack(fill="x", padx=5, pady=(2, 5))

    def bind_events(self, widget):
        widget.bind("<ButtonPress-1>", self.on_drag_start)
        widget.bind("<B1-Motion>", self.on_drag_motion)
        widget.bind("<ButtonRelease-1>", self.on_drag_stop)

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