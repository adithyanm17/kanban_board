import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

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

        # Configuration for 4 entry fields per row (Total 8 columns in grid: Label, Entry, Label, Entry...)
        def add_field(parent, label_text, attr, row, col, is_date=False):
            tk.Label(parent, text=label_text, bg="white", font=("Arial", 8, "bold")).grid(row=row, column=col*2, sticky="w", padx=(10, 2), pady=5)
            val = getattr(self.project, attr) or ""
            
            if is_date:
                widget = DateEntry(parent, width=15, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                if val: widget.set_date(val)
            else:
                widget = tk.Entry(parent, width=18)
                widget.insert(0, val)
            
            widget.grid(row=row, column=col*2 + 1, sticky="w", padx=(0, 10), pady=5)
            self.widgets[attr] = widget

        # Configuration for 2 text areas per row
        def add_text_area(parent, label_text, attr, row, col):
            frame = tk.Frame(parent, bg="white")
            frame.grid(row=row, column=col*4, columnspan=4, padx=10, pady=10, sticky="nsew")
            
            tk.Label(frame, text=label_text, bg="white", font=("Arial", 8, "bold")).pack(anchor="w")
            widget = tk.Text(frame, height=5, width=40, font=("Arial", 9), bd=1, relief="solid")
            # Preserve existing data (like description from creation)
            widget.insert("1.0", getattr(self.project, attr) or "")
            widget.pack(fill="both", expand=True)
            self.widgets[attr] = widget

        # Row 0: 4 Fields
        add_field(scrollable_frame, "Project Name:", "name", 0, 0)
        add_field(scrollable_frame, "Customer:", "customer", 0, 1)
        add_field(scrollable_frame, "Manager:", "project_manager", 0, 2)
        add_field(scrollable_frame, "Total Cost:", "total_cost", 0, 3)

        # Row 1: 4 Fields
        add_field(scrollable_frame, "Part Number:", "part_number", 1, 0)
        add_field(scrollable_frame, "Part Name:", "part_name", 1, 1)
        add_field(scrollable_frame, "PO Number:", "po_number", 1, 2)
        add_field(scrollable_frame, "Work Order:", "wo_number", 1, 3)

        # Row 2: 2 Date Fields (taking up half the row)
        add_field(scrollable_frame, "PO Date:", "po_date", 2, 0, is_date=True)
        add_field(scrollable_frame, "Due Date:", "due_date", 2, 1, is_date=True)

        # Row 3: 2 Text Areas (Scopes & Out of Scopes)
        add_text_area(scrollable_frame, "Scopes:", "scopes", 3, 0)
        add_text_area(scrollable_frame, "Out of Scopes:", "out_of_scopes", 3, 1)

        # Row 4: 2 Text Areas (Deliverables & Description/Notes)
        add_text_area(scrollable_frame, "Deliverables:", "deliverables", 4, 0)
        # This preserves the original project description entered during creation
        add_text_area(scrollable_frame, "Notes/Description:", "description", 4, 1)

        # Save Button
        btn_save = tk.Button(scrollable_frame, text="Save All Changes", bg="#4CAF50", fg="white", 
                             command=self.save_changes, font=("Arial", 10, "bold"), padx=20, pady=10)
        btn_save.grid(row=5, column=0, columnspan=8, pady=20)

    def save_changes(self):
        data = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, tk.Text):
                data[key] = widget.get("1.0", tk.END).strip()
            elif isinstance(widget, DateEntry):
                data[key] = widget.get_date().strftime("%Y-%m-%d")
            else:
                data[key] = widget.get()
        
        # Maintain hidden project data
        data["estimated_time"] = self.project.estimated_time
        data["start_date"] = self.project.start_date
        data["end_date"] = self.project.end_date

        try:
            self.db.update_project(self.project.id, data)
            for key, val in data.items(): setattr(self.project, key, val)
            messagebox.showinfo("Success", "Project data synchronized.")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")