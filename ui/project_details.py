# ui/project_details.py
import tkinter as tk
from tkinter import messagebox

class ProjectDetailsForm(tk.Frame):
    def __init__(self, parent, db, project):
        super().__init__(parent, bg="white")
        self.db = db
        self.project = project
        self.setup_ui()

    def setup_ui(self):
        # Header
        tk.Label(self, text=f"Edit Project: {self.project.name}", font=("Arial", 16, "bold"), bg="white").pack(anchor="w", pady=10, padx=20)

        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(fill="both", expand=True, padx=20)

        # Helper to create rows
        def create_row(label_text, value, row_idx, is_text_area=False):
            tk.Label(form_frame, text=label_text, bg="white", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="nw", pady=5)
            if is_text_area:
                widget = tk.Text(form_frame, width=50, height=6)
                widget.insert("1.0", value if value else "")
            else:
                widget = tk.Entry(form_frame, width=50)
                widget.insert(0, value if value else "")
            
            widget.grid(row=row_idx, column=1, sticky="w", pady=5, padx=10)
            return widget

        # Fields
        self.name_entry = create_row("Project Name:", self.project.name, 0)
        self.desc_text = create_row("Description:", self.project.description, 1, is_text_area=True)
        self.cust_entry = create_row("Customer:", self.project.customer, 2)
        self.time_entry = create_row("Est. Time:", self.project.estimated_time, 3)
        self.start_entry = create_row("Planned Date:", self.project.start_date, 4)
        self.end_entry = create_row("End Date:", self.project.end_date, 5)

        # Save Button
        btn_save = tk.Button(self, text="Save Changes", bg="#4CAF50", fg="white", command=self.save_changes, font=("Arial", 11), padx=20)
        btn_save.pack(anchor="w", padx=20, pady=20)

    def save_changes(self):
        data = {
            "name": self.name_entry.get(),
            "description": self.desc_text.get("1.0", tk.END).strip(),
            "customer": self.cust_entry.get(),
            "estimated_time": self.time_entry.get(),
            "start_date": self.start_entry.get(),
            "end_date": self.end_entry.get()
        }
        
        try:
            self.db.update_project(self.project.id, data)
            
            # Update local object
            self.project.name = data["name"]
            self.project.description = data["description"]
            self.project.customer = data["customer"]
            self.project.estimated_time = data["estimated_time"]
            self.project.start_date = data["start_date"]
            self.project.end_date = data["end_date"]
            
            messagebox.showinfo("Success", "Project details updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update project: {e}")