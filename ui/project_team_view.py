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
        
        tk.Label(header, text=f"Task Load for {self.project.name}", 
                font=("Arial", 14, "bold"), bg="white").pack(side="left")

        # Table showing ALL employees and how many tasks they have in this project
        cols = ("Code", "Name", "Designation", "Tasks Assigned")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # This fetches everyone in the master list and their specific count for this project
        # Ensure your database.py get_project_team_with_counts method uses a LEFT JOIN
        # on employees to ensure EVERYONE appears in the list.
        team_data = self.db.get_project_team_with_counts(self.project.id)
        for row in team_data:
            self.tree.insert("", "end", values=(row[1], row[2], row[3], row[4]))

        def add_to_project(self):
            selected = self.emp_var.get()
            if selected in self.emp_map:
                emp_id = self.emp_map[selected]
                self.db.add_member_to_project(self.project.id, emp_id)
                self.refresh_list()