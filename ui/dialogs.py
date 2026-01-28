import tkinter as tk
from tkinter import simpledialog

class CreateTaskDialog(simpledialog.Dialog):
    def __init__(self, parent, team_members=None):
        self.team_members = team_members or [] # List of Employee objects
        self.selected_member_ids = []
        self.title_str = None
        self.desc_str = None
        super().__init__(parent, title="Create New Task")

    def body(self, master):
        self.geometry("400x500")
        
        tk.Label(master, text="Title:").grid(row=0, sticky="w", pady=5)
        self.title_entry = tk.Entry(master, width=40)
        self.title_entry.grid(row=0, column=1, pady=5)

        tk.Label(master, text="Description:").grid(row=1, sticky="nw", pady=5)
        self.desc_text = tk.Text(master, width=30, height=5)
        self.desc_text.grid(row=1, column=1, pady=5)

        # Assignee Selection
        tk.Label(master, text="Assign To:").grid(row=2, sticky="nw", pady=10)
        
        # Using a Listbox with Multiple selection mode
        self.member_listbox = tk.Listbox(master, selectmode="multiple", width=30, height=6)
        self.member_listbox.grid(row=2, column=1, pady=10)
        
        for member in self.team_members:
            self.member_listbox.insert(tk.END, f"{member.name} ({member.emp_code})")

        return self.title_entry

    def apply(self):
        self.title_str = self.title_entry.get()
        self.desc_str = self.desc_text.get("1.0", tk.END).strip()
        
        # Get IDs of selected members
        selected_indices = self.member_listbox.curselection()
        self.selected_member_ids = [self.team_members[i].id for i in selected_indices]

class CreateProjectDialog(simpledialog.Dialog):
    def __init__(self, parent):
        self.result_data = None
        super().__init__(parent, title="New Project Details")

    def body(self, master):
        # 1. Make the dialog bigger
        self.geometry("500x500") 

        # 2. Project Name
        tk.Label(master, text="Project Name:").grid(row=0, sticky=tk.W, pady=5)
        self.name_entry = tk.Entry(master, width=50)
        self.name_entry.grid(row=0, column=1, pady=5)

        # 3. Description - FIXED LINE BELOW (tk.NW)
        tk.Label(master, text="Description:").grid(row=1, sticky=tk.NW, pady=5)
        self.desc_text = tk.Text(master, width=50, height=6)
        self.desc_text.grid(row=1, column=1, pady=5)

        # 4. Customer Name
        tk.Label(master, text="Customer Name:").grid(row=2, sticky=tk.W, pady=5)
        self.customer_entry = tk.Entry(master, width=50)
        self.customer_entry.grid(row=2, column=1, pady=5)

        # 5. Estimated Time
        tk.Label(master, text="Estimated Time:").grid(row=3, sticky=tk.W, pady=5)
        self.time_entry = tk.Entry(master, width=50)
        self.time_entry.grid(row=3, column=1, pady=5)

        # 6. Planned Date
        tk.Label(master, text="Planned Date (YYYY-MM-DD):").grid(row=4, sticky=tk.W, pady=5)
        self.start_date_entry = tk.Entry(master, width=50)
        self.start_date_entry.grid(row=4, column=1, pady=5)

        # 7. End Date
        tk.Label(master, text="End Date (YYYY-MM-DD):").grid(row=5, sticky=tk.W, pady=5)
        self.end_date_entry = tk.Entry(master, width=50)
        self.end_date_entry.grid(row=5, column=1, pady=5)

        return self.name_entry

    def apply(self):
        self.result_data = {
            "name": self.name_entry.get(),
            "description": self.desc_text.get("1.0", tk.END).strip(),
            "customer": self.customer_entry.get(),
            "estimated_time": self.time_entry.get(),
            "start_date": self.start_date_entry.get(),
            "end_date": self.end_date_entry.get()
        }
class EmployeeDialog(simpledialog.Dialog):
    def __init__(self, parent, title, employee=None):
        self.employee = employee
        self.result_data = None
        super().__init__(parent, title=title)

    def body(self, master):
        self.geometry("400x450")
        fields = [
            ("Employee Code:", "emp_code"),
            ("Name:", "name"),
            ("Date of Joining:", "doj"),
            ("Designation:", "designation"),
            ("Email ID:", "email"),
            ("GitHub Account:", "github")
        ]
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(master, text=label).grid(row=i, column=0, sticky="w", pady=5)
            entry = tk.Entry(master, width=30)
            entry.grid(row=i, column=1, pady=5, padx=10)
            if self.employee:
                val = getattr(self.employee, key)
                entry.insert(0, val if val else "")
            self.entries[key] = entry
        return self.entries["emp_code"]

    def apply(self):
        self.result_data = {k: v.get() for k, v in self.entries.items()}
def ask_new_task_info(parent):
    dialog = CreateTaskDialog(parent)
    return dialog.title_str, dialog.desc_str

def ask_new_project_info(parent):
    dialog = CreateProjectDialog(parent)
    return dialog.result_data