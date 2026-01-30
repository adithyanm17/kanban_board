import tkinter as tk
from tkinter import simpledialog

class CreateTaskDialog(simpledialog.Dialog):
    def __init__(self, parent, team_members=None):
        self.team_members = team_members or [] # List of Employee objects
        self.check_vars = {} # Stores BooleanVar for each employee ID
        self.member_frames = {} # Stores UI frames for filtering
        self.title_str = None
        self.desc_str = None
        self.selected_member_ids = []
        super().__init__(parent, title="Create New Task")

    def body(self, master):
        self.geometry("450x600")
        
        # Task Title
        tk.Label(master, text="Title:").grid(row=0, sticky="w", pady=5)
        self.title_entry = tk.Entry(master, width=40)
        self.title_entry.grid(row=0, column=1, pady=5)

        # Task Description
        tk.Label(master, text="Description:").grid(row=1, sticky="nw", pady=5)
        self.desc_text = tk.Text(master, width=30, height=4)
        self.desc_text.grid(row=1, column=1, pady=5)

        # --- Searchable Checkbox List ---
        tk.Label(master, text="Assign To:").grid(row=2, sticky="nw", pady=(10, 0))
        
        # Real-time Search Entry
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_employees)
        search_entry = tk.Entry(master, textvariable=self.search_var, width=40)
        search_entry.insert(0, "Search employees...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, tk.END) if self.search_var.get() == "Search employees..." else None)
        search_entry.grid(row=3, column=1, pady=(0, 5), sticky="w")

        # Scrollable Area for Checkboxes
        list_frame = tk.Frame(master, bd=1, relief="sunken")
        list_frame.grid(row=4, column=1, sticky="nsew")
        
        canvas = tk.Canvas(list_frame, width=250, height=150)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Populate Employee Checkboxes
        for member in self.team_members:
            var = tk.BooleanVar()
            self.check_vars[member.id] = var
            
            f = tk.Frame(self.scrollable_frame)
            f.pack(fill="x", anchor="w")
            
            cb = tk.Checkbutton(f, text=f"{member.name} ({member.emp_code})", variable=var)
            cb.pack(side="left")
            
            # Store search metadata
            self.member_frames[member.id] = (f, member.name.lower(), member.emp_code.lower())

        return self.title_entry

    def filter_employees(self, *args):
        """Filters the checkbox list as the user types."""
        query = self.search_var.get().lower()
        if query == "search employees...": return
        
        for emp_id, (frame, name, code) in self.member_frames.items():
            if query in name or query in code:
                frame.pack(fill="x", anchor="w")
            else:
                frame.pack_forget()

    def apply(self):
        self.title_str = self.title_entry.get()
        self.desc_str = self.desc_text.get("1.0", tk.END).strip()
        # Collect all checked IDs
        self.selected_member_ids = [m_id for m_id, var in self.check_vars.items() if var.get()]


class CreateProjectDialog(simpledialog.Dialog):
    def __init__(self, parent):
        self.result_data = None
        super().__init__(parent, title="New Project Details")

    def body(self, master):
        self.geometry("500x550") 
        fields = [
            ("Project Name:", "name"),
            ("Customer Name:", "customer"),
            ("Estimated Time:", "estimated_time"),
            ("Planned Date (YYYY-MM-DD):", "start_date"),
            ("End Date (YYYY-MM-DD):", "end_date")
        ]
        
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(master, text=label).grid(row=i*2, column=0, sticky="w", pady=2)
            entry = tk.Entry(master, width=50)
            entry.grid(row=i*2+1, column=0, columnspan=2, pady=(0, 10))
            self.entries[key] = entry

        tk.Label(master, text="Description:").grid(row=10, column=0, sticky="nw")
        self.desc_text = tk.Text(master, width=50, height=5)
        self.desc_text.grid(row=11, column=0, columnspan=2, pady=(0, 10))

        return self.entries["name"]

    def apply(self):
        self.result_data = {k: v.get() for k, v in self.entries.items()}
        self.result_data["description"] = self.desc_text.get("1.0", tk.END).strip()


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


# --- Helper Functions (Required by other modules) ---

def ask_new_task_info(parent, team_members=None):
    dialog = CreateTaskDialog(parent, team_members=team_members)
    return dialog.title_str, dialog.desc_str, dialog.selected_member_ids

def ask_new_project_info(parent):
    dialog = CreateProjectDialog(parent)
    return dialog.result_data