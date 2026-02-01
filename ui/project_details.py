import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
class ProjectDetailsForm(tk.Frame):
    def __init__(self, parent, db, project):
        super().__init__(parent, bg="white")
        self.db = db
        self.project = project
        self.setup_ui()

    def setup_ui(self):
        # Use a canvas for scrolling if the form gets too long
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Layout Helper
        def create_row(parent, label_text, attr_name, row_idx, is_text=False):
            tk.Label(parent, text=label_text, bg="white", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="w", pady=5, padx=10)
            val = getattr(self.project, attr_name) or ""
            if is_text:
                widget = tk.Text(parent, width=60, height=4, font=("Arial", 10), bd=1, relief="solid")
                widget.insert("1.0", val)
            else:
                widget = tk.Entry(parent, width=60, font=("Arial", 10))
                widget.insert(0, val)
            widget.grid(row=row_idx, column=1, sticky="w", pady=5, padx=10)
            return widget

        # Fields Group 1: Basics
        self.widgets = {
            "name": create_row(self.scrollable_frame, "Project Name:", "name", 0),
            "customer": create_row(self.scrollable_frame, "Customer:", "customer", 1),
            "project_manager": create_row(self.scrollable_frame, "Project Manager:", "project_manager", 2),
            "part_number": create_row(self.scrollable_frame, "Part Number:", "part_number", 3),
            "part_name": create_row(self.scrollable_frame, "Part Name:", "part_name", 4),
            "total_cost": create_row(self.scrollable_frame, "Est. Total Cost:", "total_cost", 5),
            
            # Group 2: Documentation
            "po_number": create_row(self.scrollable_frame, "PO Number:", "po_number", 6),
            "wo_number": create_row(self.scrollable_frame, "Work Order No:", "wo_number", 7),
            "po_date": create_row(self.scrollable_frame, "PO Date:", "po_date", 8),
            "due_date": create_row(self.scrollable_frame, "Due Date:", "due_date", 9),
            
            # Group 3: Large Text Fields
            "scopes": create_row(self.scrollable_frame, "Scopes:", "scopes", 10, True),
            "out_of_scopes": create_row(self.scrollable_frame, "Out of Scopes:", "out_of_scopes", 11, True),
            "deliverables": create_row(self.scrollable_frame, "Deliverables:", "deliverables", 12, True),
            "description": create_row(self.scrollable_frame, "Notes/Description:", "description", 13, True),
        }

        # Save Button
        btn_save = tk.Button(self.scrollable_frame, text="Save All Changes", bg="#4CAF50", fg="white", 
                             command=self.save_changes, font=("Arial", 11, "bold"), padx=20, pady=10)
        btn_save.grid(row=14, column=0, columnspan=2, pady=30)

    def save_changes(self):
        data = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, tk.Text):
                data[key] = widget.get("1.0", tk.END).strip()
            else:
                data[key] = widget.get()
        
        # Add the missing legacy fields so update_project doesn't break
        data["estimated_time"] = self.project.estimated_time
        data["start_date"] = self.project.start_date
        data["end_date"] = self.project.end_date

        try:
            self.db.update_project(self.project.id, data)
            # Refresh local object
            for key, val in data.items():
                setattr(self.project, key, val)
            messagebox.showinfo("Success", "Project details updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")