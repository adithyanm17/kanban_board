# ui/main_window.py
import tkinter as tk
from tkinter import simpledialog, messagebox
from ui.project_view import ProjectView
# Import the new helper function
from ui.dialogs import ask_new_project_info 

class MainWindow(tk.Tk):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.title("Python Kanban App")
        self.geometry("1200x700")
        self.current_project_view = None
        
        self.setup_ui()

    def setup_ui(self):
        # Sidebar for projects
        sidebar = tk.Frame(self, width=200, bg="#e0e0e0")
        sidebar.pack(side="left", fill="y")
        
        tk.Label(sidebar, text="Projects", font=("Arial", 14), bg="#e0e0e0", pady=10).pack()
        btn_new_proj = tk.Button(sidebar, text="+ New Project", command=self.create_project, bg="white")
        btn_new_proj.pack(fill="x", padx=10, pady=5)
        
        self.project_list_box = tk.Listbox(sidebar, bg="#e0e0e0", bd=0, highlightthickness=0, font=("Arial", 11))
        self.project_list_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.project_list_box.bind("<<ListboxSelect>>", self.on_project_select)

        # Main content area
        self.content_area = tk.Frame(self, bg="white")
        self.content_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        self.refresh_project_list()

    def create_project(self):
        # CHANGED: Use the custom dialog instead of askstring
        data = ask_new_project_info(self)
        
        if data and data['name']: # Ensure at least a name is provided
            project = self.db.create_project(data)
            if project:
                self.refresh_project_list()
            else:
                messagebox.showerror("Error", "Project name already exists.")

    def refresh_project_list(self):
        self.projects = self.db.get_projects()
        self.project_list_box.delete(0, tk.END)
        for p in self.projects:
            self.project_list_box.insert(tk.END, p.name)

    def on_project_select(self, event):
        selection = self.project_list_box.curselection()
        if selection:
            index = selection[0]
            project = self.projects[index]
            self.load_project_view(project)

    def load_project_view(self, project):
        if self.current_project_view:
            self.current_project_view.destroy()
        
        self.current_project_view = ProjectView(self.content_area, self.db, project)
        self.current_project_view.pack(fill="both", expand=True)