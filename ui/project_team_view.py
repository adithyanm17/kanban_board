import tkinter as tk
from tkinter import ttk, messagebox

class ProjectTeamView(tk.Frame):
    def __init__(self, parent, db, project):
        super().__init__(parent, bg="white")
        self.db = db
        self.project = project
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", padx=20, pady=10)
        
        tk.Label(header, text=f"Team for {self.project.name}", 
                 font=("Arial", 14, "bold"), bg="white").pack(side="left")
        
        # Dropdown to select from ALL employees
        self.emp_var = tk.StringVar()
        self.emp_dropdown = ttk.Combobox(header, textvariable=self.emp_var, state="readonly", width=30)
        self.emp_dropdown.pack(side="right", padx=5)
        
        tk.Button(header, text="Add to Project", command=self.add_to_project, 
                  bg="#2196F3", fg="white").pack(side="right")

        # Table showing current project team
        cols = ("Code", "Name", "Designation")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

    def refresh_list(self):
        # 1. Update Dropdown with all available employees
        all_emps = self.db.get_employees()
        self.emp_map = {f"{e.name} ({e.emp_code})": e.id for e in all_emps}
        self.emp_dropdown['values'] = list(self.emp_map.keys())

        # 2. Update Table with project team
        for item in self.tree.get_children():
            self.tree.delete(item)
        for emp in self.db.get_project_team(self.project.id):
            self.tree.insert("", "end", values=(emp.emp_code, emp.name, emp.designation))

    def add_to_project(self):
        selected = self.emp_var.get()
        if selected in self.emp_map:
            emp_id = self.emp_map[selected]
            self.db.add_member_to_project(self.project.id, emp_id)
            self.refresh_list()
        else:
            messagebox.showwarning("Selection", "Please select an employee first.")