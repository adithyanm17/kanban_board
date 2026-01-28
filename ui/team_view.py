import tkinter as tk
from tkinter import ttk
from ui.dialogs import EmployeeDialog


class TeamView(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent, bg="white")
        self.db = db
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", padx=20, pady=10)
        
        tk.Label(header, text="Team Management", font=("Arial", 16, "bold"), bg="white").pack(side="left")
        tk.Button(header, text="+ Add Member", command=self.add_member, bg="#4CAF50", fg="white").pack(side="right")
        tk.Button(header, text="Edit Selected", command=self.edit_member).pack(side="right", padx=10)

        # Table
        cols = ("Code", "Name", "Designation", "Email", "GitHub")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Assuming you add get_employees() to database.py
        for emp in self.db.get_employees():
            self.tree.insert("", "end", iid=emp.id, values=(emp.emp_code, emp.name, emp.designation, emp.email, emp.github))

    def add_member(self):
        dialog = EmployeeDialog(self, "Add Team Member")
        if dialog.result_data:
            self.db.save_employee(dialog.result_data)
            self.refresh_list()

    def edit_member(self):
        selected = self.tree.selection()
        if not selected:
            return
        emp_id = selected[0]
        # Fetch employee object from DB, then pass to EmployeeDialog
        emp = self.db.get_employee_by_id(emp_id)
        dialog = EmployeeDialog(self, "Edit Member", employee=emp)
        if dialog.result_data:
            self.db.update_employee(emp_id, dialog.result_data)
            self.refresh_list()