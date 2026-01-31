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
        # Using a main container with padding to prevent text touching borders
        self.container = tk.Frame(self, bg="white", padx=8, pady=8)
        self.container.pack(fill="both", expand=True)

        # 1. Title - Dynamic wrapping for long names
        # wraplength=200 ensures text moves to a new line before hitting the edge
        self.lbl_title = tk.Label(self.container, text=self.task.title, 
                                  font=("Arial", 10, "bold"), bg="white", 
                                  anchor="w", justify="left", wraplength=200)
        self.lbl_title.pack(fill="x", pady=(0, 4))
        
        # 2. Description - Wrap long descriptions
        if self.task.description:
            self.lbl_desc = tk.Label(self.container, text=self.task.description, 
                                     font=("Arial", 9), bg="white", fg="gray", 
                                     anchor="w", justify="left", wraplength=200)
            self.lbl_desc.pack(fill="x", pady=(0, 4))

        # 3. Transfer History - Multiline support
        history = self.db.get_latest_move(self.task.id)
        if history:
            from_col, move_date = history
            log_text = f"Transferred from {from_col}\non {move_date}"
            self.lbl_log = tk.Label(self.container, text=log_text, 
                                    font=("Arial", 7, "italic"), bg="white", 
                                    fg="#2196F3", anchor="w", justify="left")
            self.lbl_log.pack(fill="x", pady=(4, 0))

        # 4. Assigned Employees - Fix for many names
        assignees = self.db.get_task_assignees(self.task.id)
        if assignees:
            names_text = "Assignees: " + ", ".join(assignees)
            # wraplength=200 allows the list of names to grow vertically
            self.lbl_assignees = tk.Label(self.container, text=names_text, 
                                          font=("Arial", 8, "bold"), bg="white", 
                                          fg="#4CAF50", anchor="w", 
                                          justify="left", wraplength=200)
            self.lbl_assignees.pack(fill="x", pady=(6, 0))

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
        # 1. Capture the offset so the card doesn't 'jump' to the cursor
        self._drag_data = {"x": event.x, "y": event.y}
        
        # 2. Create the ghost window instantly
        self.drag_window = tk.Toplevel(self)
        self.drag_window.overrideredirect(True)
        self.drag_window.attributes("-topmost", True)
        
        # 3. Use a single label instead of copying the whole frame for speed
        p_frame = tk.Frame(self.drag_window, bg="#2196F3", bd=1, relief="solid")
        p_frame.pack(fill="both", expand=True)
        tk.Label(p_frame, text=self.task.title, fg="white", 
                 font=("Arial", 10, "bold"), wraplength=180).pack(padx=10, pady=10)
        
        # 4. Initial position
        self.drag_window.geometry(f"+{event.x_root}+{event.y_root}")
        self.drag_start_callback(self)

    def on_drag_motion(self, event):
        if hasattr(self, 'drag_window'):
            # Calculate new position
            x = event.x_root - self._drag_data['x']
            y = event.y_root - self._drag_data['y']
            self.drag_window.geometry(f"+{x}+{y}")
            # Force redraw to remove 'ghosting' lag
            self.drag_window.update_idletasks()
    def on_drag_stop(self, event):
        if hasattr(self, 'drag_window'):
            self.drag_window.destroy()
        self.drag_end_callback(self, event.x_root, event.y_root)