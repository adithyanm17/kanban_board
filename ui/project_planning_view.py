import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

class ProjectPlanningView(tk.Frame):
    def __init__(self, parent, db, project):
        super().__init__(parent, bg="white")
        self.db = db
        self.project = project
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        # --- Input Area ---
        input_frame = tk.LabelFrame(self, text="Add Planning Item", bg="white", padx=10, pady=10)
        input_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(input_frame, text="Todo Item:", bg="white").grid(row=0, column=0, sticky="w")
        self.todo_entry = tk.Entry(input_frame, width=40)
        self.todo_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Planned Date:", bg="white").grid(row=0, column=2, sticky="w")
        self.start_date = DateEntry(input_frame, width=15, date_pattern='yyyy-mm-dd')
        self.start_date.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="End Date:", bg="white").grid(row=0, column=4, sticky="w")
        self.end_date = DateEntry(input_frame, width=15, date_pattern='yyyy-mm-dd')
        self.end_date.grid(row=0, column=5, padx=5)

        btn_add = tk.Button(input_frame, text="Add to Plan", bg="#2196F3", fg="white", 
                            command=self.add_plan, padx=10)
        btn_add.grid(row=0, column=6, padx=10)

        # --- Table View ---
        cols = ("ID", "Todo Item", "Start Date", "End Date")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
        
        # Hide ID column
        self.tree.column("ID", width=0, stretch=tk.NO)
        self.tree.column("Todo Item", width=400)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Right-click to delete
        self.tree.bind("<Button-3>", self.show_context_menu)

    def add_plan(self):
        todo = self.todo_entry.get()
        start = self.start_date.get_date().strftime("%Y-%m-%d")
        end = self.end_date.get_date().strftime("%Y-%m-%d")

        if not todo:
            messagebox.showwarning("Input Error", "Please enter a todo item.")
            return

        self.db.add_plan_item(self.project.id, todo, start, end)
        self.todo_entry.delete(0, tk.END)
        self.refresh_list()

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        plans = self.db.get_project_plans(self.project.id)
        for row in plans:
            # row is (id, project_id, todo_item, start_date, end_date)
            self.tree.insert("", "end", values=(row[0], row[2], row[3], row[4]))

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label="Delete Item", command=self.delete_selected)
            menu.post(event.x_root, event.y_root)

    def delete_selected(self):
        selected = self.tree.selection()
        if selected:
            plan_id = self.tree.item(selected[0])['values'][0]
            if messagebox.askyesno("Confirm", "Delete this planning item?"):
                self.db.delete_plan_item(plan_id)
                self.refresh_list()