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

        # Configuration for 4 fields per row (8 columns total)
        # Increased width to 22 for entries to fill the 1200px geometry better
        def add_field(parent, label_text, attr, row, col, is_date=False):
            tk.Label(parent, text=label_text, bg="white", font=("Arial", 8, "bold")).grid(row=row, column=col*2, sticky="w", padx=(15, 2), pady=8)
            val = getattr(self.project, attr) or ""
            
            if is_date:
                widget = DateEntry(parent, width=20, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                if val: 
                    try: widget.set_date(val)
                    except: pass
            else:
                widget = tk.Entry(parent, width=25, font=("Arial", 9))
                widget.insert(0, val)
            
            widget.grid(row=row, column=col*2 + 1, sticky="w", padx=(0, 15), pady=8)
            self.widgets[attr] = widget

        # Configuration for 2 large text areas per row
        def add_text_area(parent, label_text, attr, row, col):
            frame = tk.Frame(parent, bg="white")
            # Width is increased by spans; text widget width increased to 55
            frame.grid(row=row, column=col*4, columnspan=4, padx=15, pady=10, sticky="nsew")
            
            tk.Label(frame, text=label_text, bg="white", font=("Arial", 8, "bold")).pack(anchor="w")
            widget = tk.Text(frame, height=6, width=55, font=("Arial", 9), bd=1, relief="solid")
            widget.insert("1.0", getattr(self.project, attr) or "")
            widget.pack(fill="both", expand=True)
            self.widgets[attr] = widget

        # --- ROW 0: Basic Info ---
        add_field(scrollable_frame, "Project Name:", "name", 0, 0)
        add_field(scrollable_frame, "Customer:", "customer", 0, 1)
        add_field(scrollable_frame, "Project Incharge:", "project_manager", 0, 2)
        add_field(scrollable_frame, "Total Cost:", "total_cost", 0, 3)

        # --- ROW 1: Parts & Tracking ---
        add_field(scrollable_frame, "Part Number:", "part_number", 1, 0)
        add_field(scrollable_frame, "Part Name:", "part_name", 1, 1)
        add_field(scrollable_frame, "PO Number:", "po_number", 1, 2)
        add_field(scrollable_frame, "Work Order:", "wo_number", 1, 3)

        # --- ROW 2: Dates & Duration ---
        add_field(scrollable_frame, "Planned Start:", "start_date", 2, 0, is_date=True)
        add_field(scrollable_frame, "Planned End:", "end_date", 2, 1, is_date=True)
        add_field(scrollable_frame, "Duration (Hrs):", "estimated_time", 2, 2)
        add_field(scrollable_frame, "Due Date:", "due_date", 2, 3, is_date=True)

        # --- ROW 3: Secondary Dates ---
        add_field(scrollable_frame, "PO Date:", "po_date", 3, 0, is_date=True)

        # --- LARGE TEXT AREAS (2 Per Row) ---
        add_text_area(scrollable_frame, "Scopes:", "scopes", 4, 0)
        add_text_area(scrollable_frame, "Out of Scopes:", "out_of_scopes", 4, 1)

        add_text_area(scrollable_frame, "Deliverables:", "deliverables", 5, 0)
        add_text_area(scrollable_frame, "Project Description:", "description", 5, 1)

        # Save Button
        btn_save = tk.Button(scrollable_frame, text="Save All Project Details", bg="#4CAF50", fg="white", 
                             command=self.save_changes, font=("Arial", 10, "bold"), padx=30, pady=12)
        btn_save.grid(row=6, column=0, columnspan=8, pady=30)

    def save_changes(self):
        data = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, tk.Text):
                data[key] = widget.get("1.0", tk.END).strip()
            elif isinstance(widget, DateEntry):
                data[key] = widget.get_date().strftime("%Y-%m-%d")
            else:
                data[key] = widget.get()

        try:
            self.db.update_project(self.project.id, data)
            # Sync local object with new UI values
            for key, val in data.items(): 
                setattr(self.project, key, val)
            messagebox.showinfo("Success", "All project details have been updated.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save to database: {e}")