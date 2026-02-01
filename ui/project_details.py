import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry # Requires: pip install tkcalendar

class ProjectDetailsForm(tk.Frame):
    def __init__(self, parent, db, project):
        super().__init__(parent, bg="white")
        self.db = db
        self.project = project
        self.widgets = {}
        self.setup_ui()

    def setup_ui(self):
        canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Helper for 2 Fields Per Row ---
        def add_field(parent, label_text, attr, row, col, is_date=False):
            frame = tk.Frame(parent, bg="white")
            frame.grid(row=row, column=col, padx=15, pady=5, sticky="w")
            
            tk.Label(frame, text=label_text, bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
            val = getattr(self.project, attr) or ""
            
            if is_date:
                # Standardized date entry
                widget = DateEntry(frame, width=25, background='darkblue', 
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                if val: widget.set_date(val)
            else:
                widget = tk.Entry(frame, width=28, font=("Arial", 10))
                widget.insert(0, val)
            
            widget.pack(fill="x")
            self.widgets[attr] = widget

        # --- Helper for Full-Width Text Areas ---
        def add_text_area(parent, label_text, attr, row):
            frame = tk.Frame(parent, bg="white")
            frame.grid(row=row, column=0, columnspan=2, padx=15, pady=10, sticky="ew")
            
            tk.Label(frame, text=label_text, bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
            widget = tk.Text(frame, height=4, font=("Arial", 10), bd=1, relief="solid")
            widget.insert("1.0", getattr(self.project, attr) or "")
            widget.pack(fill="x")
            self.widgets[attr] = widget

        # Row 0: Basic Info
        add_field(scrollable_frame, "Project Name:", "name", 0, 0)
        add_field(scrollable_frame, "Customer:", "customer", 0, 1)

        # Row 1: Management
        add_field(scrollable_frame, "Project Manager:", "project_manager", 1, 0)
        add_field(scrollable_frame, "Est. Total Cost:", "total_cost", 1, 1)

        # Row 2: Parts
        add_field(scrollable_frame, "Part Number:", "part_number", 2, 0)
        add_field(scrollable_frame, "Part Name:", "part_name", 2, 1)

        # Row 3: Orders
        add_field(scrollable_frame, "PO Number:", "po_number", 3, 0)
        add_field(scrollable_frame, "Work Order No:", "wo_number", 3, 1)

        # Row 4: Dates (Using DateEntry)
        add_field(scrollable_frame, "PO Date:", "po_date", 4, 0, is_date=True)
        add_field(scrollable_frame, "Due Date:", "due_date", 4, 1, is_date=True)

        # Large Text Areas
        add_text_area(scrollable_frame, "Scopes:", "scopes", 5)
        add_text_area(scrollable_frame, "Out of Scopes:", "out_of_scopes", 6)
        add_text_area(scrollable_frame, "Deliverables:", "deliverables", 7)
        add_text_area(scrollable_frame, "Notes/Description:", "description", 8)

        # Save Button
        btn_save = tk.Button(scrollable_frame, text="Save All Changes", bg="#4CAF50", fg="white", 
                             command=self.save_changes, font=("Arial", 11, "bold"), padx=20, pady=8)
        btn_save.grid(row=9, column=0, columnspan=2, pady=20)

    def save_changes(self):
        data = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, tk.Text):
                data[key] = widget.get("1.0", tk.END).strip()
            elif isinstance(widget, DateEntry):
                data[key] = widget.get_date().strftime("%Y-%m-%d")
            else:
                data[key] = widget.get()
        
        # Keep legacy hidden fields
        data["estimated_time"] = self.project.estimated_time
        data["start_date"] = self.project.start_date
        data["end_date"] = self.project.end_date

        try:
            self.db.update_project(self.project.id, data) #
            for key, val in data.items(): setattr(self.project, key, val)
            messagebox.showinfo("Success", "Project details updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")